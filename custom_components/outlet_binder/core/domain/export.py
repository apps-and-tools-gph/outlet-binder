"""The export of the current state of play (#532): one model, two renderings.

`build_export` joins the committed state lists (`get_full_state`), the area
names and live switch ids HA holds, and optionally the Plugged Into history,
into one `Export`. `render_markdown` is the file to read and `render_json`
the snapshot to parse or diff. Pure and dependency-free: the caller reads
HA's registries and passes the answers in as maps.

An Appliance has no area of its own, so its area is its host's effective one:
the CO's `effective_ha_area_id`, or the Unmanaged Outlet's `ha_area_id`. The
chain walk was already done by `get_full_state`; nothing here walks one.

Names in the history are the log's own snapshots, never today's names.
"""

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .models import PlugLogEntry

FORMAT_MARKDOWN = "markdown"
FORMAT_JSON = "json"
FORMATS = (FORMAT_MARKDOWN, FORMAT_JSON)

NONE_TEXT = "—"
PLUGGED_INTO_SEPARATOR = " › "

StateLists = Mapping[str, list[dict[str, Any]]]


@dataclass(frozen=True)
class Export:
    """What is exported. `plug_log` is `None` when the history was not asked
    for, and that is the only thing that says so: the header's
    `includes_history` is derived from it."""

    exported_at: str
    integration_version: str | None
    user_version: int
    staged_left_out: int
    uos: list[dict[str, Any]]
    cos: list[dict[str, Any]]
    co_sockets: list[dict[str, Any]]
    appliances: list[dict[str, Any]]
    plug_log: list[dict[str, Any]] | None

    @property
    def header(self) -> dict[str, Any]:
        return {
            "exported_at": self.exported_at,
            "integration_version": self.integration_version,
            "user_version": self.user_version,
            "includes_history": self.plug_log is not None,
            "staged_left_out": self.staged_left_out,
        }


def build_export(
    *,
    state: StateLists,
    history: list[PlugLogEntry] | None,
    area_name_of: Mapping[str, str],
    switch_entity_id_of: Mapping[str, str],
    exported_at: str,
    integration_version: str | None,
    user_version: int,
    staged_left_out: int,
) -> Export:
    """Join the state lists, HA's names and the history into one `Export`.

    `area_name_of` maps an HA area id to its name and `switch_entity_id_of`
    a device id to its switch's live `entity_id`; an id they lack gives
    `None` in the row. Each list is sorted by its id, so two exports diff
    cleanly. Each row keeps the keys `get_state` gives it and gains
    `area_name`, `effective_area_name` and `switch_entity_id` where they apply.
    """

    def area_name(area_id: str | None) -> str | None:
        return area_name_of.get(area_id) if area_id is not None else None

    cos_by_id = {co["co_id"]: co for co in state["cos"]}
    co_id_of_socket = {socket["co_socket_id"]: socket["co_id"] for socket in state["co_sockets"]}
    uo_by_id = {uo["uo_id"]: uo for uo in state["uos"]}

    def host_area_id(appliance: dict[str, Any]) -> str | None:
        socket_id = appliance["plugged_into_co_socket_id"]
        if socket_id is not None:
            return cos_by_id[co_id_of_socket[socket_id]]["effective_ha_area_id"]
        uo_id = appliance["uo_id"]
        return uo_by_id[uo_id]["ha_area_id"] if uo_id is not None else None

    uos = [{**uo, "area_name": area_name(uo["ha_area_id"])} for uo in state["uos"]]
    cos = [
        {
            **co,
            "area_name": area_name(
                co["location_override"]["ha_area_id"] if co["location_override"] else None
            ),
            "effective_area_name": area_name(co["effective_ha_area_id"]),
            "switch_entity_id": switch_entity_id_of.get(co["co_id"]),
        }
        for co in state["cos"]
    ]
    appliances = [
        {
            **appliance,
            "effective_area_name": area_name(host_area_id(appliance)),
            "switch_entity_id": switch_entity_id_of.get(appliance["appliance_id"]),
        }
        for appliance in state["appliances"]
    ]
    return Export(
        exported_at=exported_at,
        integration_version=integration_version,
        user_version=user_version,
        staged_left_out=staged_left_out,
        uos=sorted(uos, key=lambda row: row["uo_id"]),
        cos=sorted(cos, key=lambda row: row["co_id"]),
        co_sockets=sorted(state["co_sockets"], key=lambda row: row["co_socket_id"]),
        appliances=sorted(appliances, key=lambda row: row["appliance_id"]),
        plug_log=None if history is None else [asdict(entry) for entry in history],
    )


def export_filename(*, fmt: str, when: datetime) -> str:
    """`outlet-binder-<YYYY-MM-DD-HHMM>.md` (or `.json`)."""
    extension = "md" if fmt == FORMAT_MARKDOWN else "json"
    return f"outlet-binder-{when:%Y-%m-%d-%H%M}.{extension}"


def render_json(export: Export) -> str:
    """Pretty-printed with sorted keys, so two exports diff cleanly. The
    lists use `get_state`'s keys; `plug_log` is present only when asked for."""
    document: dict[str, Any] = {
        "export": export.header,
        "uos": export.uos,
        "cos": export.cos,
        "co_sockets": export.co_sockets,
        "appliances": export.appliances,
    }
    if export.plug_log is not None:
        document["plug_log"] = export.plug_log
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _line(text: str) -> str:
    """One line of text: a newline would end it."""
    return " ".join(text.split("\n")).replace("\r", "")


def _cell(text: str | None) -> str:
    """A table cell: `None` is a dash, and a backslash, a pipe or a newline
    cannot break the row."""
    if text is None or text == "":
        return NONE_TEXT
    return _line(text).replace("\\", "\\\\").replace("|", "\\|")


def _code(text: str | None) -> str:
    """A cell holding an id in code style, or a dash."""
    return NONE_TEXT if text is None else f"`{_cell(text)}`"


def _name_key(name: str) -> tuple[str, str]:
    """Case-insensitive, with the exact name breaking a tie."""
    return (name.casefold(), name)


def _by_name(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: _name_key(row[key]))


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render_markdown(export: Export) -> str:
    """The file to read: Appliances first, then Smart Devices with their
    Sockets, then Wall Sockets, then the history if it was asked for."""
    co_by_id = {co["co_id"]: co for co in export.cos}
    uo_by_id = {uo["uo_id"]: uo for uo in export.uos}
    socket_by_id = {socket["co_socket_id"]: socket for socket in export.co_sockets}
    device_name_by_id = {
        **{co["co_id"]: co["alias"] for co in export.cos},
        **{appliance["appliance_id"]: appliance["name"] for appliance in export.appliances},
    }

    names_in_uo: dict[str, list[str]] = {}
    for co in export.cos:
        if co["uo_id"] is not None:
            names_in_uo.setdefault(co["uo_id"], []).append(co["alias"])
    for appliance in export.appliances:
        if appliance["uo_id"] is not None:
            names_in_uo.setdefault(appliance["uo_id"], []).append(appliance["name"])

    def socket_text(socket: dict[str, Any]) -> str:
        return socket["alias"] or f"Socket {socket['position']}"

    def plugged_into(device: dict[str, Any]) -> str | None:
        """Where a CO or an Appliance is plugged in, as plain text."""
        socket_id = device["plugged_into_co_socket_id"]
        if socket_id is not None:
            socket = socket_by_id[socket_id]
            host = co_by_id[socket["co_id"]]["alias"]
            return f"{host}{PLUGGED_INTO_SEPARATOR}{socket_text(socket)}"
        uo_id = device["uo_id"]
        return uo_by_id[uo_id]["name"] if uo_id is not None else None

    header = export.header
    lines = [
        "# Outlet Binder: current state",
        "",
        f"- Exported at: {header['exported_at']}",
        f"- Integration version: {header['integration_version'] or NONE_TEXT}",
        f"- Database version: {header['user_version']}",
        f"- Includes Plugged Into history: {'yes' if header['includes_history'] else 'no'}",
        f"- Staged changes left out: {header['staged_left_out']}",
        "",
    ]
    if header["staged_left_out"]:
        lines += [
            "Staged changes are not in this file: it shows the committed state only.",
            "",
        ]
    lines += [
        "## Contents",
        "",
        "- Appliances",
        "- Smart Devices",
        "- Wall Sockets",
    ]
    if export.plug_log is not None:
        lines.append("- Plugged Into history")
    lines.append("")

    lines += ["## Appliances", ""]
    if export.appliances:
        lines += _table(
            ["Appliance [↓]", "Type", "Switch", "Plugged into", "Area"],
            [
                [
                    _cell(appliance["name"]),
                    _cell(appliance["type"]),
                    _code(appliance["switch_entity_id"]),
                    _cell(plugged_into(appliance)),
                    _cell(appliance["effective_area_name"]),
                ]
                for appliance in _by_name(export.appliances, "name")
            ],
        )
    else:
        lines.append("None.")
    lines.append("")

    lines += ["## Smart Devices", ""]
    if not export.cos:
        lines += ["None.", ""]
    for co in _by_name(export.cos, "alias"):
        lines += [
            f"### {_line(co['alias'])}",
            "",
            f"- Switch: {_code(co['switch_entity_id'])}",
            f"- Area: {_cell(co['effective_area_name'])}",
            f"- Plugged into: {_cell(plugged_into(co))}",
            "",
        ]
        sockets = sorted(
            (socket for socket in export.co_sockets if socket["co_id"] == co["co_id"]),
            key=lambda socket: (socket["position"], socket["co_socket_id"]),
        )
        if sockets:
            lines += _table(
                ["Socket [↓]", "Plugged in"],
                [
                    [
                        _cell(socket_text(socket)),
                        _cell(device_name_by_id.get(socket["occupant_device_id"])),
                    ]
                    for socket in sockets
                ],
            )
        else:
            lines.append("No Sockets.")
        lines.append("")

    lines += ["## Wall Sockets", ""]
    if export.uos:
        lines += _table(
            ["Wall Socket [↓]", "Area", "Location note", "Sockets", "Plugged in"],
            [
                [
                    _cell(uo["name"]),
                    _cell(uo["area_name"]),
                    _cell(uo["location_note"]),
                    str(uo["socket_count"]),
                    _cell(", ".join(sorted(names_in_uo.get(uo["uo_id"], []), key=_name_key))),
                ]
                for uo in _by_name(export.uos, "name")
            ],
        )
    else:
        lines.append("None.")
    lines.append("")

    if export.plug_log is not None:
        lines += ["## Plugged Into history", ""]
        if export.plug_log:
            newest_first = sorted(
                export.plug_log, key=lambda row: (row["plugged_at"], row["entry_seq"]), reverse=True
            )
            lines += _table(
                ["Device", "Socket", "Host", "Plugged at [↑]", "Unplugged at"],
                [
                    [
                        _cell(row["device_name"]),
                        _cell(row["socket_label"]),
                        _cell(row["host_name"]),
                        _cell(row["plugged_at"]),
                        _cell(row["unplugged_at"]),
                    ]
                    for row in newest_first
                ],
            )
        else:
            lines.append("None.")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"
