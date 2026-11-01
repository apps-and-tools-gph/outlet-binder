"""How HA names and identifies the switch OB owns for a CO with a plug.

A domain-layer module (#423) so `switch.py` and `entity_slug.py`
(outside the domain layer) share one derivation without importing one
another. Dependency-free: no `hass`.

A PCO's switch is `<alias> Plug`. An Unmanaged Outlet has no plug, so no
switch. An Appliance's On/Off is not one of these: it is a mirror of its
socket's on/off entity (domain/appliance_mirrors.py). `desired_switches`
decides the whole set from the state wire lists, so reslug, repoint and add
all read one answer.

## Why `unique_id` is anchored on the device id, not `name`

A rename must not change `unique_id`: `EntityRegistry.async_get_or_create`
(`homeassistant/helpers/entity_registry.py` in the installed package)
looks up by `unique_id` first and updates the existing entry in place when
found, keeping the same `entity_id`. Anchoring `unique_id` on the device's
stable id rather than its editable name is what makes a rename purely
cosmetic to HA's registry -- the live `entity_id` a user has already wired
into an automation does not change just because the name did. `name:` is
what HA slugifies into the *first-ever* `entity_id`, and only then.

## Why a plug cannot clash with a mirror

A plug's `unique_id` ends `_plug` and its entity id ends `plug`; a mirror's
`unique_id` and entity id carry the Appliance's id or `ob_` label before the
facility. They meet only if an Appliance's label and a facility make a name
that ends `plug`, which is rare and left to reslug's log-and-leave.
"""

from dataclasses import dataclass
from typing import Any, assert_never

from .models import DeviceType


class NoSwitchError(ValueError):
    """Raised for a device kind that has no switch (an Unmanaged Outlet)."""


@dataclass(frozen=True)
class SwitchSpec:
    """One plug switch OB should own: its stable id, its display name, and the
    HA entity registry id it mirrors (`None` when it has nothing to mirror,
    which is shown as unavailable)."""

    unique_id: str
    name: str
    target_registry_id: str | None


def _slug(device_id: str) -> str:
    """A device id, made safe as a HA object id -- lowercase hex and
    underscores only. An Appliance's id carries a `uuid.uuid4()` with
    hyphens; hyphens are the one character here that isn't valid."""
    return device_id.replace("-", "_")


def switch_unique_id(*, device_id: str, device_type: DeviceType, entity_id_prefix: str) -> str:
    """The switch's `unique_id` -- exported so reslug can look up the
    switch's live registry entry by the same id used to create it. Two
    independent derivations of the same id would be a silent-drift risk."""
    match device_type:
        case DeviceType.CO:
            return f"{entity_id_prefix}{_slug(device_id)}_plug"
        case DeviceType.APPLIANCE:
            raise NoSwitchError("An Appliance's On/Off is a mirror, not a plug switch")
        case DeviceType.UO:
            raise NoSwitchError("A Wall Socket has no plug, so no switch")
        case _:
            assert_never(device_type)


def switch_name(*, device_type: DeviceType, name: str) -> str:
    """The switch's display name -- exported so reslug can recompute the
    entity_id HA would derive today from a device's *current* name without
    re-deriving the suffix independently."""
    match device_type:
        case DeviceType.CO:
            return f"{name} Plug"
        case DeviceType.APPLIANCE:
            raise NoSwitchError("An Appliance's On/Off is a mirror, not a plug switch")
        case DeviceType.UO:
            raise NoSwitchError("A Wall Socket has no plug, so no switch")
        case _:
            assert_never(device_type)


def plug_switch_unique_ids(*, cos: list[dict[str, Any]], entity_id_prefix: str) -> dict[str, str]:
    """The `unique_id` of the switch of each CO that has one, keyed on the
    CO's id, by the same rule as `desired_switches` (#532: the export finds
    each one's live `entity_id` with it; the mirror sync keeps these entries
    out of its prune)."""
    return {
        co["co_id"]: switch_unique_id(
            device_id=co["co_id"], device_type=DeviceType.CO, entity_id_prefix=entity_id_prefix
        )
        for co in cos
        if co["has_plug"]
    }


def desired_switches(*, cos: list[dict[str, Any]], entity_id_prefix: str) -> list[SwitchSpec]:
    """The plug switches that should exist: one per PCO whose `has_plug` is
    true, from the `cos` list of the state wire. Keyed on `has_plug`, not
    `device_type`: an FCO would otherwise get a switch that is always
    unavailable."""
    unique_ids = plug_switch_unique_ids(cos=cos, entity_id_prefix=entity_id_prefix)
    return [
        SwitchSpec(
            unique_id=unique_ids[co["co_id"]],
            name=switch_name(device_type=DeviceType.CO, name=co["alias"]),
            target_registry_id=co["plugged_into_co_socket_id"],
        )
        for co in cos
        if co["has_plug"]
    ]
