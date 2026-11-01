"""The switch `entity_id` HA derives from a switch's display name.

`expected_switch_entity_id` is imported by both `switch.py`'s reslug step
and, through `device_switch_entity_id`, by `db/operations/devices.py`'s
collision check (#337) and discovery's disambiguation, so the id a write
is checked against is exactly the id reslug will later try to assign. It
takes the finished name from `domain/device_switch.py`, so an Appliance's
and a PCO's switch share one derivation of an entity id.

`mirror_entity_id` is the same for an Appliance's mirrors, On/Off included,
which are built from parts and not from a display name.

`reslug` is the rename both then apply, so the two cannot differ on a clash.
"""

from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .domain.device_switch import switch_name
from .domain.models import DeviceType


def reslug(
    entity_registry: er.EntityRegistry,
    entity_id: str,
    expected: str,
    clashes: set[tuple[str, str]],
) -> None:
    """Rename `entity_id` to `expected` in the registry, on every sync, so a
    drifted id heals itself (#275). When a different entity holds `expected`,
    (entity_id, expected) is added to `clashes` and the entity is left alone,
    since it is rare and the user can fix it. The caller logs the clashes, once,
    so that a lasting one does not repeat on every sync. An entity that is not
    in the registry has nothing to rename."""
    if entity_id == expected or entity_registry.async_get(entity_id) is None:
        return
    try:
        entity_registry.async_update_entity(entity_id, new_entity_id=expected)
    except ValueError:
        clashes.add((entity_id, expected))


def expected_switch_entity_id(switch_display_name: str) -> str:
    """The switch entity_id HA would derive today from a switch's current
    display name -- must match HA's own derivation exactly, or `reslug`
    would "fix" an entity_id to something HA itself would never generate."""
    return f"switch.{slugify(switch_display_name)}"


def mirror_entity_id(*, domain: str, appliance_label: str, id_suffix: str) -> str:
    """The entity_id of an Appliance's mirror (#187): `<domain>.ob_<label>_<id
    suffix>`. HA fixes the part before the dot, so `ob_` sits after it.

    Slugified as one string, never joined from a slugged label and the suffix:
    a label that slugs to nothing ("!!!") would otherwise leave `ob__power`,
    which HA refuses, since a double underscore is not a valid entity id. The
    suffix arrives already slug-safe from the resolver (domain/facilities.py).
    The id is built from these parts and not from the entity's display name,
    because a vendor facility's name ("Consumption today") does not slug to
    its suffix (`tplink_consumption_today`)."""
    return f"{domain}.{slugify(f'ob {appliance_label} {id_suffix}')}"


def appliance_id_part(appliance_label: str) -> str:
    """What every mirror id of this Appliance begins with after the dot. Two
    Appliances whose parts are equal clash on every facility they share, which
    is all a write can check: the facilities depend on the socket, and an
    Appliance may be unplugged. Two parts that differ can still meet when one
    label ends where the other's suffix begins ("Kitchen Tplink" with `power`,
    "Kitchen" with `tplink_power`); that rare case is left to reslug's
    log-and-leave."""
    return slugify(f"ob {appliance_label}")


def device_switch_entity_id(*, name: str) -> str:
    """The entity_id HA would give the plug switch of a PCO with this alias --
    the one place the two steps above are put together."""
    return expected_switch_entity_id(switch_name(device_type=DeviceType.CO, name=name))
