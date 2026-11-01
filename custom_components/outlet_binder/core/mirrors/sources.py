"""What each socket an Appliance is plugged into gives it (#187).

The step between the database and domain/appliance_mirrors.py: it reads HA's
registries once, as plain snapshots, and asks domain/facilities.py what each
plugged-in socket provides. A CO does not record which pattern matched it, so
the pattern is found again from the CO's device with `fitting_patterns`, which
`websocket_api` uses too for a socket's default name; the most specific
candidate is the one that matched.

A socket whose on/off entity is gone from HA is left out, and the Appliance
plugged into it has no entities. One whose CO's device is gone, or that no
pattern fits, still gives the On/Off, which needs neither, and nothing else.
Must run on the event loop: the registries are loop-only.
"""

from collections.abc import Mapping
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from ..device_identification.registry_match import fitting_patterns
from ..domain.discovery import CoPattern
from ..domain.facilities import (
    RegistryDevice,
    RegistryEntity,
    SocketFacilities,
    on_off_only,
    socket_facilities,
)
from ..domain.facility_rules import StandardFacility
from ..domain.identifiers import (
    FacilityName,
    HaDeviceRegistryId,
    HaEntityDottedId,
    HaEntityRegistryId,
    VendorFacilityKey,
)


def _registry_entity(entry: er.RegistryEntry) -> RegistryEntity:
    return RegistryEntity(
        id=HaEntityRegistryId(entry.id),
        entity_id=HaEntityDottedId(entry.entity_id),
        unique_id=entry.unique_id,
        domain=entry.domain,
        platform=entry.platform,
        translation_key=(
            VendorFacilityKey(entry.translation_key) if entry.translation_key else None
        ),
        original_name=entry.original_name,
        device_id=HaDeviceRegistryId(entry.device_id) if entry.device_id else None,
        disabled=entry.disabled_by is not None,
    )


def _registry_device(device: dr.DeviceEntry) -> RegistryDevice:
    return RegistryDevice(
        id=HaDeviceRegistryId(device.id),
        via_device_id=(HaDeviceRegistryId(device.via_device_id) if device.via_device_id else None),
        identifiers=frozenset(device.identifiers),
    )


@callback
def facilities_by_socket(
    hass: HomeAssistant,
    state: Mapping[str, Any],
    *,
    patterns: tuple[CoPattern, ...],
    standard: Mapping[FacilityName, StandardFacility],
) -> dict[str, SocketFacilities]:
    """`{co_socket_id: what it gives}` for every socket an Appliance is plugged
    into. `state` is the state wire."""
    in_use = {
        appliance["plugged_into_co_socket_id"]
        for appliance in state["appliances"]
        if appliance["plugged_into_co_socket_id"] is not None
    }
    if not in_use:
        return {}
    co_of = {socket["co_socket_id"]: socket["co_id"] for socket in state["co_sockets"]}
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    devices = [
        _registry_device(device)
        for device in device_registry.devices
        if isinstance(device, dr.DeviceEntry)
    ]
    entities = [_registry_entity(entry) for entry in entity_registry.entities.values()]

    found: dict[str, SocketFacilities] = {}
    for socket_id in in_use:
        on_off = entity_registry.async_get(socket_id)
        if on_off is None:
            continue
        host = device_registry.async_get(co_of.get(socket_id, ""))
        # A CO's device is never a `ChildDeviceEntry`, which has no model. The
        # On/Off needs neither the device nor a pattern, so losing one leaves it.
        if not isinstance(host, dr.DeviceEntry):
            found[socket_id] = on_off_only(_registry_entity(on_off), standard)
            continue
        pattern = next(iter(fitting_patterns(hass, host, patterns)), None)
        if pattern is None:
            found[socket_id] = on_off_only(_registry_entity(on_off), standard)
            continue
        found[socket_id] = socket_facilities(
            pattern,
            standard,
            host=_registry_device(host),
            on_off_entity=_registry_entity(on_off),
            devices=devices,
            entities=entities,
        )
    return found
