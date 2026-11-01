"""The OB entities that copy a CO Socket's facilities onto an Appliance (#187).

Each one copies one HA entity, its source, like a symlink: it keeps no state of
its own, takes its value and attributes from the source's state, and forwards a
control (switch, number, select, button) to the source. Which source an entity
copies is decided on every sync (domain/appliance_mirrors.py), so a move
repoints the entity and keeps its identity.

What a mirror copies, so it reports what its source reports:

- `unavailable` makes the mirror unavailable; a state that is not a value
  (`unknown` included) gives it no value.
- A sensor's unit, device class, state class and enum options are copied before
  the entity is registered, since HA stores them at registration. A value its
  device class cannot hold (a timestamp that is not a timestamp, a number that
  is not one) becomes no value: HA's sensor raises on such a value at every
  state write, which would break the mirror and not only that reading.
- Every attribute HA does not itself compute from the entity is passed through.

A control resolves its source from the entity registry when it is called, so a
source renamed in HA still receives it before the next sync.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from math import isfinite
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.components.sensor.const import NON_NUMERIC_DEVICE_CLASSES
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util
from homeassistant.util.enum import try_parse_enum

from ..domain.appliance_mirrors import MirrorSpec
from ..entity_slug import mirror_entity_id

# Attributes HA computes from the entity's own properties. Passing one through
# as an extra attribute would fight the property that writes it.
_COMPUTED_ATTRIBUTES = frozenset(
    {
        "assumed_state",
        "device_class",
        "editable",
        "entity_picture",
        "friendly_name",
        "icon",
        "max",
        "min",
        "mode",
        "options",
        "state_class",
        "step",
        "supported_features",
        "unit_of_measurement",
    }
)


def _number(raw: str) -> float | None:
    """The state as a finite number, or None."""
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if isfinite(value) else None


def _as_reported(raw: str) -> float | None:
    """The state as a number, an int when the source wrote one, so the mirror
    reads `30` where its source reads `30` and not `30.0`."""
    value = _number(raw)
    return int(value) if value is not None and raw.lstrip("-").isdigit() else value


def _is_on(state: State) -> bool | None:
    """An on/off source's value: None for `unknown`, which is no value."""
    return None if state.state == STATE_UNKNOWN else state.state == "on"


class MirrorEntity(Entity):
    """The part every mirror shares: identity, following the source's state,
    and forwarding a control. `_copy` is each domain's own part."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, spec: MirrorSpec, state: State | None) -> None:
        self._attr_name = spec.name
        self._attr_unique_id = spec.unique_id
        # Pre-set, so HA registers the entity under `ob_<appliance>_<id suffix>`
        # and not under an id slugified from the display name.
        self.entity_id = mirror_entity_id(
            domain=spec.domain, appliance_label=spec.appliance_label, id_suffix=spec.id_suffix
        )
        self._source_registry_id = spec.source
        self._tracked = ""
        self._unsub: CALLBACK_TYPE | None = None
        self._apply(state)

    def _copy(self, state: State) -> None:
        raise NotImplementedError

    def _apply(self, state: State | None) -> None:
        self._attr_available = state is not None and state.state != STATE_UNAVAILABLE
        if state is not None and self._attr_available:
            self._attr_icon = state.attributes.get(ATTR_ICON)
            self._attr_extra_state_attributes = {
                key: value
                for key, value in state.attributes.items()
                if key not in _COMPUTED_ATTRIBUTES
            }
            self._copy(state)

    def _source_entity_id(self) -> str:
        entry = er.async_get(self.hass).async_get(self._source_registry_id)
        return entry.entity_id if entry is not None else ""

    @callback
    def _refresh(self) -> None:
        self._apply(self.hass.states.get(self._tracked) if self._tracked else None)

    @callback
    def _untrack(self) -> None:
        if self._unsub is not None:
            self._unsub()
            self._unsub = None

    @callback
    def _track(self) -> None:
        self._untrack()
        self._tracked = self._source_entity_id()
        if self._tracked:
            self._unsub = async_track_state_change_event(
                self.hass, [self._tracked], self._async_source_changed
            )

    @callback
    def _async_source_changed(self, event: Event[EventStateChangedData]) -> None:
        self._refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self._track()
        self._refresh()

    async def async_will_remove_from_hass(self) -> None:
        self._untrack()

    @callback
    def async_update_spec(self, spec: MirrorSpec) -> None:
        """Adopt the Appliance's current name and source. Called on every sync;
        a no-op when nothing changed. An entity that was never added (a
        disabled one) only stores them, since it has no state to write."""
        changed = spec.name != self._attr_name or spec.source != self._source_registry_id
        self._attr_name = spec.name
        self._source_registry_id = spec.source
        if self.hass is None:
            return
        # The source's own entity id can change with the registry id unchanged.
        if changed or self._source_entity_id() != self._tracked:
            self._track()
            self._refresh()
            self.async_write_ha_state()

    async def _async_forward(self, domain: str, service: str, data: Mapping[str, Any]) -> None:
        target = self._source_entity_id()
        if not target:
            raise HomeAssistantError(f"{self.name} has no socket to send this to")
        await self.hass.services.async_call(
            domain, service, {"entity_id": target, **data}, blocking=True, context=self._context
        )


class MirrorSensor(MirrorEntity, SensorEntity):
    def _copy(self, state: State) -> None:
        attributes = state.attributes
        device_class = try_parse_enum(SensorDeviceClass, attributes.get(ATTR_DEVICE_CLASS))
        unit = attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        state_class = try_parse_enum(SensorStateClass, attributes.get("state_class"))
        options = attributes.get("options")
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        # HA refuses a unit on a device class that holds no number.
        self._attr_native_unit_of_measurement = (
            None if device_class in NON_NUMERIC_DEVICE_CLASSES else unit
        )
        # HA raises on every state write if options are set without the enum class.
        self._attr_options = (
            list(options)
            if options is not None and device_class is SensorDeviceClass.ENUM
            else None
        )
        self._attr_native_value = self._value(
            state.state,
            device_class=device_class,
            numeric=unit is not None
            or state_class is not None
            or (device_class is not None and device_class not in NON_NUMERIC_DEVICE_CLASSES),
        )

    def _value(self, raw: str, *, device_class: SensorDeviceClass | None, numeric: bool) -> Any:
        if device_class in (SensorDeviceClass.TIMESTAMP, SensorDeviceClass.UPTIME):
            moment = dt_util.parse_datetime(raw)
            return moment if moment is not None and moment.tzinfo is not None else None
        if device_class is SensorDeviceClass.DATE:
            return dt_util.parse_date(raw)
        if self._attr_options is not None and raw not in self._attr_options:
            return None
        if numeric and device_class is not SensorDeviceClass.ENUM and _number(raw) is None:
            return None
        return raw


class MirrorBinarySensor(MirrorEntity, BinarySensorEntity):
    def _copy(self, state: State) -> None:
        self._attr_device_class = try_parse_enum(
            BinarySensorDeviceClass, state.attributes.get(ATTR_DEVICE_CLASS)
        )
        self._attr_is_on = _is_on(state)


class MirrorSwitch(MirrorEntity, SwitchEntity):
    """A switch facility, and the socket's own on/off. Forwards through
    `homeassistant.turn_on`/`turn_off`, which any domain answers, so a socket
    whose on/off is a light still works."""

    def _copy(self, state: State) -> None:
        self._attr_device_class = try_parse_enum(
            SwitchDeviceClass, state.attributes.get(ATTR_DEVICE_CLASS)
        )
        self._attr_is_on = _is_on(state)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_forward("homeassistant", "turn_on", {})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_forward("homeassistant", "turn_off", {})


class MirrorNumber(MirrorEntity, NumberEntity):
    def _copy(self, state: State) -> None:
        attributes = state.attributes
        self._attr_device_class = try_parse_enum(
            NumberDeviceClass, attributes.get(ATTR_DEVICE_CLASS)
        )
        self._attr_native_unit_of_measurement = attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        self._attr_native_min_value = float(attributes.get("min", 0.0))
        self._attr_native_max_value = float(attributes.get("max", 100.0))
        self._attr_native_step = float(attributes.get("step", 1.0))
        self._attr_mode = try_parse_enum(NumberMode, attributes.get("mode")) or NumberMode.AUTO
        self._attr_native_value = _as_reported(state.state)

    async def async_set_native_value(self, value: float) -> None:
        await self._async_forward("number", "set_value", {"value": value})


class MirrorSelect(MirrorEntity, SelectEntity):
    def __init__(self, spec: MirrorSpec, state: State | None) -> None:
        # HA raises when it adds a select that has no `options`, and `_copy`
        # sets them only from a source that has a state.
        self._attr_options = []
        super().__init__(spec, state)

    def _copy(self, state: State) -> None:
        self._attr_options = list(state.attributes.get("options", ()))
        self._attr_current_option = state.state if state.state in self._attr_options else None

    async def async_select_option(self, option: str) -> None:
        await self._async_forward("select", "select_option", {"option": option})


class MirrorButton(MirrorEntity, ButtonEntity):
    """A button has no value to copy: HA's own state for it is when it was last
    pressed, which this entity records for its own presses."""

    def _copy(self, state: State) -> None:
        self._attr_device_class = try_parse_enum(
            ButtonDeviceClass, state.attributes.get(ATTR_DEVICE_CLASS)
        )

    async def async_press(self) -> None:
        await self._async_forward("button", "press", {})


MIRROR_CLASSES: Mapping[str, Callable[[MirrorSpec, State | None], MirrorEntity]] = {
    "binary_sensor": MirrorBinarySensor,
    "button": MirrorButton,
    "number": MirrorNumber,
    "select": MirrorSelect,
    "sensor": MirrorSensor,
    "switch": MirrorSwitch,
}
