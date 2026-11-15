"""How one vendor entity is recognised and mapped to OB's facility names (#211).

Pure and dependency-free, like domain/discovery.py. An entry of an
integration's vocabulary-and-defaults file
(`device_patterns/<integration>/vocabulary_and_defaults.yaml`), or of a model
pattern's own `device.facilities` or `sockets.facilities`, states the facts that
recognise one entity (`EntityRecogniser`) and, optionally, what OB makes of it
(`FacilityRule`). This module is separate from domain/facilities.py so that
domain/discovery.py can hold both on a `CoPattern` without importing the
resolver, which itself imports discovery.
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


@dataclass(frozen=True, kw_only=True)
class EntityRecogniser:
    """The facts that recognise one entity of an integration: it is in HA domain
    `domain`, its `unique_id` ends `unique_id_suffix` (a literal `endswith`), and,
    if `device_class` is given, it also has that device class. `name` is the
    entry's own key: the `<name>` in `<integration>_<name>`. A person writes it,
    so it never changes with HA's language or with the integration."""

    domain: str
    name: VendorFacilityKey
    unique_id_suffix: str
    device_class: str | None = None

    def recognises(self, *, domain: str, unique_id: str | None, device_class: str | None) -> bool:
        return (
            domain == self.domain
            and unique_id is not None
            and unique_id.endswith(self.unique_id_suffix)
            and (self.device_class is None or self.device_class == device_class)
        )

    def overlaps(self, other: EntityRecogniser) -> bool:
        """Whether one entity could satisfy both: the same domain, one suffix
        ending with the other (equal suffixes included), and compatible device
        classes (equal, or one absent)."""
        return (
            self.domain == other.domain
            and (
                self.unique_id_suffix.endswith(other.unique_id_suffix)
                or other.unique_id_suffix.endswith(self.unique_id_suffix)
            )
            and (
                self.device_class is None
                or other.device_class is None
                or self.device_class == other.device_class
            )
        )


@dataclass(frozen=True)
class FacilityRule:
    """What to do with the entity the `EntityRecogniser` named `key` recognises
    in HA domain `domain`.

    Exactly one of `facility_name` and `host_only` is set. The constructor enforces
    it, so a rule that says both or neither cannot exist. An entry with neither
    has a recogniser and no rule: it is offered as `<integration>_<key>` only.

    `host_only` marks an entity in the file's `host` section. It exists only at
    the CO level (restart, LED, signal strength, a whole-strip total): a CO
    Socket has no such facility, so an Appliance never mirrors it.
    `facility_name` is the key of the facility in OB's facility vocabulary. `key` is
    the entry's name.
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
class FacilityEntry:
    """One entry of a vocabulary file or a model's own list: how to recognise
    the entity, and what OB makes of it, if anything. A rule names the same domain
    and name as its recogniser, so the entry cannot recognise one entity and map
    another."""

    recogniser: EntityRecogniser
    rule: FacilityRule | None = None

    def __post_init__(self) -> None:
        rule = self.rule
        if rule is not None and (rule.domain, rule.key) != (
            self.recogniser.domain,
            self.recogniser.name,
        ):
            raise ValueError(
                f"facility rule {rule.domain}.{rule.key} is on the entry for"
                f" {self.recogniser.domain}.{self.recogniser.name}"
            )


@dataclass(frozen=True)
class IntegrationVocabulary:
    """What an integration's vocabulary-and-defaults file says: every entity it
    lists, each with its recogniser and optional rule."""

    entries: tuple[FacilityEntry, ...] = ()


def effective_entries(
    base: Iterable[FacilityEntry], *, overrides: Iterable[FacilityEntry]
) -> tuple[FacilityEntry, ...]:
    """The integration's entries with a model's own laid over them, keyed by
    (domain, name). A model's entry replaces the integration's whole, for that
    one entity and that model alone, and a name the integration lacks is added:
    nothing is merged field by field, so the result is always exactly the
    entries as written. Run once, when a pattern loads; a pattern carries the
    result."""
    merged = {(e.recogniser.domain, e.recogniser.name): e for e in base}
    merged.update({(e.recogniser.domain, e.recogniser.name): e for e in overrides})
    return tuple(merged.values())
