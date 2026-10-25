"""The switch `entity_id` HA derives from a switch's display name.

`expected_switch_entity_id` is imported by both `switch.py`'s reslug step
and, through `device_switch_entity_id`, by `db/operations/devices.py`'s
collision check (#337) and discovery's disambiguation, so the id a write
is checked against is exactly the id reslug will later try to assign. It
takes the finished name from `domain/device_switch.py`, so an Appliance's
and a PCO's switch share one derivation of an entity id.
"""

from homeassistant.util import slugify

from .domain.device_switch import switch_name
from .domain.models import DeviceType


def expected_switch_entity_id(switch_display_name: str) -> str:
    """The switch entity_id HA would derive today from a switch's current
    display name -- must match HA's own derivation exactly, or `_reslug`
    would "fix" an entity_id to something HA itself would never generate."""
    return f"switch.{slugify(switch_display_name)}"


def device_switch_entity_id(
    *, device_type: DeviceType, name: str, appliance_type: str | None
) -> str:
    """The entity_id HA would give the switch of a device with this name
    (and, for an Appliance, type) -- the one place the two steps above
    are put together."""
    return expected_switch_entity_id(
        switch_name(device_type=device_type, name=name, appliance_type=appliance_type)
    )
