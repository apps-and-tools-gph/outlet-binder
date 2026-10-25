"""The Outlet & Appliance Binding integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from homeassistant.components.frontend import async_remove_panel
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_DEBUG_MODE,
    CONF_MODE,
    CONF_SOCKET_REGION,
    DEFAULT_DEBUG_MODE,
    DEFAULT_MODE,
    DEFAULT_SOCKET_REGION,
    MODE_IMMEDIATE,
    PANEL_URL_PATH,
)
from .db.migrate import MigrationError
from .db.session import async_bootstrap, get_db_path
from .device_identification.pattern_loader import load_patterns
from .domain.discovery import CoPattern
from .panel import async_register_panel, async_register_static_path
from .websocket_api import async_register_websocket_commands


@dataclass(frozen=True)
class OutletBinderData:
    """Per-config-entry runtime state, stored on `ConfigEntry.runtime_data`.

    Deliberately just the DB path, not a live `sqlite3.Connection`: HA
    dispatches `hass.async_add_executor_job` calls to a thread pool, and a
    single connection reused across calls from different (or concurrent)
    executor threads isn't safe — `sqlite3` connections aren't safe for
    concurrent multi-thread use even with `check_same_thread=False` (that
    flag only disables the same-thread check, not concurrent access).
    Every db-layer call instead opens its own short-lived connection via
    db/session.py's `connection` — negligible overhead for a local SQLite
    file at this project's stated scale — so there's nothing to keep open,
    and nothing for `async_unload_entry` to close.

    `patterns` is loaded once here from the shipped YAML files
    (device_identification/pattern_loader.py, docs/LLD.md §4), not re-read on every
    `discover_cos` call.

    `immediate`, `debug_mode` and `socket_region` are resolved once here
    from `entry.options` (#186) rather than re-derived at each call site,
    so no consumer has to know the option keys or the defaults. Rebuilt
    from scratch on every options save -- `OptionsFlowWithReload` reloads
    the entry, so there is no mutation path for this frozen dataclass to
    worry about.

    `socket_region` is an option, not a per-browser panel setting, because
    which regional socket shape is in the room is a fact about the
    installation, not the viewer.
    """

    db_path: Path
    patterns: tuple[CoPattern, ...]
    immediate: bool
    debug_mode: bool
    socket_region: str


type OutletBinderConfigEntry = ConfigEntry[OutletBinderData]

# switch.py (#368) -- one DeviceSwitch per device with a plug. No other platform:
# OB owns no other entity.
PLATFORMS = [Platform.SWITCH]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Component-level setup, run exactly once per HA run regardless of
    how many times the config entry itself reloads (#186) -- see
    panel.py's `async_register_static_path` for why that distinction
    matters.
    """
    await async_register_static_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: OutletBinderConfigEntry) -> bool:
    """Set up Outlet & Appliance Binding from a config entry."""
    try:
        await async_bootstrap(hass)
    except MigrationError as err:
        # A schema migration failed and the database was already restored
        # to its pre-migration state (see db/migrate.py) — this needs a
        # human to look at it, not an automatic HA retry, so
        # ConfigEntryError rather than ConfigEntryNotReady.
        raise ConfigEntryError(str(err)) from err
    patterns = await hass.async_add_executor_job(load_patterns)
    immediate = entry.options.get(CONF_MODE, DEFAULT_MODE) == MODE_IMMEDIATE
    debug_mode = entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)
    socket_region = entry.options.get(CONF_SOCKET_REGION, DEFAULT_SOCKET_REGION)
    entry.runtime_data = OutletBinderData(
        db_path=get_db_path(hass),
        patterns=patterns,
        immediate=immediate,
        debug_mode=debug_mode,
        socket_region=socket_region,
    )
    await async_register_panel(hass)
    await async_register_websocket_commands(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: OutletBinderConfigEntry) -> bool:
    """Unload a config entry."""
    async_remove_panel(hass, PANEL_URL_PATH)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
