"""Which device patterns fit a device in HA's device registry.

`websocket_api` (a socket's default name) and `mirrors/sources.py` (a socket's
facilities) both find a CO's pattern again from its device, since a CO does not
record which one matched. They share this, so the two can never ask
`candidate_patterns` different questions of the same device.

Must run on the event loop, like the registries it reads.
"""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from ..domain.discovery import CoPattern, DiscoveredDevice, candidate_patterns, first_non_blank
from ..domain.identifiers import HaDeviceRegistryId


def fitting_patterns(
    hass: HomeAssistant, device: dr.DeviceEntry, patterns: tuple[CoPattern, ...]
) -> tuple[CoPattern, ...]:
    """The patterns that fit `device`, most specific first.

    Only the fields `candidate_patterns` compares are filled in: it takes no
    entities, so none are read. The integration is the config entry's domain, not
    the domain element of the device's identifiers, which is only a convention
    (#383); with no config entry there is none, and no fallback to identifiers."""
    config_entry = hass.config_entries.async_get_entry(device.config_entry_id)
    return candidate_patterns(
        DiscoveredDevice(
            ha_device_registry_id=HaDeviceRegistryId(device.id),
            integration_domain=config_entry.domain if config_entry is not None else None,
            manufacturer=device.manufacturer,
            model=device.model,
            hw_version=device.hw_version,
            name=first_non_blank(device.name_by_user, device.name),
            entities=(),
            via_device_id=None,
        ),
        patterns,
    )
