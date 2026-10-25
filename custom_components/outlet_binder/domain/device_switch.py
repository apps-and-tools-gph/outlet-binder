"""How HA names and identifies the switch OB owns for a device with a plug.

A domain-layer module (#423) so `switch.py` and `entity_slug.py`
(outside the domain layer) share one derivation without importing one
another. Dependency-free: no `hass`.

An Appliance's switch is `<name> On/Off` (`<name> <type> On/Off` when it has
a type) and a PCO's is `<alias> Plug`. An Unmanaged Outlet has no plug, so no
switch. `desired_switches` decides the whole set from the state wire lists,
so prune, reslug, repoint and add all read one answer.

## Why `unique_id` is anchored on the device id, not `name`

A rename must not change `unique_id`: `EntityRegistry.async_get_or_create`
(`homeassistant/helpers/entity_registry.py` in the installed package)
looks up by `unique_id` first and updates the existing entry in place when
found, keeping the same `entity_id`. Anchoring `unique_id` on the device's
stable id rather than its editable name is what makes a rename purely
cosmetic to HA's registry -- the live `entity_id` a user has already wired
into an automation does not change just because the name did. `name:` is
what HA slugifies into the *first-ever* `entity_id`, and only then.

## Why the two kinds cannot clash

An Appliance's `unique_id` ends `_onoff` and a CO's `_plug`, and an
Appliance's switch name ends `On/Off` and a CO's `Plug`, so neither the
`unique_id`s nor the entity ids of the two sets can meet.
"""

from dataclasses import dataclass
from typing import Any, assert_never

from .models import DeviceType


class NoSwitchError(ValueError):
    """Raised for a device kind that has no switch (an Unmanaged Outlet)."""


@dataclass(frozen=True)
class SwitchSpec:
    """One switch OB should own: its stable id, its display name, and the
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
        case DeviceType.APPLIANCE:
            suffix = "onoff"
        case DeviceType.CO:
            suffix = "plug"
        case DeviceType.UO:
            raise NoSwitchError("A Wall Socket has no plug, so no switch")
        case _:
            assert_never(device_type)
    return f"{entity_id_prefix}{_slug(device_id)}_{suffix}"


def switch_name(*, device_type: DeviceType, name: str, appliance_type: str | None) -> str:
    """The switch's display name -- exported so reslug can recompute the
    entity_id HA would derive today from a device's *current* name without
    re-deriving the suffix independently. `appliance_type` is read for an
    Appliance only."""
    match device_type:
        case DeviceType.APPLIANCE:
            typed = f" {appliance_type}" if appliance_type else ""
            return f"{name}{typed} On/Off"
        case DeviceType.CO:
            return f"{name} Plug"
        case DeviceType.UO:
            raise NoSwitchError("A Wall Socket has no plug, so no switch")
        case _:
            assert_never(device_type)


def desired_switches(
    *,
    cos: list[dict[str, Any]],
    appliances: list[dict[str, Any]],
    entity_id_prefix: str,
) -> list[SwitchSpec]:
    """The switches that should exist: one per Appliance and one per PCO
    whose `has_plug` is true, from the `cos` and `appliances` lists of the
    state wire. Keyed on `has_plug`, not `device_type`: an FCO would
    otherwise get a switch that is always unavailable."""
    specs = [
        SwitchSpec(
            unique_id=switch_unique_id(
                device_id=appliance["appliance_id"],
                device_type=DeviceType.APPLIANCE,
                entity_id_prefix=entity_id_prefix,
            ),
            name=switch_name(
                device_type=DeviceType.APPLIANCE,
                name=appliance["name"],
                appliance_type=appliance["type"],
            ),
            target_registry_id=appliance["plugged_into_co_socket_id"],
        )
        for appliance in appliances
    ]
    specs.extend(
        SwitchSpec(
            unique_id=switch_unique_id(
                device_id=co["co_id"],
                device_type=DeviceType.CO,
                entity_id_prefix=entity_id_prefix,
            ),
            name=switch_name(device_type=DeviceType.CO, name=co["alias"], appliance_type=None),
            target_registry_id=co["plugged_into_co_socket_id"],
        )
        for co in cos
        if co["has_plug"]
    )
    return specs
