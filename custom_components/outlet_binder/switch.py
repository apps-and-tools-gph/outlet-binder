"""OB-owned switch platform (#368).

A `switch` entity per CO whose `has_plug` is true that OB registers itself,
repointed to its hosting CO Socket on every plug/unplug. A PCO's switch
mirrors the one socket it is plugged into and nothing upstream of it; in a
Unmanaged Outlet it is unavailable. Shape follows core's
`homeassistant/components/switch_as_x/entity.py`, adapted for one config
entry owning many entities (switch_as_x is one config entry per wrapped
entity).

An Appliance's switches, On/Off included, are not made here: this platform
registers with core/mirrors/sync.py, which makes them. It also runs this platform's
`_sync_entities`, on the state it has just read and under its one lock, and
prunes this platform's registry entries: one sync knows both sets, so neither
can be applied over the other from an older read.

No `device_entry` link: the hosting CO Socket changes on every replug, so
linking to it would make the switch jump between device pages.

## One sync entry point

`_sync_entities` is the only entry point -- run by core/mirrors/sync.py on each of
its syncs: once the switch platform registers, once per
`SIGNAL_SWITCHES_CHANGED` dispatcher signal (sent by websocket_api.py's
`_sync_after_write` after every write, on the failure paths too), and after
HA's registries change. The whole set comes from `desired_switches`
(`core/domain/device_switch.py`) and the live entities are keyed by `unique_id`,
so the steps cannot disagree about which switches exist. It always does all
of:

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

Unconditional on every sync, cheap on the common case (nothing plugged
in changed), rather than gated on "did this write touch a device with a plug".

History: docs/HISTORY-INDEX.md
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import OutletBinderConfigEntry
from .core.const import ENTITY_ID_PREFIX
from .core.domain.device_switch import SwitchSpec, desired_switches
from .core.entity_slug import expected_switch_entity_id, reslug

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
    """A PCO's plug: mirrors the hosting CO Socket's on/off state and forwards
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


@callback
def _sync_entities(
    hass: HomeAssistant,
    state: dict[str, Any],
    entities: dict[str, DeviceSwitch],
    async_add_entities: AddEntitiesCallback,
    clashes: set[tuple[str, str]],
) -> None:
    """Bring the PCO plugs in line with `state`. A drifted entity_id that
    cannot be renamed back is added to `clashes` as (entity_id, expected)."""
    entity_registry = er.async_get(hass)
    specs = desired_switches(cos=state["cos"], entity_id_prefix=ENTITY_ID_PREFIX)
    current_ids = {spec.unique_id for spec in specs}

    for unique_id in [uid for uid in entities if uid not in current_ids]:
        del entities[unique_id]

    new_entities: list[DeviceSwitch] = []
    for spec in specs:
        target = _resolve_target(entity_registry, spec.target_registry_id)

        if spec.unique_id in entities:
            entity = entities[spec.unique_id]
            entity.async_rename(spec.name)
            reslug(entity_registry, entity.entity_id, expected_switch_entity_id(spec.name), clashes)
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
    """Set up one `DeviceSwitch` per PCO with a plug, kept in sync by
    core/mirrors/sync.py along with the Appliances' switches: it reads the state
    once and applies both under one lock, so an older read is never applied
    over a newer one."""
    entities: dict[str, DeviceSwitch] = {}

    @callback
    def sync_plugs(state: dict[str, Any], clashes: set[tuple[str, str]]) -> None:
        _sync_entities(hass, state, entities, async_add_entities, clashes)

    await entry.runtime_data.mirrors.async_register(
        "switch", async_add_entities, sync_plugs=sync_plugs
    )
