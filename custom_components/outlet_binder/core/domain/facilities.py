"""A CO Socket's facilities, and the OB entities each one gives (#211).

Pure and dependency-free, like domain/discovery.py: it takes snapshots of the
HA registry rows it needs and returns plain data, so a BDD scenario can drive it
without `hass`. The platforms that mirror a socket's facilities build the
snapshots from the live registries; nothing here is stored.

A socket's *facilities* are the entities on the socket's own HA device, plus the
pattern's on/off entity, which can sit on the parent device (a strip's socket
switches). Names follow docs/DECISIONS.md, _A CO Socket's facilities are found
and named live_:

- the OB-named entity, for a facility the pattern's rules map to a standard name;
- the vendor-named entity, `<integration>_<name>` from the entry's YAML key,
  unless that equals the standard name;
- nothing for a host-only entity, a disabled one, an unlisted one, or one from
  another integration (a user's `switch_as_x` wrapper is not the socket's).

An entity is found by the facts its entry states: HA domain, `unique_id` ending
and, optionally, device class. The entity registry's `translation_key` plays no
part.

The on/off entity is the pattern's `on_off` role, never a file entry, and has no
vendor-named entity: its vendor name is the socket's own name on a strip.

An enabled entity of the integration that no entry recognises is a *gap*,
reported beside the mirrors. It gets no OB entity at all.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace

from .discovery import CoPattern, expected_identifiers
from .facility_rules import ON_OFF, FacilityEntry, StandardFacility
from .identifiers import (
    FacilityName,
    HaDeviceRegistryId,
    HaEntityDottedId,
    HaEntityRegistryId,
)
from .repairs import stale_issue_ids


@dataclass(frozen=True, kw_only=True)
class RegistryDevice:
    """One device registry row, reduced to what finding a socket's device
    needs."""

    id: HaDeviceRegistryId
    via_device_id: HaDeviceRegistryId | None
    identifiers: frozenset[tuple[str, str]]


@dataclass(frozen=True, kw_only=True)
class RegistryEntity:
    """One entity registry row, reduced to what naming a facility needs.
    `device_class` is the registry's `device_class`, else its
    `original_device_class`. `disabled` is true for any `disabled_by`, whoever
    set it."""

    id: HaEntityRegistryId
    entity_id: HaEntityDottedId
    unique_id: str | None
    domain: str
    platform: str
    device_class: str | None
    original_name: str | None
    device_id: HaDeviceRegistryId | None
    disabled: bool


@dataclass(frozen=True, kw_only=True)
class SocketFacility:
    """One OB entity an Appliance would own: it mirrors `source`, in HA domain
    `domain`, and its entity id and unique_id end `id_suffix`. `display_name`
    is what follows the Appliance's name in the entity's friendly name. `vendor`
    is the manufacturer when the entity is named by it and not by OB's
    vocabulary, so a reader can say so."""

    source: HaEntityRegistryId
    domain: str
    id_suffix: str
    display_name: str
    vendor: str | None = None


@dataclass(frozen=True, kw_only=True, order=True)
class FacilityClash:
    """A (domain, id ending) that two or more sources would have produced."""

    domain: str
    id_suffix: str


@dataclass(frozen=True, kw_only=True, order=True)
class FacilityGap:
    """An enabled entity of `integration_domain` on a socket's device that the
    pattern's vocabulary does not list. Described by facts only, since OB names
    nothing it has not been told about."""

    integration_domain: str
    entity_registry_id: HaEntityRegistryId
    entity_id: HaEntityDottedId
    domain: str
    device_class: str | None


@dataclass(frozen=True)
class SocketFacilities:
    """What a socket gives an Appliance. `clashes` lists each id that two or
    more sources would have produced; none of those is in `mirrors`, since
    nothing guesses which source is meant. `gaps` lists each enabled entity of
    the socket's device that the pattern's vocabulary does not list."""

    mirrors: tuple[SocketFacility, ...]
    clashes: tuple[FacilityClash, ...]
    gaps: tuple[FacilityGap, ...] = ()


# The Repairs issues for gaps have their own id namespace, so pruning stale ones
# (`stale_gap_issue_ids`) can never delete another `outlet_binder` issue, the
# near-miss ones included. The `.` between the parts is not in a domain or in an
# entity registry id, and a registry id is one entity's, so two gaps never share
# an issue id.
FACILITY_GAP_ISSUE_PREFIX = "facility_gap_"

# The key of the gap issue's text in strings.json.
FACILITY_GAP_TRANSLATION_KEY = "facility_not_in_vocabulary"

# What the text says for an entity with no device class. A placeholder must be a
# string, and a bare "None" would read as a device class.
NO_DEVICE_CLASS = "none"


def gap_issue_id(gap: FacilityGap) -> str:
    return f"{FACILITY_GAP_ISSUE_PREFIX}{gap.integration_domain}.{gap.entity_registry_id}"


def gap_placeholders(gap: FacilityGap) -> dict[str, str]:
    """Translation placeholders for a gap's Repairs issue. HA renders a raw
    `{name}` with no error if a key is missing, so
    tests/test_facility_gap_repairs.py checks them against strings.json."""
    return {
        "integration": gap.integration_domain,
        "entity_id": str(gap.entity_id),
        "domain": gap.domain,
        "device_class": gap.device_class or NO_DEVICE_CLASS,
    }


def stale_gap_issue_ids(
    current: Iterable[FacilityGap], *, existing: frozenset[str]
) -> frozenset[str]:
    """Every gap-prefixed Repairs issue id in `existing` that `current` gaps no
    longer justify. An id outside the prefix is never returned, so this cannot
    prune an unrelated `outlet_binder` issue."""
    return stale_issue_ids(
        (gap_issue_id(gap) for gap in current),
        prefix=FACILITY_GAP_ISSUE_PREFIX,
        existing=existing,
    )


def socket_device_id(
    pattern: CoPattern,
    *,
    host: RegistryDevice,
    on_off_entity: RegistryEntity,
    devices: Iterable[RegistryDevice],
) -> HaDeviceRegistryId | None:
    """The HA device that holds the socket's own entities, or None.

    The pattern's `on_off.identified_by` says how: for `device: self` the
    socket's device is the host's own; for `device: child` it is the one child
    of the host (`via_device_id`) carrying the identifier that rule expects for
    this socket's on/off entity. No child, or more than one, means no device:
    nothing matches by substring or guesses."""
    rule = pattern.on_off.identified_by
    if rule is None or on_off_entity.unique_id is None:
        return None
    if rule.device == "self":
        return host.id
    domain = pattern.integration_domain
    own = {value for d, value in host.identifiers if d == domain}
    expected = expected_identifiers(rule, on_off_entity.unique_id, own)
    matches = {
        device.id
        for device in devices
        if device.via_device_id == host.id
        and any(d == domain and value in expected for d, value in device.identifiers)
    }
    return next(iter(matches)) if len(matches) == 1 else None


def _on_off_mirror(
    on_off_entity: RegistryEntity, standard: Mapping[FacilityName, StandardFacility]
) -> SocketFacility:
    # Always a switch, whatever the source is: some integrations show a
    # socket as a light, and an automation targets `switch.ob_<name>_on_off`.
    return SocketFacility(
        source=on_off_entity.id,
        domain="switch",
        id_suffix=standard[ON_OFF].entity_id_name,
        display_name=standard[ON_OFF].display_name,
    )


def on_off_only(
    on_off_entity: RegistryEntity, standard: Mapping[FacilityName, StandardFacility]
) -> SocketFacilities:
    """What a socket gives when its pattern or host device cannot be found: the
    On/Off alone, since it needs only the socket's own entity and an automation
    targets it."""
    return SocketFacilities(mirrors=(_on_off_mirror(on_off_entity, standard),), clashes=())


def socket_facilities(
    pattern: CoPattern,
    standard: Mapping[FacilityName, StandardFacility],
    *,
    host: RegistryDevice,
    on_off_entity: RegistryEntity,
    devices: Iterable[RegistryDevice],
    entities: Iterable[RegistryEntity],
) -> SocketFacilities:
    """The OB entities a socket gives, from a snapshot of the registries.

    `standard` is OB's facility vocabulary; it must hold every `facility_name` a
    rule uses and `on_off` (the loader checks both, so a miss here is a defect,
    not a data problem)."""
    mirrors = [_on_off_mirror(on_off_entity, standard)]
    gaps: set[FacilityGap] = set()
    device_id = socket_device_id(pattern, host=host, on_off_entity=on_off_entity, devices=devices)
    if device_id is not None:
        for entity in entities:
            if (
                entity.device_id == device_id
                and entity.platform == pattern.integration_domain
                and not entity.disabled
                and entity.id != on_off_entity.id
            ):
                entry = _entry_of(entity, pattern.entries)
                if entry is None:
                    gaps.add(_gap_of(entity, pattern))
                    continue
                mirrors.extend(
                    _mirrors_of(
                        entity, entry, standard, pattern.integration_domain, pattern.manufacturer
                    )
                )
    return replace(_without_clashes(mirrors), gaps=tuple(sorted(gaps)))


def _entry_of(entity: RegistryEntity, entries: Iterable[FacilityEntry]) -> FacilityEntry | None:
    """The entry that recognises `entity`. The loader refuses entries that one
    entity could satisfy together, so there is at most one."""
    return next(
        (
            e
            for e in entries
            if e.recogniser.recognises(
                domain=entity.domain, unique_id=entity.unique_id, device_class=entity.device_class
            )
        ),
        None,
    )


def _gap_of(entity: RegistryEntity, pattern: CoPattern) -> FacilityGap:
    return FacilityGap(
        integration_domain=pattern.integration_domain,
        entity_registry_id=entity.id,
        entity_id=entity.entity_id,
        domain=entity.domain,
        device_class=entity.device_class,
    )


def _mirrors_of(
    entity: RegistryEntity,
    entry: FacilityEntry,
    standard: Mapping[FacilityName, StandardFacility],
    integration_domain: str,
    manufacturer: str,
) -> list[SocketFacility]:
    key = entry.recogniser.name
    rule = entry.rule
    if rule is not None and rule.host_only:
        return []
    found: list[SocketFacility] = []
    ob_ending = None
    if rule is not None:
        assert rule.facility_name is not None
        ob_ending = standard[rule.facility_name].entity_id_name
        found.append(
            SocketFacility(
                source=entity.id,
                domain=entity.domain,
                id_suffix=ob_ending,
                display_name=standard[rule.facility_name].display_name,
            )
        )
    # A vendor name equal to the facility's id ending would only repeat the
    # OB-named entity, so a mapped facility gets the second entity only when
    # they differ.
    if ob_ending != str(key):
        found.append(
            SocketFacility(
                source=entity.id,
                domain=entity.domain,
                id_suffix=f"{integration_domain}_{key}",
                display_name=entity.original_name or key,
                vendor=manufacturer,
            )
        )
    return found


def _without_clashes(mirrors: list[SocketFacility]) -> SocketFacilities:
    by_id: dict[tuple[str, str], list[SocketFacility]] = defaultdict(list)
    for mirror in mirrors:
        by_id[(mirror.domain, mirror.id_suffix)].append(mirror)
    kept = [group[0] for group in by_id.values() if len(group) == 1]
    clashes = sorted(
        FacilityClash(domain=domain, id_suffix=id_suffix)
        for (domain, id_suffix), group in by_id.items()
        if len(group) > 1
    )
    return SocketFacilities(
        mirrors=tuple(sorted(kept, key=lambda m: (m.domain, m.id_suffix))),
        clashes=tuple(clashes),
    )
