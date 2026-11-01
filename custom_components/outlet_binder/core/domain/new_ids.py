"""Minting the app-generated ids, each with its kind's prefix.

The one place an id is generated, so an Unmanaged Outlet, an Appliance and a dumb
socket cannot be minted with the wrong prefix in one call site and the right
one in another. A CO's and a smart socket's ids are Home Assistant's own
registry ids and are never minted here. The prefixes themselves live in
domain/identifiers.py, which the database `CHECK`s are built from too.

Dependency-free: no `hass`, no persistence.
"""

import uuid
from collections.abc import Sequence

from .identifiers import (
    APPLIANCE_ID_PREFIX,
    DUMB_SOCKET_ID_PREFIX,
    UO_ID_PREFIX,
    ApplianceId,
    DeviceId,
    SocketId,
    UoId,
)
from .models import Socket

# A new Unmanaged Outlet starts with this many dumb sockets; plugging into a full
# one adds another.
DUMB_SOCKETS_PER_NEW_UO = 2


def mint_uo_id() -> UoId:
    return UoId(DeviceId(f"{UO_ID_PREFIX}{uuid.uuid4()}"))


def mint_appliance_id() -> ApplianceId:
    return ApplianceId(DeviceId(f"{APPLIANCE_ID_PREFIX}{uuid.uuid4()}"))


def new_dumb_socket(*, device_id: DeviceId, position: int) -> Socket:
    """A dumb socket on `device_id`. Its alias and position carry no meaning
    -- dumb sockets are interchangeable and the panel shows only a count --
    but the table needs both, and the alias must not be blank."""
    return Socket(
        socket_id=SocketId(f"{DUMB_SOCKET_ID_PREFIX}{uuid.uuid4()}"),
        device_id=device_id,
        is_smart=False,
        alias=f"Socket {position}",
        socket_type=None,
        position=position,
        physical_position=None,
        monitoring_entity_registry_id=None,
    )


def next_dumb_socket(*, device_id: DeviceId, sockets: Sequence[Socket]) -> Socket:
    """The dumb socket that grows an Unmanaged Outlet by one: a position after the
    highest it has. The one place growth picks a position, whether it was a
    plug into a full Unmanaged Outlet or a count set by hand."""
    return new_dumb_socket(
        device_id=device_id, position=max((socket.position for socket in sockets), default=0) + 1
    )
