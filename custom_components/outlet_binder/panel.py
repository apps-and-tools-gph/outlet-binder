"""Frontend panel registration for the Outlet & Appliance Binding integration."""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_ICON, PANEL_TITLE, PANEL_URL_PATH

STATIC_URL_BASE = f"/{DOMAIN}_static"
_FRONTEND_DIR = Path(__file__).parent / "frontend"
_FRONTEND_SCRIPT = _FRONTEND_DIR / "outlet-binder-panel.js"


def _script_url() -> str:
    """The bundle's URL, carrying a hash of its own contents.

    The panel is registered with `embed_iframe: True`, and a browser caches
    an ES module by URL. Without something in the URL that changes when the
    bundle changes, a deployed update keeps running the *old* module inside
    that iframe -- and a hard refresh of the outer page does not reliably
    evict it. `cache_headers=False` below is not sufficient on its own: it
    stops Home Assistant sending long-lived cache headers, but says nothing
    about a module the browser has already cached.

    That failure mode is silent whenever the payload shape hasn't changed:
    the panel simply renders slightly stale behaviour. When the shape has
    changed, the stale module reads fields that no longer exist.

    A content hash rather than the manifest version, because the bundle is
    rebuilt far more often than the version is bumped -- during development
    the version would not change at all.
    """
    digest = hashlib.sha256(_FRONTEND_SCRIPT.read_bytes()).hexdigest()[:12]
    return f"{STATIC_URL_BASE}/outlet-binder-panel.js?hash={digest}"


def socket_key_url(current: str) -> str:
    """The options dialog's key of every region's socket shape with `current`
    outlined, written next to the bundle by the frontend build
    (frontend/scripts/write-socket-icons.ts)."""
    return f"{STATIC_URL_BASE}/socket-key-{current}.svg"


async def async_register_static_path(hass: HomeAssistant) -> None:
    """Serve the bundled frontend JS. Called once from `async_setup`
    (`__init__.py`), never from `async_setup_entry` -- aiohttp's router
    freezes after startup, and `async_register_static_paths` raises
    `RuntimeError: Cannot register a resource into frozen router` if
    called again on a config-entry reload (#186 surfaced this: the
    options flow is the first thing that ever reloads this entry).
    `async_setup` itself only ever runs once per HA run, guarded by
    `domain in hass.config.components` (`homeassistant/setup.py`), which
    is what makes this safe to call unconditionally here.
    """
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL_BASE, str(_FRONTEND_DIR), cache_headers=False)]
    )


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the sidebar panel. The static path it points at must
    already be registered -- see `async_register_static_path`."""
    # read_bytes() is blocking I/O, so it may not run on the event loop.
    script_url = await hass.async_add_executor_job(_script_url)

    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        frontend_url_path=PANEL_URL_PATH,
        config={
            "_panel_custom": {
                "name": "outlet-binder-panel",
                "embed_iframe": True,
                "trust_external": False,
                "module_url": script_url,
            }
        },
        require_admin=True,
    )
