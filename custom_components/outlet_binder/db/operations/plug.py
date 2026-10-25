"""Plugging a device into a socket, and unplugging it again.

A plug goes four ways: an Appliance into a CO's socket, an Appliance into a
Unmanaged Outlet, a CO into an Unmanaged Outlet, and a CO into another CO's socket,
which chains them. The typed entry points below accept those call shapes and
refuse anything else, so another pairing is "not found". They share one core,
`_plug`, which takes any device and any socket and does not check their
kinds, only that the device has a plug and that plugging it in would not make
a loop.

An operation here reads two or three concepts to write a third (the device,
its socket and the socket's owner, to write the plug and its history), which
is why it lives in db/operations/ and not db/sql/.
"""

import sqlite3

from ...domain.chain import ParentOf, parent_via_socket, would_loop
from ...domain.identifiers import (
    ApplianceId,
    CoId,
    DeviceId,
    SocketId,
    Timestamp,
    UoId,
)
from ...domain.models import Device, DeviceType, Socket
from ...domain.new_ids import next_dumb_socket
from ..sql import devices as devices_sql
from ..sql import plug_log as plug_log_sql
from ..sql import sockets as sockets_sql
from ..sql import transaction
from .errors import FixedDeviceError, LoopError, NotFoundError, WrongKindError


def _not_found(exists: bool, message: str) -> NotFoundError:
    """`WrongKindError` for a row that exists but is the wrong kind, so a
    test can tell the two apart; the message, and so the wire, is the same."""
    return WrongKindError(message) if exists else NotFoundError(message)


def _parent_of(conn: sqlite3.Connection) -> ParentOf:
    """The parent of a device, read from the database one row at a time."""

    def plug_of(device_id: DeviceId) -> SocketId | None:
        device = devices_sql.get(conn, device_id)
        return device.plugged_into_socket_id if device is not None else None

    def owner_of(socket_id: SocketId) -> DeviceId | None:
        socket = sockets_sql.get(conn, socket_id)
        return socket.device_id if socket is not None else None

    return parent_via_socket(plug_of=plug_of, owner_of=owner_of)


def _host_of(conn: sqlite3.Connection, device: Device) -> Device | None:
    """The device that owns the socket `device` is plugged into, if any."""
    host_id = _parent_of(conn)(device.device_id)
    return devices_sql.get(conn, host_id) if host_id is not None else None


def _plug(
    conn: sqlite3.Connection, *, device: Device, socket: Socket, host: Device, now: Timestamp
) -> None:
    """Put `device`'s plug in `socket`, which `host` owns. Must run inside a
    transaction.

    Raises `FixedDeviceError` before anything is written when `device` has no
    plug, and `LoopError` when `host` is `device` or hangs from it, so no
    entry point can plug in a fixed device or write a loop.

    Displaces whichever of the device's current plug and the socket's current
    occupant exist, closing each one's open history row, then plugs in and
    opens a new row -- so history stays consistent with current state. The
    occupant is released before the new plug is written because the plug
    column is `UNIQUE`.
    """
    if not device.has_plug:
        raise FixedDeviceError(f"'{device.device_name}' is fixed in place and cannot be plugged in")
    if would_loop(device_id=device.device_id, host_id=host.device_id, parent_of=_parent_of(conn)):
        raise LoopError(
            f"Cannot plug '{device.device_name}' into '{socket.alias}' on '{host.device_name}':"
            " that would make a loop"
        )
    occupant = devices_sql.get_occupant(conn, socket_id=socket.socket_id)
    if occupant is not None and occupant.device_id != device.device_id:
        devices_sql.clear_plug(conn, device_id=occupant.device_id, now=now)
    plug_log_sql.close_for_device(conn, device_id=device.device_id, now=now)
    plug_log_sql.close_for_socket(conn, socket_id=socket.socket_id, now=now)

    devices_sql.set_plug(conn, device_id=device.device_id, socket_id=socket.socket_id, now=now)
    plug_log_sql.open_entry(
        conn,
        device_id=device.device_id,
        device_name=device.device_name,
        socket_id=socket.socket_id,
        socket_label=socket.alias,
        host_device_id=host.device_id,
        host_name=host.device_name,
        now=now,
    )


def _take_dumb_socket(
    conn: sqlite3.Connection, *, device: Device, uo: Device, now: Timestamp
) -> Socket:
    """The socket of `uo` that `device` is about to plug into.

    Dumb sockets are interchangeable, so a device takes the lowest free one;
    an Unmanaged Outlet with none free grows by one, so there is no capacity limit.
    A device already in this Unmanaged Outlet is unplugged first, so its own
    socket counts as free and re-plugging it never grows the count. Must run
    inside a transaction.
    """
    sockets = sockets_sql.list_for_device(conn, device_id=uo.device_id)
    if device.plugged_into_socket_id in {socket.socket_id for socket in sockets}:
        _unplug(conn, device=device, now=now)
    occupied = devices_sql.list_occupied_socket_ids(conn)
    free = [socket for socket in sockets if socket.socket_id not in occupied]
    if free:
        return free[0]
    grown = next_dumb_socket(device_id=uo.device_id, sockets=sockets)
    sockets_sql.insert(conn, grown)
    return grown


def _unplug(conn: sqlite3.Connection, *, device: Device, now: Timestamp) -> None:
    """Take `device`'s plug out, if it has one. Must run inside a
    transaction."""
    if device.plugged_into_socket_id is not None:
        devices_sql.clear_plug(conn, device_id=device.device_id, now=now)
        plug_log_sql.close_for_device(conn, device_id=device.device_id, now=now)


def create_plugged_into(
    conn: sqlite3.Connection, *, appliance_id: ApplianceId, socket_id: SocketId, now: Timestamp
) -> None:
    """Plug an Appliance into a PCO's socket.

    Displaces whichever of the Appliance's and the socket's current plugs
    exist, then plugs in -- all inside one `BEGIN IMMEDIATE` transaction.
    Raises `NotFoundError` if `appliance_id` is not an Appliance or
    `socket_id` is not a socket of a CO.

    The lookups are validation, not reads for their own sake, which is why
    they are inside the transaction: without that, a concurrent writer could
    delete the Appliance between the check and the write.
    """
    with transaction.immediate(conn):
        appliance = devices_sql.get(conn, appliance_id)
        if appliance is None or appliance.device_type is not DeviceType.APPLIANCE:
            raise _not_found(appliance is not None, "That Appliance no longer exists.")
        socket = sockets_sql.get(conn, socket_id)
        host = devices_sql.get(conn, socket.device_id) if socket is not None else None
        if socket is None or host is None or host.device_type is not DeviceType.CO:
            raise _not_found(socket is not None, "That Socket no longer exists.")
        _plug(conn, device=appliance, socket=socket, host=host, now=now)


def unplug_plugged_into(
    conn: sqlite3.Connection, *, appliance_id: ApplianceId, now: Timestamp
) -> None:
    """Unplug an Appliance from a PCO's socket, if it is in one.

    A no-op (not an error) if the id is not an Appliance or it is not
    plugged into a CO -- including when it is in an Unmanaged Outlet, which only
    `unplug_appliance_from_uo` undoes -- so "unplug" is idempotent
    from the caller's perspective and never takes an Appliance out of the
    wrong place.
    """
    _unplug_from(
        conn,
        device_id=appliance_id,
        device_type=DeviceType.APPLIANCE,
        host_type=DeviceType.CO,
        now=now,
    )


def assign_co_to_uo(conn: sqlite3.Connection, *, co_id: CoId, uo_id: UoId, now: Timestamp) -> None:
    """Plug a PCO into an Unmanaged Outlet.

    The CO takes a dumb socket as `_take_dumb_socket` says. Raises
    `NotFoundError` if `co_id` is not a CO or `uo_id` is not a
    Unmanaged Outlet.
    """
    with transaction.immediate(conn):
        co = devices_sql.get(conn, co_id)
        if co is None or co.device_type is not DeviceType.CO:
            raise _not_found(co is not None, "That Smart Device no longer exists.")
        uo = devices_sql.get(conn, uo_id)
        if uo is None or uo.device_type is not DeviceType.UO:
            raise _not_found(uo is not None, "That Wall Socket no longer exists.")
        target = _take_dumb_socket(conn, device=co, uo=uo, now=now)
        _plug(conn, device=co, socket=target, host=uo, now=now)


def _unplug_from(
    conn: sqlite3.Connection,
    *,
    device_id: DeviceId,
    device_type: DeviceType,
    host_type: DeviceType,
    now: Timestamp,
) -> None:
    """Unplug a device of `device_type` only if it hangs from a device of
    `host_type`; anything else, including not being plugged in, is left
    alone. The one place that decides an unplug may not take a device out of
    the wrong place."""
    with transaction.immediate(conn):
        device = devices_sql.get(conn, device_id)
        if device is None or device.device_type is not device_type:
            return
        host = _host_of(conn, device)
        if host is not None and host.device_type is host_type:
            _unplug(conn, device=device, now=now)


def unassign_co_from_uo(conn: sqlite3.Connection, *, co_id: CoId, now: Timestamp) -> None:
    """Unplug a PCO from its Unmanaged Outlet, if it is in one.

    A no-op (not an error) if the id is not a CO or it is not plugged into
    an Unmanaged Outlet -- including when it hangs from another CO, which only
    `unplug_co_from_co_socket` undoes. That matches `unplug_plugged_into`'s
    precedent rather than `assign_co_to_uo`'s `NotFoundError`:
    there is nothing to displace either way.
    """
    _unplug_from(
        conn,
        device_id=co_id,
        device_type=DeviceType.CO,
        host_type=DeviceType.UO,
        now=now,
    )


def plug_co_into_co_socket(
    conn: sqlite3.Connection, *, co_id: CoId, socket_id: SocketId, now: Timestamp
) -> None:
    """Plug a PCO into a socket of another PCO, chaining them.

    Displaces whichever of the CO's and the socket's current plugs exist,
    then plugs in. Raises `NotFoundError` if `co_id` is not a CO or
    `socket_id` is not a socket of a CO, and `LoopError` if the CO is the
    socket's owner or hangs above it.
    """
    with transaction.immediate(conn):
        co = devices_sql.get(conn, co_id)
        if co is None or co.device_type is not DeviceType.CO:
            raise _not_found(co is not None, "That Smart Device no longer exists.")
        socket = sockets_sql.get(conn, socket_id)
        host = devices_sql.get(conn, socket.device_id) if socket is not None else None
        if socket is None or host is None or host.device_type is not DeviceType.CO:
            raise _not_found(socket is not None, "That Socket no longer exists.")
        _plug(conn, device=co, socket=socket, host=host, now=now)


def unplug_co_from_co_socket(conn: sqlite3.Connection, *, co_id: CoId, now: Timestamp) -> None:
    """Unplug a PCO from the socket of another PCO, if it is in one.

    A no-op if the id is not a CO or it is not plugged into a CO's socket,
    so it never takes a CO out of an Unmanaged Outlet.
    """
    _unplug_from(
        conn,
        device_id=co_id,
        device_type=DeviceType.CO,
        host_type=DeviceType.CO,
        now=now,
    )


def plug_appliance_into_uo(
    conn: sqlite3.Connection,
    *,
    appliance_id: ApplianceId,
    uo_id: UoId,
    now: Timestamp,
) -> None:
    """Plug an Appliance straight into an Unmanaged Outlet, with no PCO between.

    It records where the Appliance physically is. The Appliance takes a dumb
    socket as `_take_dumb_socket` says, and an Appliance owns no socket, so
    this can never make a loop. Raises `NotFoundError` if `appliance_id` is
    not an Appliance or `uo_id` is not an Unmanaged Outlet.
    """
    with transaction.immediate(conn):
        appliance = devices_sql.get(conn, appliance_id)
        if appliance is None or appliance.device_type is not DeviceType.APPLIANCE:
            raise _not_found(appliance is not None, "That Appliance no longer exists.")
        uo = devices_sql.get(conn, uo_id)
        if uo is None or uo.device_type is not DeviceType.UO:
            raise _not_found(uo is not None, "That Wall Socket no longer exists.")
        target = _take_dumb_socket(conn, device=appliance, uo=uo, now=now)
        _plug(conn, device=appliance, socket=target, host=uo, now=now)


def unplug_appliance_from_uo(
    conn: sqlite3.Connection, *, appliance_id: ApplianceId, now: Timestamp
) -> None:
    """Unplug an Appliance from its Unmanaged Outlet, if it is in one.

    A no-op if the id is not an Appliance or it is not plugged into an Unmanaged
    Outlet, so it never takes an Appliance out of a CO's socket.
    """
    _unplug_from(
        conn,
        device_id=appliance_id,
        device_type=DeviceType.APPLIANCE,
        host_type=DeviceType.UO,
        now=now,
    )
