"""Constants for the Outlet & Appliance Binding integration."""

DOMAIN = "outlet_binder"

PANEL_URL_PATH = DOMAIN
PANEL_TITLE = "Outlet Binder"
PANEL_ICON = "mdi:power-plug-outline"

CONF_MODE = "mode"
MODE_BATCH = "batch"
MODE_IMMEDIATE = "immediate"
# The options flow's choices, in its order. get_state reports one of them
# as `mode`, and the panel's MODES in domain.ts is the same list; both are
# checked against tests/fixtures/modes.json (#537).
MODES = (MODE_BATCH, MODE_IMMEDIATE)
DEFAULT_MODE = MODE_BATCH

# General debug-mode switch (#246). Named and framed broadly rather than
# after its first gated behaviour (individual delete) -- renaming an
# options key later strands whatever's already stored in existing config
# entries, and more debug-only behaviour may hang off this flag in future.
CONF_DEBUG_MODE = "debug_mode"
DEFAULT_DEBUG_MODE = False

# Which regional socket icon the panel renders (#128) -- a shared,
# installation-wide fact (one household has one physical socket region),
# so this lives in config-entry options rather than per-browser
# localStorage, the same way CONF_MODE and CONF_DEBUG_MODE do. Codes match
# the keys of frontend/src/outlet-binder-panel/socket-icons.ts's
# SOCKET_ICON_PATHS, which is SocketRegion, in the same order. Both are
# checked against tests/fixtures/socket_regions.json, and
# tests/test_options_flow.py checks that each has a label below.
CONF_SOCKET_REGION = "socket_region"
SOCKET_REGIONS = ("uk", "eu", "us", "de", "fr", "it", "jp", "au", "ch")
DEFAULT_SOCKET_REGION = "uk"
# How the options dialog names each region. The code leads, matching its
# caption in the dialog's key of socket shapes; the plug types are the IEC
# letters.
SOCKET_REGION_LABELS = {
    "uk": "UK (Type G)",
    "eu": "EU – Europe (Type C/E/F)",
    "us": "US (Type A/B)",
    "de": "DE – Germany (Type F)",
    "fr": "FR – France (Type E)",
    "it": "IT – Italy (Type L)",
    "jp": "JP – Japan (Type A/B)",
    "au": "AU – Australia (Type I)",
    "ch": "CH – Switzerland (Type J)",
}

# Fixed prefix on the unique_id of every OB-owned switch (#368). Not
# a namespace HA enforces: switch.py's orphan prune only considers registry
# entries on OB's own platform.
ENTITY_ID_PREFIX = "ob_"

# Dispatcher signal (#368): websocket_api.py's `_sync_after_write` sends
# this after every write; switch.py's platform listens and resyncs its
# entities. Lives here, not in switch.py, because websocket_api.py also
# needs it and importing it from switch.py would import `. import
# OutletBinderConfigEntry` against __init__.py's still-initializing module
# -- __init__.py imports websocket_api.py at module load time, long before
# switch.py is ever imported (HA only imports platforms lazily, at
# `async_forward_entry_setups` time).
SIGNAL_SWITCHES_CHANGED = f"{DOMAIN}_switches_changed"
