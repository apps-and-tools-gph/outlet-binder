"""HA device/entity discovery and classification for COs (docs/LLD.md §4).

Pure, dependency-free pattern matching and reconciliation — no `hass`, no
persistence, matching domain/chain.py's convention: takes and returns
only plain data, so it's testable without HA fixtures. websocket_api.py
is responsible for the HA-coupled edges (building the plain-data
snapshots below from real device_registry/entity_registry objects) and
db/operations/devices.py for persistence.

Classification is pattern-driven on manufacturer/model (docs/LLD.md §4) —
a much stronger, lower-false-positive signal than per-entity device_class
heuristics, which is why a match is auto-written with no confirmation
step (see that section for the full rationale).
"""

import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Literal

from .identifiers import HaDeviceRegistryId, HaEntityDottedId, HaEntityRegistryId
from .normalization import normalize_name
from .versions import ANY_VERSION, VersionConstraint, parse_version


class PatternKind(StrEnum):
    """Whether a discovered outlet has a plug of its own (#422).

    The values are what a pattern file's `device.kind` holds, and the schema's
    enum must list the same two. Discovery always writes a CO row; this is
    the one place that says whether that CO is portable or fixed in place,
    and `has_plug` is what `devices.has_plug` stores.
    """

    PLUG_IN = "PLUG_IN"
    FIXED = "FIXED"

    @property
    def has_plug(self) -> bool:
        return self is PatternKind.PLUG_IN


@dataclass(frozen=True)
class DiscoveredEntity:
    """One HA entity registry entry, reduced to what pattern matching
    needs.

    `id` is the entity registry's own immutable id (distinct from both
    `entity_id`, which a user can rename, and `unique_id`, which is
    integration-set) — verified via a real HA instance's
    `core.entity_registry` storage.

    `source_device_id` is the HA device this entity actually belongs to
    *before* any multi-device family folding (group_device_families) —
    still correct after folding pools several devices' entities into one
    flat tuple, since folding only concatenates entity lists and never
    touches each entity's own fields."""

    entity_id: HaEntityDottedId
    id: HaEntityRegistryId
    unique_id: str | None
    domain: str  # "switch", "sensor", "binary_sensor", ...
    device_class: str | None
    source_device_id: HaDeviceRegistryId


@dataclass(frozen=True)
class DiscoveredDevice:
    """One HA device registry entry plus its (non-disabled) entities,
    reduced to what pattern matching needs. Built by websocket_api.py from
    real device_registry/entity_registry objects — kept as this module's
    own plain-data shape so it stays import-free of homeassistant.*.

    `ha_device_registry_id` is the device registry's own immutable id (the same
    field CO/CO Socket rows are keyed on throughout, see domain/models.py).

    `via_device_id` is the `ha_device_registry_id` of the device this one "connects
    through", or None. A Tapo P304M power strip
    registers as 5 HA devices (1 parent + 4 per-socket children, each
    child's via_device_id pointing at the parent) rather than one device
    like the KP115 — group_device_families below uses this field to fold
    a device family like that back into a single DiscoveredDevice before
    matching.

    `identifiers` is the device's own `identifiers` (HA's `(domain, id)`
    tuples) — who HA's registry says actually created this device, as
    opposed to `manufacturer`/`model`, which are just strings that
    integration self-reports and could coincidentally collide with an
    unrelated device. Used only by a role's `identified_by` (see
    `IdentifiedBy`), which compares the identifier values themselves. Which
    integration owns the device is `integration_domain`, not anything read
    off these tuples.

    `integration_domain` is the domain of the config entry that created the
    device (`DeviceEntry.config_entry_id` -> `ConfigEntry.domain`), the one
    anchor HA mandates for "which integration made this device" -- unlike
    the domain element of `identifiers`, which is only a convention. A
    pattern matches a device only when this equals the pattern's own
    integration domain (its top-level folder); None means the config entry
    could not be found, and then no pattern matches. It has no default, so
    a construction site that forgets it fails loudly instead of quietly
    becoming a device that matches nothing.

    `child_identifiers` is every identifier of every child device
    `group_device_families` folded into this one, pooled: a folded child
    is dropped from the result, so this is the only place its identifiers
    survive. Pooled rather than per-child because the entities that
    `identified_by` pairs with a child (a KP303's socket switches) belong
    to the *parent* device, so nothing but the identifier itself links
    them to their own child.

    `mac` is the device's network MAC address, upper-cased with colon
    separators (websocket_api.py's `_device_mac` reads it off
    `device.connections` via `dr.CONNECTION_NETWORK_MAC`), or None if the
    integration reports none. Used only by `disambiguate_aliases` (issue #185) as a suffix
    source when two discovered devices would otherwise propose the same
    alias — real, stable, and already the user's own manual naming
    convention on this project's test instance."""

    ha_device_registry_id: HaDeviceRegistryId
    integration_domain: str | None
    manufacturer: str | None
    model: str | None
    hw_version: str | None
    name: str | None
    entities: tuple[DiscoveredEntity, ...]
    via_device_id: HaDeviceRegistryId | None
    identifiers: frozenset[tuple[str, str]] = frozenset()
    child_identifiers: frozenset[tuple[str, str]] = frozenset()
    mac: str | None = None


@dataclass(frozen=True)
class IdentifiedBy:
    """A role's exact identity rule: an entity is accepted only if the
    device has an identifier equal to `identifier` filled in from that
    entity. Replaces guessing identity from a `unique_id` suffix, which
    can coincide with an unrelated id (issue #341: a KP303 master whose
    MAC ends in `00`, `01` or `02`).

    `device` names which device's identifiers are compared: `"self"` is the
    matched device, `"child"` is any of its folded children
    (`DiscoveredDevice.child_identifiers`). Only identifiers whose domain
    is the pattern's `integration_domain` are compared.

    `identifier` is a template over a closed set of placeholders, filled
    in from the entity and the matched device: `{unique_id}` is the
    entity's, `{parent_identifier}` is the matched device's own identifier
    (any one of them, in the pattern's integration domain), and is only
    valid with `device="child"`. Everything device-specific, such as the
    `_` a KP303 puts between the two, is written in the pattern's YAML;
    the code only fills in the template and compares strings exactly.
    """

    device: Literal["self", "child"]
    identifier: str


UNIQUE_ID_PLACEHOLDER = "{unique_id}"
PARENT_IDENTIFIER_PLACEHOLDER = "{parent_identifier}"


@dataclass(frozen=True)
class EntityRoleMatch:
    """How to find the entity/entities filling one role within a device's
    entity list, by HA entity domain and (optionally) device_class.

    `domain`/`device_class` alone aren't always precise enough on real
    devices: a TP-Link KP115, a single-socket smart
    plug, has *two* switch-domain entities (the main power switch plus an
    accessory LED-indicator switch) — `identified_by` (or, where identity
    can't be confirmed, `exclude_unique_id_suffixes`) disambiguates those
    without needing per-device special-casing in the matching algorithm
    itself. The same device also has *three* sensors
    with device_class "energy" (today's/this month's/total consumption),
    sidestepped entirely by `monitoring` matching on device_class "power"
    instead — see the real KP115 pattern (device_identification/device_patterns/README.md).
    """

    domain: str
    device_class: str | None = None
    exclude_unique_id_suffixes: tuple[str, ...] = ()
    unique_id_suffixes: tuple[str, ...] = ()
    """Ordered per-socket suffixes (index 0 = position 1, ...), used
    instead of the domain/device_class-then-sort-by-entity_id rule below
    when a device's entity_ids aren't reliably position-sortable.
    A KP303's 3 individual socket switches live
    on the *parent* device (not per-child, despite `child_models`) with
    unique_ids ending "00"/"01"/"02", but their `entity_id`s are derived
    from arbitrary user-facing friendly names with no positional meaning
    at all -- sorting by entity_id gives the wrong socket order. Each
    suffix must match exactly one entity (checked against the full,
    literal `unique_id` via `endswith` -- not a "positional segment"
    extraction) or the whole device fails to match (see match_device's
    docstring).

    A declared suffix isn't always the bare 2-digit code itself: verified
    against a real P304M, whose per-socket power sensor lives on a
    separate *child* device (unlike its on_off switch, which is on the
    parent) with a unique_id like `<base>00_current_power_w` --
    HA-core's tplink integration appends `_<feature key>` to every
    non-primary entity's unique_id (see `homeassistant/components/
    tplink/entity.py`'s `_get_feature_unique_id`). So `monitoring`'s
    declared suffix there is the whole trailing string,
    `"00_current_power_w"`, not just `"00"` -- see
    `device_identification/device_patterns/tplink/TP-Link/P304M/any.yaml`. When both `on_off` and
    `monitoring` are declared, `device_identification/pattern_loader.py` requires both or
    neither to set `unique_id_suffixes` (issue #235): `_match_pattern`
    pairs the two roles' resolved lists purely by index, so if only one
    role were suffix-ordered, index i would only coincidentally mean the
    same physical socket in both."""

    identified_by: IdentifiedBy | None = None
    """Restricts a role's candidates to entities the device's identifiers
    confirm (see `IdentifiedBy`). A filter only: it never orders sockets,
    so it does not take part in the "both or neither" rule above --
    `unique_id_suffixes` still sets position. Applied to the candidates
    before any suffix is tried, so an entity it rejects can never
    collide with one a suffix picks."""


@dataclass(frozen=True)
class CoPattern:
    """One known device pattern: a manufacturer/model (+ optional hardware
    version) match plus how to derive CO Sockets from the matched
    device's entities.

    `kind` says whether the device has a plug of its own (`PLUG_IN`) or is
    fixed in place (`FIXED`); it has no default, because nothing may guess it.

    Exactly three named roles are privileged to the matching code --
    nothing else needs code-level identity anywhere in matching,
    persistence, or the frontend:

    - `on_off` (per socket, required, match-blocking) — defines socket
      count/shape.
    - `monitoring` (per socket, optional, best-effort) — no default: a
      pattern declares it explicitly (typically `{domain: sensor,
      device_class: power}`) whenever the device has a monitoring-capable
      entity worth pointing at, same as `all_on_off` below -- deliberately
      not silently defaulted in device_identification/pattern_loader.py, so a pattern file fully
      explains its own matching behavior without needing to know about a
      hidden Python-side default (see device_identification/device_patterns/README.md).
    - `all_on_off` (per device, optional, no default) — a whole-device
      master on/off switch, if one exists (e.g. a KP303's whole-strip
      switch), distinct from any individual socket's own on/off.

    A matched device's other entities aren't recorded anywhere — nothing
    beyond these three named roles needs code-level identity, and nothing
    reads a device's remaining entities today.

    Matching is scoped by integration first, then manufacturer and model.
    `integration_domain` (e.g. `"tplink"`) is the domain of the config
    entry that created the device (`DiscoveredDevice.integration_domain`),
    compared exactly and case-sensitively (HA domains are lowercase); it
    is the pattern file's top-level folder. Manufacturer/model are
    exact-string, case-insensitive, and only need to be unique within one
    integration, which controls what it reports: `DeviceEntry.manufacturer`
    is whatever string the *integration* set, not a device-intrinsic
    property (for TP-Link devices it is one hardcoded `"TP-Link"` in
    `homeassistant/components/tplink/entity.py`), so two integrations can
    report the same manufacturer+model without colliding here. The domain
    is the config entry's, not a cross-check against the device's
    identifier domains: identifier domains are only a convention, whereas
    the config entry's domain is the field HA requires. A device whose
    integration has no patterns is simply unknown, the same as an unknown
    manufacturer/model; a manufacturer/
    model mismatch within a known integration still surfaces as a
    `NearMiss`.
    `hw_version` is a `VersionConstraint` (domain/versions.py, issue
    #136) — `ANY_VERSION` (the default) matches every hardware version;
    a floor matches that version and everything after; an exact pin
    (`=`) matches only that exact version, a backstop for a case the
    floor ladder genuinely can't express. See `candidate_patterns` below
    for how a device's patterns are ordered and selected against this.
    `sw_version` is the same type, parsed from the pattern filename
    alongside it, but not enforced in matching today — a mechanical gap,
    not a design objection: `DiscoveredDevice` has no `sw_version` field
    to compare against yet. A floor is the right constraint for firmware:
    real firmware strings update via OTA too often to pin against, but a
    floor like `1.0.13` keeps matching after an OTA to `1.0.14`. Every shipped
    pattern uses `ANY_VERSION` for it. Reserved for a future device that
    genuinely needs firmware-differentiated behavior.
    Accepted, known limitation in the meantime: a firmware update that
    changes entity/capability shape stops matching, with no `sw_version`
    enforcement to catch it -- though `match_device` reports it as a
    `NearMiss`, so it does not fail silently. Entity-shape
    checks (see match_device) only decide whether a manufacturer/model(/hw_version)
    match resolves cleanly enough to propose a CO, never widen which
    devices match.
    """

    pattern_id: str
    integration_domain: str
    manufacturer: str
    model: str
    kind: PatternKind
    socket_count: int
    on_off: EntityRoleMatch
    monitoring: EntityRoleMatch | None = None
    all_on_off: EntityRoleMatch | None = None
    hw_version: VersionConstraint = ANY_VERSION
    sw_version: VersionConstraint = ANY_VERSION
    child_models: tuple[str, ...] = ()
    """The model string(s) this device's own per-socket child devices
    report, if any (docs/LLD.md §4's hub-plus-children case). Verified
    against real hardware: a Tapo P304M's children report model "P304M"
    (same as the parent); a Kasa KP303's children report model "Socket
    for KP303(UK)" (different from the parent's "KP303") -- there's no
    reliable general rule linking a parent's model string to its
    children's, so each pattern declares its own children's model(s)
    explicitly rather than group_device_families guessing from raw field
    comparisons. Empty (the default) means this device has no children to
    fold in."""

    default_socket_name: re.Pattern[str] | None = None
    """The names this device's integration gives its Sockets before anyone
    renames them (e.g. `Tapo P304M_\\d+`), matched against a Socket's
    whole name. Reference data for the "Appliances from Socket names"
    dialog (issue #394), which leaves such Sockets out; it is not one of the
    three named roles above and plays no part in matching. None means the
    pattern declares no default names."""


# Known device patterns are loaded from
# custom_components/outlet_binder/device_identification/device_patterns/*.yaml
# by device_identification/pattern_loader.py
# (docs/LLD.md §4: a pattern is reference data describing a class of device,
# not application logic; hardcoding it here would mean every new supported
# device needs a Python change and a redeploy).


@dataclass(frozen=True)
class ProposedCoSocket:
    position: int
    on_off_entity_registry_id: HaEntityRegistryId
    monitoring_entity_registry_id: HaEntityRegistryId | None


@dataclass(frozen=True)
class ProposedCo:
    ha_device_registry_id: HaDeviceRegistryId
    alias: str
    kind: PatternKind
    all_on_off_entity_registry_id: HaEntityRegistryId | None
    sockets: tuple[ProposedCoSocket, ...]
    pattern_id: str
    superseded_pattern_ids: tuple[str, ...]
    """The candidates that outranked the winner but failed their `on_off`
    shape check, in the order tried (most specific first, from
    `candidate_patterns`); empty when the top candidate won. hw_version
    exclusions never outranked the winner, so they are not listed (issue
    #146). No default: a construction site that forgets it must fail type
    checking rather than report "nothing superseded"."""
    mac: str | None = None
    """Carried over from the matched `DiscoveredDevice.mac`, unchanged --
    `disambiguate_aliases`' suffix source when this proposal's alias
    collides with another (issue #185)."""


@dataclass(frozen=True)
class PatternRejection:
    """Why one pattern, whose manufacturer and model matched a device, did
    not produce a CO for it. `reason` is one plain sentence naming the
    failed role and what was found (issue #353)."""

    pattern_id: str
    reason: str


@dataclass(frozen=True)
class NearMiss:
    """A device whose manufacturer and model match at least one known
    pattern, yet which no pattern turned into a CO. Returned by
    `match_device` in place of a `ProposedCo` so the caller can report
    it: a pattern that is too loose or too strict would otherwise fail
    silently (issue #353). Carries every pattern tried, in the order tried
    (hw_version exclusions first)."""

    ha_device_registry_id: HaDeviceRegistryId
    name: str | None
    manufacturer: str | None
    model: str | None
    rejections: tuple[PatternRejection, ...]


@dataclass(frozen=True)
class _Unresolved:
    """A role that did not resolve to exactly one entity per socket, and
    why. Private: `_match_pattern` turns it into a `PatternRejection`."""

    reason: str


@dataclass(frozen=True)
class _Identity:
    """The identifier values `identified_by` compares against, already
    narrowed to the pattern's `integration_domain`. Empty when the device
    carries none in that domain, so an `identified_by` role then accepts
    nothing (fails closed) rather than everything."""

    own: frozenset[str]
    children: frozenset[str]


def _identity_of(device: DiscoveredDevice, pattern: CoPattern) -> _Identity:
    domain = pattern.integration_domain

    def values(identifiers: frozenset[tuple[str, str]]) -> frozenset[str]:
        return frozenset(value for d, value in identifiers if d == domain)

    return _Identity(values(device.identifiers), values(device.child_identifiers))


_PLACEHOLDER_RE = re.compile(r"\{(unique_id|parent_identifier)\}")


def _fill(template: str, values: dict[str, str]) -> str:
    """Single pass, so a value that itself looks like a placeholder is
    never expanded a second time. A placeholder with no value (a
    `{parent_identifier}` under `device: self`, which the loader rejects)
    stays literal and so matches no identifier."""
    return _PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), template)


def _identified(entity: DiscoveredEntity, role: EntityRoleMatch, identity: _Identity) -> bool:
    rule = role.identified_by
    if rule is None:
        return True
    if entity.unique_id is None:
        return False
    if rule.device == "self":
        return _fill(rule.identifier, {"unique_id": entity.unique_id}) in identity.own
    return any(
        _fill(rule.identifier, {"unique_id": entity.unique_id, "parent_identifier": own})
        in identity.children
        for own in identity.own
    )


def _matches_role(entity: DiscoveredEntity, role: EntityRoleMatch, identity: _Identity) -> bool:
    if entity.domain != role.domain:
        return False
    if role.device_class is not None and entity.device_class != role.device_class:
        return False
    if not _identified(entity, role, identity):
        return False
    if entity.unique_id is not None and any(
        entity.unique_id.endswith(suffix) for suffix in role.exclude_unique_id_suffixes
    ):
        return False
    return True


def _entities_by_role(
    entities: tuple[DiscoveredEntity, ...], role: EntityRoleMatch, identity: _Identity
) -> list[DiscoveredEntity]:
    """Entities matching a role, sorted by entity_id.

    Sorting by entity_id (not unique_id, which varies by integration) is
    the per-socket ordering rule: HA's own naming for multi-outlet devices
    is reliably suffix-numbered (switch.kasa_strip_1, _2, ...), so this is
    deterministic without needing device-specific knowledge -- but only
    while entity_id actually carries positional meaning. It stops holding
    the moment a user renames a device's child entities, since HA derives
    entity_id from the (user-editable) friendly name, not from anything
    stable -- a renamed P304M's stored positions scramble for exactly this
    reason (issue #234). `unique_id_suffixes` below is the fallback for a
    device where this can't be trusted.
    """
    matches = [e for e in entities if _matches_role(e, role, identity)]
    return sorted(matches, key=lambda e: e.entity_id)


def _entity_ids(entities: list[DiscoveredEntity]) -> str:
    return ", ".join(str(e.entity_id) for e in entities)


def _role_matches_by_position(
    entities: tuple[DiscoveredEntity, ...],
    role: EntityRoleMatch,
    socket_count: int,
    identity: _Identity,
) -> list[DiscoveredEntity] | _Unresolved:
    """A socket-level role's matches, in position order (index i = socket
    i+1), or an `_Unresolved` saying why it doesn't resolve cleanly.

    If `role.unique_id_suffixes` is set, each suffix positionally
    identifies one socket's entity directly, in the order declared --
    used when a device's entity_ids aren't reliably position-sortable
    (see EntityRoleMatch's docstring / the KP303 case). Otherwise falls
    back to the general rule: gather every entity matching
    domain/device_class/suffix filters, then sort by entity_id.

    `role.identified_by` filters in both branches. The suffix branch does
    not go through `_matches_role`, so it must apply it itself -- skipping
    it there would leave the very case `identified_by` exists for (a
    KP303) unprotected.
    """
    after = " after identified_by" if role.identified_by is not None else ""
    if role.unique_id_suffixes:
        ordered = []
        for suffix in role.unique_id_suffixes:
            candidates = [
                e
                for e in entities
                if e.domain == role.domain
                and (role.device_class is None or e.device_class == role.device_class)
                and _identified(e, role, identity)
                and e.unique_id is not None
                and e.unique_id.endswith(suffix)
            ]
            if len(candidates) != 1:
                found = f"{len(candidates)} entities"
                if candidates:
                    found += f" ({_entity_ids(candidates)})"
                return _Unresolved(f"suffix '{suffix}' matched {found}{after}, expected exactly 1")
            ordered.append(candidates[0])
        # Defense in depth for a CoPattern constructed directly (bypassing
        # device_identification/pattern_loader.py's load-time length check -- every test in
        # tests/test_discovery_matching.py does this): fail closed rather
        # than let _match_pattern index past the end of (or silently
        # under-fill) `ordered` when unique_id_suffixes' length doesn't
        # match socket_count.
        if len(ordered) != socket_count:
            return _Unresolved(
                f"{len(role.unique_id_suffixes)} suffixes declared for {socket_count} sockets"
            )
        return ordered
    matches = _entities_by_role(entities, role, identity)
    if len(matches) != socket_count:
        found = f"{len(matches)} entities"
        if matches:
            found += f" ({_entity_ids(matches)})"
        return _Unresolved(f"{found} matched{after}, expected {socket_count}")
    return matches


def _pattern_model_matches(device: DiscoveredDevice, pattern: CoPattern) -> bool:
    """Integration/manufacturer/model identity check only — version
    constraints are handled separately by candidate_patterns, deliberately
    after this filter: which vendor's version-string quirks
    apply can only be known once the matching vendor's patterns are known,
    and only our own side of the comparison (the pattern's filename token)
    needs to stay universal across every manufacturer. The integration
    domain is compared exactly, so a same-string device from another
    integration is unknown here rather than a near-miss (issue #383)."""
    return (
        device.integration_domain == pattern.integration_domain
        and device.manufacturer is not None
        and device.model is not None
        and device.manufacturer.strip().casefold() == pattern.manufacturer.casefold()
        and device.model.strip().casefold() == pattern.model.casefold()
    )


def candidate_patterns(
    device: DiscoveredDevice, patterns: tuple[CoPattern, ...]
) -> tuple[CoPattern, ...]:
    """Every pattern whose manufacturer/model matches `device` and whose
    hw_version constraint the device's (parsed) hw_version satisfies,
    ordered most-specific-first: an exact pin outranks every floor
    regardless of version, and among floors a higher one outranks a lower
    one (VersionConstraint.rank) — with pattern_id ascending as a
    deterministic tie-break. Implemented as two stable sorts (pattern_id
    ascending, then rank descending) rather than a combined key, so the
    tie-break falls out of sort stability.

    Shared by match_device and group_device_families's parent-pattern
    lookup, so both start from the same ordered candidates. They can still end
    on different patterns: group_device_families folds using only the *first*
    candidate's `child_models`, while
    match_device skips a first candidate that fails its shape check and
    goes on to a later one. Making them agree would need folding to depend
    on matching, which itself needs the folded entities. It matters only
    for a lower-ranked pattern under the same model that declares
    different `child_models`; none exists, so this is stated rather than
    engineered around (issue #341).
    """
    model_matches = [p for p in patterns if _pattern_model_matches(device, p)]
    device_version = parse_version(device.hw_version)
    version_matches = [p for p in model_matches if p.hw_version.allows(device_version)]
    ordered = sorted(version_matches, key=lambda p: p.pattern_id)
    ordered.sort(key=lambda p: p.hw_version.rank, reverse=True)
    return tuple(ordered)


def group_device_families(
    devices: tuple[DiscoveredDevice, ...],
    patterns: tuple[CoPattern, ...],
) -> tuple[DiscoveredDevice, ...]:
    """Fold each child device's entities into its parent's DiscoveredDevice
    where via_device_id links them AND the child's model is one the
    parent's own matched pattern declares as a child_models entry
    (docs/LLD.md §4's hub-plus-children case -- e.g. a Tapo P304M power
    strip registers as 5 HA devices, 1 parent + 4 per-socket children).

    Deliberately not a generic heuristic (e.g. "same manufacturer as the
    parent"): a P304M's children report
    model "P304M" (same as the parent) while a Kasa KP303's children
    report model "Socket for KP303(UK)" (different from the parent's
    "KP303") -- there's no reliable rule linking a parent's model string
    to its children's in general. Instead, each pattern declares its own
    children's model(s) explicitly (CoPattern.child_models), the same way
    it declares everything else about its device -- so this only ever
    needs a *parent*-pattern lookup, never a second match attempt on the
    child itself. A parent whose matched pattern declares no child_models
    (the default) never absorbs anything, regardless of via_device_id
    links -- e.g. a Zigbee coordinator's many unrelated child devices are
    never merged, since no pattern claims them as children.

    A device absorbed as a child is dropped from the result entirely; its
    parent keeps its own identity fields (ha_device_registry_id, manufacturer,
    model, ...) with entities = its own entities + every qualifying
    child's entities. Each entity keeps its own `source_device_id`
    unchanged by this pooling (see DiscoveredEntity's docstring) -- this
    is what lets `_match_pattern` later recover which physical device an
    otherwise-undeclared, pooled-in entity actually came from. Standalone
    devices, and any device whose via_device_id doesn't resolve to a
    family match, pass through unchanged.

    Called once per discovery pass, before match_device -- see
    websocket_api.py's handle_discover_cos.

    Built from two plain, purely structural maps -- decided before any
    pattern logic runs at all:
    - candidates_by_parent: every device that HAS a via_device_id, grouped
      by what it points to. Unfiltered -- just "who links to whom".
    - childless_by_id: every device that does NOT have a via_device_id, by
      its own id. Every parent we've ever seen is childless itself (no
      via_device_id chains), so this map doubles as "resolve a
      via_device_id to the real device it points to".

    Only then is a pattern-based decision made: for each parent in
    childless_by_id with any raw candidates, look up its matched pattern's
    child_models and keep only the candidates it actually declares.
    """
    candidates_by_parent: dict[HaDeviceRegistryId, list[DiscoveredDevice]] = {}
    for device in devices:
        if device.via_device_id is not None:
            candidates_by_parent.setdefault(device.via_device_id, []).append(device)
    childless_by_id = {d.ha_device_registry_id: d for d in devices if d.via_device_id is None}

    confirmed_children_by_parent: dict[HaDeviceRegistryId, list[DiscoveredDevice]] = {}
    for parent_id, candidates in candidates_by_parent.items():
        parent = childless_by_id.get(parent_id)
        if parent is None:
            continue  # dangling via_device_id -- doesn't resolve to a real childless device
        parent_pattern = next(iter(candidate_patterns(parent, patterns)), None)
        if parent_pattern is None:
            continue
        confirmed = [
            c
            for c in candidates
            if c.model is not None
            and any(c.model.strip().casefold() == m.casefold() for m in parent_pattern.child_models)
        ]
        if confirmed:
            confirmed_children_by_parent[parent_id] = confirmed
    confirmed_child_ids = {
        c.ha_device_registry_id
        for children in confirmed_children_by_parent.values()
        for c in children
    }

    result = []
    for device in devices:
        if device.ha_device_registry_id in confirmed_child_ids:
            continue
        children = confirmed_children_by_parent.get(device.ha_device_registry_id)
        if not children:
            result.append(device)
            continue
        pooled_entities = device.entities + tuple(
            entity for child in children for entity in child.entities
        )
        result.append(
            replace(
                device,
                entities=pooled_entities,
                child_identifiers=device.child_identifiers.union(
                    *(child.identifiers for child in children)
                ),
            )
        )
    return tuple(result)


def first_non_blank(*candidates: str | None) -> str | None:
    """The first candidate with something in it, trimmed of leading and
    trailing whitespace like a name typed into the panel (issue #317). A name
    of only whitespace counts as missing: stored as an alias it would hit the
    schema's non-blank `CHECK`, which `create_discovered_co` reports as a
    duplicate, skipping the device with a misleading log."""
    return next((c.strip() for c in candidates if c is not None and c.strip()), None)


def _match_pattern(
    device: DiscoveredDevice, pattern: CoPattern, *, superseded_pattern_ids: tuple[str, ...]
) -> ProposedCo | PatternRejection:
    """Entity-shape check only — identity (manufacturer/model/hw_version)
    is already guaranteed by candidate_patterns, match_device's only
    caller of this function. Returns a `PatternRejection` when `on_off`
    does not resolve; `monitoring` and `all_on_off` are best-effort and
    never produce one. `superseded_pattern_ids` is passed through to the
    `ProposedCo`."""
    identity = _identity_of(device, pattern)
    on_off_matches = _role_matches_by_position(
        device.entities, pattern.on_off, pattern.socket_count, identity
    )
    if isinstance(on_off_matches, _Unresolved):
        return PatternRejection(pattern.pattern_id, f"on_off: {on_off_matches.reason}")

    monitoring_matches: list[DiscoveredEntity] | None = None
    if pattern.monitoring is not None:
        resolved = _role_matches_by_position(
            device.entities, pattern.monitoring, pattern.socket_count, identity
        )
        monitoring_matches = None if isinstance(resolved, _Unresolved) else resolved

    all_on_off_match: DiscoveredEntity | None = None
    if pattern.all_on_off is not None:
        matches = _entities_by_role(device.entities, pattern.all_on_off, identity)
        if len(matches) == 1:
            all_on_off_match = matches[0]

    sockets = tuple(
        ProposedCoSocket(
            position=i + 1,
            on_off_entity_registry_id=on_off_matches[i].id,
            monitoring_entity_registry_id=(
                monitoring_matches[i].id if monitoring_matches is not None else None
            ),
        )
        for i in range(pattern.socket_count)
    )

    return ProposedCo(
        ha_device_registry_id=device.ha_device_registry_id,
        alias=first_non_blank(device.name) or f"{device.manufacturer} {device.model}",
        kind=pattern.kind,
        all_on_off_entity_registry_id=(
            all_on_off_match.id if all_on_off_match is not None else None
        ),
        sockets=sockets,
        pattern_id=pattern.pattern_id,
        superseded_pattern_ids=superseded_pattern_ids,
        mac=device.mac,
    )


def match_device(
    device: DiscoveredDevice, patterns: tuple[CoPattern, ...]
) -> ProposedCo | NearMiss | None:
    """Match one discovered device against known patterns (docs/LLD.md §4).

    Manufacturer/model must match exactly (case-insensitive) for a pattern
    to be considered at all; a device matching none is unknown and returns
    None. Beyond that, only the CO Socket *shape* is a hard requirement
    -- `on_off` must resolve to exactly `socket_count` entities, since
    that's what defines how many CO Sockets this device has at all.
    `monitoring`/`all_on_off` are best-effort: attached if they resolve
    cleanly, silently omitted otherwise, never a reason to reject the
    device. Discovery's job is mapping a device to its CO/CO Sockets and
    recording the three named roles, not guaranteeing every entity the
    device exposes is semantically labeled. Deterministic: same input
    always produces the same output, no HA calls, no randomness. Tries
    candidate_patterns' most-specific-first ordering and returns the
    first one that fully matches -- a candidate that outranks the
    eventual winner but fails its own shape check is skipped, not a
    reason to reject the device. The skip is reported: the winning
    `ProposedCo` lists those candidates in `superseded_pattern_ids`.

    When no pattern produces a CO but at least one matched on
    manufacturer/model, returns a `NearMiss` listing why each pattern
    failed -- a pattern excluded by hw_version, or one whose `on_off`
    shape did not resolve -- so the caller can report it instead of
    failing silently (issue #353). The same pass decides the match and
    records the reasons, so the two cannot disagree.
    """
    model_matched = [p for p in patterns if _pattern_model_matches(device, p)]
    if not model_matched:
        return None
    candidates = candidate_patterns(device, patterns)
    hw_exclusions = [
        PatternRejection(
            p.pattern_id, f"hw_version {device.hw_version!r} not allowed by this pattern"
        )
        for p in model_matched
        if p not in candidates
    ]
    shape_rejections: list[PatternRejection] = []
    for pattern in candidates:
        result = _match_pattern(
            device,
            pattern,
            superseded_pattern_ids=tuple(r.pattern_id for r in shape_rejections),
        )
        if isinstance(result, ProposedCo):
            return result
        shape_rejections.append(result)
    return NearMiss(
        ha_device_registry_id=device.ha_device_registry_id,
        name=device.name,
        manufacturer=device.manufacturer,
        model=device.model,
        rejections=(*hw_exclusions, *shape_rejections),
    )


NEAR_MISS_ISSUE_PREFIX = "near_miss_"


def near_miss_issue_id(device_id: HaDeviceRegistryId) -> str:
    """The Repairs issue id for a near-miss device (issue #356). The
    `near_miss_` prefix gives these issues their own namespace, so pruning
    stale ones (`stale_near_miss_issue_ids`) can never delete any other
    `outlet_binder` issue added later."""
    return f"{NEAR_MISS_ISSUE_PREFIX}{device_id}"


def near_miss_placeholders(near_miss: NearMiss) -> dict[str, str]:
    """Translation placeholders for the near_miss Repairs issue (issue
    #356). Falls back to a placeholder string for a `None` name/
    manufacturer/model -- `translation_placeholders` values must be `str`,
    and HA renders a raw `{name}` with no error if a key is ever missing
    (see the guard in tests/test_near_miss_placeholder_guard.py)."""
    return {
        "device": near_miss.name or "(unnamed)",
        "manufacturer": near_miss.manufacturer or "unknown",
        "model": near_miss.model or "unknown",
        "reasons": "\n".join(f"- {r.pattern_id}: {r.reason}" for r in near_miss.rejections),
    }


def stale_near_miss_issue_ids(
    current: tuple[NearMiss, ...], *, existing: frozenset[str]
) -> frozenset[str]:
    """Every `near_miss_`-prefixed Repairs issue id in `existing` that this
    pass's `current` near-misses no longer justify (issue #356) -- covering a device that now
    matches, one that got a CO, and one removed from HA in one prune,
    rather than three separate paths. `existing` need not already be
    filtered to the prefix: an id outside it is never returned, so this
    can't be used to prune an unrelated `outlet_binder` issue."""
    current_ids = {near_miss_issue_id(nm.ha_device_registry_id) for nm in current}
    return frozenset(
        issue_id
        for issue_id in existing
        if issue_id.startswith(NEAR_MISS_ISSUE_PREFIX) and issue_id not in current_ids
    )


def _mac_suffix(mac: str) -> str:
    """The last three octets, upper-case, no separators -- e.g.
    `"EC:B9:31:3C:FD:C8"` -> `"3CFDC8"`. The first three octets are the
    OUI, shared per-manufacturer, so they disambiguate nothing between two
    units of the same model."""
    return "".join(mac.split(":")[-3:])


def _disambiguate_one(proposal: ProposedCo, clashes: Callable[[str], bool]) -> ProposedCo:
    """Rename one colliding proposal against everything already claimed.

    MAC suffix first, if the device reported one -- real, stable, and
    already the user's own manual naming convention on real hardware.
    Falls back to the lowest free integer suffix otherwise (or in the
    practically-impossible case that the MAC suffix itself still
    collides).
    """
    if proposal.mac is not None:
        candidate = f"{proposal.alias} {_mac_suffix(proposal.mac)}"
        if not clashes(candidate):
            return replace(proposal, alias=candidate)
    n = 2
    while True:
        candidate = f"{proposal.alias} {n}"
        if not clashes(candidate):
            return replace(proposal, alias=candidate)
        n += 1


def disambiguate_aliases(
    proposals: tuple[ProposedCo, ...],
    *,
    taken: frozenset[str],
    taken_switch_ids: frozenset[str],
    switch_id_of: Callable[[str], str],
) -> tuple[ProposedCo, ...]:
    """Rename every proposal whose (normalised) alias is shared by another
    proposal in this same batch, or matches an existing CO's alias in
    `taken` (issue #185: two identical devices, e.g. two Tapo P304Ms,
    arrive from HA identically named).

    A proposal with a plug is also renamed when its switch's entity id
    clashes, in the batch or with `taken_switch_ids` (the existing COs
    with a plug). The slug ignores punctuation, so "Lamp" and "Lamp!" are
    different names with one entity id, and the second switch would
    otherwise register as `_2` and be reslugged on every sync.
    `switch_id_of` maps a CO alias to that entity id; the caller passes it
    in because the slug is HA's, and this module has no HA imports.

    Every member of a same-batch colliding group is renamed, not just the
    ones after the first -- e.g. two duplicate COs both end up suffixed
    (`Unnamed P304M 3CFDC8` / `Unnamed P304M D67052`), neither left as the
    ambiguous bare name. A proposal that only collides with an existing
    `taken` alias (not with anything else in this batch) is the one
    that's renamed either way, since the existing CO's alias is already
    committed.

    Ordered by `ha_device_registry_id` first -- HA's device registry
    iteration order isn't guaranteed, so without an explicit sort two
    identical devices discovered in the same pass could swap aliases
    between runs.
    """
    ordered = sorted(proposals, key=lambda p: p.ha_device_registry_id)
    normalized_taken = {normalize_name(alias) for alias in taken}
    switch_ids_taken = set(taken_switch_ids)

    name_counts = Counter(normalize_name(p.alias) for p in ordered)
    switch_counts = Counter(switch_id_of(p.alias) for p in ordered if p.kind.has_plug)

    def clashes(alias: str, *, has_plug: bool) -> bool:
        return normalize_name(alias) in normalized_taken or (
            has_plug and switch_id_of(alias) in switch_ids_taken
        )

    result = []
    for proposal in ordered:
        has_plug = proposal.kind.has_plug
        in_batch = name_counts[normalize_name(proposal.alias)] > 1 or (
            has_plug and switch_counts[switch_id_of(proposal.alias)] > 1
        )
        if in_batch or clashes(proposal.alias, has_plug=has_plug):
            proposal = _disambiguate_one(proposal, lambda alias: clashes(alias, has_plug=has_plug))
        normalized_taken.add(normalize_name(proposal.alias))
        if has_plug:
            switch_ids_taken.add(switch_id_of(proposal.alias))
        result.append(proposal)
    return tuple(result)
