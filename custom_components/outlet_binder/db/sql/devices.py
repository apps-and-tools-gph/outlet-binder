"""Every SQL statement about the Device concept.

A device is an Unmanaged Outlet, a CO (a Controllable Outlet, with or without a plug) or an
Appliance, told apart by `device_type`. They share one table because a plug
can go into any socket, and `plugged_into_socket_id` -- zero-or-one, and
`UNIQUE` so a socket holds at most one plug -- is the only connection
between things.

The kind decides which columns may be set and what a name must be unique
against, so the constraints are written per kind: a name is unique within
its own kind (an Appliance's together with its type), and a column that
belongs to one kind is `NULL` on the others. `has_plug` is stored on every
row: an Unmanaged Outlet is 0, an Appliance 1 and a CO either, and a device with
no plug cannot be plugged in. What a `CHECK` cannot see
across tables -- that a CO owns a smart socket, that an Appliance owns no
socket -- is kept by db/operations/ and tested there.

The plug's history lives with the Plug Log concept, in sql/plug_log.py.
"""

import sqlite3

from ...domain.identifiers import (
    APPLIANCE_ID_PREFIX,
    UO_ID_PREFIX,
    ApplianceId,
    CoId,
    DeviceId,
    HaAreaId,
    SocketId,
    Timestamp,
    UoId,
)
from ...domain.models import Device, DeviceType

# The columns every SELECT below names, in the order `_to_device` reads them.
_COLUMNS = (
    "device_id, device_name, device_type, has_plug, appliance_type, description,"
    " ha_area_id, location_note, all_on_off_entity_registry_id,"
    " plugged_into_socket_id, created_at, updated_at"
)

# The prefixes an app-generated device id carries; a CO's id must start with
# none of them.
_APP_ID_PREFIXES = (UO_ID_PREFIX, APPLIANCE_ID_PREFIX)

_BLANK_TRIM = "' ' || char(9) || char(10) || char(13)"


def _device_types_sql() -> str:
    return ", ".join(f"'{device_type.value}'" for device_type in DeviceType)


def _has_prefix_sql(column: str, prefix: str) -> str:
    """One prefix, compared at that prefix's own length."""
    return f"substr({column}, 1, {len(prefix)}) = '{prefix}'"


def has_any_prefix_sql(column: str, prefixes: tuple[str, ...]) -> str:
    """True when `column` starts with any of `prefixes`, each compared at its
    own length, so the prefixes need not be the same size. Used to build the
    id-prefix `CHECK`s; `prefix_match_sql` below runs the same fragment, so a
    test can show it right for prefixes of different lengths."""
    return "(" + " OR ".join(_has_prefix_sql(column, prefix) for prefix in prefixes) + ")"


def prefix_match_sql(conn: sqlite3.Connection, value: str, *, prefixes: tuple[str, ...]) -> bool:
    """Whether the real `CHECK` fragment accepts `value` as starting with one
    of `prefixes` -- a schema-invariant probe (db/sql/__init__.py), not a
    second copy of the expression."""
    row = conn.execute(
        "SELECT "
        + has_any_prefix_sql("device_id", prefixes)
        + " FROM (SELECT :value AS device_id)",
        {"value": value},
    ).fetchone()
    return bool(row[0])


def create_table(conn: sqlite3.Connection) -> None:
    """`sockets` is created after this table and references it back, which
    SQLite allows: a foreign key's parent is only looked up when a row is
    written. Deleting a device cascades to its sockets, and a plug in one of
    those sockets is set to `NULL` -- a plug moves, a socket only releases.
    """
    conn.execute(
        f"""
        CREATE TABLE devices (
          device_id                     TEXT PRIMARY KEY,
          device_name                   TEXT NOT NULL
            CHECK (trim(device_name, {_BLANK_TRIM}) <> ''),
          device_type                   TEXT NOT NULL
            CHECK (device_type IN ({_device_types_sql()})),
          has_plug                      INTEGER NOT NULL CHECK (has_plug IN (0, 1)),
          appliance_type                TEXT,
          description                   TEXT,
          ha_area_id                    TEXT,
          location_note                 TEXT,
          all_on_off_entity_registry_id TEXT,
          plugged_into_socket_id         TEXT UNIQUE
            REFERENCES sockets(socket_id) ON DELETE SET NULL,
          created_at                    TEXT NOT NULL,
          updated_at                    TEXT NOT NULL,
          name_norm TEXT GENERATED ALWAYS AS (lower(replace(device_name,' ','_'))) VIRTUAL,
          type_norm TEXT GENERATED ALWAYS AS (lower(coalesce(appliance_type,''))) VIRTUAL,
          CHECK (device_type <> '{DeviceType.UO}' OR has_plug = 0),
          CHECK (device_type <> '{DeviceType.APPLIANCE}' OR has_plug = 1),
          CHECK (has_plug = 1 OR plugged_into_socket_id IS NULL),
          CHECK (device_type <> '{DeviceType.UO}'
                 OR {has_any_prefix_sql("device_id", (UO_ID_PREFIX,))}),
          CHECK (device_type <> '{DeviceType.APPLIANCE}'
                 OR {has_any_prefix_sql("device_id", (APPLIANCE_ID_PREFIX,))}),
          CHECK (device_type <> '{DeviceType.CO}'
                 OR NOT {has_any_prefix_sql("device_id", _APP_ID_PREFIXES)}),
          CHECK (device_type = '{DeviceType.APPLIANCE}'
                 OR (appliance_type IS NULL AND description IS NULL)),
          CHECK (device_type = '{DeviceType.CO}' OR all_on_off_entity_registry_id IS NULL)
        )
        """
    )


def create_co_name_index(conn: sqlite3.Connection) -> None:
    """At most one CO per normalised name -- the identity HA's own label
    registry would otherwise collide on (issue #185)."""
    conn.execute(
        f"""
        CREATE UNIQUE INDEX ux_devices_co_name_norm
          ON devices(name_norm) WHERE device_type = '{DeviceType.CO}'
        """
    )


def create_uo_name_index(conn: sqlite3.Connection) -> None:
    """At most one Unmanaged Outlet per normalised name."""
    conn.execute(
        f"""
        CREATE UNIQUE INDEX ux_devices_uo_name_norm
          ON devices(name_norm) WHERE device_type = '{DeviceType.UO}'
        """
    )


def create_appliance_name_type_index(conn: sqlite3.Connection) -> None:
    """At most one Appliance per normalised (name, type) pair. `type_norm`
    coalesces `NULL` to '', so two untyped Appliances sharing a name collide
    too, not just two with the same explicit type."""
    conn.execute(
        f"""
        CREATE UNIQUE INDEX ux_devices_appliance_name_type_norm
          ON devices(name_norm, type_norm) WHERE device_type = '{DeviceType.APPLIANCE}'
        """
    )


def _to_device(row: sqlite3.Row) -> Device:
    return Device(
        device_id=row["device_id"],
        device_name=row["device_name"],
        device_type=DeviceType(row["device_type"]),
        has_plug=bool(row["has_plug"]),
        appliance_type=row["appliance_type"],
        description=row["description"],
        ha_area_id=row["ha_area_id"],
        location_note=row["location_note"],
        all_on_off_entity_registry_id=row["all_on_off_entity_registry_id"],
        plugged_into_socket_id=row["plugged_into_socket_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_all(conn: sqlite3.Connection) -> list[Device]:
    rows = conn.execute("SELECT " + _COLUMNS + " FROM devices").fetchall()
    return [_to_device(row) for row in rows]


def list_of_type(conn: sqlite3.Connection, *, device_type: DeviceType) -> list[Device]:
    rows = conn.execute(
        "SELECT " + _COLUMNS + " FROM devices WHERE device_type = :device_type",
        {"device_type": device_type},
    ).fetchall()
    return [_to_device(row) for row in rows]


def get(conn: sqlite3.Connection, device_id: DeviceId) -> Device | None:
    row = conn.execute(
        "SELECT " + _COLUMNS + " FROM devices WHERE device_id = ?", (device_id,)
    ).fetchone()
    return _to_device(row) if row is not None else None


def get_occupant(conn: sqlite3.Connection, *, socket_id: SocketId) -> Device | None:
    """The device whose plug is in `socket_id`, if any. `UNIQUE` on the plug
    column means there is at most one."""
    row = conn.execute(
        "SELECT " + _COLUMNS + " FROM devices WHERE plugged_into_socket_id = ?",
        (socket_id,),
    ).fetchone()
    return _to_device(row) if row is not None else None


def list_occupied_socket_ids(conn: sqlite3.Connection) -> set[SocketId]:
    """Every socket that currently holds a plug -- what choosing a free
    socket for a plug reads, together with the Unmanaged Outlet's own sockets."""
    rows = conn.execute(
        "SELECT plugged_into_socket_id FROM devices WHERE plugged_into_socket_id IS NOT NULL"
    ).fetchall()
    return {row["plugged_into_socket_id"] for row in rows}


def insert(conn: sqlite3.Connection, device: Device) -> None:
    conn.execute(
        "INSERT INTO devices"
        " (device_id, device_name, device_type, has_plug, appliance_type, description,"
        "  ha_area_id, location_note, all_on_off_entity_registry_id,"
        "  plugged_into_socket_id, created_at, updated_at)"
        " VALUES (:device_id, :device_name, :device_type, :has_plug, :appliance_type,"
        " :description,"
        " :ha_area_id, :location_note, :all_on_off_entity_registry_id,"
        " :plugged_into_socket_id, :created_at, :updated_at)",
        {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "has_plug": int(device.has_plug),
            "appliance_type": device.appliance_type,
            "description": device.description,
            "ha_area_id": device.ha_area_id,
            "location_note": device.location_note,
            "all_on_off_entity_registry_id": device.all_on_off_entity_registry_id,
            "plugged_into_socket_id": device.plugged_into_socket_id,
            "created_at": device.created_at,
            "updated_at": device.updated_at,
        },
    )


def update_name_and_location(
    conn: sqlite3.Connection,
    *,
    device_id: UoId | CoId,
    name: str,
    ha_area_id: HaAreaId | None,
    location_note: str | None,
    now: Timestamp,
) -> None:
    """An Unmanaged Outlet's or a CO's editable fields. An Appliance has no
    location, so it takes `update_appliance_fields` instead."""
    conn.execute(
        "UPDATE devices SET device_name = :name, ha_area_id = :ha_area_id,"
        " location_note = :location_note, updated_at = :now"
        " WHERE device_id = :device_id",
        {
            "device_id": device_id,
            "name": name,
            "ha_area_id": ha_area_id,
            "location_note": location_note,
            "now": now,
        },
    )


def update_appliance_fields(
    conn: sqlite3.Connection,
    *,
    device_id: ApplianceId,
    name: str,
    appliance_type: str | None,
    description: str | None,
    now: Timestamp,
) -> None:
    conn.execute(
        "UPDATE devices SET device_name = :name, appliance_type = :appliance_type,"
        " description = :description, updated_at = :now"
        " WHERE device_id = :device_id",
        {
            "device_id": device_id,
            "name": name,
            "appliance_type": appliance_type,
            "description": description,
            "now": now,
        },
    )


def set_plug(
    conn: sqlite3.Connection, *, device_id: DeviceId, socket_id: SocketId, now: Timestamp
) -> None:
    """Point a device's plug at a socket. Only a CO's `updated_at` moves: an
    Appliance's plugging is not an edit of the Appliance."""
    conn.execute(
        "UPDATE devices SET plugged_into_socket_id = :socket_id,"
        " updated_at = CASE WHEN device_type = :co THEN :now ELSE updated_at END"
        " WHERE device_id = :device_id",
        {"device_id": device_id, "socket_id": socket_id, "co": DeviceType.CO, "now": now},
    )


def clear_plug(conn: sqlite3.Connection, *, device_id: DeviceId, now: Timestamp) -> None:
    """Unplug a device. As `set_plug`, only a CO's `updated_at` moves."""
    conn.execute(
        "UPDATE devices SET plugged_into_socket_id = NULL,"
        " updated_at = CASE WHEN device_type = :co THEN :now ELSE updated_at END"
        " WHERE device_id = :device_id",
        {"device_id": device_id, "co": DeviceType.CO, "now": now},
    )


def delete(conn: sqlite3.Connection, device_id: DeviceId) -> None:
    conn.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))


# One probe id per kind: each must satisfy that kind's id-prefix `CHECK`, and
# the CO's must avoid both app prefixes.
_PROBE_IDS: dict[DeviceType, DeviceId] = {
    DeviceType.UO: DeviceId(f"{UO_ID_PREFIX}_norm_probe__"),
    DeviceType.CO: DeviceId("__norm_probe__"),
    DeviceType.APPLIANCE: DeviceId(f"{APPLIANCE_ID_PREFIX}_norm_probe__"),
}


def _probe(
    conn: sqlite3.Connection,
    *,
    device_type: DeviceType,
    name: str,
    appliance_type: str | None,
    column: str,
) -> str:
    probe_id = _PROBE_IDS[device_type]
    insert(
        conn,
        Device(
            device_id=probe_id,
            device_name=name,
            device_type=device_type,
            has_plug=device_type is not DeviceType.UO,
            appliance_type=appliance_type,
            description=None,
            ha_area_id=None,
            location_note=None,
            all_on_off_entity_registry_id=None,
            plugged_into_socket_id=None,
            created_at=Timestamp("t"),
            updated_at=Timestamp("t"),
        ),
    )
    row = conn.execute(
        "SELECT " + column + " FROM devices WHERE device_id = ?", (probe_id,)
    ).fetchone()
    delete(conn, probe_id)
    return row[0]


def name_norm_sql(conn: sqlite3.Connection, name: str, *, device_type: DeviceType) -> str:
    """The real `name_norm` generated column's computed value, read off a
    throwaway probe row of the given kind inserted via `insert()` above --
    not a hand-typed duplicate of its DDL expression, which could silently
    drift from the real column if the DDL is ever edited without updating a
    matching copy here too. A schema-invariant probe (db/sql/__init__.py)
    for tests/test_normalization_agreement.py to compare
    `domain.normalization.normalize_name` against.

    Only safe against a connection with no unrelated row already occupying
    the probe id or colliding on the name -- true of the fresh, empty `conn`
    fixture this is called against, not asserted here.
    """
    return _probe(conn, device_type=device_type, name=name, appliance_type=None, column="name_norm")


def type_norm_sql(conn: sqlite3.Connection, type_: str | None) -> str:
    """As `name_norm_sql` above, for `type_norm` (an Appliance-only column)."""
    return _probe(
        conn,
        device_type=DeviceType.APPLIANCE,
        name="probe",
        appliance_type=type_,
        column="type_norm",
    )
