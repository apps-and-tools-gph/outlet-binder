"""Mirrors, in Python, the two normalising expressions the schema's
generated columns compute in SQL (db/sql/devices.py's `name_norm`/
`type_norm` -- issue #185).

SQLite's `lower()` only lowercases ASCII A-Z, leaving every other
character untouched. Python's `str.lower()`/`.casefold()` are
Unicode-aware and would disagree with SQLite on non-ASCII input, so this
module implements the same ASCII-only rule explicitly via a translation
table rather than calling either. tests/test_normalization_agreement.py
asserts the two never diverge, across a corpus that includes non-ASCII
strings.

Used by `domain.discovery.disambiguate_aliases` to detect a collision
*before* attempting a write -- the schema's unique index is still what
actually enforces this; this module only has to agree with it, not
replace it.
"""

_ASCII_UPPER_TO_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def _ascii_lower(value: str) -> str:
    return value.translate(_ASCII_UPPER_TO_LOWER)


def normalize_name(name: str) -> str:
    """Mirrors `lower(replace(name,' ','_'))` -- the identity formula
    shared by `appliance.name` and `co.alias`."""
    return _ascii_lower(name.replace(" ", "_"))


def normalize_type(type_: str | None) -> str:
    """Mirrors `lower(coalesce(type,''))` -- unifies `NULL` and `""` so two
    untyped Appliances collide, matching the panel's `blankToNull`."""
    return _ascii_lower(type_ or "")
