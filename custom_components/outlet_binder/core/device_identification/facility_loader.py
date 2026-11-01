"""Loads OB's facility vocabulary and each integration's vocabulary and
defaults (#681).

    device_identification/ob_facility_vocabulary.yaml        OB's facility vocabulary
    device_identification/device_patterns/<integration>/vocabulary_and_defaults.yaml
                                                             one integration's ids

Both are checked against a JSON Schema first (`ob_facility_vocabulary_schema.yaml`,
`vocabulary_and_defaults_schema.yaml`, both in `schemas/`), then against the
rules a schema cannot express: every `socket` facility is in OB's facility vocabulary
and in its own domain, `ob_on_off` is never mapped (it is the pattern's role,
not a file entry), and no facility is mapped twice. A model's own rules
(`device.facilities`, `sockets.facilities`) are checked by the same rules.
A file that fails raises `ValueError` naming why, rather than loading
partly: a file that quietly lost entries would rename an Appliance's
entities, and an automation would target the wrong one.

Blocking file I/O: callers run this in an executor, like pattern_loader.py.
This module does not import pattern_loader.py, which imports it.
"""

import re
from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

import yaml
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import load_yaml_dict
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from ..domain.facility_rules import (
    ON_OFF,
    FacilityRule,
    IntegrationVocabulary,
    StandardFacility,
)
from ..domain.identifiers import FacilityName, VendorFacilityKey

# The YAML files that are not patterns: OB's facility vocabulary and the schemas.
SCHEMAS_DIR = Path(__file__).parent / "schemas"
OB_FACILITY_VOCABULARY_PATH = Path(__file__).parent / "ob_facility_vocabulary.yaml"
OB_FACILITY_VOCABULARY_SCHEMA_PATH = SCHEMAS_DIR / "ob_facility_vocabulary_schema.yaml"
VOCABULARY_SCHEMA_PATH = SCHEMAS_DIR / "vocabulary_and_defaults_schema.yaml"

# Sits directly in an integration's folder, beside the Manufacturer folders.
VOCABULARY_FILE_NAME = "vocabulary_and_defaults.yaml"


# HA integration domains are lowercase letters, digits and underscores.
# The pattern tree's top-level folder must look like one, so a manufacturer
# folder left at the old depth (`TP-Link/`) is a path error, not silently
# read as an integration nobody has.
_DOMAIN_RE = re.compile(r"^[a-z0-9_]+$")


def is_integration_domain(name: str) -> bool:
    """Whether a folder name looks like an HA integration domain."""
    return _DOMAIN_RE.match(name) is not None


def is_vocabulary_file(path: Path, patterns_dir: Path) -> bool:
    """Whether `path` is an integration's vocabulary-and-defaults file rather
    than a device pattern. Only `<integration domain>/vocabulary_and_defaults.yaml`
    counts, so a model folder cannot hide a pattern by naming it that, and a
    misplaced `TP-Link/vocabulary_and_defaults.yaml` is not quietly set aside as
    one: both stay pattern files and fail the pattern loader's own path check."""
    parts = path.relative_to(patterns_dir).parts
    return path.name == VOCABULARY_FILE_NAME and len(parts) == 2 and is_integration_domain(parts[0])


def vocabulary_paths(directory: Path) -> list[Path]:
    """Every integration vocabulary file under `directory`, in load order. The
    one definition, beside `pattern_paths` for the pattern files."""
    return [
        path for path in sorted(directory.rglob("*.yaml")) if is_vocabulary_file(path, directory)
    ]


def refuse_repeated_keys(path: Path) -> None:
    """Raises ValueError if any mapping in `path` repeats a key. HA's YAML
    loader only logs a warning and keeps the last, so a repeated id would
    quietly replace the first one's default and rename an Appliance's
    entities. Every file that holds facility rules is read through this: the
    facility vocabulary, the integrations' vocabulary files and the patterns."""
    try:
        root = yaml.compose(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as err:
        raise ValueError(f"{path}: {err}") from err
    pending = [root] if root is not None else []
    # An alias makes the node graph shared, even cyclic: each node is read once.
    visited: set[int] = set()
    while pending:
        node = pending.pop()
        if id(node) in visited:
            continue
        visited.add(id(node))
        if isinstance(node, yaml.MappingNode):
            seen: set[object] = set()
            for key, value in node.value:
                if isinstance(key, yaml.ScalarNode):
                    if key.value in seen:
                        raise ValueError(
                            f"{path}: line {key.start_mark.line + 1}: {key.value!r} appears twice"
                            " in one mapping"
                        )
                    seen.add(key.value)
                pending.append(value)
        elif isinstance(node, yaml.SequenceNode):
            pending.extend(node.value)


def _read_checked(path: Path, schema_path: Path) -> dict:
    refuse_repeated_keys(path)
    try:
        raw = load_yaml_dict(path)
    except HomeAssistantError as err:
        raise ValueError(f"{path}: {err}") from err
    validator = Draft202012Validator(load_yaml_dict(schema_path))
    errors = list(validator.iter_errors(raw))
    if errors:
        error = best_match(errors)
        raise ValueError(f"{path}: {error.json_path}: {error.message}")
    return raw


def read_ob_facility_vocabulary(path: Path) -> Mapping[FacilityName, StandardFacility]:
    """OB's facility vocabulary in `path`. Raises ValueError if the file is
    malformed, names one facility under two domains (a mapping names a
    facility, not a facility and a domain) or does not name `ob_on_off`, which
    the resolver looks up for every socket."""
    raw = _read_checked(path, OB_FACILITY_VOCABULARY_SCHEMA_PATH)["facilities"]
    standard: dict[FacilityName, StandardFacility] = {}
    endings: dict[tuple[str, str], str] = {}
    for domain, group in raw.items():
        for name, entry in group.items():
            if name in standard:
                raise ValueError(
                    f"{path}: {name!r} is listed under both {standard[name].domain!r} and"
                    f" {domain!r}"
                )
            ending = (domain, entry["entity_id_name"])
            if ending in endings:
                raise ValueError(
                    f"{path}: {name!r} and {endings[ending]!r} both give {domain} entity ids"
                    f" ending {entry['entity_id_name']!r}"
                )
            endings[ending] = name
            standard[FacilityName(name)] = StandardFacility(
                domain=domain,
                entity_id_name=entry["entity_id_name"],
                display_name=entry["display_name"],
            )
    if ON_OFF not in standard:
        raise ValueError(
            f"{path}: OB's facility vocabulary must name {ON_OFF!r}, "
            "which the pattern's on/off role uses"
        )
    return MappingProxyType(standard)


@lru_cache(maxsize=1)
def ob_facility_vocabulary() -> Mapping[FacilityName, StandardFacility]:
    """OB's facility vocabulary. Cached: the file ships with OB and does not
    change while HA runs."""
    return read_ob_facility_vocabulary(OB_FACILITY_VOCABULARY_PATH)


def parse_facility_rules(
    raw: Mapping[str, Mapping[str, Iterable[Mapping]]],
) -> tuple[FacilityRule, ...]:
    """Rules from a `facilities` mapping (`host` and `socket`, each HA domain
    to its entries) already checked against the schema (here, or by the pattern
    schema's own copy of the entries). The domain is the group an entry is
    listed under, and a `host` entry is `host_only` by being in that section."""
    return tuple(
        FacilityRule(
            domain=domain,
            key=VendorFacilityKey(entry["integration_name"]),
            facility_name=FacilityName(entry["facility_name"]) if section == "socket" else None,
            host_only=section == "host",
        )
        for section, groups in raw.items()
        for domain, entries in groups.items()
        for entry in entries
    )


def parse_vocabulary(raw: Mapping[str, Mapping[str, object]]) -> IntegrationVocabulary:
    """The vocabulary in a `vocabulary:` mapping already checked against the
    schema: each id to its default (nothing, `device` or `socket: facility`).
    `device` is `host_only`, by being a CO-level id."""
    ids: set[tuple[str, VendorFacilityKey]] = set()
    defaults: list[FacilityRule] = []
    for domain, entries in raw.items():
        for name, default in entries.items():
            key = VendorFacilityKey(name)
            ids.add((domain, key))
            if default is None:
                continue
            if default == "device":
                defaults.append(FacilityRule(domain=domain, key=key, host_only=True))
            else:
                assert isinstance(default, Mapping)
                defaults.append(
                    FacilityRule(
                        domain=domain, key=key, facility_name=FacilityName(default["socket"])
                    )
                )
    return IntegrationVocabulary(ids=frozenset(ids), defaults=tuple(defaults))


def check_rules(
    rules: Iterable[FacilityRule], standard: Mapping[FacilityName, StandardFacility]
) -> None:
    """Raises ValueError for a rule set that would mis-name an entity."""
    seen: set[tuple[str, VendorFacilityKey]] = set()
    mapped: dict[FacilityName, str] = {}
    for rule in rules:
        where = f"{rule.domain}.{rule.key}"
        if (rule.domain, rule.key) in seen:
            raise ValueError(f"{where} is listed more than once")
        seen.add((rule.domain, rule.key))
        if rule.facility_name is None:
            continue
        if rule.facility_name == ON_OFF:
            raise ValueError(
                f"{where} maps to {ON_OFF!r}, which is the pattern's on/off role and"
                " never a file entry"
            )
        if rule.facility_name not in standard:
            raise ValueError(
                f"{where} maps to {rule.facility_name!r}, which is not in OB's facility vocabulary"
            )
        facility_domain = standard[rule.facility_name].domain
        if rule.domain != facility_domain:
            raise ValueError(
                f"{where} maps to {rule.facility_name!r}, which is a {facility_domain}:"
                " one facility has one domain, or its entity id would change with the socket"
            )
        if rule.facility_name in mapped:
            raise ValueError(
                f"{where} maps to {rule.facility_name!r}, which {mapped[rule.facility_name]}"
                " already maps to: two entities for one facility would give the same entity id"
            )
        mapped[rule.facility_name] = where


def load_vocabulary_file(path: Path) -> IntegrationVocabulary:
    """One integration's vocabulary and defaults, fully checked. Raises
    ValueError, naming the file and the reason, if it is malformed."""
    vocabulary = parse_vocabulary(_read_checked(path, VOCABULARY_SCHEMA_PATH)["vocabulary"])
    # Read outside the `try`: a broken facility vocabulary is OB's defect, and its
    # error names its own file, not this one.
    standard = ob_facility_vocabulary()
    try:
        check_rules(vocabulary.defaults, standard)
    except ValueError as err:
        raise ValueError(f"{path}: {err}") from err
    return vocabulary


def load_integration_vocabulary(
    integration_domain: str, patterns_dir: Path
) -> IntegrationVocabulary:
    """The vocabulary for one integration. A missing file raises, as a malformed
    one does (see this module's docstring): an integration with patterns and no
    vocabulary would give every entity a gap that is not the entity's fault."""
    path = patterns_dir / integration_domain / VOCABULARY_FILE_NAME
    if not path.is_file():
        raise ValueError(f"{path}: {integration_domain} has patterns but no {VOCABULARY_FILE_NAME}")
    return load_vocabulary_file(path)
