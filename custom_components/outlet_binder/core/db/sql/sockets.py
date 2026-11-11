"""Every SQL statement about the Socket concept.

A socket is a place a plug can go, owned by one device. A CO's sockets are
smart: the socket's id is Home Assistant's entity-registry id for its on/off
entity, so it stays stable across a database wipe. An Unmanaged Outlet's sockets
are dumb: generated ids, interchangeable, and their alias and position carry
no meaning.

What is plugged into a socket is the owning concept's business, in
sql/devices.py, and the history of it is in sql/plug_log.py.
"""

import sqlite3

from ...domain.identifiers import DeviceId, SocketId
from ...domain.models import Socket

_COLUMNS = (
    "socket_id, device_id, is_smart, alias, socket_type, position,"
    " physical_position, monitoring_entity_registry_id"
)


def _to_socket(row: sqlite3.Row) -> Socket:
    return Socket(
        socket_id=row["socket_id"],
        device_id=row["device_id"],
        is_smart=bool(row["is_smart"]),
        alias=row["alias"],
        socket_type=row["socket_type"],
        position=row["position"],
        physical_position=row["physical_position"],
        monitoring_entity_registry_id=row["monitoring_entity_registry_id"],
    )


def list_all(conn: sqlite3.Connection) -> list[Socket]:
    rows = conn.execute("SELECT " + _COLUMNS + " FROM sockets").fetchall()
    return [_to_socket(row) for row in rows]


def get(conn: sqlite3.Connection, socket_id: SocketId) -> Socket | None:
    row = conn.execute(
        "SELECT " + _COLUMNS + " FROM sockets WHERE socket_id = ?", (socket_id,)
    ).fetchone()
    return _to_socket(row) if row is not None else None


def list_for_device(conn: sqlite3.Connection, *, device_id: DeviceId) -> list[Socket]:
    """Every socket one device owns, lowest position first."""
    rows = conn.execute(
        "SELECT " + _COLUMNS + " FROM sockets WHERE device_id = ? ORDER BY position",
        (device_id,),
    ).fetchall()
    return [_to_socket(row) for row in rows]


def insert(conn: sqlite3.Connection, socket: Socket) -> None:
    conn.execute(
        "INSERT INTO sockets"
        " (socket_id, device_id, is_smart, alias, socket_type, position,"
        "  physical_position, monitoring_entity_registry_id)"
        " VALUES (:socket_id, :device_id, :is_smart, :alias, :socket_type, :position,"
        " :physical_position, :monitoring_entity_registry_id)",
        {
            "socket_id": socket.socket_id,
            "device_id": socket.device_id,
            "is_smart": int(socket.is_smart),
            "alias": socket.alias,
            "socket_type": socket.socket_type,
            "position": socket.position,
            "physical_position": socket.physical_position,
            "monitoring_entity_registry_id": socket.monitoring_entity_registry_id,
        },
    )


def update_fields(
    conn: sqlite3.Connection,
    *,
    socket_id: SocketId,
    alias: str,
    socket_type: str | None,
    physical_position: int | None,
) -> None:
    """No `now`/`updated_at` -- this table carries no timestamp columns."""
    conn.execute(
        "UPDATE sockets SET alias = :alias, socket_type = :socket_type,"
        " physical_position = :physical_position WHERE socket_id = :socket_id",
        {
            "socket_id": socket_id,
            "alias": alias,
            "socket_type": socket_type,
            "physical_position": physical_position,
        },
    )


def delete(conn: sqlite3.Connection, socket_id: SocketId) -> None:
    """Remove one socket. A plug in it would be set to `NULL` by the foreign
    key, so the caller removes only free ones."""
    conn.execute("DELETE FROM sockets WHERE socket_id = ?", (socket_id,))
