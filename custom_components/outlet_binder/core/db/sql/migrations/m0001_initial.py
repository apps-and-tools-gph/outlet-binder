"""Migration 1: the initial schema, as literal SQL.

Every statement is written out in full, with no values taken from the live
code (enum members, id prefixes, helper functions), so nothing outside this
file can change what Migration 1 builds. Once the schema is frozen this file is
never edited; a schema change is a new `mNNNN_<slug>.py` (docs/MIGRATIONS.md).

The statements run in the order listed. `devices` and `sockets` reference each
other (a socket's owner, a device's plug); SQLite looks a foreign key's parent
up only when a row is written, so the order between the two does not matter.
"""

STATEMENTS: tuple[str, ...] = (
    # `sockets` is created after this table and references it back, which
    # SQLite allows: a foreign key's parent is only looked up when a row is
    # written. Deleting a device cascades to its sockets, and a plug in one of
    # those sockets is set to `NULL` -- a plug moves, a socket only releases.
    """
        CREATE TABLE devices (
          device_id                     TEXT PRIMARY KEY,
          device_name                   TEXT NOT NULL
            CHECK (trim(device_name, ' ' || char(9) || char(10) || char(13)) <> ''),
          device_type                   TEXT NOT NULL
            CHECK (device_type IN ('UO', 'CO', 'APPLIANCE')),
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
          CHECK (device_type <> 'UO' OR has_plug = 0),
          CHECK (device_type <> 'APPLIANCE' OR has_plug = 1),
          CHECK (has_plug = 1 OR plugged_into_socket_id IS NULL),
          CHECK (device_type <> 'UO'
                 OR (substr(device_id, 1, 3) = 'uo_')),
          CHECK (device_type <> 'APPLIANCE'
                 OR (substr(device_id, 1, 3) = 'ap_')),
          CHECK (device_type <> 'CO'
                 OR NOT (substr(device_id, 1, 3) = 'uo_' OR substr(device_id, 1, 3) = 'ap_')),
          CHECK (device_type = 'APPLIANCE'
                 OR (appliance_type IS NULL AND description IS NULL)),
          CHECK (device_type = 'CO' OR all_on_off_entity_registry_id IS NULL)
        )
        """,
    # At most one CO per normalised name -- the identity HA's own label
    # registry would otherwise collide on (issue #185).
    """
        CREATE UNIQUE INDEX ux_devices_co_name_norm
          ON devices(name_norm) WHERE device_type = 'CO'
        """,
    # At most one Unmanaged Outlet per normalised name.
    """
        CREATE UNIQUE INDEX ux_devices_uo_name_norm
          ON devices(name_norm) WHERE device_type = 'UO'
        """,
    # At most one Appliance per normalised (name, type) pair. `type_norm`
    # coalesces `NULL` to '', so two untyped Appliances sharing a name collide
    # too, not just two with the same explicit type.
    """
        CREATE UNIQUE INDEX ux_devices_appliance_name_type_norm
          ON devices(name_norm, type_norm) WHERE device_type = 'APPLIANCE'
        """,
    """
        CREATE TABLE sockets (
          socket_id                     TEXT PRIMARY KEY,
          device_id                     TEXT NOT NULL
            REFERENCES devices(device_id) ON DELETE CASCADE,
          is_smart                      INTEGER NOT NULL CHECK (is_smart IN (0, 1)),
          alias                         TEXT NOT NULL
            CHECK (trim(alias, ' ' || char(9) || char(10) || char(13)) <> ''),
          socket_type                   TEXT,
          position                      INTEGER NOT NULL,
          physical_position             INTEGER,
          monitoring_entity_registry_id TEXT,
          UNIQUE (device_id, position),
          CHECK ((is_smart = 0)
                 = (substr(socket_id, 1, 3) = 'sk_'))
        )
        """,
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
        """,
    # At most one open row per device.
    """
        CREATE UNIQUE INDEX ux_plug_log_open_device
          ON plug_log(device_id) WHERE unplugged_at IS NULL
        """,
    # At most one open row per socket.
    """
        CREATE UNIQUE INDEX ux_plug_log_open_socket
          ON plug_log(socket_id) WHERE unplugged_at IS NULL
        """,
    # No foreign key to anything above -- edit_log's payload is an opaque
    # JSON blob of ids, not typed columns.
    """
        CREATE TABLE edit_log (
          entry_seq   INTEGER PRIMARY KEY,
          command     TEXT NOT NULL,
          payload     TEXT NOT NULL,
          appended_at TEXT NOT NULL,
          group_seq   INTEGER NOT NULL
        )
        """,
    """
        CREATE TABLE edit_session (
          singleton         INTEGER PRIMARY KEY CHECK (singleton = 1),
          cursor_seq        INTEGER NOT NULL,
          opened_by_version TEXT
        )
        """,
)
