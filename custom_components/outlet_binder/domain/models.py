"""Plain, dependency-free dataclasses mirroring the tables in db/sql/.

`Device` and `Socket` are the two current-state tables, `PlugLogEntry` the
history log, and the two-table edit session (issue #189): EditLogEntry
mirrors `edit_log`, EditSession mirrors the single-row `edit_session`
cursor.

No `hass`, no persistence, no behavior beyond the plain data itself. Each
db/sql/ concept module converts between these and raw SQLite rows, next to
the statements that produce them.
"""

from dataclasses import dataclass
from enum import StrEnum

from .identifiers import DeviceId, HaAreaId, HaEntityRegistryId, SocketId, Timestamp


class DeviceType(StrEnum):
    """The stored kind of a device. The values are what `devices.device_type`
    holds, so the database `CHECK` and this enum must list the same three."""

    UO = "UO"
    CO = "CO"
    APPLIANCE = "APPLIANCE"


@dataclass(frozen=True)
class Device:
    """One row of `devices`: an Unmanaged Outlet, a CO or an Appliance.

    `has_plug` says whether the device has a plug of its own. An Unmanaged Outlet
    never does and an Appliance always does; a CO is portable (it does) or
    fixed in place (it does not), as its pattern's kind says. Only a device
    with a plug can have `plugged_into_socket_id`, the one connection between
    things: the socket this device's plug is in, or `None`. `appliance_type`
    and `description` are set only on an Appliance, and
    `all_on_off_entity_registry_id` only on a CO. The area and the note are
    two independent columns.
    """

    device_id: DeviceId
    device_name: str
    device_type: DeviceType
    has_plug: bool
    appliance_type: str | None
    description: str | None
    ha_area_id: HaAreaId | None
    location_note: str | None
    all_on_off_entity_registry_id: HaEntityRegistryId | None
    plugged_into_socket_id: SocketId | None
    created_at: Timestamp
    updated_at: Timestamp


@dataclass(frozen=True)
class Socket:
    """One row of `sockets`: a place a plug can go, owned by one device.

    A smart socket's id is its on/off entity registry id and its
    `monitoring_entity_registry_id` is best-effort, so nullable. A dumb
    socket has a generated id, and its `alias` and `position` carry no
    meaning.
    """

    socket_id: SocketId
    device_id: DeviceId
    is_smart: bool
    alias: str
    socket_type: str | None
    position: int
    physical_position: int | None
    monitoring_entity_registry_id: HaEntityRegistryId | None


@dataclass(frozen=True)
class PlugLogEntry:
    """One row of `plug_log`: a device's stay in a socket, still open while
    `unplugged_at` is None.

    The names and the socket label are snapshots taken when the device was
    plugged in, not live lookups, so renaming any of them afterwards does not
    rewrite the past. `host_name` names the device that owns the socket,
    since a socket label alone is only a position and names nothing once the
    socket is deleted.

    None of the ids is a foreign key in `plug_log`, so each may name a
    row that has since been deleted: deleting a device closes its open log
    rows but leaves the history behind.
    """

    entry_seq: int
    device_id: DeviceId
    device_name: str
    socket_id: SocketId
    socket_label: str
    host_device_id: DeviceId
    host_name: str
    plugged_at: Timestamp
    unplugged_at: Timestamp | None


@dataclass(frozen=True)
class EditLogEntry:
    """One staged edit in `edit_log` (issue #189): a connection command
    appended but not yet committed.

    `payload` is the command's arguments as a JSON object -- opaque here,
    since interpreting it (parsing, wrapping each value in its identifier
    type, and calling the matching db/operations/ function) is the
    dispatch registry's job in db/edit_session.py, not this
    module's. Unlike PlugLogEntry, this carries no snapshot fields:
    the payload names ids, not display text, because replay resolves
    those ids against whatever is live at replay time."""

    entry_seq: int
    command: str
    payload: str
    appended_at: Timestamp
    group_seq: int


@dataclass(frozen=True)
class EditSession:
    """The single row of `edit_session` (issue #189): where the cursor
    into `edit_log` currently sits.

    `cursor_seq` is the `entry_seq` of the last entry included in the
    projection, not a count -- entries are appended with contiguous
    `entry_seq` values (SQLite's default rowid allocation, since
    `edit_log.entry_seq` is declared `INTEGER PRIMARY KEY` without
    `AUTOINCREMENT`, matching `plug_log`'s own precedent), so
    undo/redo can move it by plain +-1 arithmetic."""

    cursor_seq: int
