"""WebSocket API commands for the Outlet & Appliance Binding integration.

Per docs/LLD.md §13's adapter pattern: a handler loads DTOs via
the db layer and returns them; no domain decision is needed for a pure
read, so no domain/ function is called from `get_state`'s path.
`get_socket_ha_names` is the one read that calls one
(`resolve_socket_name`), since choosing among HA's names is a rule.

Uses `from homeassistant.components import websocket_api` +
`websocket_api.async_register_command` — not `hass.components.websocket_api`:
`hass` has no `.components` attribute in current Home Assistant.

History: docs/HISTORY-INDEX.md
"""

import logging
import re
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MODE_BATCH, MODE_IMMEDIATE, SIGNAL_SWITCHES_CHANGED
from .db import edit_session
from .db.operations import devices as device_ops
from .db.operations import sockets as socket_ops
from .db.operations.errors import (
    DuplicateError,
    FixedDeviceError,
    LoopError,
    NotFoundError,
)
from .db.operations.state import list_co_socket_owners
from .db.session import connection as db_connection
from .db.sql import devices as devices_sql
from .domain.discovery import (
    CoPattern,
    DiscoveredDevice,
    DiscoveredEntity,
    NearMiss,
    ProposedCo,
    candidate_patterns,
    disambiguate_aliases,
    first_non_blank,
    group_device_families,
    match_device,
    near_miss_issue_id,
    near_miss_placeholders,
    stale_near_miss_issue_ids,
)
from .domain.identifiers import (
    ApplianceId,
    CoId,
    DeviceId,
    HaAreaId,
    HaDeviceRegistryId,
    HaEntityDottedId,
    HaEntityRegistryId,
    SocketId,
    Timestamp,
    UoId,
)
from .domain.models import DeviceType
from .domain.socket_names import is_default_socket_name, resolve_socket_name
from .entity_slug import device_switch_entity_id

if TYPE_CHECKING:
    # __init__ imports this module, so a runtime import would be circular.
    from . import OutletBinderData

_LOGGER = logging.getLogger(__name__)


def _trimmed_non_blank(value: str) -> str:
    """The name with leading and trailing whitespace removed, refused if
    nothing is left. `str.strip()` is the authority for "blank", covering
    Unicode whitespace that the schema's `CHECK` (which names only space,
    tab, newline and carriage return) does not. Trimming here means
    `"Kettle "` cannot be stored beside `"Kettle"`: the uniqueness columns
    turn a space into `_`, so they would not collide (#317)."""
    trimmed = value.strip()
    if not trimmed:
        raise vol.Invalid("must not be blank")
    return trimmed


# Every `name`/`alias` field in a command schema uses this, so a blank one
# fails validation with a clear message rather than reaching the database's
# `CHECK` and surfacing as an IntegrityError; enforced by
# tests/test_name_validator_guard.py.
NON_BLANK_STR = vol.All(str, _trimmed_non_blank)


def _not_a_bool(value: int) -> int:
    """`True` and `False` are `int`s in Python, so a plain `int` check lets
    `socket_count: true` through as 1."""
    if isinstance(value, bool):
        raise vol.Invalid("must be a whole number, not true or false")
    return value


# A whole number from JSON: not a float (`3.0`), not a string, not a bool.
# tests/test_strict_int_schema_guard.py rejects a schema that uses `int` or
# an HA validator that accepts a bool instead.
STRICT_INT = vol.All(int, _not_a_bool)

# The near-miss Repairs issue's "Learn more" link, into the public release repo
# (the dev repo is private). tests/test_near_miss_learn_more_url.py checks that
# a publish would put the file there, with the heading.
NEAR_MISS_LEARN_MORE_URL = (
    "https://github.com/apps-and-tools-gph/outlet-binder/blob/main/"
    "custom_components/outlet_binder/device_identification/device_patterns/README.md"
    "#when-a-pattern-does-not-match"
)


def _runtime_data(hass: HomeAssistant) -> OutletBinderData:
    """Return the loaded config entry's `runtime_data`.

    Goes through the (single, per `manifest.json`'s `single_config_entry`)
    loaded config entry rather than deriving values directly from
    `hass.config` — this ties WS access to "the integration confirmed it's
    set up and migrated," and correctly fails if the entry was unloaded.
    Must be called on the event loop: it goes through
    `async_loaded_entries`, which is decorated `@callback` in the installed
    `homeassistant` package (#213) -- never call it, or any `_get_*` below,
    from inside a `_write()` closure handed to `hass.async_add_executor_job`.
    """
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise HomeAssistantError("Outlet & Appliance Binding is not loaded")
    return entries[0].runtime_data


def _get_db_path(hass: HomeAssistant) -> Path:
    """Return the loaded config entry's DB path -- see _runtime_data."""
    return _runtime_data(hass).db_path


def _get_patterns(hass: HomeAssistant) -> tuple[CoPattern, ...]:
    """Return the loaded config entry's device patterns (docs/LLD.md §4),
    loaded once at setup by device_identification/pattern_loader.py."""
    return _runtime_data(hass).patterns


def _get_immediate(hass: HomeAssistant) -> bool:
    """Return whether the loaded config entry is in immediate mode (#186)."""
    return _runtime_data(hass).immediate


def _get_debug_mode(hass: HomeAssistant) -> bool:
    """Return whether the loaded config entry has debug mode enabled (#246)."""
    return _runtime_data(hass).debug_mode


def _get_socket_region(hass: HomeAssistant) -> str:
    """Return the loaded config entry's socket-icon region (#128)."""
    return _runtime_data(hass).socket_region


def _debug_mode_enabled_or_error(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> bool:
    """Gate for debug-only commands (#246, currently individual delete on
    Unmanaged Outlet/Appliance/CO). Returns True if debug mode is enabled; the
    caller must call this first and return immediately if it's False --
    it has already sent ERR_NOT_ALLOWED itself in that case.

    A dedicated error code rather than a silent no-op: all three deletes
    are already idempotent for an unknown id (a bare ack, not
    NotFoundError -- see handle_delete_co), so a silently-refusing gate
    would be indistinguishable from a successful delete to the caller.
    Also distinct from ERR_NOT_FOUND, which already means "the row was
    already gone" on these same commands.

    Must be called on the event loop, before any executor dispatch
    -- _get_debug_mode goes through the same @callback-decorated HA API
    as _get_immediate.
    """
    if _get_debug_mode(hass):
        return True
    connection.send_error(
        msg["id"],
        websocket_api.const.ERR_NOT_ALLOWED,
        "Individual delete requires debug mode to be enabled in "
        "Outlet & Appliance Binding's options",
    )
    return False


def _now() -> Timestamp:
    """The single point where a raw string first becomes a `Timestamp` in
    production code -- everywhere downstream just carries the type."""
    return Timestamp(dt_util.utcnow().isoformat())


def _co_switch_id(alias: str) -> str:
    """The entity id HA would give a CO's switch under `alias`."""
    return device_switch_entity_id(device_type=DeviceType.CO, name=alias, appliance_type=None)


def _append_and_maybe_commit(
    conn: sqlite3.Connection,
    *,
    immediate: bool,
    command: edit_session.EditCommand,
    payload: dict[str, str],
    now: Timestamp,
    continue_group: bool,
) -> None:
    """Stage one edit-session entry, then commit immediately if the config
    entry is in immediate mode (#186: immediate
    is auto-commit after every log entry, not a second write path). The one
    call site for every staging handler below, so the branch lives in
    exactly one place.

    `immediate` is resolved by the caller on the event loop -- this
    runs inside a `_write()` closure on an executor thread, where calling
    `_get_immediate(hass)` directly would invoke a `@callback`-decorated HA
    API off the loop.

    Immediate mode keeps the log empty. It starts empty, because the
    options flow refuses the switch while the log has entries; a success
    flushes; and a refused entry is withdrawn before the error goes back,
    or every later write would replay it first and fail with its error.
    So the new entry is the only one `commit` replays, and each of the
    three refusals is raised before it writes a row. Any other error
    leaves the entry in the log, since it may have been applied, for the
    toolbar's Undo and Flush to recover.
    """
    entry_seq = edit_session.append(
        conn, command=command, payload=payload, now=now, continue_group=continue_group
    )
    if immediate:
        try:
            edit_session.commit(conn)
        except NotFoundError, FixedDeviceError, LoopError:
            edit_session.withdraw(conn, entry_seq=entry_seq)
            raise


async def _sync_after_write(hass: HomeAssistant) -> None:
    """Tell switch.py's platform to resync its entities (#368), after
    every write. Sending a signal only schedules the platform's own resync
    as a background task (HA's dispatcher runs a coroutine target via
    `async_run_hass_job`) -- it cannot raise back into this write's
    result, so a sync failure can never turn an already-committed write
    into an error result."""
    async_dispatcher_send(hass, SIGNAL_SWITCHES_CHANGED)


async def _run_write(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
    write: Callable[[], None],
) -> None:
    """Run a blocking db/operations/ write, then send the WS response
    itself -- a bare ack on success, or the mapped error on failure
    (docs/LLD.md §13). Every write command's handler ends with
    `await _run_write(...)` and nothing else.

    - `NotFoundError` (db/operations/errors.py) sends `ERR_NOT_FOUND`
      directly. `ActiveConnection.async_handle_exception` has no path to
      that code for a *raised* exception -- its dispatch is a fixed
      `isinstance` chain with exactly one code per recognised type, and a
      `HomeAssistantError` subclass still resolves to the generic
      `ERR_HOME_ASSISTANT_ERROR`. Calling `send_error` here directly is
      the only way to surface `ERR_NOT_FOUND` at all.
    - Any other `ValueError` becomes `HomeAssistantError`, so
      `async_handle_exception`'s existing dispatch sends
      `ERR_HOME_ASSISTANT_ERROR` with the message intact, rather than the
      `ERR_UNKNOWN_ERROR`/"Unknown error" fallback an unmatched
      `ValueError` would otherwise get.

    After every attempted write -- success or failure, whatever it raises,
    and before the response goes back -- `_sync_after_write` sends `SIGNAL_SWITCHES_CHANGED`, for
    every write command that routes through here, with no
    per-command flag deciding whether to send it. It runs on the failure
    paths too (#336): `edit_session.commit` has no cross-entry atomicity,
    so a write that raises can already have committed part of itself, and
    skipping the signal would leave the switches pointing at the old
    sockets. It is cheap to send when nothing switch-shaped changed
    (switch.py's own sync diffs against its current entities and does
    nothing when nothing's changed) and correct to send when something
    did, so there is nothing for a per-command gate to buy here, only a
    place the next command could forget it. This call sits directly in
    `_run_write`, which already runs on the event loop rather than inside
    an executor closure (`write` above is what gets dispatched to the
    executor, not this function) -- the same reason
    `tests/test_executor_closure_guard.py` already exempts this function
    by name, and why sending the signal is safe to do from here.
    """
    try:
        try:
            await hass.async_add_executor_job(write)
        finally:
            await _sync_after_write(hass)
    except NotFoundError as err:
        connection.send_error(msg["id"], websocket_api.const.ERR_NOT_FOUND, str(err))
        return
    except ValueError as err:
        raise HomeAssistantError(str(err)) from err
    connection.send_result(msg["id"])


@websocket_api.websocket_command({"type": "outlet_binder/get_state"})
@websocket_api.async_response
async def handle_get_state(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the full application state (V1 read model, docs/LLD.md §13),
    projected through any staged edit-session entries (#190), plus the
    `edit_session` sidecar describing what's pending, the `debug_mode`
    sidecar the panel uses to decide whether to render its
    debug-only delete controls, the `socket_region` sidecar the
    panel uses to pick which regional socket icon to render, and the
    `mode` sidecar the panel uses to show whether a button stages
    -- all purely presentational; the WebSocket handlers enforce the
    debug_mode gate and pick staged or immediate themselves regardless of
    what the panel shows, and socket_region drives no server-side
    behaviour at all."""
    db_path = _get_db_path(hass)

    def _read() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
        with db_connection(db_path) as conn:
            return edit_session.projected_state_and_diff(conn)

    state, sidecar = await hass.async_add_executor_job(_read)
    connection.send_result(
        msg["id"],
        {
            **state,
            "edit_session": sidecar,
            "debug_mode": _get_debug_mode(hass),
            "socket_region": _get_socket_region(hass),
            "mode": MODE_IMMEDIATE if _get_immediate(hass) else MODE_BATCH,
        },
    )


def _default_name_rules(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    patterns: tuple[CoPattern, ...],
    co_id: CoId,
) -> tuple[re.Pattern[str], ...]:
    """The `default_name` rules of every pattern that fits a CO's device
    (#394). A CO does not record which pattern matched it, so this asks
    `candidate_patterns` again, with just the fields it compares, rather
    than a second identity check. Every candidate's rule counts, since the
    one that matched is not known. A CO's id is its device's registry id.
    Must run on the event loop."""
    device = device_registry.async_get(co_id)
    # HA 2026.9's registry can also return a `ChildDeviceEntry` (#366), which
    # has no manufacturer or model; a CO is never one.
    if not isinstance(device, dr.DeviceEntry):
        return ()
    config_entry = hass.config_entries.async_get_entry(device.config_entry_id)
    fitting = candidate_patterns(
        DiscoveredDevice(
            ha_device_registry_id=HaDeviceRegistryId(device.id),
            integration_domain=config_entry.domain if config_entry is not None else None,
            manufacturer=device.manufacturer,
            model=device.model,
            hw_version=device.hw_version,
            name=first_non_blank(device.name_by_user, device.name),
            entities=(),
            via_device_id=None,
        ),
        patterns,
    )
    return tuple(p.default_socket_name for p in fitting if p.default_socket_name is not None)


def _socket_ha_names(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    co_socket_id: SocketId,
    default_name_rules: tuple[re.Pattern[str], ...],
) -> dict[str, str | None]:
    """What HA holds for one CO Socket's on/off switch (#394): `name`, the
    name proposed for an Appliance (`resolve_socket_name`),
    `friendly_name`, the full name HA displays for the entity (device
    prefix included), which the dialogs show as information, and
    `integration_domain`, the domain of the device's config entry (the one
    discovery records). All three are None if the switch is gone from the
    registry; `friendly_name` is also None while the entity has no state
    (disabled, or not yet loaded), and `integration_domain` when the
    switch has no device or its config entry is gone.

    `name` is also None when it is one of the device's default names
    (`default_name_rules`), so such a Socket is left out like an unnamed
    one; `friendly_name` still shows what HA displays.

    A CO Socket's id is its switch's entity-registry id, which
    `EntityRegistry.async_get` accepts as well as a dotted entity_id.
    Must run on the event loop, like `_build_discovered_devices`.
    """
    entity = entity_registry.async_get(co_socket_id)
    if entity is None:
        return {"name": None, "friendly_name": None, "integration_domain": None}
    device = device_registry.async_get(entity.device_id) if entity.device_id else None
    config_entry = (
        hass.config_entries.async_get_entry(device.config_entry_id)
        if isinstance(device, dr.DeviceEntry)
        else None
    )
    state = hass.states.get(entity.entity_id)
    friendly_name = state.attributes.get(ATTR_FRIENDLY_NAME) if state else None
    name = resolve_socket_name(
        entity_name=entity.name,
        entity_original_name_unprefixed=entity.original_name_unprefixed,
        entity_original_name=entity.original_name,
        has_entity_name=entity.has_entity_name,
        device_name_by_user=device.name_by_user if device else None,
        device_name=device.name if device else None,
    )
    return {
        "name": None
        if name is not None and is_default_socket_name(name, default_name_rules)
        else name,
        "friendly_name": friendly_name if isinstance(friendly_name, str) else None,
        "integration_domain": config_entry.domain if config_entry is not None else None,
    }


@websocket_api.websocket_command({"type": "outlet_binder/get_socket_ha_names"})
@websocket_api.async_response
async def handle_get_socket_ha_names(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return `{co_socket_id: {name, friendly_name, integration_domain}}`
    for every CO Socket (#394); see `_socket_ha_names` for the fields.

    Read-only, so not admin-gated (like `handle_get_state`). It runs on the
    server because the panel's `hass.entities` display entry carries no
    registry id, and a CO Socket is keyed on that id (reading straight off `hass`
    can't map a Socket to its entity). The ids come from the DB on the
    executor; the registries and states are read back on the event loop,
    since they are loop-only."""
    db_path = _get_db_path(hass)
    patterns = _get_patterns(hass)

    def _read() -> list[tuple[SocketId, CoId]]:
        with db_connection(db_path) as conn:
            return list_co_socket_owners(conn)

    sockets = await hass.async_add_executor_job(_read)
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    rules_by_co = {
        co_id: _default_name_rules(hass, device_registry, patterns, co_id)
        for co_id in {co_id for _socket_id, co_id in sockets}
    }
    connection.send_result(
        msg["id"],
        {
            socket_id: _socket_ha_names(
                hass, entity_registry, device_registry, socket_id, rules_by_co[co_id]
            )
            for socket_id, co_id in sockets
        },
    )


def _device_mac(device: dr.DeviceEntry) -> str | None:
    """The device's network MAC, upper-cased with colon separators, or
    None if it reports none. The panel reads the same connection off
    `hass.devices` for a CO's own MAC (frontend `device-info.ts`, #369); both
    upper-case it, and a test on each side pins the format."""
    return next(
        (
            conn_id.upper()
            for conn_type, conn_id in device.connections
            if conn_type == dr.CONNECTION_NETWORK_MAC
        ),
        None,
    )


def _build_discovered_devices(hass: HomeAssistant) -> list[DiscoveredDevice]:
    """Snapshot HA's device/entity registries as plain data (docs/LLD.md §4).

    Must run on the event loop, before any executor job -- `dr.async_get`/
    `er.async_get` return live in-memory registries, not executor-safe.

    The only place HA registry objects are read for discovery, which is what
    makes it the one construction site for domain/identifiers.py's HA-side
    types (`_socket_ha_names` reads them too, but only to look one up by a
    CO Socket's id and never builds those types). Note
    `entry.entity_id` and `entry.id` becoming *different* types: the dotted
    one a user can rename, the registry one they cannot, and it is the
    latter a CO Socket is keyed on.
    """
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    devices = []
    for device in device_registry.devices:
        entries = er.async_entries_for_device(
            entity_registry, device.id, include_disabled_entities=False
        )
        # The config entry's domain, not the domain element of the device's
        # identifiers: HA requires the former, the latter is only a
        # convention (issue #383). No fallback to identifiers when the
        # lookup fails -- that would bring the convention-based check back.
        config_entry = hass.config_entries.async_get_entry(device.config_entry_id)
        devices.append(
            DiscoveredDevice(
                ha_device_registry_id=HaDeviceRegistryId(device.id),
                integration_domain=config_entry.domain if config_entry is not None else None,
                manufacturer=device.manufacturer,
                model=device.model,
                hw_version=device.hw_version,
                name=first_non_blank(device.name_by_user, device.name),
                entities=tuple(
                    DiscoveredEntity(
                        entity_id=HaEntityDottedId(entry.entity_id),
                        id=HaEntityRegistryId(entry.id),
                        unique_id=entry.unique_id,
                        domain=entry.domain,
                        device_class=entry.device_class or entry.original_device_class,
                        # `device.id`, not `entry.device_id`: identical here by
                        # construction (these entries came from
                        # async_entries_for_device for this very device), but
                        # HA types `RegistryEntry.device_id` as `str | None`
                        # since an entity need not belong to a device at all.
                        # Taking it from the device keeps the field genuinely
                        # non-optional instead of relying on the caller knowing
                        # that the None case cannot arise here.
                        source_device_id=HaDeviceRegistryId(device.id),
                    )
                    for entry in entries
                ),
                # A real narrowing: HA types this `str | None`, so mypy
                # checks the wrap -- unlike db/sql/'s row mappers, where the
                # value arrives as `Any` and a wrap would prove nothing.
                via_device_id=(
                    HaDeviceRegistryId(device.via_device_id)
                    if device.via_device_id is not None
                    else None
                ),
                identifiers=frozenset(device.identifiers),
                mac=_device_mac(device),
            )
        )
    return devices


@websocket_api.websocket_command({"type": "outlet_binder/discover_cos"})
@websocket_api.require_admin
@websocket_api.async_response
async def handle_discover_cos(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Run one discovery pass over HA's devices (docs/LLD.md §4).
    Auto-writes new COs for pattern matches on devices not already known
    -- no confirmation step, additive-only, never touches an existing CO.
    Returns `{"created": [{co_id, integration_domain, pattern_id}]}`: the
    COs this pass actually wrote (issue #195), so the panel can announce
    them once. Not a bare ack like the user writes' -- discovery is
    not a user edit, and a refetch cannot recover the set, since nothing
    ties a row's `created_at` to a pass. Only the integration and the
    matched pattern are returned: nothing else stores them, while alias and
    Sockets come from the `get_state` that follows and device fields from
    `hass.devices`. An object rather than a bare list so a later key does not
    change its shape.

    group_device_families runs before anything else: some HA devices (e.g.
    a Tapo P304M power strip) register as a parent device plus several
    per-socket child devices rather than one device -- this folds each
    such family back into a single DiscoveredDevice so match_device sees
    one device with a complete entity list.

    Proposals are disambiguated *before* any write, against
    both this batch's own aliases and every existing CO's, and for a
    device with a plug its switch's entity id too -- so two
    identical devices (e.g. two Tapo P304Ms) never propose the same alias
    to begin with. The per-device `DuplicateError` catch below is
    therefore a defensive backstop, not an expected path: it should never
    actually fire, but if disambiguation ever left a collision anyway, one
    bad device logs a warning and is skipped rather than aborting the rest
    of the pass.

    A device matched by a lower-ranked pattern because a higher-ranked one
    failed its shape check logs one warning naming the skipped patterns. It
    is logged once per CO -- on the pass that creates it -- because a device
    with a CO is never matched again.

    Every near-miss also gets a Repairs issue, on top of the
    log warning: `_write` runs on an executor thread and can't touch the
    issue registry (`async_get_or_create`/`async_delete` both call
    `hass.verify_event_loop_thread`, and a `handle_*` closure referencing
    `hass` fails tests/test_executor_closure_guard.py), so it returns its
    near-misses instead, and the registry is updated here, back on the
    event loop, before the result is sent. Every pass prunes any
    `near_miss_`-prefixed issue this pass's near-misses no longer justify
    -- a device that now matches, one that got a CO, or one removed from
    HA all clear the same way.
    """
    db_path = _get_db_path(hass)
    patterns = _get_patterns(hass)
    discovered = group_device_families(tuple(_build_discovered_devices(hass)), patterns)

    integration_by_device = {d.ha_device_registry_id: d.integration_domain for d in discovered}

    def _write() -> tuple[tuple[NearMiss, ...], list[dict[str, Any]]]:
        with db_connection(db_path) as conn:
            now = _now()
            cos = devices_sql.list_of_type(conn, device_type=DeviceType.CO)
            existing_co_ids = {HaDeviceRegistryId(co.device_id) for co in cos}
            taken = frozenset(co.device_name for co in cos)
            taken_switch_ids = frozenset(_co_switch_id(co.device_name) for co in cos if co.has_plug)

            proposals = []
            near_misses = []
            for device in discovered:
                if device.ha_device_registry_id in existing_co_ids:
                    continue
                result = match_device(device, patterns)
                if isinstance(result, ProposedCo):
                    proposals.append(result)
                    if result.superseded_pattern_ids:
                        # Once per CO (issue #146): a device that already
                        # has a CO is skipped above, so this stays quiet
                        # after the pass that creates it.
                        _LOGGER.warning(
                            "Device %s (%s) fell back to pattern %s; higher-ranked"
                            " pattern(s) %s failed their shape check",
                            result.ha_device_registry_id,
                            device.name,
                            result.pattern_id,
                            ", ".join(result.superseded_pattern_ids),
                        )
                elif isinstance(result, NearMiss):
                    near_misses.append(result)
                    # Warn on every pass, no suppression (issue #353): the
                    # pattern YAML is what needs fixing, not this device.
                    _LOGGER.warning(
                        "Device %s (%s, %s %s) matched a pattern on"
                        " manufacturer/model but got no CO; the pattern YAML"
                        " needs tightening. %s",
                        result.ha_device_registry_id,
                        result.name,
                        result.manufacturer,
                        result.model,
                        "; ".join(f"{r.pattern_id}: {r.reason}" for r in result.rejections),
                    )

            created: list[dict[str, Any]] = []
            for proposal in disambiguate_aliases(
                tuple(proposals),
                taken=taken,
                taken_switch_ids=taken_switch_ids,
                switch_id_of=_co_switch_id,
            ):
                try:
                    device_ops.create_discovered_co(conn, proposal, now=now)
                except DuplicateError as err:
                    _LOGGER.warning(
                        "Skipping discovered CO %s: %s", proposal.ha_device_registry_id, err
                    )
                    continue
                created.append(
                    {
                        "co_id": proposal.ha_device_registry_id,
                        "integration_domain": integration_by_device[proposal.ha_device_registry_id],
                        "pattern_id": proposal.pattern_id,
                    }
                )

            return tuple(near_misses), created

    # A new CO gets a switch (#423); this handler does not go through
    # `_run_write`, so it sends the sync signal itself, whatever `_write`
    # raises: each device is its own transaction, so the COs before an
    # error are already committed.
    try:
        near_misses, created = await hass.async_add_executor_job(_write)
    finally:
        await _sync_after_write(hass)

    registry = ir.async_get(hass)
    existing_near_miss_ids = frozenset(
        issue_id for (issue_domain, issue_id) in registry.issues if issue_domain == DOMAIN
    )
    for issue_id in stale_near_miss_issue_ids(near_misses, existing=existing_near_miss_ids):
        ir.async_delete_issue(hass, DOMAIN, issue_id)
    for near_miss in near_misses:
        ir.async_create_issue(
            hass,
            DOMAIN,
            near_miss_issue_id(near_miss.ha_device_registry_id),
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="near_miss",
            translation_placeholders=near_miss_placeholders(near_miss),
            learn_more_url=NEAR_MISS_LEARN_MORE_URL,
        )

    connection.send_result(msg["id"], {"created": created})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/create_uo",
        vol.Required("name"): NON_BLANK_STR,
        vol.Optional("ha_area_id"): vol.Any(str, None),
        vol.Optional("location_note"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_create_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Create an Unmanaged Outlet (docs/LLD.md §13) -- the command precedent
    every later write command follows: admin-gated, its errors mapped by
    _run_write (which also sends the response itself), and a bare ack
    rather than the created row, since the frontend re-calls get_state to
    render the change.
    """
    db_path = _get_db_path(hass)
    name = msg["name"]
    ha_area_id = msg.get("ha_area_id")
    location_note = msg.get("location_note")

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.create_uo(
                conn,
                name=name,
                ha_area_id=HaAreaId(ha_area_id) if ha_area_id is not None else None,
                location_note=location_note,
                now=_now(),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/create_appliance",
        vol.Required("name"): NON_BLANK_STR,
        vol.Optional("appliance_type"): vol.Any(str, None),
        vol.Optional("description"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_create_appliance(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Create an Appliance (docs/LLD.md §13), following create_uo's
    precedent: admin-gated, errors mapped by _run_write, bare ack.

    The message field is `appliance_type`, not `type` -- the command's own
    schema discriminator key *is* "type"
    (`vol.Required("type"): "outlet_binder/create_appliance"`), and
    voluptuous Markers hash/compare by their key string, so a second `type`
    key in the same schema dict would silently overwrite the discriminator
    entry rather than raising -- confirmed directly against the installed
    voluptuous package before writing this.
    """
    db_path = _get_db_path(hass)
    name = msg["name"]
    appliance_type = msg.get("appliance_type")
    description = msg.get("description")

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.create_appliance(
                conn,
                name=name,
                appliance_type=appliance_type,
                description=description,
                now=_now(),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/create_plugged_into",
        vol.Required("appliance_id"): str,
        vol.Required("co_socket_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_create_plugged_into(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage plugging an Appliance into a CO Socket (#190) -- appends to
    the edit-session log rather than writing immediately. Staging does not
    validate: in batch mode a bad id surfaces as `failed_entry` on the
    next get_state rather than being rejected here (db/edit_session.py's
    module docstring); in immediate mode the auto-commit refuses it. The id coercions
    db/edit_session.py's dispatch table already applies at replay time are
    not duplicated here -- raw strings go straight into the payload.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="create_plugged_into",
                payload={
                    "appliance_id": msg["appliance_id"],
                    "co_socket_id": msg["co_socket_id"],
                },
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/unplug_plugged_into",
        vol.Required("appliance_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_unplug_plugged_into(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage unplugging an Appliance (#190) -- see handle_create_plugged_into
    for the staging/validation contract this and the other three connection
    handlers share.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="unplug_plugged_into",
                payload={"appliance_id": msg["appliance_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/assign_co_to_uo",
        vol.Required("co_id"): str,
        vol.Required("uo_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_assign_co_to_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage assigning a PCO to an Unmanaged Outlet (#190) -- see
    handle_create_plugged_into for the staging/validation contract.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="assign_co_to_uo",
                payload={"co_id": msg["co_id"], "uo_id": msg["uo_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/unassign_co_from_uo",
        vol.Required("co_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_unassign_co_from_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage unassigning a PCO from its Unmanaged Outlet (#190) -- see
    handle_create_plugged_into for the staging/validation contract.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="unassign_co_from_uo",
                payload={"co_id": msg["co_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/assign_appliance_to_uo",
        vol.Required("appliance_id"): str,
        vol.Required("uo_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_assign_appliance_to_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage plugging an Appliance straight into an Unmanaged Outlet (#422) -- see
    handle_create_plugged_into for the staging/validation contract. The
    Appliance's switch stays `unavailable` there: an Unmanaged Outlet is never an
    automation target.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="assign_appliance_to_uo",
                payload={
                    "appliance_id": msg["appliance_id"],
                    "uo_id": msg["uo_id"],
                },
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/unassign_appliance_from_uo",
        vol.Required("appliance_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_unassign_appliance_from_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage unplugging an Appliance from its Unmanaged Outlet -- see
    handle_create_plugged_into for the staging/validation contract. A no-op
    for an Appliance that is in a CO's socket or nowhere.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="unassign_appliance_from_uo",
                payload={"appliance_id": msg["appliance_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/assign_co_to_co_socket",
        vol.Required("co_id"): str,
        vol.Required("co_socket_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_assign_co_to_co_socket(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage plugging a PCO into a socket of another PCO (#421) -- see
    handle_create_plugged_into for the staging/validation contract. A plug
    that would make a loop is refused at replay and at commit, not here.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="assign_co_to_co_socket",
                payload={"co_id": msg["co_id"], "co_socket_id": msg["co_socket_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/unassign_co_from_co_socket",
        vol.Required("co_id"): str,
        vol.Optional("continue_group"): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_unassign_co_from_co_socket(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Stage unplugging a PCO from the socket of another PCO (#421) -- see
    handle_create_plugged_into for the staging/validation contract.
    """
    db_path = _get_db_path(hass)
    immediate = _get_immediate(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            _append_and_maybe_commit(
                conn,
                immediate=immediate,
                command="unassign_co_from_co_socket",
                payload={"co_id": msg["co_id"]},
                now=_now(),
                continue_group=msg.get("continue_group", False),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/update_uo",
        vol.Required("uo_id"): str,
        vol.Required("name"): NON_BLANK_STR,
        vol.Required("ha_area_id"): vol.Any(str, None),
        vol.Required("location_note"): vol.Any(str, None),
        vol.Required("socket_count"): STRICT_INT,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_update_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update an Unmanaged Outlet's editable fields (docs/LLD.md §13), following
    create_uo's precedent: admin-gated, errors mapped by
    _run_write, bare ack. Raises NotFoundError for an unknown
    uo_id -- this edits a specific existing row rather than
    unlinking something, so it follows assign_co_to_uo's
    precedent rather than unassign's idempotent one.

    `ha_area_id`/`location_note` are `vol.Required` (nullable, not
    optional) so an omitted field cannot silently clear the column -- see
    #214. Send the current value to leave it unchanged, or explicit `null`
    to clear it. `socket_count` is a whole number the server checks against
    the plugs in use; the name changes only if the count is accepted.
    """
    db_path = _get_db_path(hass)
    uo_id = UoId(DeviceId(msg["uo_id"]))
    name = msg["name"]
    ha_area_id = msg["ha_area_id"]
    location_note = msg["location_note"]
    socket_count = msg["socket_count"]

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.update_uo(
                conn,
                uo_id=uo_id,
                name=name,
                ha_area_id=HaAreaId(ha_area_id) if ha_area_id is not None else None,
                location_note=location_note,
                socket_count=socket_count,
                now=_now(),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/update_appliance",
        vol.Required("appliance_id"): str,
        vol.Required("name"): NON_BLANK_STR,
        vol.Required("appliance_type"): vol.Any(str, None),
        vol.Required("description"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_update_appliance(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update an Appliance's editable fields (docs/LLD.md §13), following
    create_uo's precedent: admin-gated, errors mapped by
    _run_write, bare ack. `appliance_type`, not `type`, for the same reason
    as create_appliance -- the schema's own discriminator key is "type".

    `appliance_type`/`description` are `vol.Required` (nullable, not
    optional) so an omitted field cannot silently clear the column -- see
    #214. Send the current value to leave it unchanged, or explicit `null`
    to clear it.
    """
    db_path = _get_db_path(hass)
    appliance_id = ApplianceId(DeviceId(msg["appliance_id"]))
    name = msg["name"]
    appliance_type = msg["appliance_type"]
    description = msg["description"]

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.update_appliance(
                conn,
                appliance_id=appliance_id,
                name=name,
                appliance_type=appliance_type,
                description=description,
                now=_now(),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/update_co",
        vol.Required("co_id"): str,
        vol.Required("alias"): NON_BLANK_STR,
        vol.Required("location_override_ha_area_id"): vol.Any(str, None),
        vol.Required("location_override_location_note"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_update_co(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update a CO's editable fields (docs/LLD.md §13), following
    create_uo's precedent: admin-gated, errors mapped by
    _run_write, bare ack. `uo_id` is a separate write path
    (assign/unassign, phase 4), not a field edit here.

    `location_override_ha_area_id`/`location_override_location_note` are
    `vol.Required` (nullable, not optional) so an omitted field cannot
    silently clear the area or the note -- see #214. The two are independent: each
    is stored as sent, and a read gives `location_override` as `None` when both
    are NULL (db/operations/state.py's `_location_override_to_json`).
    """
    db_path = _get_db_path(hass)
    co_id = CoId(DeviceId(msg["co_id"]))
    alias = msg["alias"]
    ha_area_id = msg["location_override_ha_area_id"]
    location_note = msg["location_override_location_note"]

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.update_co(
                conn,
                co_id=co_id,
                alias=alias,
                ha_area_id=HaAreaId(ha_area_id) if ha_area_id is not None else None,
                location_note=location_note,
                now=_now(),
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/update_co_socket",
        vol.Required("co_socket_id"): str,
        vol.Required("alias"): NON_BLANK_STR,
        vol.Required("socket_type"): vol.Any(str, None),
        vol.Required("physical_position"): vol.Any(STRICT_INT, None),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_update_co_socket(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update a CO Socket's editable fields (docs/LLD.md §13), following
    create_uo's precedent: admin-gated, errors mapped by
    _run_write, bare ack.

    `socket_type`/`physical_position` are `vol.Required` (nullable, not
    optional) so an omitted field cannot silently clear the column -- see
    #214. Send the current value to leave it unchanged, or explicit `null`
    to clear it.
    """
    db_path = _get_db_path(hass)
    co_socket_id = SocketId(msg["co_socket_id"])
    alias = msg["alias"]
    socket_type = msg["socket_type"]
    physical_position = msg["physical_position"]

    def _write() -> None:
        with db_connection(db_path) as conn:
            socket_ops.update_co_socket(
                conn,
                socket_id=co_socket_id,
                alias=alias,
                socket_type=socket_type,
                physical_position=physical_position,
            )

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/delete_co",
        vol.Required("co_id"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_delete_co(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Delete a CO (docs/LLD.md §13), following create_uo's
    precedent: admin-gated, errors mapped by _run_write, bare ack.
    Gated behind debug mode (#246) -- deleting a CO is a reset, not a
    removal: discovery is additive and recreates it, with a fresh alias
    and default sockets, on the panel's next load.

    Cascades to the CO's sockets at the DB level and releases whatever was
    plugged into them (db/operations/devices.py's delete_co closes any open
    history log rows first, since a cascade never touches a log table). Idempotent --
    a no-op, not NotFoundError, for an unknown co_id, matching
    unassign_co_from_uo's precedent rather than
    update_co's: there is nothing left to delete either way.
    """
    if not _debug_mode_enabled_or_error(hass, connection, msg):
        return
    db_path = _get_db_path(hass)
    co_id = CoId(DeviceId(msg["co_id"]))

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.delete_co(conn, co_id, now=_now())

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/delete_uo",
        vol.Required("uo_id"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_delete_uo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Delete an Unmanaged Outlet (docs/LLD.md §13), following delete_co's
    precedent: admin-gated, gated behind debug mode (#246), errors mapped
    by _run_write, bare ack.

    Releases every PCO plugged into it at the DB level
    (db/operations/devices.py's delete_uo closes each
    affected CO's open plug_log row first). Idempotent -- a
    no-op for an unknown uo_id, matching delete_co.
    """
    if not _debug_mode_enabled_or_error(hass, connection, msg):
        return
    db_path = _get_db_path(hass)
    uo_id = UoId(DeviceId(msg["uo_id"]))

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.delete_uo(conn, uo_id, now=_now())

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "outlet_binder/delete_appliance",
        vol.Required("appliance_id"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def handle_delete_appliance(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Delete an Appliance (docs/LLD.md §13), following delete_co's
    precedent: admin-gated, gated behind debug mode (#246), errors mapped
    by _run_write, bare ack.

    Frees the socket it was plugged into at the DB level
    (db/operations/devices.py's delete_appliance closes any open
    plug_log row first). Idempotent -- a no-op for an unknown
    appliance_id, matching delete_co.
    """
    if not _debug_mode_enabled_or_error(hass, connection, msg):
        return
    db_path = _get_db_path(hass)
    appliance_id = ApplianceId(DeviceId(msg["appliance_id"]))

    def _write() -> None:
        with db_connection(db_path) as conn:
            device_ops.delete_appliance(conn, appliance_id, now=_now())

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command({"type": "outlet_binder/edit_session_undo"})
@websocket_api.require_admin
@websocket_api.async_response
async def handle_edit_session_undo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Move the edit-session cursor back past the whole group at the tail,
    in one call (#190). Bare ack -- the panel re-fetches get_state and
    reads the new cursor_seq off the edit_session sidecar.
    """
    db_path = _get_db_path(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            edit_session.undo(conn)

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command({"type": "outlet_binder/edit_session_redo"})
@websocket_api.require_admin
@websocket_api.async_response
async def handle_edit_session_redo(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Move the edit-session cursor forward past the whole group
    immediately ahead of it, in one call (#190). Bare ack, same reasoning
    as handle_edit_session_undo.
    """
    db_path = _get_db_path(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            edit_session.redo(conn)

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command({"type": "outlet_binder/edit_session_commit"})
@websocket_api.require_admin
@websocket_api.async_response
async def handle_edit_session_commit(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Apply every staged entry up to the cursor for real, then start a
    fresh session (#190). Deliberately does not use the projection's
    failure-collecting replay: a stale entry raises NotFoundError, which
    _run_write maps to ERR_NOT_FOUND, and a loop raises LoopError and a plug
    of a fixed device raises FixedDeviceError, which it maps to
    ERR_HOME_ASSISTANT_ERROR, with entries before the failure
    already committed and the log left un-flushed
    (db/edit_session.py's commit docstring -- no cross-entry atomicity).
    """
    db_path = _get_db_path(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            edit_session.commit(conn)

    await _run_write(hass, connection, msg, _write)


@websocket_api.websocket_command({"type": "outlet_binder/edit_session_flush"})
@websocket_api.require_admin
@websocket_api.async_response
async def handle_edit_session_flush(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Discard the whole staged session -- nothing is written (#190)."""
    db_path = _get_db_path(hass)

    def _write() -> None:
        with db_connection(db_path) as conn:
            edit_session.flush(conn)

    await _run_write(hass, connection, msg, _write)


async def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register this integration's WebSocket commands."""
    websocket_api.async_register_command(hass, handle_get_state)
    websocket_api.async_register_command(hass, handle_get_socket_ha_names)
    websocket_api.async_register_command(hass, handle_discover_cos)
    websocket_api.async_register_command(hass, handle_create_uo)
    websocket_api.async_register_command(hass, handle_create_appliance)
    websocket_api.async_register_command(hass, handle_create_plugged_into)
    websocket_api.async_register_command(hass, handle_unplug_plugged_into)
    websocket_api.async_register_command(hass, handle_assign_co_to_uo)
    websocket_api.async_register_command(hass, handle_assign_appliance_to_uo)
    websocket_api.async_register_command(hass, handle_unassign_appliance_from_uo)
    websocket_api.async_register_command(hass, handle_unassign_co_from_uo)
    websocket_api.async_register_command(hass, handle_assign_co_to_co_socket)
    websocket_api.async_register_command(hass, handle_unassign_co_from_co_socket)
    websocket_api.async_register_command(hass, handle_update_uo)
    websocket_api.async_register_command(hass, handle_update_appliance)
    websocket_api.async_register_command(hass, handle_update_co)
    websocket_api.async_register_command(hass, handle_update_co_socket)
    websocket_api.async_register_command(hass, handle_delete_co)
    websocket_api.async_register_command(hass, handle_delete_uo)
    websocket_api.async_register_command(hass, handle_delete_appliance)
    websocket_api.async_register_command(hass, handle_edit_session_undo)
    websocket_api.async_register_command(hass, handle_edit_session_redo)
    websocket_api.async_register_command(hass, handle_edit_session_commit)
    websocket_api.async_register_command(hass, handle_edit_session_flush)
