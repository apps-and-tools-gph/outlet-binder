"""OB-owned switch platform (#368).

A `switch` entity per device with a plug that OB registers itself: an
Appliance, or a CO whose `has_plug` is true. A permanent entity per device,
repointed to its hosting CO Socket on every plug/unplug. A PCO's switch
mirrors the one socket it is plugged into and nothing upstream of it; in a
Unmanaged Outlet it is unavailable. Shape follows core's
`homeassistant/components/switch_as_x/entity.py`, adapted for one config
entry owning many entities (switch_as_x is one config entry per wrapped
entity).

No `device_entry` link: the hosting CO Socket changes on every replug, so
linking to it would make the switch jump between device pages.

## One sync entry point

`_sync_entities` is the only entry point -- run once at platform setup and
once per `SIGNAL_SWITCHES_CHANGED` dispatcher signal (sent by
websocket_api.py's `_sync_after_write` after every write, on the failure
paths too). The whole set comes from `desired_switches`
(`domain/device_switch.py`) and the live entities are keyed by `unique_id`,
so the steps cannot disagree about which switches exist. It always does all
of:

- **Prune** -- remove registry entries whose device no longer has a switch. A
  live entity's removal cascades automatically
  (`Entity._async_process_registry_update_or_remove` reacts to
  `EntityRegistry.async_remove` and calls the entity's own
  `async_remove()`), so nothing further is needed for a currently-loaded
  entity; a *not yet loaded* orphan (left over from a device deleted
  while HA was off) is found by an id-membership scan.
- **Rename** -- give the entity its *current* display name
  (`DeviceSwitch.async_rename`). HA fixes the name when an entity is first
  added, so without this a renamed device keeps its old friendly name until
  the next reload.
- **Reslug** -- rename a drifted entity_id back to what HA would derive
  from the switch's *current* name. Only meaningful for a switch already
  tracked in `entities`; one freshly (re)registered in this same
  sync always gets the current name, either as a brand new registration or
  by reattaching to its own already-correct prior registry entry
  (`EntityRegistry.async_get_or_create` resolves by `unique_id` first) --
  so it needs no explicit reslug.
- **Repoint** -- re-resolve each switch's on/off target from
  `plugged_into_co_socket_id` and hand it to the entity, which
  re-subscribes only if the target actually changed
  (`DeviceSwitch.async_repoint`).
- **Add** -- a switch not yet in `entities` gets a new `DeviceSwitch`,
  added through the stored `async_add_entities`.

Unconditional on every signal, cheap on the common case (nothing plugged
in changed), rather than gated on "did this write touch a device with a plug".

History: docs/HISTORY-INDEX.md
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import OutletBinderConfigEntry
from .const import DOMAIN, ENTITY_ID_PREFIX, SIGNAL_SWITCHES_CHANGED
from .db.operations.state import get_full_state
from .db.session import connection as db_connection
from .domain.device_switch import SwitchSpec, desired_switches
from .entity_slug import expected_switch_entity_id

_LOGGER = logging.getLogger(__name__)

_UNAVAILABLE_STATES = (None, "unknown", "unavailable")


def _resolve_target(entity_registry: er.EntityRegistry, registry_id: str | None) -> str:
    """A HA entity/device registry id -> its current dotted `entity_id`,
    or `""` if there's nothing to resolve. `""` means "unavailable", not
    "no change"; see `DeviceSwitch._apply_target_state`."""
    if registry_id is None:
        return ""
    entry = entity_registry.entities.get_entry(registry_id)
    return entry.entity_id if entry is not None else ""


class DeviceSwitch(SwitchEntity):
    """Mirrors the hosting CO Socket's on/off state and forwards
    turn_on/turn_off to it. `homeassistant.turn_on`/`turn_off`, not
    `switch.turn_on`/`off`, kept domain-agnostic on purpose -- a
    switch->light repoint must keep working."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, spec: SwitchSpec, target: str) -> None:
        self._attr_name = spec.name
        self._attr_unique_id = spec.unique_id
        self._target = target
        self._unsub_target: CALLBACK_TYPE | None = None

    def _apply_target_state(self) -> None:
        state = self.hass.states.get(self._target) if self._target else None
        value = state.state if state is not None else None
        self._attr_available = bool(self._target) and value not in _UNAVAILABLE_STATES
        self._attr_is_on = value == "on"

    @callback
    def _async_target_changed(self, event: Event[EventStateChangedData]) -> None:
        self._apply_target_state()
        self.async_write_ha_state()

    @callback
    def _async_subscribe_target(self) -> None:
        if self._unsub_target is not None:
            self._unsub_target()
            self._unsub_target = None
        if self._target:
            self._unsub_target = async_track_state_change_event(
                self.hass, [self._target], self._async_target_changed
            )

    async def async_added_to_hass(self) -> None:
        self._async_subscribe_target()
        self._apply_target_state()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_target is not None:
            self._unsub_target()
            self._unsub_target = None

    @callback
    def async_rename(self, name: str) -> None:
        """Adopt the device's current display name. Called on every sync,
        unconditionally (module docstring); a no-op when nothing changed.
        Writing the state is what makes HA update the friendly name and the
        registry's `original_name`. A switch that was never added (a
        disabled one) only stores the name, as `async_repoint` does."""
        if name == self._attr_name:
            return
        self._attr_name = name
        if self.hass is None:
            return
        self.async_write_ha_state()

    @callback
    def async_repoint(self, target: str) -> None:
        """Re-resolve the on/off target. Called on every sync,
        unconditionally (module docstring); a no-op when nothing changed,
        which is the overwhelmingly common case.

        A disabled switch's entity is tracked in `entities` (module
        docstring: `_sync_entities` builds it once, on first sight) but
        was never actually added -- HA's entity_platform aborts before
        `async_added_to_hass` for a disabled entity
        (`Entity.add_to_platform_abort` sets `self.hass`/`self.platform`
        back to `None`). Only the stored target is updated in that case:
        there is no live subscription or state to touch, and enabling
        the entity reloads the whole config entry, which rebuilds this
        entity fresh from the then-current target anyway."""
        if target == self._target:
            return
        self._target = target
        if self.hass is None:
            return
        self._async_subscribe_target()
        self._apply_target_state()
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_forward("turn_on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_forward("turn_off")

    async def _async_forward(self, service: str) -> None:
        if not self._target:
            return
        await self.hass.services.async_call(
            "homeassistant",
            service,
            {"entity_id": self._target},
            blocking=True,
            context=self._context,
        )


def _prune_orphaned_registry_entries(
    entity_registry: er.EntityRegistry, specs: list[SwitchSpec]
) -> None:
    """Remove registry entries this platform owns whose device no longer has
    a switch (#337) -- a deleted device, a CO that became fixed, a device
    never loaded as a live entity this session (a leftover from a deletion
    while HA was off). A currently-loaded entity's removal cascades from the
    registry event (module docstring); this only needs to reach the
    registry."""
    expected = {spec.unique_id for spec in specs}
    for entry in list(entity_registry.entities.values()):
        if entry.domain != "switch" or entry.platform != DOMAIN:
            continue
        if not entry.unique_id.startswith(ENTITY_ID_PREFIX) or entry.unique_id in expected:
            continue
        entity_registry.async_remove(entry.entity_id)


def _reslug(entity_registry: er.EntityRegistry, entity: DeviceSwitch, name: str) -> None:
    """Rename `entity`'s entity_id back to what HA would derive from its
    switch's *current* name, unconditionally every sync (#275) --
    self-healing any drift, at the cost of one cheap comparison on the
    common case where nothing changed. A collision is logged and left
    alone (not worth building machinery for a rare, user-fixable
    conflict)."""
    expected = expected_switch_entity_id(name)
    if entity.entity_id == expected:
        return
    try:
        entity_registry.async_update_entity(entity.entity_id, new_entity_id=expected)
    except ValueError:
        _LOGGER.warning(
            "Outlet & Appliance Binding: couldn't rename %s to %s -- "
            "%s is already registered to a different entity. Rename "
            "or remove the conflicting entity to clear this -- if two "
            "devices swapped names, rename one of them to something "
            "else, wait for a sync, then rename it to what you wanted.",
            entity.entity_id,
            expected,
            expected,
        )


@callback
def _sync_entities(
    hass: HomeAssistant,
    state: dict[str, Any],
    entities: dict[str, DeviceSwitch],
    async_add_entities: AddEntitiesCallback,
) -> None:
    entity_registry = er.async_get(hass)
    specs = desired_switches(
        cos=state["cos"], appliances=state["appliances"], entity_id_prefix=ENTITY_ID_PREFIX
    )
    current_ids = {spec.unique_id for spec in specs}

    _prune_orphaned_registry_entries(entity_registry, specs)
    for unique_id in [uid for uid in entities if uid not in current_ids]:
        del entities[unique_id]

    new_entities: list[DeviceSwitch] = []
    for spec in specs:
        target = _resolve_target(entity_registry, spec.target_registry_id)

        if spec.unique_id in entities:
            entity = entities[spec.unique_id]
            entity.async_rename(spec.name)
            _reslug(entity_registry, entity, spec.name)
            entity.async_repoint(target)
            continue

        entity = DeviceSwitch(spec, target)
        entities[spec.unique_id] = entity
        new_entities.append(entity)

    if new_entities:
        async_add_entities(new_entities)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OutletBinderConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one `DeviceSwitch` per device with a plug, then keep them in
    sync with every write via `SIGNAL_SWITCHES_CHANGED`."""
    entities: dict[str, DeviceSwitch] = {}
    # The read runs on an executor thread, so two syncs could otherwise
    # overlap and an older read be applied after a newer one. One at a
    # time, each sync reads after the last has applied.
    sync_lock = asyncio.Lock()

    def _read_state() -> dict[str, Any]:
        with db_connection(entry.runtime_data.db_path) as conn:
            return get_full_state(conn)

    async def _async_sync(*_args: Any) -> None:
        async with sync_lock:
            state = await hass.async_add_executor_job(_read_state)
            _sync_entities(hass, state, entities, async_add_entities)

    await _async_sync()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_SWITCHES_CHANGED, _async_sync))
