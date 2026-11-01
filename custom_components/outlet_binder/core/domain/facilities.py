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
- the vendor-named entity, from the entity's `translation_key`, unless that
  equals the standard name;
- nothing for a host-only entity, a disabled one, one with no
  `translation_key`, or one from another integration (a user's `switch_as_x`
  wrapper is not the socket's).

The on/off entity is the pattern's `on_off` role, never a file entry, and has no
vendor-named entity: its vendor name is the socket's own name on a strip.

An entity whose id has no rule is a *gap*, reported beside the mirrors: its
id is in the pattern's vocabulary but has no default, or it is not in the
vocabulary at all. It still gets the vendor-named entity.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from enum import StrEnum

from .discovery import CoPattern, expected_identifiers
from .facility_rules import ON_OFF, FacilityRule, StandardFacility
from .identifiers import (
    FacilityName,
    HaDeviceRegistryId,
    HaEntityDottedId,
    HaEntityRegistryId,
    VendorFacilityKey,
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
    `disabled` is true for any `disabled_by`, whoever set it."""

    id: HaEntityRegistryId
    entity_id: HaEntityDottedId
    unique_id: str | None
    domain: str
    platform: str
    translation_key: VendorFacilityKey | None
    original_name: str | None
    device_id: HaDeviceRegistryId | None
    disabled: bool


@dataclass(frozen=True, kw_only=True)
class SocketFacility:
    """One OB entity an Appliance would own: it mirrors `source`, in HA domain
    `domain`, and its entity id and unique_id end `id_suffix`. `display_name`
    is what follows the Appliance's name in the entity's friendly name."""

    source: HaEntityRegistryId
    domain: str
    id_suffix: str
    display_name: str


@dataclass(frozen=True, kw_only=True, order=True)
class FacilityClash:
    """A (domain, id ending) that two or more sources would have produced."""

    domain: str
    id_suffix: str


class GapKind(StrEnum):
    """Why an entity has no rule. The value is the suffix of the Repairs
    issue's translation key (`facility_<value>`)."""

    NO_DEFAULT = "no_default"
    NOT_IN_VOCABULARY = "not_in_vocabulary"

    @property
    def translation_key(self) -> str:
        return f"facility_{self.value}"

    @property
    def log_reason(self) -> str:
        """What the log line says is missing. A match on every member, so a
        new kind without wording fails the type check."""
        match self:
            case GapKind.NO_DEFAULT:
                return "has no default in its vocabulary file"
            case GapKind.NOT_IN_VOCABULARY:
                return "is not in its vocabulary file"


@dataclass(frozen=True, kw_only=True, order=True)
class FacilityGap:
    """An entity id of `integration_domain`, in HA domain `domain`, that the
    pattern has no rule for (#681)."""

    integration_domain: str
    domain: str
    key: VendorFacilityKey
    kind: GapKind


@dataclass(frozen=True)
class SocketFacilities:
    """What a socket gives an Appliance. `clashes` lists each id that two or
    more sources would have produced; none of those is in `mirrors`, since
    nothing guesses which source is meant. `gaps` lists each id the socket's
    entities have that the pattern has no rule for."""

    mirrors: tuple[SocketFacility, ...]
    clashes: tuple[FacilityClash, ...]
    gaps: tuple[FacilityGap, ...] = ()


# The Repairs issues for gaps have their own id namespace, so pruning stale ones
# (`stale_gap_issue_ids`) can never delete another `outlet_binder` issue, the
# near-miss ones included. The `.` between the parts is not in a domain or an
# id, so two gaps never share an issue id.
FACILITY_GAP_ISSUE_PREFIX = "facility_gap_"


def gap_issue_id(gap: FacilityGap) -> str:
    return f"{FACILITY_GAP_ISSUE_PREFIX}{gap.integration_domain}.{gap.domain}.{gap.key}"


def gap_placeholders(gap: FacilityGap) -> dict[str, str]:
    """Translation placeholders for a gap's Repairs issue. HA renders a raw
    `{name}` with no error if a key is missing, so
    tests/test_facility_gap_repairs.py checks them against strings.json."""
    return {"integration": gap.integration_domain, "domain": gap.domain, "id": str(gap.key)}


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
        rules = pattern.facility_rules
        for entity in entities:
            if (
                entity.device_id == device_id
                and entity.platform == pattern.integration_domain
                and not entity.disabled
                and entity.id != on_off_entity.id
                and entity.translation_key is not None
            ):
                mirrors.extend(_mirrors_of(entity, rules, standard, pattern.integration_domain))
                gap = _gap_of(entity, entity.translation_key, rules, pattern)
                if gap is not None:
                    gaps.add(gap)
    return replace(_without_clashes(mirrors), gaps=tuple(sorted(gaps)))


def _gap_of(
    entity: RegistryEntity,
    key: VendorFacilityKey,
    rules: Mapping[tuple[str, VendorFacilityKey], FacilityRule],
    pattern: CoPattern,
) -> FacilityGap | None:
    if (entity.domain, key) in rules:
        return None
    in_vocabulary = (entity.domain, key) in pattern.vocabulary
    return FacilityGap(
        integration_domain=pattern.integration_domain,
        domain=entity.domain,
        key=key,
        kind=GapKind.NO_DEFAULT if in_vocabulary else GapKind.NOT_IN_VOCABULARY,
    )


def _mirrors_of(
    entity: RegistryEntity,
    rules: Mapping[tuple[str, VendorFacilityKey], FacilityRule],
    standard: Mapping[FacilityName, StandardFacility],
    integration_domain: str,
) -> list[SocketFacility]:
    key = entity.translation_key
    assert key is not None
    rule = rules.get((entity.domain, key))
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
