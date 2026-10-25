"""Config flow for the Outlet & Appliance Binding integration."""

from pathlib import Path
from typing import Any, override

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from .const import (
    CONF_DEBUG_MODE,
    CONF_MODE,
    CONF_SOCKET_REGION,
    DEFAULT_DEBUG_MODE,
    DEFAULT_MODE,
    DEFAULT_SOCKET_REGION,
    DOMAIN,
    MODE_IMMEDIATE,
    MODES,
    SOCKET_REGION_LABELS,
    SOCKET_REGIONS,
)
from .db import edit_session
from .db.session import connection as db_connection
from .db.session import get_db_path
from .panel import socket_key_url

# The options form's sections, top to bottom. Each option sits in a box of
# its own; a section's fields arrive nested under its key, and are stored
# flat, so existing entries read them unchanged. Mode has a second,
# locked variant (see async_step_init), with its own description.
SECTION_SOCKET = "socket"
SECTION_MODE = "mode_options"
SECTION_MODE_LOCKED = "mode_locked"
SECTION_DEBUG = "debug"
_SECTIONS = (SECTION_SOCKET, SECTION_MODE, SECTION_MODE_LOCKED, SECTION_DEBUG)


def _box(fields: dict[vol.Marker, Any]) -> section:
    return section(vol.Schema(fields), {"collapsed": False})


class OutletBinderConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Outlet & Appliance Binding."""

    @override
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the single confirmation step."""
        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title="Outlet & Appliance Binding", data={})

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> OutletBinderOptionsFlow:
        """Return this integration's options flow."""
        return OutletBinderOptionsFlow()


class OutletBinderOptionsFlow(OptionsFlowWithReload):
    """Handle the Configure dialog -- the batch/immediate setting (#186),
    the debug mode switch and the panel's socket-icon region (see
    const.py's CONF_DEBUG_MODE and CONF_SOCKET_REGION).

    Extends `OptionsFlowWithReload` rather than plain `OptionsFlow`: OB
    registers no config-entry update listeners (that class's one
    restriction), so HA reloads the entry for us on save instead of this
    needing a hand-rolled reload.
    """

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the single options step.

        Switching to immediate mode is not offered while the edit log holds
        any entry, staged or redoable: immediate mode withdraws a refused
        write on the assumption that it is the only entry in the log. The
        Mode box then holds only the message to commit or flush first.
        A submitted switch is checked again, for an entry staged while the
        form was open, and the form comes back locked. Already in immediate
        mode, nothing is withheld. A batch write staged between the check on
        submit and the reload gets past it; that is rare, and Undo or Flush
        recovers it."""
        current_mode = self.config_entry.options.get(CONF_MODE, DEFAULT_MODE)
        mode_locked = current_mode != MODE_IMMEDIATE and await self.hass.async_add_executor_job(
            _has_log_entries, get_db_path(self.hass)
        )
        if user_input is not None:
            flat = {
                key: value for name in _SECTIONS for key, value in user_input.get(name, {}).items()
            }
            # The region chooser offers only a change, so left empty it keeps
            # the region as it is.
            flat.setdefault(
                CONF_SOCKET_REGION,
                self.config_entry.options.get(CONF_SOCKET_REGION, DEFAULT_SOCKET_REGION),
            )
            if not mode_locked:
                return self.async_create_entry(title="", data=flat)
            if CONF_MODE not in flat:
                # The locked box has no field, so batch is kept as it is.
                return self.async_create_entry(title="", data={**flat, CONF_MODE: current_mode})

        current_debug_mode = self.config_entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)
        current_socket_region = self.config_entry.options.get(
            CONF_SOCKET_REGION, DEFAULT_SOCKET_REGION
        )
        schema = vol.Schema(
            {
                vol.Required(SECTION_SOCKET): _box(
                    {
                        vol.Optional(CONF_SOCKET_REGION): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=[
                                    selector.SelectOptionDict(
                                        value=region, label=SOCKET_REGION_LABELS[region]
                                    )
                                    for region in SOCKET_REGIONS
                                    if region != current_socket_region
                                ]
                            )
                        )
                    }
                ),
                # Locked, the box holds only its description: the message.
                vol.Required(SECTION_MODE_LOCKED if mode_locked else SECTION_MODE): _box(
                    {}
                    if mode_locked
                    else {
                        vol.Optional(CONF_MODE, default=current_mode): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=list(MODES),
                                mode=selector.SelectSelectorMode.LIST,
                                # Each choice's label explains it (strings.json
                                # "selector"); the field's description says
                                # which changes stage at all.
                                translation_key=CONF_MODE,
                            )
                        )
                    }
                ),
                # Last: debug mode is developer-only, not a setting for a
                # real install.
                vol.Required(SECTION_DEBUG): _box(
                    {
                        vol.Optional(
                            CONF_DEBUG_MODE, default=current_debug_mode
                        ): selector.BooleanSelector()
                    }
                ),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={"socket_key": socket_key_url(current_socket_region)},
        )


def _has_log_entries(db_path: Path) -> bool:
    with db_connection(db_path) as conn:
        return edit_session.entry_count(conn) > 0
