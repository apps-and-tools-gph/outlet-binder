"""Device operations: create, update and delete for the three kinds, and the
discovery write.

Typed entry points over private helpers, so the sequencing that a delete
needs -- close the device's own plug history and each of its sockets' before
the row goes -- exists once, whatever the kind.

A device given to an operation of another kind is treated as not found, with
the same message: `WrongKindError` for an id that names a different kind,
`NotFoundError` for one that names nothing. A delete or unplug of the wrong
kind is a no-op, as one of a missing id is.
"""

import sqlite3

from ...domain.discovery import ProposedCo
from ...domain.identifiers import (
    ApplianceId,
    CoId,
    DeviceId,
    HaAreaId,
    SocketId,
    Timestamp,
    UoId,
)
from ...domain.models import Device, DeviceType, Socket
from ...domain.new_ids import (
    DUMB_SOCKETS_PER_NEW_UO,
    mint_appliance_id,
    mint_uo_id,
    new_dumb_socket,
    next_dumb_socket,
)
from ...domain.uo_capacity import check_count, plan_resize
from ...entity_slug import device_switch_entity_id
from ..sql import devices as devices_sql
from ..sql import plug_log as plug_log_sql
from ..sql import sockets as sockets_sql
from ..sql import transaction
from .errors import DuplicateError, NotFoundError, WrongKindError


def _require(
    conn: sqlite3.Connection, device_id: DeviceId, *, device_type: DeviceType, message: str
) -> Device:
    """The device, if it exists and is of `device_type`; otherwise the
    not-found error carrying `message`."""
    device = devices_sql.get(conn, device_id)
    if device is None:
        raise NotFoundError(message)
    if device.device_type is not device_type:
        raise WrongKindError(message)
    return device


def _delete(
    conn: sqlite3.Connection, device_id: DeviceId, *, device_type: DeviceType, now: Timestamp
) -> None:
    """Delete a device of `device_type`, if there is one; otherwise do
    nothing.

    The cascade removes the device's sockets and sets to `NULL` the plug of
    anything plugged into them, but a cascade never touches a log table, so
    the open rows -- the device's own stay in a socket, and every stay in
    one of its sockets -- are closed first.
    """
    device = devices_sql.get(conn, device_id)
    if device is None or device.device_type is not device_type:
        return
    plug_log_sql.close_for_device(conn, device_id=device_id, now=now)
    for socket in sockets_sql.list_for_device(conn, device_id=device_id):
        plug_log_sql.close_for_socket(conn, socket_id=socket.socket_id, now=now)
    devices_sql.delete(conn, device_id)


def create_uo(
    conn: sqlite3.Connection,
    *,
    name: str,
    ha_area_id: HaAreaId | None,
    location_note: str | None,
    now: Timestamp,
) -> Device:
    """Create an Unmanaged Outlet with its starting dumb sockets, in one
    transaction. The id is app-generated, since there is no HA registry id
    to draw from."""
    uo = Device(
        device_id=mint_uo_id(),
        device_name=name,
        device_type=DeviceType.UO,
        has_plug=False,
        appliance_type=None,
        description=None,
        ha_area_id=ha_area_id,
        location_note=location_note,
        all_on_off_entity_registry_id=None,
        plugged_into_socket_id=None,
        created_at=now,
        updated_at=now,
    )
    with transaction.immediate(conn):
        try:
            devices_sql.insert(conn, uo)
        except sqlite3.IntegrityError as err:
            raise DuplicateError(f"A Wall Socket named {name!r} already exists") from err
        for position in range(1, DUMB_SOCKETS_PER_NEW_UO + 1):
            sockets_sql.insert(conn, new_dumb_socket(device_id=uo.device_id, position=position))
    return uo


def update_uo(
    conn: sqlite3.Connection,
    *,
    uo_id: UoId,
    name: str,
    ha_area_id: HaAreaId | None,
    location_note: str | None,
    socket_count: int,
    now: Timestamp,
) -> Device:
    """Update an Unmanaged Outlet's editable fields and its socket count, in one
    transaction, so a refused count leaves the name as it was. Raises
    `NotFoundError` if `uo_id` is not an Unmanaged Outlet -- this is an
    edit of a specific existing row, not an idempotent unlink -- and
    `SocketCountError` for a count below one or below the plugs in use.

    Raising adds sockets and lowering removes free ones only, so a plug is
    never dropped; the count is checked against the stored sockets.
    """
    with transaction.immediate(conn):
        uo = _require(
            conn,
            uo_id,
            device_type=DeviceType.UO,
            message="That Wall Socket no longer exists.",
        )
        sockets = sockets_sql.list_for_device(conn, device_id=uo_id)
        occupied = devices_sql.list_occupied_socket_ids(conn)
        check_count(
            name=uo.device_name,
            requested=socket_count,
            in_use=sum(1 for socket in sockets if socket.socket_id in occupied),
        )
        resize = plan_resize(
            sockets=[(socket.socket_id, socket.socket_id in occupied) for socket in sockets],
            requested=socket_count,
        )
        for socket_id in resize.remove:
            sockets_sql.delete(conn, socket_id)
        for _ in range(resize.add):
            grown = next_dumb_socket(device_id=uo_id, sockets=sockets)
            sockets_sql.insert(conn, grown)
            sockets = [*sockets, grown]
        try:
            devices_sql.update_name_and_location(
                conn,
                device_id=uo_id,
                name=name,
                ha_area_id=ha_area_id,
                location_note=location_note,
                now=now,
            )
        except sqlite3.IntegrityError as err:
            raise DuplicateError(f"A Wall Socket named {name!r} already exists") from err

    # Deliberately re-read *after* COMMIT, not inside the block: the
    # returned row should reflect committed state.
    updated = devices_sql.get(conn, uo_id)
    assert updated is not None  # just wrote this row
    return updated


def delete_uo(conn: sqlite3.Connection, uo_id: UoId, *, now: Timestamp) -> None:
    """Delete an Unmanaged Outlet, closing the open history row of every device
    plugged into one of its sockets first. A no-op for an id that is not a
    Unmanaged Outlet."""
    with transaction.immediate(conn):
        _delete(conn, uo_id, device_type=DeviceType.UO, now=now)


def _reject_switch_slug_clash(
    conn: sqlite3.Connection,
    *,
    device_type: DeviceType,
    name: str,
    appliance_type: str | None,
    exclude: DeviceId | None,
) -> None:
    """Two devices of one kind whose switch names slugify to the same entity_id
    can't both get it (#337). The (name, type) unique index can't see
    this: the slug ignores punctuation, so "Lamp!" and "Lamp" clash despite
    being distinct there. An Appliance's switch name includes its type, so
    two Appliances of different types may share a name. Only a device with
    a plug has a switch, and an Appliance's slug never meets a PCO's (one
    ends `on_off`, the other `plug`), so each kind is compared with its
    own."""
    slug = device_switch_entity_id(
        device_type=device_type, name=name, appliance_type=appliance_type
    )
    for other in devices_sql.list_of_type(conn, device_type=device_type):
        if other.device_id == exclude or not other.has_plug:
            continue
        other_slug = device_switch_entity_id(
            device_type=device_type,
            name=other.device_name,
            appliance_type=other.appliance_type,
        )
        if other_slug == slug:
            kind = "An Appliance" if device_type is DeviceType.APPLIANCE else "A Smart Device"
            raise DuplicateError(
                f"{kind} named {other.device_name!r} already exists "
                f"with the same switch entity id ({slug})"
            )


def _appliance_exists_message(name: str, appliance_type: str | None) -> str:
    typed = f" of type {appliance_type!r}" if appliance_type else ""
    return f"An Appliance named {name!r}{typed} already exists"


def create_appliance(
    conn: sqlite3.Connection,
    *,
    name: str,
    appliance_type: str | None,
    description: str | None,
    now: Timestamp,
) -> Device:
    """Create a new Appliance. The id is app-generated."""
    appliance = Device(
        device_id=mint_appliance_id(),
        device_name=name,
        device_type=DeviceType.APPLIANCE,
        has_plug=True,
        appliance_type=appliance_type,
        description=description,
        ha_area_id=None,
        location_note=None,
        all_on_off_entity_registry_id=None,
        plugged_into_socket_id=None,
        created_at=now,
        updated_at=now,
    )
    with transaction.immediate(conn):
        _reject_switch_slug_clash(
            conn,
            device_type=DeviceType.APPLIANCE,
            name=name,
            appliance_type=appliance_type,
            exclude=None,
        )
        try:
            devices_sql.insert(conn, appliance)
        except sqlite3.IntegrityError as err:
            raise DuplicateError(_appliance_exists_message(name, appliance_type)) from err
    return appliance


def update_appliance(
    conn: sqlite3.Connection,
    *,
    appliance_id: ApplianceId,
    name: str,
    appliance_type: str | None,
    description: str | None,
    now: Timestamp,
) -> Device:
    """Update an Appliance's editable fields. Raises `NotFoundError` if
    `appliance_id` is not an Appliance."""
    with transaction.immediate(conn):
        _require(
            conn,
            appliance_id,
            device_type=DeviceType.APPLIANCE,
            message="That Appliance no longer exists.",
        )
        _reject_switch_slug_clash(
            conn,
            device_type=DeviceType.APPLIANCE,
            name=name,
            appliance_type=appliance_type,
            exclude=appliance_id,
        )
        try:
            devices_sql.update_appliance_fields(
                conn,
                device_id=appliance_id,
                name=name,
                appliance_type=appliance_type,
                description=description,
                now=now,
            )
        except sqlite3.IntegrityError as err:
            raise DuplicateError(_appliance_exists_message(name, appliance_type)) from err

    # Deliberately re-read *after* COMMIT, not inside the block.
    updated = devices_sql.get(conn, appliance_id)
    assert updated is not None  # just wrote this row
    return updated


def delete_appliance(
    conn: sqlite3.Connection, appliance_id: ApplianceId, *, now: Timestamp
) -> None:
    """Delete an Appliance, closing its open history row first. A no-op for
    an id that is not an Appliance."""
    with transaction.immediate(conn):
        _delete(conn, appliance_id, device_type=DeviceType.APPLIANCE, now=now)


def create_discovered_co(
    conn: sqlite3.Connection, proposal: ProposedCo, *, now: Timestamp
) -> Device:
    """Persist a discovery match as a new CO with its smart sockets.

    Always a CO row: the pattern's kind decides only whether it has a plug
    (`has_plug`), so a fixed outlet is a CO that cannot be plugged in.

    One `BEGIN IMMEDIATE` covering the CO row and its sockets, so a
    partially-created CO never becomes visible to a concurrent reader.
    Discovery has no way to infer an area or a note, so both are `None`.

    Ids come straight from HA's own registries (the device's registry id,
    each socket's on/off entity registry id) -- no `uuid.uuid4()`, since
    these ids already are the primary keys. This function is therefore where
    an HA registry id *becomes* one of ours: the `CoId(...)` and
    `SocketId(...)` calls below are that decision written down, and the only
    narrowing of an HA id in the codebase.
    """
    co = Device(
        device_id=CoId(DeviceId(proposal.ha_device_registry_id)),
        device_name=proposal.alias,
        device_type=DeviceType.CO,
        has_plug=proposal.kind.has_plug,
        appliance_type=None,
        description=None,
        ha_area_id=None,
        location_note=None,
        all_on_off_entity_registry_id=proposal.all_on_off_entity_registry_id,
        plugged_into_socket_id=None,
        created_at=now,
        updated_at=now,
    )
    with transaction.immediate(conn):
        try:
            devices_sql.insert(conn, co)
        except sqlite3.IntegrityError as err:
            raise DuplicateError(
                f"A Smart Device named {co.device_name!r} already exists."
            ) from err
        # A backstop: `disambiguate_aliases` already renames a proposal
        # whose switch entity id would clash. After the insert, as in
        # `update_co`, so a name the unique index refuses keeps its own
        # message; the raise rolls the insert back.
        if co.has_plug:
            _reject_switch_slug_clash(
                conn,
                device_type=DeviceType.CO,
                name=co.device_name,
                appliance_type=None,
                exclude=co.device_id,
            )
        for socket in proposal.sockets:
            try:
                sockets_sql.insert(
                    conn,
                    Socket(
                        socket_id=SocketId(socket.on_off_entity_registry_id),
                        device_id=co.device_id,
                        is_smart=True,
                        alias=str(socket.position),
                        socket_type=None,
                        position=socket.position,
                        physical_position=None,
                        monitoring_entity_registry_id=socket.monitoring_entity_registry_id,
                    ),
                )
            except sqlite3.IntegrityError as err:
                # A socket's own PK collision or its UNIQUE(device_id,
                # position) is just as much a "this proposal can't be
                # written" case as a duplicate CO alias, and the caller
                # (handle_discover_cos) treats DuplicateError as "skip this
                # device, keep going" -- a raw IntegrityError would instead
                # abort the rest of the discovery pass (#340).
                raise DuplicateError(
                    f"A Socket for Smart Device {co.device_name!r} could not be created: {err}"
                ) from err
    return co


def update_co(
    conn: sqlite3.Connection,
    *,
    co_id: CoId,
    alias: str,
    ha_area_id: HaAreaId | None,
    location_note: str | None,
    now: Timestamp,
) -> Device:
    """Update a CO's editable fields (`alias`, `ha_area_id`, `location_note`;
    the last two are independent, either may be `None`). Which
    socket it is plugged into is a separate write path (the plug
    operations). Raises `NotFoundError` if `co_id` is not a CO."""
    with transaction.immediate(conn):
        co = _require(
            conn, co_id, device_type=DeviceType.CO, message="That Smart Device no longer exists."
        )
        try:
            devices_sql.update_name_and_location(
                conn,
                device_id=co_id,
                name=alias,
                ha_area_id=ha_area_id,
                location_note=location_note,
                now=now,
            )
        except sqlite3.IntegrityError as err:
            raise DuplicateError(f"A Smart Device named {alias!r} already exists.") from err
        # After the write, so an alias the unique index already refuses keeps its
        # own message; the raise rolls the write back.
        if co.has_plug:
            _reject_switch_slug_clash(
                conn,
                device_type=DeviceType.CO,
                name=alias,
                appliance_type=None,
                exclude=co_id,
            )

    # Deliberately re-read *after* COMMIT, not inside the block.
    updated = devices_sql.get(conn, co_id)
    assert updated is not None  # just wrote this row
    return updated


def delete_co(conn: sqlite3.Connection, co_id: CoId, *, now: Timestamp) -> None:
    """Delete a CO. Its sockets go with it and anything plugged into them
    is released; the CO's own stay in an Unmanaged Outlet and every stay in one of
    its sockets are closed first. A no-op for an id that is not a CO."""
    with transaction.immediate(conn):
        _delete(conn, co_id, device_type=DeviceType.CO, now=now)
