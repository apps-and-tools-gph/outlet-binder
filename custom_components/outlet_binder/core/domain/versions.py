"""Version parsing and comparison for pattern hw/sw version matching
(docs/LLD.md §4, issue #136's floor/exact model).

Pure, dependency-free -- no `homeassistant` import, no I/O -- matching
domain/chain.py's convention. `awesomeversion` (already a hard Home
Assistant core dependency) was evaluated and rejected: it can't parse
real TP-Link firmware strings like "1.0.13 Build 230411 Rel.145121"
(`.valid` is False, comparing raises), it considers "1" < "1.0", and
using it would introduce the first non-stdlib import into `domain/`,
whose contract is purity.

A missing or unparseable device-reported version is treated as version
zero, not as "no match" and not as a special case -- a device can never
silently drop out of discovery because its version string was odd or
absent. This asymmetry
matters: device-reported strings are lenient (anything unrecognisable
becomes zero and still matches the base pattern), while a pattern's own
filename token is strict authored content -- see device_identification/pattern_loader.py for
where that strictness is enforced.
"""

import re
from dataclasses import dataclass

VersionKey = tuple[int, ...]

ZERO_VERSION: VersionKey = ()

_LEADING_VERSION_RE = re.compile(r"^\d+(?:\.\d+)*")


def parse_version(raw: str | None) -> VersionKey:
    """Parse the leading dot-separated integer run of `raw` into a
    canonical VersionKey, ignoring everything from the first
    non-matching character onward -- so a TP-Link firmware string's
    build/release tail (e.g. "1.0.13 Build 230411 Rel.145121") is
    dropped by this general rule, not a three-segment special case.

    `None`, an empty string, or a string with no leading digit (e.g.
    "Rev A", "v1.2" -- a leading "v" is not stripped) all yield
    ZERO_VERSION. Trailing zero components are stripped, so "1.0",
    "1.0.0" and "1" all parse to the same canonical (1,).
    """
    if raw is None:
        return ZERO_VERSION
    match = _LEADING_VERSION_RE.match(raw)
    if match is None:
        return ZERO_VERSION
    parts = [int(p) for p in match.group().split(".")]
    while parts and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def version_at_least(version: VersionKey, floor: VersionKey) -> bool:
    """True if `version` is at or above `floor`. Both are zero-padded to
    equal length before comparing as integer tuples, so e.g. (1,)
    satisfies a (1, 0) floor."""
    length = max(len(version), len(floor))
    padded_version = version + (0,) * (length - len(version))
    padded_floor = floor + (0,) * (length - len(floor))
    return padded_version >= padded_floor


@dataclass(frozen=True)
class VersionConstraint:
    """One hardware/software version constraint, parsed from a pattern
    filename token (`any`, a floor like `1.5`, or an exact pin `=2.0` --
    see device_identification/pattern_loader.py).

    A single combined field rather than a `floor`/`exact` pair on
    CoPattern deliberately: every combination of `version`/`exact` here
    is meaningful, including `VersionConstraint(exact=True)`, which pins
    "exactly version zero", i.e. only a device reporting nothing
    parseable -- a `floor`+`exact` pair could represent "both set" or
    "neither set", states nothing should ever be in (global CLAUDE.md
    rule "the toolchain, not the reviewer, prevents mistakes", tier 1:
    make it unrepresentable).

    The default, `ANY_VERSION` (`version=ZERO_VERSION, exact=False`),
    matches every device -- it's the floor-zero case, not a separate
    "no constraint" flag.
    """

    version: VersionKey = ZERO_VERSION
    exact: bool = False

    def allows(self, version: VersionKey) -> bool:
        if self.exact:
            return version == self.version
        return version_at_least(version, self.version)

    @property
    def rank(self) -> tuple[bool, VersionKey]:
        """Sort key for most-specific-first candidate ordering
        (domain/discovery.py's candidate_patterns): an exact pin always
        outranks every floor regardless of its own version (`True` sorts
        above `False`), and among floors, a higher version outranks a
        lower one. `=` is a backstop for what the ladder can't express,
        never a co-equal alternative to a floor -- this ranking is what
        makes it a hard override rather than just another rung."""
        return (self.exact, self.version)


ANY_VERSION = VersionConstraint()
