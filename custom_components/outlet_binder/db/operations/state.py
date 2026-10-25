"""Full application state assembly (V1 read model, docs/LLD.md §13)."""

import sqlite3
from typing import Any

from ...domain.chain import area_source, effective_area, parent_via_socket
from ...domain.identifiers import CoId, DeviceId, HaAreaId, SocketId
from ...domain.models import Device, DeviceType
from ..sql import devices as devices_sql
from ..sql import sockets as sockets_sql


def _location_override_to_json(device: Device) -> dict[str, str | None] | None:
    """A CO's area and note as the wire's `location_override` pair, or
    `None` when both are unset -- the two columns cannot tell "no override"
    from an override to nothing, and nothing is lost by treating them alike."""
    if device.ha_area_id is None and device.location_note is None:
        return None
    return {"ha_area_id": device.ha_area_id, "location_note": device.location_note}


def list_co_socket_owners(conn: sqlite3.Connection) -> list[tuple[SocketId, CoId]]:
    """Every socket of a CO with the CO that owns it. An Unmanaged Outlet's dumb
    sockets are left out: they are not CO Sockets and have no HA entity."""
    co_ids = {
        device.device_id for device in devices_sql.list_of_type(conn, device_type=DeviceType.CO)
    }
    return [
        (socket.socket_id, CoId(socket.device_id))
        for socket in sockets_sql.list_all(conn)
        if socket.device_id in co_ids
    ]


def get_full_state(conn: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    """Assemble the full application state as a plain JSON-serializable dict.

    V1 read model, per docs/LLD.md §13: one command returns everything, as
    flat lists carrying their own foreign keys (`uo_id` on a CO,
    `occupant_device_id` on a CO Socket, etc.) rather than a
    server-side-nested tree — the frontend joins by ID. The lists are a
    projection of `devices` and `sockets` onto the four shapes the frontend
    knows, and are built here in Python: each is a filter on the owner's
    kind, which a generic statement would get wrong without any error. A CO
    plugged into another CO's socket has `uo_id` `None` and
    `plugged_into_co_socket_id` set; exactly one of the two is set while it
    is plugged in, and the same holds for an Appliance, which is never given a
    dumb socket's id as a CO socket. `effective_ha_area_id` is the CO's own area, else the
    nearest one up its chain. `inherited_ha_area_source_id` is the nearest device above the CO
    with an area of its own (its override never counts), or `None`: what clearing the
    override would give.

    Does not read the plug log -- current state stays independent of
    history (db/sql/plug_log.py's module docstring).

    `manufacturer`/`model`/MAC/live area aren't included here or anywhere
    in the `get_state` response -- not stored, and this function stays
    DB-only (no `hass`, so no registry access). The panel reads them from
    `hass.devices[co_id]` (#369).
    """
    devices = devices_sql.list_all(conn)
    sockets = sockets_sql.list_all(conn)
    device_by_id = {device.device_id: device for device in devices}
    owner_by_socket = {socket.socket_id: device_by_id[socket.device_id] for socket in sockets}
    occupant_by_socket = {
        device.plugged_into_socket_id: device
        for device in devices
        if device.plugged_into_socket_id is not None
    }

    def plug_of(device_id: DeviceId) -> SocketId | None:
        device = device_by_id.get(device_id)
        return device.plugged_into_socket_id if device is not None else None

    def owner_of(socket_id: SocketId) -> DeviceId | None:
        owner = owner_by_socket.get(socket_id)
        return owner.device_id if owner is not None else None

    parent_of = parent_via_socket(plug_of=plug_of, owner_of=owner_of)

    def hosting(device: Device) -> Device | None:
        """The device that owns the socket `device` is plugged into."""
        host_id = parent_of(device.device_id)
        return device_by_id[host_id] if host_id is not None else None

    def own_area_of(device_id: DeviceId) -> HaAreaId | None:
        return device_by_id[device_id].ha_area_id

    sockets_owned: dict[DeviceId, int] = {}
    sockets_held: dict[DeviceId, int] = {}
    for socket in sockets:
        sockets_owned[socket.device_id] = sockets_owned.get(socket.device_id, 0) + 1
        if socket.socket_id in occupant_by_socket:
            sockets_held[socket.device_id] = sockets_held.get(socket.device_id, 0) + 1

    uos = [
        {
            "uo_id": device.device_id,
            "name": device.device_name,
            "ha_area_id": device.ha_area_id,
            "location_note": device.location_note,
            "socket_count": sockets_owned.get(device.device_id, 0),
            "sockets_in_use": sockets_held.get(device.device_id, 0),
        }
        for device in devices
        if device.device_type is DeviceType.UO
    ]

    cos = []
    for device in devices:
        if device.device_type is not DeviceType.CO:
            continue
        host = hosting(device)
        cos.append(
            {
                "co_id": device.device_id,
                "alias": device.device_name,
                "has_plug": device.has_plug,
                "uo_id": (
                    host.device_id
                    if host is not None and host.device_type is DeviceType.UO
                    else None
                ),
                "plugged_into_co_socket_id": (
                    device.plugged_into_socket_id
                    if host is not None and host.device_type is DeviceType.CO
                    else None
                ),
                "location_override": _location_override_to_json(device),
                "effective_ha_area_id": effective_area(
                    device_id=device.device_id, own_area_of=own_area_of, parent_of=parent_of
                ),
                "inherited_ha_area_source_id": (
                    area_source(
                        device_id=host.device_id, own_area_of=own_area_of, parent_of=parent_of
                    )
                    if host is not None
                    else None
                ),
                "all_on_off_entity_registry_id": device.all_on_off_entity_registry_id,
                "created_at": device.created_at,
            }
        )

    co_sockets = []
    for socket in sockets:
        if owner_by_socket[socket.socket_id].device_type is not DeviceType.CO:
            continue
        occupant = occupant_by_socket.get(socket.socket_id)
        co_sockets.append(
            {
                "co_socket_id": socket.socket_id,
                "co_id": socket.device_id,
                "alias": socket.alias,
                "socket_type": socket.socket_type,
                "position": socket.position,
                "physical_position": socket.physical_position,
                "monitoring_entity_registry_id": socket.monitoring_entity_registry_id,
                "plugged_into_appliance_id": (
                    occupant.device_id
                    if occupant is not None and occupant.device_type is DeviceType.APPLIANCE
                    else None
                ),
                "occupant_device_id": occupant.device_id if occupant is not None else None,
            }
        )

    appliances = []
    for device in devices:
        if device.device_type is not DeviceType.APPLIANCE:
            continue
        host = hosting(device)
        appliances.append(
            {
                "appliance_id": device.device_id,
                "name": device.device_name,
                "type": device.appliance_type,
                "description": device.description,
                "plugged_into_co_socket_id": (
                    device.plugged_into_socket_id
                    if host is not None and host.device_type is DeviceType.CO
                    else None
                ),
                "uo_id": (
                    host.device_id
                    if host is not None and host.device_type is DeviceType.UO
                    else None
                ),
            }
        )

    return {
        "uos": uos,
        "cos": cos,
        "co_sockets": co_sockets,
        "appliances": appliances,
    }
