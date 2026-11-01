"""How one vendor entity maps to OB's facility names (#211).

Pure and dependency-free, like domain/discovery.py. A rule is the default of
one id in an integration's vocabulary-and-defaults file
(`device_patterns/<integration>/vocabulary_and_defaults.yaml`), or an entry of a
model pattern's own `device.facilities` or `sockets.facilities`. This module is
separate from domain/facilities.py so that domain/discovery.py can hold rules on
a `CoPattern` without importing the resolver, which itself imports discovery.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from .identifiers import FacilityName, VendorFacilityKey

# The pattern's on/off role, never a file entry: its entity is the socket's
# own switch, which has no vendor-named entity (domain/facilities.py).
ON_OFF = FacilityName("ob_on_off")


@dataclass(frozen=True, kw_only=True)
class StandardFacility:
    """One entry of OB's facility vocabulary: the facility's nature.

    `domain` is the HA entity domain every entity named for this facility has,
    whichever integration it comes from. A facility with two domains would
    give `sensor.ob_<appliance>_voltage` on one socket and
    `number.ob_<appliance>_voltage` on another, and an automation using the
    first would break when the Appliance moved. `entity_id_name` is what the
    Appliance's entity id ends with. `display_name` follows the Appliance's
    name in an entity's friendly name."""

    domain: str
    entity_id_name: str
    display_name: str


@dataclass(frozen=True)
class FacilityRule:
    """What to do with the entity whose registry `translation_key` is `key`
    in HA domain `domain`.

    Exactly one of `facility_name` and `host_only` is set. The constructor enforces
    it, so a rule that says both or neither cannot exist.

    `host_only` marks an entity in the file's `host` section. It exists only at
    the CO level (restart, LED, signal strength, a whole-strip total): a CO
    Socket has no such facility, so an Appliance never mirrors it.
    `facility_name` is the key of the facility in OB's facility vocabulary. `key` is
    the file's `integration_name`.
    """

    domain: str
    key: VendorFacilityKey
    facility_name: FacilityName | None = None
    host_only: bool = False

    def __post_init__(self) -> None:
        if (self.facility_name is not None) == self.host_only:
            raise ValueError(
                f"facility rule {self.domain}.{self.key} must set exactly one of facility_name and"
                " host_only"
            )


@dataclass(frozen=True)
class IntegrationVocabulary:
    """What an integration's vocabulary-and-defaults file says (#681): every
    (HA domain, id) the integration offers, and the rule for each id that has a
    default. A default is for an id in `ids`, never outside it: the file lists
    the two together."""

    ids: frozenset[tuple[str, VendorFacilityKey]] = frozenset()
    defaults: tuple[FacilityRule, ...] = ()


def effective_rules(
    defaults: Iterable[FacilityRule], *, overrides: Iterable[FacilityRule]
) -> dict[tuple[str, VendorFacilityKey], FacilityRule]:
    """The integration's defaults with a model's own rules laid over them, keyed
    by (domain, key). A model's rule replaces the default for that one entity
    and for that model alone: nothing is merged field by field, so the result
    is always exactly one of the two rules as written. Run once, when a pattern
    loads (#681); a pattern carries the result."""
    merged = {(rule.domain, rule.key): rule for rule in defaults}
    merged.update({(rule.domain, rule.key): rule for rule in overrides})
    return merged
