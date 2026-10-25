"""Loads CO device patterns from
custom_components/outlet_binder/device_identification/device_patterns/ into domain/discovery.py's
CoPattern/EntityRoleMatch objects (docs/LLD.md §4's revision note).

Thin, HA-adjacent adapter -- file I/O and YAML parsing happen here,
deliberately kept out of domain/discovery.py to preserve that module's
"pure, dependency-free, testable without HA fixtures" property.

Patterns live in an integration_domain/Manufacturer/Model/HwVersion-SwVersion.yaml
directory tree rather than a database table: they're load-once, read-only reference
data shipped with the integration, not per-installation operational
state -- a file per pattern is simpler, git/PR-friendly, and makes the
pattern set genuinely shareable (adding a device is "add a YAML file",
no Python knowledge or redeploy needed), matching how Zigbee2MQTT/HA's
own zigbee quirks work. The directory structure itself carries
integration_domain/manufacturer/model/hw_version/sw_version, so a pattern
file's content only needs the matching-role rules, not repeated identity
fields.

The top-level directory is the HA integration's domain (e.g. `tplink`), the
next level the manufacturer string that integration reports -- see
custom_components/outlet_binder/device_identification/device_patterns/README.md
and CoPattern's docstring in domain/discovery.py for the full rationale
(issue #383). The top-level folder must look like a domain (`[a-z0-9_]+`),
which rejects a `TP-Link/` folder at that level.

The filename is either the bare sentinel `any` (no constraint on either
axis) or `HwVersion-SwVersion`, each half one of `any` (no constraint on
that axis), a floor like `1.5` (that version and everything after, until
a higher pin supersedes it), or an exact pin `=2.0` (a backstop for a
case the floor ladder genuinely can't express -- see CoPattern's
docstring in domain/discovery.py). `sw_version` is parsed
and stored but not currently enforced anywhere -- see CoPattern's
docstring in domain/discovery.py for why.

Pattern filename tokens are strict, unlike a device's own reported
version string (domain/versions.py's `parse_version`, which is lenient
-- anything unrecognisable becomes "version zero" and still matches the
unconstrained base pattern). A pattern is authored content in this repo,
so a malformed token (not `any`, not a bare `digits(.digits)*` floor, not
an `=`-prefixed exact pin of the same shape) is a hard error -- logged
and the whole pattern file skipped, the same
as any other malformed pattern -- rather than silently degrading to
"matches everything".

A pattern file's content is split into two top-level blocks, both required,
`device:` and `sockets:` -- see
custom_components/outlet_binder/device_identification/device_patterns/README.md
for the exact schema.
`device:` holds whole-device concerns (`kind`, required, and `all_on_off`,
optional); `sockets:` holds everything about deriving individual CO Sockets
(`count`, `child_models`, `on_off`, `monitoring`). `kind` says whether the
device has a plug of its own, and is never defaulted.

A pattern's `integration_domain` is taken from its path alone (`parts[0]`),
never from the file's content: `additionalProperties: false` in the schema
rejects a stale `device.integration_domain` key, so the path is the one
place it can be written. It is a hard match condition against the device's
config entry domain -- see CoPattern's docstring for the full rationale.

Every pattern file is checked against a JSON Schema --
`device_patterns_schema.yaml` (a sibling of this module and of
device_patterns/, deliberately outside it), also published for
editors via a yaml-language-server modeline -- before anything else:
required keys, types, unknown keys, and `identified_by.device`'s
`self`/`child` vocabulary all fail there. A file that fails
the schema is logged and skipped, not a hard failure -- one bad
community-contributed file shouldn't break every other pattern.

The schema can't express the rules that span fields, so those still run
here, after it passes, and are likewise skipped on failure: a role's
`unique_id_suffixes` whose length doesn't match `sockets.count`, or that
contains a duplicate; an `on_off`/`monitoring` pair that disagree on
whether they use `unique_id_suffixes` at all (this would let
`_match_pattern` in domain/discovery.py pair the two roles' entities by
index while index i means a different physical socket in each); an `all_on_off`
role that declares `unique_id_suffixes` at all, since `_entities_by_role` never
reads that field there and would
silently ignore it; and a role's `identified_by` whose rule
could never match or would not mean what it says given *this* pattern's
own child_models -- no `{unique_id}` in the template,
`{parent_identifier}` under `device: self`, or `device: child` with no
`sockets.child_models`.

`monitoring` (like `all_on_off`) is optional and has no default: a
pattern declares it explicitly whenever the device has a monitoring-
capable entity worth pointing at, deliberately not silently filled in
here -- a pattern file should fully explain its own matching behavior on
its own, without a reader needing to know about a hidden Python-side
default.

History: docs/HISTORY-INDEX.md
"""

import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import load_yaml_dict
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match
from jsonschema.validators import extend

from ..domain.discovery import (
    PARENT_IDENTIFIER_PLACEHOLDER,
    UNIQUE_ID_PLACEHOLDER,
    CoPattern,
    EntityRoleMatch,
    IdentifiedBy,
    PatternKind,
)
from ..domain.versions import ANY_VERSION, VersionConstraint, parse_version

_LOGGER = logging.getLogger(__name__)

PATTERNS_DIR = Path(__file__).parent / "device_patterns"

# Sits next to device_patterns/, not inside it -- load_patterns reads every
# *.yaml under device_patterns/ via rglob below, and a schema file there
# would be read as a (wrongly placed) pattern. Keeping it out entirely
# means no exclusion is needed at all.
PATTERN_SCHEMA_PATH = Path(__file__).parent / "device_patterns_schema.yaml"

# HA integration domains are lowercase letters, digits and underscores.
# The pattern tree's top-level folder must look like one, so a manufacturer
# folder left at the old depth (`TP-Link/`) is a path error, not silently
# read as an integration nobody has.
_DOMAIN_RE = re.compile(r"^[a-z0-9_]+$")

# Filename stem token meaning "no constraint on this axis -- matches any",
# used for both the hw_version and sw_version halves of a
# HwVersion-SwVersion.yaml filename.
_ANY_VERSION = "any"

# Grammar for a non-"any" version token: a floor ("1.5") or an exact pin
# ("=2.0"). Pattern filenames are strict -- see this module's docstring.
_VERSION_TOKEN_RE = re.compile(r"^=?\d+(?:\.\d+)*$")


def _parse_version_token(token: str) -> VersionConstraint:
    """Parse one half of a HwVersion-SwVersion filename into a
    VersionConstraint -- `any` (ANY_VERSION), a floor (`1.5`), or an
    exact pin (`=2.0`). Raises ValueError for anything else, caught by
    load_patterns' existing malformed-pattern handling."""
    if token == _ANY_VERSION:
        return ANY_VERSION
    if not _VERSION_TOKEN_RE.match(token):
        raise ValueError(
            f"invalid version token {token!r} -- expected 'any', a floor like '1.5', or an"
            " exact pin like '=2.0'"
        )
    exact = token.startswith("=")
    return VersionConstraint(version=parse_version(token[1:] if exact else token), exact=exact)


_KNOWN_PLACEHOLDERS = (UNIQUE_ID_PLACEHOLDER, PARENT_IDENTIFIER_PLACEHOLDER)
_PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}")


def _is_strict_int(_checker: object, instance: object) -> bool:
    """JSON Schema's `integer` type accepts any number with a zero
    fractional part, so `sockets.count: 3.0` validates as `integer` under
    the draft's own default type checker. That leaves `socket_count` a Python
    `float`, which only fails later at `range(pattern.socket_count)`
    (domain/discovery.py) during matching, not at load -- the exact gap
    issue #339 was filed against. Redefining the type check to strict
    `int` (excluding `bool`, itself an `int` subclass) closes it at the
    schema layer, where the validator command benefits from the
    same fix rather than needing a parallel Python-side check."""
    return isinstance(instance, int) and not isinstance(instance, bool)


_StrictIntValidator = extend(
    Draft202012Validator,
    type_checker=Draft202012Validator.TYPE_CHECKER.redefine("integer", _is_strict_int),
)


@lru_cache(maxsize=1)
def _pattern_validator() -> Draft202012Validator:
    """Loaded lazily and cached, not at import time -- load_patterns runs
    in an executor (blocking file I/O), never on the event loop."""
    return _StrictIntValidator(load_yaml_dict(PATTERN_SCHEMA_PATH))


def _raise_if_invalid(validator: Draft202012Validator, raw: object) -> None:
    """Raises ValueError naming the most specific failure (jsonschema's
    own `best_match`, for a deterministic message) if `raw` doesn't
    satisfy `validator`'s schema -- caught by the caller's existing
    malformed-pattern handling, the same as any other structural
    mistake."""
    errors = list(validator.iter_errors(raw))
    if not errors:
        return
    error = best_match(errors)
    raise ValueError(f"{error.json_path}: {error.message}")


def _parse_identified_by(raw: dict) -> IdentifiedBy:
    """Shape and vocabulary (unknown keys, the `device` enum, `identifier`
    being a string) are enforced by the pattern schema before this runs.
    What the rule means for the *pattern* it sits in (child models) is
    checked separately by `_validate_identified_by`, which needs that
    context."""
    return IdentifiedBy(device=raw["device"], identifier=raw["identifier"])


def _parse_role(raw: dict) -> EntityRoleMatch:
    identified_by_raw = raw.get("identified_by")
    return EntityRoleMatch(
        domain=raw["domain"],
        device_class=raw.get("device_class"),
        exclude_unique_id_suffixes=tuple(raw.get("exclude_unique_id_suffixes", ())),
        unique_id_suffixes=tuple(raw.get("unique_id_suffixes", ())),
        identified_by=(
            _parse_identified_by(identified_by_raw) if identified_by_raw is not None else None
        ),
    )


def _validate_identified_by(
    role_name: str,
    role: EntityRoleMatch,
    *,
    child_models: tuple[str, ...],
) -> None:
    """Rejects an `identified_by` that could never match, or that would
    silently mean something else than it says. Each case would otherwise
    surface only at discovery time, as a device that quietly gets no CO
    -- the failure this option exists to end (issue #341)."""
    rule = role.identified_by
    if rule is None:
        return
    if rule.device == "child" and not child_models:
        raise ValueError(
            f"{role_name} role declares identified_by with device: child but the pattern has no"
            " sockets.child_models -- no child device is ever folded in to compare against"
        )
    if UNIQUE_ID_PLACEHOLDER not in rule.identifier:
        raise ValueError(
            f"{role_name} role's identified_by.identifier has no {UNIQUE_ID_PLACEHOLDER} -- it"
            " would not depend on the entity, so it could not tell entities apart"
        )
    if rule.device == "self" and PARENT_IDENTIFIER_PLACEHOLDER in rule.identifier:
        raise ValueError(
            f"{role_name} role uses {PARENT_IDENTIFIER_PLACEHOLDER} with device: self -- the"
            " parent identifier is only defined when comparing against a child"
        )
    placeholders = _PLACEHOLDER_RE.findall(rule.identifier)
    unknown = sorted({p for p in placeholders if p not in _KNOWN_PLACEHOLDERS})
    if unknown:
        raise ValueError(
            f"{role_name} role's identified_by.identifier has unknown placeholder(s) {unknown};"
            f" known: {list(_KNOWN_PLACEHOLDERS)}"
        )
    remainder = _PLACEHOLDER_RE.sub("", rule.identifier)
    if "{" in remainder or "}" in remainder:
        raise ValueError(
            f"{role_name} role's identified_by.identifier has an unmatched brace:"
            f" {rule.identifier!r}"
        )


def _warn_if_suffix_fields_conflict(role_name: str, raw: dict) -> list[str]:
    if raw.get("unique_id_suffixes") and raw.get("exclude_unique_id_suffixes"):
        return [
            f"{role_name} role sets unique_id_suffixes together with"
            " exclude_unique_id_suffixes -- these are mutually exclusive"
            " (custom_components/outlet_binder/device_identification/device_patterns/README.md);"
            " exclude_unique_id_suffixes is silently ignored when unique_id_suffixes is set."
        ]
    return []


def _validate_role_suffix_count(role_name: str, role: EntityRoleMatch, socket_count: int) -> None:
    """A role declaring unique_id_suffixes must declare exactly one per
    socket, and each one distinct -- _role_matches_by_position
    (domain/discovery.py) resolves each declared suffix independently, so
    a repeated suffix silently resolves two different socket positions to
    the *same* entity (one position gets a phantom duplicate, another
    gets none) rather than failing to match at all -- a mismatched count
    at least fails closed; a duplicate wouldn't, without this check.
    Caught here at load time instead, per this module's "logged and
    skipped, not a hard failure" convention (see the sockets/on_off
    presence checks in the caller below)."""
    if not role.unique_id_suffixes:
        return
    if len(role.unique_id_suffixes) != socket_count:
        raise ValueError(
            f"{role_name} role declares {len(role.unique_id_suffixes)} unique_id_suffixes but"
            f" sockets.count is {socket_count} -- each socket position needs exactly one"
            " declared suffix, in order"
        )
    if len(set(role.unique_id_suffixes)) != len(role.unique_id_suffixes):
        raise ValueError(
            f"{role_name} role's unique_id_suffixes contains a duplicate -- each socket"
            " position needs its own distinct suffix, or _role_matches_by_position"
            " (domain/discovery.py) would silently resolve two positions to the same entity"
        )


def _validate_all_on_off_has_no_suffixes(all_on_off: EntityRoleMatch | None) -> None:
    """all_on_off shares EntityRoleMatch with on_off/monitoring, so
    nothing in the type stops a pattern author declaring
    unique_id_suffixes on it too -- but all_on_off is resolved through
    _entities_by_role (domain/discovery.py), which only ever reads
    domain/device_class/exclude_unique_id_suffixes and never consults
    unique_id_suffixes at all. Silently doing nothing would mislead a
    pattern author who followed the on_off/monitoring convention into
    believing suffix-based matching applied here too. Rejected at load
    time instead, matching this module's "logged and skipped" convention
    for every other structural mistake."""
    if all_on_off is not None and all_on_off.unique_id_suffixes:
        raise ValueError(
            "all_on_off role declares unique_id_suffixes, but all_on_off is resolved by"
            " _entities_by_role (domain/discovery.py), which never reads that field -- it"
            " would be silently ignored. all_on_off must resolve to exactly one entity via"
            " domain/device_class/exclude_unique_id_suffixes instead"
        )


def _validate_positional_ordering_agrees(
    on_off: EntityRoleMatch, monitoring: EntityRoleMatch | None
) -> None:
    """on_off and monitoring must agree on *whether* they use
    unique_id_suffixes at all (issue #235): _match_pattern resolves each
    socket-level role independently, then pairs the two resulting lists
    purely by index -- if one role is suffix-ordered and the other falls
    back to sorting by entity_id, index i is only coincidentally the same
    physical socket in both. Suffixing on_off alone would break exactly
    that pairing.

    Deliberately does NOT require the two roles' suffix tuples to be
    *equal* -- only that both declare one, one entry per socket (checked
    separately by _validate_role_suffix_count). A role's own unique_id
    scheme can differ from the other's -- see device_patterns/tplink/TP-Link/P304M/any.yaml:
    on_off's bare "00" vs monitoring's "00_current_power_w", since HA's
    tplink integration appends a feature-key suffix to every non-primary
    entity's unique_id but not to the primary switch. The pattern author
    still lists both in the same declared order, asserting the
    correspondence themselves and verified against real hardware -- the
    same trust this module already places in a single role's own suffix
    order. This only catches the structural half of the mistake (one
    role committed to a positional declaration, the other didn't); it
    can't prove the two declared orders actually agree."""
    if monitoring is None:
        return
    if bool(on_off.unique_id_suffixes) != bool(monitoring.unique_id_suffixes):
        raise ValueError(
            "on_off and monitoring must agree on positional-ordering strategy: either both"
            " declare unique_id_suffixes (one entry per socket, in position order) or neither"
            " does -- otherwise _match_pattern's index-based pairing between the two roles"
            " isn't guaranteed to mean the same physical socket in both (issue #235)"
        )


def _compile_default_name(raw: str | None) -> re.Pattern[str] | None:
    """`sockets.default_name` as a compiled regex. The schema only knows it
    is a string, so a pattern that does not compile is caught here and the
    file skipped with the reason, like any other malformed pattern."""
    if raw is None:
        return None
    try:
        return re.compile(raw)
    except re.error as err:
        raise ValueError(f"sockets.default_name is not a valid regular expression: {err}") from err


def _parse_pattern(
    raw: dict,
    *,
    integration_domain: str,
    manufacturer: str,
    model: str,
    hw_version: VersionConstraint,
    sw_version: VersionConstraint,
    pattern_id: str,
    warnings: list[str],
) -> CoPattern:
    device_raw = raw["device"]
    sockets_raw = raw["sockets"]

    on_off_raw = sockets_raw["on_off"]
    monitoring_raw = sockets_raw.get("monitoring")
    all_on_off_raw = device_raw.get("all_on_off")

    warnings.extend(_warn_if_suffix_fields_conflict("on_off", on_off_raw))
    if monitoring_raw is not None:
        warnings.extend(_warn_if_suffix_fields_conflict("monitoring", monitoring_raw))
    if all_on_off_raw is not None:
        warnings.extend(_warn_if_suffix_fields_conflict("all_on_off", all_on_off_raw))

    on_off = _parse_role(on_off_raw)
    monitoring = _parse_role(monitoring_raw) if monitoring_raw is not None else None
    all_on_off = _parse_role(all_on_off_raw) if all_on_off_raw is not None else None

    socket_count = sockets_raw["count"]
    _validate_role_suffix_count("on_off", on_off, socket_count)
    if monitoring is not None:
        _validate_role_suffix_count("monitoring", monitoring, socket_count)
    _validate_positional_ordering_agrees(on_off, monitoring)
    _validate_all_on_off_has_no_suffixes(all_on_off)

    child_models = tuple(sockets_raw.get("child_models", ()))
    default_socket_name = _compile_default_name(sockets_raw.get("default_name"))
    for role_name, role in (
        ("on_off", on_off),
        ("monitoring", monitoring),
        ("all_on_off", all_on_off),
    ):
        if role is not None:
            _validate_identified_by(role_name, role, child_models=child_models)

    return CoPattern(
        pattern_id=pattern_id,
        integration_domain=integration_domain,
        manufacturer=manufacturer,
        model=model,
        kind=PatternKind(device_raw["kind"]),
        socket_count=socket_count,
        on_off=on_off,
        monitoring=monitoring,
        all_on_off=all_on_off,
        hw_version=hw_version,
        sw_version=sw_version,
        child_models=child_models,
        default_socket_name=default_socket_name,
    )


@dataclass(frozen=True)
class LoadResult:
    """The outcome of parsing one device pattern file. Exactly one of
    `pattern`/`skip_reason` is set. `warnings` are non-fatal issues the
    file still loaded despite (e.g. the suffix-fields-conflict
    warning) -- kept structured here, rather than logged directly, so
    the validator command (#373) can print them without depending on
    logging."""

    pattern: CoPattern | None
    skip_reason: str | None
    warnings: tuple[str, ...] = ()
    is_path_error: bool = False
    """True when skip_reason describes the file's path or filename itself
    (wrong directory depth, a malformed HwVersion-SwVersion token shape)
    rather than its YAML content. load_patterns logs these two cases with
    different prefixes ("Skipping device pattern" vs "Skipping malformed
    device pattern"), a distinction older than this dataclass that
    existing tests assert on directly."""


def _load_one_pattern_file(
    path: Path,
    *,
    integration_domain: str,
    manufacturer: str,
    model: str,
    pattern_id: str,
    hw_token: str,
    sw_token: str,
) -> LoadResult:
    """Parses one device pattern file already known to sit at the right
    path depth. Schema-validates the file exactly as written, so an editor
    checking the file in place sees the same result the loader does, with
    one known exception: _is_strict_int rejects a whole-number float like
    `count: 3.0`, which a standard schema-aware editor -- following the
    JSON Schema spec's own "any zero-fractional-part number is an integer"
    rule -- likely still accepts (issue #339) -- then runs this module's
    own cross-field checks. Never raises: HomeAssistantError, KeyError and
    ValueError are all reported back as `skip_reason` for the caller to
    log, matching this module's "logged and skipped" convention."""
    warnings: list[str] = []
    try:
        raw = load_yaml_dict(path)
        _raise_if_invalid(_pattern_validator(), raw)
        pattern = _parse_pattern(
            raw,
            integration_domain=integration_domain,
            manufacturer=manufacturer,
            model=model,
            hw_version=_parse_version_token(hw_token),
            sw_version=_parse_version_token(sw_token),
            pattern_id=pattern_id,
            warnings=warnings,
        )
    except (HomeAssistantError, KeyError, ValueError) as err:
        return LoadResult(pattern=None, skip_reason=str(err), warnings=tuple(warnings))
    return LoadResult(pattern=pattern, skip_reason=None, warnings=tuple(warnings))


def process_pattern_path(path: Path, directory: Path) -> tuple[str, LoadResult]:
    """Parses one candidate pattern file at `path` (relative to
    `directory`, whose immediate children are integration-domain folders),
    by the same rules `load_patterns` applies to every file it finds --
    shared so a caller validating just one file (the validator command's
    single-file mode, #373) sees exactly what `load_patterns` would
    decide for it, never a copy of its rules."""
    parts = path.relative_to(directory).parts
    pattern_id = str(path.relative_to(directory).with_suffix(""))
    if len(parts) != 4:
        return pattern_id, LoadResult(
            pattern=None,
            skip_reason=(
                "expected integration_domain/Manufacturer/Model/HwVersion-SwVersion.yaml"
                f" (4 levels deep), found {len(parts)}"
            ),
            is_path_error=True,
        )
    integration_domain, manufacturer, model, _filename = parts
    if not _DOMAIN_RE.match(integration_domain):
        return pattern_id, LoadResult(
            pattern=None,
            skip_reason=(
                f"top-level folder {integration_domain!r} is not an HA integration domain"
                " (lowercase letters, digits and underscores)"
            ),
            is_path_error=True,
        )
    if path.stem == _ANY_VERSION:
        # Shorthand for "no constraint on either axis".
        hw_token = sw_token = _ANY_VERSION
    else:
        version_tokens = path.stem.split("-", 1)
        if len(version_tokens) != 2:
            return pattern_id, LoadResult(
                pattern=None,
                skip_reason=(
                    f"expected a HwVersion-SwVersion filename (e.g. 1.0-any), found {path.stem!r}"
                ),
                is_path_error=True,
            )
        hw_token, sw_token = version_tokens
    return pattern_id, _load_one_pattern_file(
        path,
        integration_domain=integration_domain,
        manufacturer=manufacturer,
        model=model,
        pattern_id=pattern_id,
        hw_token=hw_token,
        sw_token=sw_token,
    )


def iter_pattern_files(directory: Path) -> Iterator[tuple[str, LoadResult]]:
    """Yields (pattern_id, LoadResult) for every candidate pattern file
    under `directory`, in the same order and by the same rules
    `load_patterns` uses -- the shared walk both it and the validator
    command's directory mode (#373) are built on."""
    for path in sorted(directory.rglob("*.yaml")):
        yield process_pattern_path(path, directory)


def load_patterns(directory: Path = PATTERNS_DIR) -> tuple[CoPattern, ...]:
    """Load every integration_domain/manufacturer/model/hw_version-sw_version.yaml file under
    `directory` into CoPattern objects. Blocking file I/O -- caller must
    run this in an executor, not on the event loop.
    """
    patterns = []
    for pattern_id, result in iter_pattern_files(directory):
        for warning in result.warnings:
            _LOGGER.warning("Pattern %s: %s", pattern_id, warning)
        if result.skip_reason is not None:
            prefix = (
                "Skipping device pattern"
                if result.is_path_error
                else ("Skipping malformed device pattern")
            )
            _LOGGER.warning("%s %s: %s", prefix, pattern_id, result.skip_reason)
            continue
        assert result.pattern is not None
        patterns.append(result.pattern)
    return tuple(patterns)
