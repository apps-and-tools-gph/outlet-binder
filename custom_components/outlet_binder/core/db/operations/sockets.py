"""Socket operations."""

import sqlite3

from ...domain.identifiers import SocketId
from ...domain.models import DeviceType, Socket
from ..sql import devices as devices_sql
from ..sql import sockets as sockets_sql
from ..sql import transaction
from .errors import NotFoundError, WrongKindError


def update_co_socket(
    conn: sqlite3.Connection,
    *,
    socket_id: SocketId,
    alias: str,
    socket_type: str | None,
    physical_position: int | None,
) -> Socket:
    """Update a CO Socket's editable fields (`alias`, `socket_type`,
    `physical_position`) -- the owner and `position` are discovery-owned
    identity, not editable fields. Raises `NotFoundError` if `socket_id` is
    not a socket of a CO: an Unmanaged Outlet's dumb socket has no editable
    fields, and the panel never offers one."""
    message = "That Socket no longer exists."
    with transaction.immediate(conn):
        socket = sockets_sql.get(conn, socket_id)
        if socket is None:
            raise NotFoundError(message)
        owner = devices_sql.get(conn, socket.device_id)
        if owner is None or owner.device_type is not DeviceType.CO:
            raise WrongKindError(message)
        sockets_sql.update_fields(
            conn,
            socket_id=socket_id,
            alias=alias,
            socket_type=socket_type,
            physical_position=physical_position,
        )

    # Deliberately re-read *after* COMMIT, not inside the block.
    updated = sockets_sql.get(conn, socket_id)
    assert updated is not None  # just wrote this row
    return updated
