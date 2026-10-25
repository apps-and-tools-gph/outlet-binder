"""Every SQL statement about the edit-session concept (issue #189).

Two tables, one idea: `edit_log` is the append-only record of every staged
connection-command edit, `edit_session` is the single-row cursor into it.
They live in one module because the session is this log's own state, not
a separate concept. `edit_session`'s single row is enforced by
its `singleton` primary key (`CHECK (singleton = 1)`) rather
than by convention -- a second row is unrepresentable, not merely avoided.

`edit_log` carries no foreign keys: `payload` is an opaque JSON blob of
command arguments, not typed columns, so there is nothing here for a
REFERENCES clause to point at -- that is deliberate (docs/DECISIONS.md),
since the whole point is a log table whose shape never changes as staged
commands are added.

Nothing here opens a transaction, dispatches a command, or knows what a
command payload means -- that is db/edit_session.py's job.
"""

import sqlite3

from ...domain.identifiers import Timestamp
from ...domain.models import EditLogEntry, EditSession


def create_log_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE edit_log (
          entry_seq   INTEGER PRIMARY KEY,
          command     TEXT NOT NULL,
          payload     TEXT NOT NULL,
          appended_at TEXT NOT NULL,
          group_seq   INTEGER NOT NULL
        )
        """
    )


def create_session_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE edit_session (
          singleton  INTEGER PRIMARY KEY CHECK (singleton = 1),
          cursor_seq INTEGER NOT NULL
        )
        """
    )


def _to_entry(row: sqlite3.Row) -> EditLogEntry:
    return EditLogEntry(
        entry_seq=row["entry_seq"],
        command=row["command"],
        payload=row["payload"],
        appended_at=row["appended_at"],
        group_seq=row["group_seq"],
    )


def append_entry(
    conn: sqlite3.Connection,
    *,
    command: str,
    payload: str,
    appended_at: Timestamp,
    group_seq: int,
) -> int:
    """Insert one log row and return its `entry_seq`.

    `.lastrowid` is safe here specifically because `entry_seq` is declared
    `INTEGER PRIMARY KEY` -- SQLite's rowid alias -- so it names the row
    just inserted on this connection, not a guess.
    """
    cursor = conn.execute(
        "INSERT INTO edit_log (command, payload, appended_at, group_seq)"
        " VALUES (:command, :payload, :appended_at, :group_seq)",
        {
            "command": command,
            "payload": payload,
            "appended_at": appended_at,
            "group_seq": group_seq,
        },
    )
    assert cursor.lastrowid is not None  # just inserted this row
    return cursor.lastrowid


def next_group_seq(conn: sqlite3.Connection) -> int:
    """A group id not yet used by any row still in the log -- `MAX+1`
    computed explicitly, mirroring SQLite's own rowid-reuse arithmetic for
    `entry_seq` (see `append`'s docstring), since `group_seq` is a plain
    column rather than the table's primary key."""
    row = conn.execute("SELECT COALESCE(MAX(group_seq), 0) + 1 AS next FROM edit_log").fetchone()
    return row["next"]


def group_seq_of(conn: sqlite3.Connection, *, entry_seq: int) -> int:
    """The group a given entry belongs to. Only ever called with an
    `entry_seq` known to exist (the cursor, or the first entry past it)."""
    row = conn.execute(
        "SELECT group_seq FROM edit_log WHERE entry_seq = ?", (entry_seq,)
    ).fetchone()
    assert row is not None
    return row["group_seq"]


def min_entry_seq_in_group(conn: sqlite3.Connection, *, group_seq: int) -> int:
    """Only ever called with a `group_seq` known to have at least one row
    -- the caller always derived it from an existing entry's own
    `group_seq` (see `group_seq_of`). A zero-row match would mean the
    group invariant broke elsewhere; the assert turns that into a clear
    failure here rather than a `NoneType - int` `TypeError` at the
    caller (`undo`'s `... - 1`)."""
    row = conn.execute(
        "SELECT MIN(entry_seq) AS min_seq FROM edit_log WHERE group_seq = ?", (group_seq,)
    ).fetchone()
    assert row["min_seq"] is not None
    return row["min_seq"]


def max_entry_seq_in_group(conn: sqlite3.Connection, *, group_seq: int) -> int:
    """See `min_entry_seq_in_group`'s docstring -- same guarantee, same
    reason for the assert."""
    row = conn.execute(
        "SELECT MAX(entry_seq) AS max_seq FROM edit_log WHERE group_seq = ?", (group_seq,)
    ).fetchone()
    assert row["max_seq"] is not None
    return row["max_seq"]


def count_groups_up_to(conn: sqlite3.Connection, *, up_to_seq: int) -> int:
    """How many distinct undo groups sit at or before `up_to_seq` -- the
    true "one Apply is one undo step" count (#190), not a raw entry count.

    Correct only because a group never straddles `up_to_seq` when that
    value is a real cursor position: `append` always discards every entry
    past the cursor before adding a new one, and `undo`/`redo` always land
    the cursor on a group boundary (`min_entry_seq_in_group - 1` or
    `max_entry_seq_in_group`), never mid-group. A `COUNT(DISTINCT ...)`
    over zero matching rows is `0`, so this needs no empty-log guard."""
    row = conn.execute(
        "SELECT COUNT(DISTINCT group_seq) AS n FROM edit_log WHERE entry_seq <= ?",
        (up_to_seq,),
    ).fetchone()
    return row["n"]


def count_groups_after(conn: sqlite3.Connection, *, after_seq: int) -> int:
    """The redo-side counterpart to `count_groups_up_to` -- how many
    distinct undo groups sit strictly after `after_seq`. Same no-straddle
    guarantee, same reason no empty-log guard is needed."""
    row = conn.execute(
        "SELECT COUNT(DISTINCT group_seq) AS n FROM edit_log WHERE entry_seq > ?",
        (after_seq,),
    ).fetchone()
    return row["n"]


def first_entry_seq_after(conn: sqlite3.Connection, *, after_seq: int) -> int | None:
    row = conn.execute(
        "SELECT MIN(entry_seq) AS next_seq FROM edit_log WHERE entry_seq > ?", (after_seq,)
    ).fetchone()
    return row["next_seq"]


def delete_entries_after(conn: sqlite3.Connection, *, after_seq: int) -> None:
    """Discard every staged entry past `after_seq` -- what a new append
    does to whatever redo history sat ahead of the cursor."""
    conn.execute("DELETE FROM edit_log WHERE entry_seq > ?", (after_seq,))


def delete_entry(conn: sqlite3.Connection, *, entry_seq: int) -> None:
    conn.execute("DELETE FROM edit_log WHERE entry_seq = ?", (entry_seq,))


def delete_all_entries(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM edit_log")


def list_entries_up_to(conn: sqlite3.Connection, *, up_to_seq: int) -> list[EditLogEntry]:
    """Every entry from the start of the log through `up_to_seq`, in
    order -- the replay range for a projection at that cursor."""
    rows = conn.execute(
        "SELECT entry_seq, command, payload, appended_at, group_seq FROM edit_log"
        " WHERE entry_seq <= ? ORDER BY entry_seq",
        (up_to_seq,),
    ).fetchall()
    return [_to_entry(row) for row in rows]


def count_entries(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS n FROM edit_log").fetchone()
    return row["n"]


def get_session(conn: sqlite3.Connection) -> EditSession | None:
    """The single session row, or `None` before the first-ever append --
    `edit_session` starts empty and is seeded lazily (see
    db/edit_session.py's `_ensure_session`)."""
    row = conn.execute("SELECT cursor_seq FROM edit_session").fetchone()
    if row is None:
        return None
    return EditSession(cursor_seq=row["cursor_seq"])


def insert_session(conn: sqlite3.Connection, *, cursor_seq: int) -> None:
    conn.execute(
        "INSERT INTO edit_session (singleton, cursor_seq) VALUES (1, :cursor_seq)",
        {"cursor_seq": cursor_seq},
    )


def update_cursor(conn: sqlite3.Connection, *, cursor_seq: int) -> None:
    conn.execute("UPDATE edit_session SET cursor_seq = ?", (cursor_seq,))
