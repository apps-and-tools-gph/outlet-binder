"""Every SQL statement about the Plug Log concept.

`plug_log` records every stay of a device in a socket, whatever the kind:
an Appliance in a CO's socket, a CO in an Unmanaged Outlet's socket. A row is
open while `unplugged_at` is `NULL`. It carries snapshots and no foreign
keys, so a row stays readable after the device or socket it names is
deleted -- which is the whole reason it is a log rather than a view.

The current state of a plug is `devices.plugged_into_socket_id`
(sql/devices.py). Nothing here opens a transaction: plugging displaces up to
two existing plugs and touches this table and `devices`, so its sequencing
lives in db/operations/plug.py.
"""

import sqlite3

from ...domain.identifiers import DeviceId, SocketId, Timestamp
from ...domain.models import PlugLogEntry

_COLUMNS = (
    "entry_seq, device_id, device_name, socket_id, socket_label,"
    " host_device_id, host_name, plugged_at, unplugged_at"
)


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE plug_log (
          entry_seq      INTEGER PRIMARY KEY,
          device_id      TEXT NOT NULL,
          device_name    TEXT NOT NULL,
          socket_id      TEXT NOT NULL,
          socket_label   TEXT NOT NULL,
          host_device_id TEXT NOT NULL,
          host_name      TEXT NOT NULL,
          plugged_at     TEXT NOT NULL,
          unplugged_at   TEXT
        )
        """
    )


def create_open_device_index(conn: sqlite3.Connection) -> None:
    """At most one open row per device."""
    conn.execute(
        """
        CREATE UNIQUE INDEX ux_plug_log_open_device
          ON plug_log(device_id) WHERE unplugged_at IS NULL
        """
    )


def create_open_socket_index(conn: sqlite3.Connection) -> None:
    """At most one open row per socket."""
    conn.execute(
        """
        CREATE UNIQUE INDEX ux_plug_log_open_socket
          ON plug_log(socket_id) WHERE unplugged_at IS NULL
        """
    )


def _to_entry(row: sqlite3.Row) -> PlugLogEntry:
    return PlugLogEntry(
        entry_seq=row["entry_seq"],
        device_id=row["device_id"],
        device_name=row["device_name"],
        socket_id=row["socket_id"],
        socket_label=row["socket_label"],
        host_device_id=row["host_device_id"],
        host_name=row["host_name"],
        plugged_at=row["plugged_at"],
        unplugged_at=row["unplugged_at"],
    )


def open_entry(
    conn: sqlite3.Connection,
    *,
    device_id: DeviceId,
    device_name: str,
    socket_id: SocketId,
    socket_label: str,
    host_device_id: DeviceId,
    host_name: str,
    now: Timestamp,
) -> None:
    """Open a history row. The names and the label are snapshots, not
    lookups.

    `socket_label` alone does not identify a socket -- a socket's identity is
    (owner, position), and the label carries only the position half. The
    host's name is the other half, so a row stays readable after the socket
    it names is deleted (issue #60)."""
    conn.execute(
        """
        INSERT INTO plug_log
          (device_id, device_name, socket_id, socket_label,
           host_device_id, host_name, plugged_at, unplugged_at)
        VALUES (:device_id, :device_name, :socket_id, :socket_label,
                :host_device_id, :host_name, :plugged_at, NULL)
        """,
        {
            "device_id": device_id,
            "device_name": device_name,
            "socket_id": socket_id,
            "socket_label": socket_label,
            "host_device_id": host_device_id,
            "host_name": host_name,
            "plugged_at": now,
        },
    )


def close_for_device(conn: sqlite3.Connection, *, device_id: DeviceId, now: Timestamp) -> None:
    conn.execute(
        "UPDATE plug_log SET unplugged_at = ? WHERE device_id = ? AND unplugged_at IS NULL",
        (now, device_id),
    )


def close_for_socket(conn: sqlite3.Connection, *, socket_id: SocketId, now: Timestamp) -> None:
    conn.execute(
        "UPDATE plug_log SET unplugged_at = ? WHERE socket_id = ? AND unplugged_at IS NULL",
        (now, socket_id),
    )


def list_all(conn: sqlite3.Connection) -> list[PlugLogEntry]:
    """Every history row, oldest first."""
    rows = conn.execute("SELECT " + _COLUMNS + " FROM plug_log ORDER BY entry_seq").fetchall()
    return [_to_entry(row) for row in rows]


def list_open(conn: sqlite3.Connection) -> list[PlugLogEntry]:
    """Every currently-open row, oldest first."""
    rows = conn.execute(
        "SELECT " + _COLUMNS + " FROM plug_log WHERE unplugged_at IS NULL ORDER BY entry_seq"
    ).fetchall()
    return [_to_entry(row) for row in rows]


def list_for_device(conn: sqlite3.Connection, device_id: DeviceId) -> list[PlugLogEntry]:
    """Every history row for one device, oldest first."""
    rows = conn.execute(
        "SELECT " + _COLUMNS + " FROM plug_log WHERE device_id = ? ORDER BY entry_seq",
        (device_id,),
    ).fetchall()
    return [_to_entry(row) for row in rows]


def list_for_socket(conn: sqlite3.Connection, socket_id: SocketId) -> list[PlugLogEntry]:
    """Every history row for one socket, oldest first."""
    rows = conn.execute(
        "SELECT " + _COLUMNS + " FROM plug_log WHERE socket_id = ? ORDER BY entry_seq",
        (socket_id,),
    ).fetchall()
    return [_to_entry(row) for row in rows]
