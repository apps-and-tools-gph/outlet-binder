"""The OB entities each Appliance owns, from the sockets it is plugged into (#187).

Pure and dependency-free, like domain/device_switch.py: it takes the state wire's
`appliances` list and what the resolver found on each socket
(domain/facilities.py), and returns every mirror OB should hold. The platforms
read one answer, so create, repoint, rename and prune cannot disagree about
which entities exist.

An Appliance's mirrors are exactly its current socket's facilities: an unplugged
Appliance has none, and a facility the socket lacks has no entity. Nothing is
kept from an earlier socket.

The entity id is `<domain>.ob_<appliance>[_<type>]_<id suffix>`. HA fixes the
part before the dot, so `ob_` sits after it. This module returns the id's parts
and not the id: slugifying belongs to entity_slug.py, which holds the one
derivation that creation and reslug share.

`unique_id` is `<prefix><appliance id>_<id suffix>`. A rename of the Appliance
keeps it. Two mirrors in one domain never share one, because the resolver returns
neither of two that would give the same (domain, id suffix). Mirrors in different
domains can, so an entity is identified by its domain and its `unique_id`.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .facilities import SocketFacilities
from .identifiers import ApplianceId


@dataclass(frozen=True, kw_only=True)
class MirrorSpec:
    """One OB entity an Appliance should own.

    `appliance_label` is the Appliance's name, with its type when it has one: what
    the entity id and the friendly name begin with. `source` is the HA entity
    registry id the entity copies. `appliance_id` says whose entity it is, so a
    reader can group the specs without taking the id back out of `unique_id`."""

    appliance_id: ApplianceId
    domain: str
    unique_id: str
    appliance_label: str
    id_suffix: str
    display_name: str
    source: str
    vendor: str | None = None

    @property
    def name(self) -> str:
        return f"{self.appliance_label} {self.display_name}"


# The id ending of an Appliance's On/Off: the `entity_id_name` that OB's facility vocabulary gives
# `ob_on_off` (a test holds the two together).
ON_OFF_ID_SUFFIX = "on_off"


def appliance_label(*, name: str, appliance_type: str | None) -> str:
    """The Appliance's name, followed by its type when it has one."""
    return f"{name} {appliance_type}" if appliance_type else name


def mirror_unique_id(*, appliance_id: str, id_suffix: str, entity_id_prefix: str) -> str:
    """The `unique_id` of the Appliance's entity ending `id_suffix`. Anchored on
    the Appliance's stable id, never its name, so a rename keeps the registry
    entry. An id carries hyphens when it is a uuid, and a HA object id cannot."""
    return f"{entity_id_prefix}{appliance_id.replace('-', '_')}_{id_suffix}"


def desired_mirrors(
    *,
    appliances: list[dict[str, Any]],
    facilities_by_socket: Mapping[str, SocketFacilities],
    entity_id_prefix: str,
) -> list[MirrorSpec]:
    """Every mirror that should exist, from the `appliances` list of the state
    wire. `facilities_by_socket` is keyed by CO Socket id; a socket missing from
    it (its on/off entity is gone from HA) gives nothing."""
    specs: list[MirrorSpec] = []
    for appliance in appliances:
        socket_id = appliance["plugged_into_co_socket_id"]
        facilities = facilities_by_socket.get(socket_id) if socket_id is not None else None
        if facilities is None:
            continue
        label = appliance_label(name=appliance["name"], appliance_type=appliance["type"])
        specs.extend(
            MirrorSpec(
                appliance_id=appliance["appliance_id"],
                domain=mirror.domain,
                unique_id=mirror_unique_id(
                    appliance_id=appliance["appliance_id"],
                    id_suffix=mirror.id_suffix,
                    entity_id_prefix=entity_id_prefix,
                ),
                appliance_label=label,
                id_suffix=mirror.id_suffix,
                display_name=mirror.display_name,
                source=mirror.source,
                vendor=mirror.vendor,
            )
            for mirror in facilities.mirrors
        )
    return specs
