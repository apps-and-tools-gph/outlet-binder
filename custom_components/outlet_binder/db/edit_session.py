"""The edit-session engine: append, undo, redo, flush, commit, and the
clone-replay projection that backs both validation and the `*`-marker
diff (#189).

Lives directly under db/, not db/operations/, even though it dispatches
to that layer's plug and unplug functions by name (the `_DISPATCH_TABLE`
below) -- exactly as websocket_api.py already does today, one layer up. It
does not sequence their writes, touch their SQL, or duplicate their
validation, so it is orchestration *above* the operations layer rather than
a peer operation reaching sideways into another concept's writes -- the
thing db/operations/__init__.py's "modules never import one another" rule
exists to prevent. Placing it here instead of alongside them needs no
documented exception to that rule at all.

No WebSocket surface lives here; the WS commands are in websocket_api.py.

## Why clone-replay, not a rolled-back transaction

Projection cannot be "replay the log inside a transaction, then roll
back": every db/operations/ function -- including each one
this module dispatches to -- opens its own `BEGIN IMMEDIATE` via
db/sql/transaction.py's `immediate`, which raises `RuntimeError` on a
second `BEGIN` on the same connection (tests/test_sql_transaction.py:
74-78 pins this), and there is no `SAVEPOINT` support anywhere in the
repo.

Replaying instead against a throwaway in-memory clone
(`sqlite3.Connection.backup()`) needs no change to those functions and
no transaction nesting: each opens and commits its own transaction
against the clone exactly as it would against the real connection, and
the clone is discarded afterwards. `sqlite3.connect(...)` is called
directly here rather than through db/session.py's `connect` -- the same
pattern db/migrate.py's own `_write_backup`/`_restore_backup` already use
for their transient backup connection, which is not "the real app
connection" db/session.py exists to gate either.

## The asymmetry decision

The staged commands do not fail the same way (settled per command,
docs/LLD.md, the write commands' error mapping): the ones that plug
(create_plugged_into, assign_co_to_uo, assign_co_to_co_socket,
assign_appliance_to_uo) raise NotFoundError when either end is
missing; the ones that unplug are idempotent no-ops on a stale id. So a
staged entry whose target was deleted by a later immediate write fails replay in one direction and
silently succeeds in the other.

**Decision: leave that asymmetry alone.** No pre-dispatch existence check
is added to force the idempotent pair to fail too. Two reasons: first,
the resulting projection is still correct either way -- an unplug/
unassign of an already-gone target achieves the same end state (not
linked) whether the target vanished by deletion or by this command, so
there is nothing wrong to report. Second, detecting "the target vanished"
before dispatching would duplicate the existence check the idempotent
functions already perform internally, as a second copy of logic with no
behavioural payoff beyond manufacturing a failure for an operation that
already correctly succeeded.

## Loops and fixed devices

A plug that would make a device its own ancestor raises `LoopError`
(domain/chain.py), and a plug of a device with no plug of its own raises
`FixedDeviceError`. Staging checks neither: `append` stays a bare append, and
the plug is refused when replay reaches it -- shown as `failed_entry` in the
preview, with the entry and everything after it not applied -- and again at
`commit`. A loop can depend on earlier staged entries (stage A into B, then
B into A), so only a replay can tell.

## Why commit() has no cross-entry atomicity

Each of those functions commits for real as it runs; there is no
outer transaction to wrap them in (the same nesting restriction that
rules out a rolled-back replay above). If one entry raises partway
through a commit, entries before it are already committed and stay that
way -- this mirrors every other multi-step db/operations/ sequence in
this codebase, none of which has cross-function atomicity either. A
retry is safe: re-dispatching an already-applied entry is idempotent by
effect (each plug unconditionally displaces-then-inserts; unplug/unassign are
no-ops once already applied), so retrying a failed
commit simply re-does the harmless prefix and reports the same failure.
One visible side effect of that replay-on-retry: `plug_log`
gains a zero-duration closed/reopened row each time an already-applied
plug entry is re-dispatched (its own close-then-open
history bookkeeping runs again, with the same `appended_at` both times).
Harmless -- current state is unaffected -- but real, and not worth
machinery to suppress given this project's one-writer scale.

History: docs/HISTORY-INDEX.md
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from ..domain.identifiers import (
    ApplianceId,
    CoId,
    DeviceId,
    SocketId,
    Timestamp,
    UoId,
)
from ..domain.models import EditLogEntry
from .operations.errors import FixedDeviceError, LoopError, NotFoundError
from .operations.plug import (
    assign_co_to_uo,
    create_plugged_into,
    plug_appliance_into_uo,
    plug_co_into_co_socket,
    unassign_co_from_uo,
    unplug_appliance_from_uo,
    unplug_co_from_co_socket,
    unplug_plugged_into,
)
from .operations.state import get_full_state
from .sql import edit_session as edit_session_sql
from .sql import pragma, transaction

EditCommand = Literal[
    "create_plugged_into",
    "unplug_plugged_into",
    "assign_co_to_uo",
    "unassign_co_from_uo",
    "assign_co_to_co_socket",
    "unassign_co_from_co_socket",
    "assign_appliance_to_uo",
    "unassign_appliance_from_uo",
]

# The fixed payload vocabulary (#189's issue body): each staged command
# takes exactly these keys, and every value is a bare id string -- the
# NewTypes below erase to str at runtime, so a JSON payload is already
# their wire shape. Wrapping happens only at dispatch time.
REQUIRED_KEYS: dict[EditCommand, frozenset[str]] = {
    "create_plugged_into": frozenset({"appliance_id", "co_socket_id"}),
    "unplug_plugged_into": frozenset({"appliance_id"}),
    "assign_co_to_uo": frozenset({"co_id", "uo_id"}),
    "unassign_co_from_uo": frozenset({"co_id"}),
    "assign_co_to_co_socket": frozenset({"co_id", "co_socket_id"}),
    "unassign_co_from_co_socket": frozenset({"co_id"}),
    "assign_appliance_to_uo": frozenset({"appliance_id", "uo_id"}),
    "unassign_appliance_from_uo": frozenset({"appliance_id"}),
}


class _DispatchHandler(Protocol):
    """The exact shape of `_dispatch_*` below -- `payload`/`now` are
    keyword-only, so a plain `Callable[[Connection, dict, Timestamp],
    None]` would describe a positional call `_DISPATCH_TABLE` never
    makes and mypy would reject as incompatible with these functions."""

    def __call__(
        self, conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
    ) -> None: ...


def _dispatch_create_plugged_into(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    create_plugged_into(
        conn,
        appliance_id=ApplianceId(DeviceId(payload["appliance_id"])),
        socket_id=SocketId(payload["co_socket_id"]),
        now=now,
    )


def _dispatch_unplug_plugged_into(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    unplug_plugged_into(conn, appliance_id=ApplianceId(DeviceId(payload["appliance_id"])), now=now)


def _dispatch_assign_co_to_uo(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    assign_co_to_uo(
        conn,
        co_id=CoId(DeviceId(payload["co_id"])),
        uo_id=UoId(DeviceId(payload["uo_id"])),
        now=now,
    )


def _dispatch_unassign_co_from_uo(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    unassign_co_from_uo(conn, co_id=CoId(DeviceId(payload["co_id"])), now=now)


def _dispatch_assign_co_to_co_socket(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    plug_co_into_co_socket(
        conn,
        co_id=CoId(DeviceId(payload["co_id"])),
        socket_id=SocketId(payload["co_socket_id"]),
        now=now,
    )


def _dispatch_unassign_co_from_co_socket(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    unplug_co_from_co_socket(conn, co_id=CoId(DeviceId(payload["co_id"])), now=now)


def _dispatch_assign_appliance_to_uo(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    plug_appliance_into_uo(
        conn,
        appliance_id=ApplianceId(DeviceId(payload["appliance_id"])),
        uo_id=UoId(DeviceId(payload["uo_id"])),
        now=now,
    )


def _dispatch_unassign_appliance_from_uo(
    conn: sqlite3.Connection, *, payload: dict[str, str], now: Timestamp
) -> None:
    unplug_appliance_from_uo(
        conn, appliance_id=ApplianceId(DeviceId(payload["appliance_id"])), now=now
    )


# Not named `execute` -- tests/test_sql_layer_guard.py's
# test_no_sql_execution_outside_db_sql matches the attribute name on any
# receiver, not just sqlite3.Connection.
_DISPATCH_TABLE: dict[EditCommand, _DispatchHandler] = {
    "create_plugged_into": _dispatch_create_plugged_into,
    "unplug_plugged_into": _dispatch_unplug_plugged_into,
    "assign_co_to_uo": _dispatch_assign_co_to_uo,
    "unassign_co_from_uo": _dispatch_unassign_co_from_uo,
    "assign_co_to_co_socket": _dispatch_assign_co_to_co_socket,
    "unassign_co_from_co_socket": _dispatch_unassign_co_from_co_socket,
    "assign_appliance_to_uo": _dispatch_assign_appliance_to_uo,
    "unassign_appliance_from_uo": _dispatch_unassign_appliance_from_uo,
}


def _apply_entry(conn: sqlite3.Connection, entry: EditLogEntry) -> None:
    payload: dict[str, str] = json.loads(entry.payload)
    handler = _DISPATCH_TABLE[entry.command]  # type: ignore[index]
    handler(conn, payload=payload, now=entry.appended_at)


@dataclass(frozen=True)
class FailedEntry:
    """A staged entry that stopped replay -- see `project`'s docstring."""

    entry_seq: int
    command: str
    message: str


def _cursor_seq(conn: sqlite3.Connection) -> int:
    """The current cursor, or 0 before the first-ever append -- the
    read-only counterpart to `_ensure_session` below, which also seeds
    the row. Every reader shares this one place that knows an unstarted
    session reads as cursor 0."""
    session = edit_session_sql.get_session(conn)
    return session.cursor_seq if session is not None else 0


def _ensure_session(conn: sqlite3.Connection) -> int:
    """`_cursor_seq`, seeding the singleton `edit_session` row (structurally
    enforced, #241) on first use -- only `append` needs the write side;
    every other caller only ever reads, so it calls `_cursor_seq`
    instead."""
    session = edit_session_sql.get_session(conn)
    if session is None:
        edit_session_sql.insert_session(conn, cursor_seq=0)
        return 0
    return session.cursor_seq


def append(
    conn: sqlite3.Connection,
    *,
    command: EditCommand,
    payload: dict[str, str],
    now: Timestamp,
    continue_group: bool = False,
) -> int:
    """Stage one connection-command edit. Returns its `entry_seq`.

    Nothing is validated against current state here -- that is the whole
    point of staging: the target need not exist yet, and validation
    happens at projection/commit time via `project`/`commit`. Only the
    payload's own shape is checked, since the WS schema is the real
    boundary and this is a cheap consistency check against it.

    A new append while the cursor sits behind the end of the log discards
    every entry ahead of it first -- editing after an undo overwrites the
    redo tail rather than branching it.

    `continue_group` attaches this entry to the group of the entry
    currently at the cursor (the tail) rather than starting a fresh one --
    used by a multi-command Apply so the whole batch undoes as one step
    (#190). There is no client-supplied group id: a caller can only ever
    extend *the* tail, which is what makes a non-contiguous or overlapping
    group unrepresentable rather than merely discouraged. At an empty log
    (cursor 0) there is no tail entry to extend, so this falls back to a
    fresh group exactly as `continue_group=False` would.
    """
    required = REQUIRED_KEYS[command]
    if payload.keys() != required:
        raise ValueError(f"{command} requires exactly {sorted(required)}, got {sorted(payload)}")

    with transaction.immediate(conn):
        cursor_seq = _ensure_session(conn)
        edit_session_sql.delete_entries_after(conn, after_seq=cursor_seq)
        group_seq = (
            edit_session_sql.group_seq_of(conn, entry_seq=cursor_seq)
            if continue_group and cursor_seq != 0
            else edit_session_sql.next_group_seq(conn)
        )
        entry_seq = edit_session_sql.append_entry(
            conn,
            command=command,
            payload=json.dumps(payload, sort_keys=True),
            appended_at=now,
            group_seq=group_seq,
        )
        edit_session_sql.update_cursor(conn, cursor_seq=entry_seq)
    return entry_seq


def undo(conn: sqlite3.Connection) -> int:
    """Move the cursor back past the whole group at the cursor, in one
    call (#190 -- one Apply is one undo step). A no-op at the start of the
    log -- boundary undo/redo calls are idempotent, matching the
    staged commands' own idempotent-at-the-boundary style. Returns the new
    cursor."""
    with transaction.immediate(conn):
        cursor_seq = _cursor_seq(conn)
        if cursor_seq == 0:
            return 0
        group_seq = edit_session_sql.group_seq_of(conn, entry_seq=cursor_seq)
        new_cursor = edit_session_sql.min_entry_seq_in_group(conn, group_seq=group_seq) - 1
        edit_session_sql.update_cursor(conn, cursor_seq=new_cursor)
    return new_cursor


def redo(conn: sqlite3.Connection) -> int:
    """Move the cursor forward past the whole group immediately ahead of
    it, in one call. A no-op at the end of the log. Returns the new
    cursor."""
    with transaction.immediate(conn):
        cursor_seq = _cursor_seq(conn)
        entry_count = edit_session_sql.count_entries(conn)
        if cursor_seq >= entry_count:
            return cursor_seq
        next_seq = edit_session_sql.first_entry_seq_after(conn, after_seq=cursor_seq)
        assert next_seq is not None  # cursor_seq < entry_count guarantees one exists
        group_seq = edit_session_sql.group_seq_of(conn, entry_seq=next_seq)
        new_cursor = edit_session_sql.max_entry_seq_in_group(conn, group_seq=group_seq)
        edit_session_sql.update_cursor(conn, cursor_seq=new_cursor)
    return new_cursor


def entry_count(conn: sqlite3.Connection) -> int:
    """Every entry in the log, staged or redoable."""
    return edit_session_sql.count_entries(conn)


def withdraw(conn: sqlite3.Connection, *, entry_seq: int) -> None:
    """Take back the entry `append` just returned, putting the cursor back
    at the end of what is left -- how immediate mode undoes a refused
    auto-commit (#524). It must still be the tail with the cursor on it,
    which a failed `commit` guarantees because it never reached `flush`.

    Any redo tail `append` discarded is not restored. Immediate mode has
    none: the options flow refuses the switch while the log has entries."""
    with transaction.immediate(conn):
        # `entry_seq` is dense (only the tail is ever deleted, and SQLite
        # reuses the freed rowid), so the count is the tail's seq.
        assert _cursor_seq(conn) == entry_seq == edit_session_sql.count_entries(conn)
        edit_session_sql.delete_entry(conn, entry_seq=entry_seq)
        edit_session_sql.update_cursor(conn, cursor_seq=entry_seq - 1)


def flush(conn: sqlite3.Connection) -> None:
    """Discard the whole log -- staged and redo-tail entries alike -- and
    reset the cursor. Ends the session without writing anything staged.

    `update_cursor` needs no existence guard: its `UPDATE` matches zero
    rows and does nothing when no session has ever started, the same
    outcome as skipping it."""
    with transaction.immediate(conn):
        edit_session_sql.delete_all_entries(conn)
        edit_session_sql.update_cursor(conn, cursor_seq=0)


def commit(conn: sqlite3.Connection) -> None:
    """Apply every entry up to the cursor for real, then start a fresh
    session (flush).

    Each entry supplies its own `now` (the log row's `appended_at`,
    recorded at append time) rather than a fresh timestamp taken here --
    so a projected diff and the committed result agree on when each
    change happened. See the module docstring for why a failure partway
    through leaves earlier entries committed rather than rolling back,
    and for the zero-duration history row a retry can leave behind.
    """
    cursor_seq = _cursor_seq(conn)
    for entry in edit_session_sql.list_entries_up_to(conn, up_to_seq=cursor_seq):
        _apply_entry(conn, entry)
    flush(conn)


def _clone(conn: sqlite3.Connection) -> sqlite3.Connection:
    """A throwaway in-memory copy of `conn`'s database -- see the module
    docstring for why `sqlite3.connect` is called directly here rather
    than through db/session.py's `connect` (mirrors db/migrate.py's own
    transient backup connection)."""
    clone = sqlite3.connect(":memory:", autocommit=True)
    clone.row_factory = sqlite3.Row
    pragma.enable_foreign_keys(clone)
    conn.backup(clone)
    return clone


def _replay_collecting_failure(
    conn: sqlite3.Connection, entries: list[EditLogEntry]
) -> FailedEntry | None:
    """Apply `entries` in order, stopping at (and reporting) the first
    that raises `NotFoundError`, `FixedDeviceError` or `LoopError` rather than
    propagating it -- used by
    `project`, where a broken staged entry is something to *show*, not an
    exception to raise. `commit` does not use this: a write failing is
    reported the same way every other db/operations/ write already is."""
    for entry in entries:
        try:
            _apply_entry(conn, entry)
        except (NotFoundError, FixedDeviceError, LoopError) as err:
            return FailedEntry(entry_seq=entry.entry_seq, command=entry.command, message=str(err))
    return None


def project(
    conn: sqlite3.Connection, *, up_to_seq: int
) -> tuple[dict[str, list[dict[str, Any]]], FailedEntry | None]:
    """The full application state with every entry through `up_to_seq`
    replayed over it, plus the first entry that failed to replay, if any.

    `up_to_seq=0` (or an empty log) needs no clone: replaying nothing is
    just the stored state, read directly off `conn`. Otherwise a clone is
    made, entries are replayed against it via the real db/operations/
    functions, state is read off the clone, and the clone is discarded.
    See the module docstring for the asymmetry decision this embeds via
    `_apply_entry`/`_replay_collecting_failure`: a failing entry stops
    replay and the returned state reflects only what came before it; an
    idempotent no-op on a since-vanished target is not treated as a
    failure at all.
    """
    entries = edit_session_sql.list_entries_up_to(conn, up_to_seq=up_to_seq)
    if not entries:
        return get_full_state(conn), None
    clone = _clone(conn)
    try:
        failed = _replay_collecting_failure(clone, entries)
        return get_full_state(clone), failed
    finally:
        clone.close()


def _diff_map(
    baseline_rows: list[dict[str, Any]],
    projected_rows: list[dict[str, Any]],
    *,
    id_key: str,
    fields: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    """One entity type's slice of the wire diff (#189's "What the diff
    must return"): id -> {field: stored value for every field in
    `fields`}, present only where at least one of them changed.
    Compared over `fields` only, not the whole row -- the plug commands
    also touch `co.updated_at`, and a blind diff would mark a row pending
    because of a timestamp the panel never displays. The entry carries
    every field, not just the changed ones, because a row can have two
    (a CO's Unmanaged Outlet and its CO socket) and the panel reads the
    stored place as a whole: an absent field would read as `undefined`
    rather than as the stored value.
    """
    stored_by_id = {row[id_key]: row for row in baseline_rows}
    result: dict[str, dict[str, Any]] = {}
    for row in projected_rows:
        entity_id = row[id_key]
        # A projected row with no baseline row has nothing stored: every
        # field reads as None, which differs from the projected value, so it
        # is reported as changed.
        stored = stored_by_id.get(entity_id)
        stored_fields = {field: stored[field] if stored is not None else None for field in fields}
        if any(row[field] != stored_fields[field] for field in fields):
            result[entity_id] = stored_fields
    return result


def _entry_wire(entry: EditLogEntry) -> dict[str, Any]:
    """One edit_log entry's wire shape for a consequence listing
    (commit_entries/flush_entries) -- `payload` decoded from its opaque
    stored string into the JSON object it actually is. `group_seq`
    (#301) lets the frontend number a range's listing by group rather than
    by raw entry -- the group count already shown next to a button can
    otherwise disagree with a flat per-entry line count whenever a
    continue_group batch sits in the range. It also lets the frontend
    derive Undo's full preview as commit_entries's groups reversed, and
    Redo's as flush_entries's tail past commit_entries -- no separate
    single-group field or query is needed for either."""
    return {
        "entry_seq": entry.entry_seq,
        "command": entry.command,
        "payload": json.loads(entry.payload),
        "group_seq": entry.group_seq,
    }


# Entity key in the wire object -> (id column, the fields the staged
# commands can ever change on that entity). One data table instead of three
# near-identical _diff_map calls -- see _diff_map's own docstring for why
# the comparison covers these fields, not the whole row.
_DIFF_SPECS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("appliances", "appliance_id", ("plugged_into_co_socket_id", "uo_id")),
    ("co_sockets", "co_socket_id", ("plugged_into_appliance_id", "occupant_device_id")),
    ("cos", "co_id", ("uo_id", "plugged_into_co_socket_id")),
)


def projected_state_and_diff(
    conn: sqlite3.Connection,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """The projected application state, plus the `edit_session` wire
    object `get_state` attaches alongside it -- built together so
    the shape has exactly one definition and callers needing both (i.e.
    `get_state` itself) pay for one baseline read and one clone rather
    than two. See #189's issue body ("What the diff must return") for the
    full sidecar contract; this is its reference implementation, not a
    re-derivation of it.
    """
    cursor_seq = _cursor_seq(conn)
    entry_count = edit_session_sql.count_entries(conn)

    baseline = get_full_state(conn)
    # At cursor 0 the projection is the stored state by definition --
    # project()'s own empty-entries branch would compute the identical
    # get_full_state(conn) a second time, so it is skipped here.
    if cursor_seq == 0:
        projected, failed = baseline, None
    else:
        projected, failed = project(conn, up_to_seq=cursor_seq)

    # At cursor 0, projected is baseline (see above) -- every _diff_map
    # call would compare each row against itself and return {}. Skipped
    # rather than computed and discarded: get_state calls this on every
    # panel load and refresh, and "nothing staged" is the overwhelmingly
    # common case.
    diffs = (
        {key: {} for key, _, _ in _DIFF_SPECS}
        if cursor_seq == 0
        else {
            key: _diff_map(baseline[key], projected[key], id_key=id_key, fields=fields)
            for key, id_key, fields in _DIFF_SPECS
        }
    )
    sidecar = {
        "cursor_seq": cursor_seq,
        "entry_count": entry_count,
        # True undo/redo-step counts (#300), distinct from cursor_seq/
        # entry_count's raw entry counts -- see count_groups_up_to's
        # docstring for the no-straddle invariant these depend on.
        "undo_group_count": edit_session_sql.count_groups_up_to(conn, up_to_seq=cursor_seq),
        "redo_group_count": edit_session_sql.count_groups_after(conn, after_seq=cursor_seq),
        # Full consequence listings, not just counts -- Commit's is scoped
        # to [1, cursor_seq] (the exact range it replays), Flush's to the
        # whole log [1, entry_count] (a superset whenever a redo tail
        # exists past the cursor -- the two must be able to differ, see
        # test_flush_entries_lists_the_whole_log_including_any_redo_tail).
        # Both reuse list_entries_up_to with a different bound; no new SQL.
        "commit_entries": [
            _entry_wire(e) for e in edit_session_sql.list_entries_up_to(conn, up_to_seq=cursor_seq)
        ],
        "flush_entries": [
            _entry_wire(e) for e in edit_session_sql.list_entries_up_to(conn, up_to_seq=entry_count)
        ],
        "failed_entry": None
        if failed is None
        else {"entry_seq": failed.entry_seq, "command": failed.command, "message": failed.message},
        **diffs,
    }
    return projected, sidecar


def diff_from_baseline(conn: sqlite3.Connection) -> dict[str, Any]:
    """The `edit_session` sidecar alone -- a thin wrapper over
    `projected_state_and_diff` for callers that don't need the projected
    state itself (this module's own tests)."""
    _, sidecar = projected_state_and_diff(conn)
    return sidecar
