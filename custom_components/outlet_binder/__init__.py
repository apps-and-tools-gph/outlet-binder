"""The Outlet & Appliance Binding integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from homeassistant.components.frontend import async_remove_panel
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import ConfigType

from .core.build_stamp import (
    BUILD_STAMP_KEY,
    DEPLOYED_COMMIT_DIR,
    build_stamp,
    integration_version,
    read_deployed_commit,
)
from .core.const import (
    CONF_DEBUG_MODE,
    CONF_MODE,
    CONF_SOCKET_REGION,
    DEFAULT_DEBUG_MODE,
    DEFAULT_MODE,
    DEFAULT_SOCKET_REGION,
    DOMAIN,
    EDIT_SESSION_DISCARDED_ISSUE_ID,
    MODE_IMMEDIATE,
    PANEL_URL_PATH,
    SIGNAL_SWITCHES_CHANGED,
)
from .core.db.migrate import MigrationError
from .core.db.session import async_bootstrap, get_db_path
from .core.device_identification.facility_loader import ob_facility_vocabulary
from .core.device_identification.pattern_loader import load_patterns
from .core.domain.discovery import CoPattern
from .core.mirrors.sync import MirrorSync
from .core.panel import async_register_panel, async_register_static_path
from .core.websocket_api import async_register_websocket_commands


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
    core/db/session.py's `connection` — negligible overhead for a local SQLite
    file at this project's stated scale — so there's nothing to keep open,
    and nothing for `async_unload_entry` to close.

    `ob_version` is the running integration's version, which the edit session
    stamps on the log it opens (core/domain/edit_session_upgrade.py).

    `patterns` is loaded once here from the shipped YAML files
    (core/device_identification/pattern_loader.py, docs/LLD.md §4), not re-read on every
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
    ob_version: str
    patterns: tuple[CoPattern, ...]
    mirrors: MirrorSync
    immediate: bool
    debug_mode: bool
    socket_region: str


type OutletBinderConfigEntry = ConfigEntry[OutletBinderData]

# switch.py (#368) -- one DeviceSwitch per device with a plug. The others each
# register with core/mirrors/sync.py, which creates an Appliance's mirrors of its
# socket's facilities in that domain.
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Component-level setup, run exactly once per HA run regardless of
    how many times the config entry itself reloads (#186) -- see
    panel.py's `async_register_static_path` for why that distinction
    matters.
    """
    await async_register_static_path(hass)
    deployed_commit = await hass.async_add_executor_job(read_deployed_commit, DEPLOYED_COMMIT_DIR)
    hass.data[BUILD_STAMP_KEY] = build_stamp(await integration_version(hass), deployed_commit)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: OutletBinderConfigEntry) -> bool:
    """Set up Outlet & Appliance Binding from a config entry."""
    ob_version = await integration_version(hass) or "unknown"
    try:
        session_discarded = await async_bootstrap(hass, running_version=ob_version)
    except MigrationError as err:
        # A migration failed and the database was restored to its
        # pre-migration state, or the database is newer than this code and was
        # left untouched (see core/db/migrate.py) — either needs a human to
        # look at it, not an automatic HA retry, so ConfigEntryError rather
        # than ConfigEntryNotReady.
        raise ConfigEntryError(str(err)) from err
    if session_discarded:
        ir.async_create_issue(
            hass,
            DOMAIN,
            EDIT_SESSION_DISCARDED_ISSUE_ID,
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=EDIT_SESSION_DISCARDED_ISSUE_ID,
        )
    patterns = await hass.async_add_executor_job(load_patterns)
    standard = await hass.async_add_executor_job(ob_facility_vocabulary)
    db_path = get_db_path(hass)
    mirrors = MirrorSync(
        hass,
        db_path=db_path,
        patterns=patterns,
        standard=standard,
    )
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_SWITCHES_CHANGED, mirrors.async_sync)
    )
    entry.async_on_unload(mirrors.async_listen())
    immediate = entry.options.get(CONF_MODE, DEFAULT_MODE) == MODE_IMMEDIATE
    debug_mode = entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)
    socket_region = entry.options.get(CONF_SOCKET_REGION, DEFAULT_SOCKET_REGION)
    entry.runtime_data = OutletBinderData(
        db_path=db_path,
        ob_version=ob_version,
        patterns=patterns,
        mirrors=mirrors,
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
