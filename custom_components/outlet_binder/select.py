"""The `select` mirrors of an Appliance's socket facilities (#187). The coordinator
in core/mirrors/sync.py creates and keeps them; this platform only registers with it."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OutletBinderConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OutletBinderConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await entry.runtime_data.mirrors.async_register("select", async_add_entities)
