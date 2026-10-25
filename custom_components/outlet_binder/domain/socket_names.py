"""The name HA holds for a CO Socket's on/off switch (#394).

Kept out of `domain/discovery.py`: this feeds Appliance creation, not
pattern matching. Takes plain values rather than registry entries so a BDD scenario can
exercise it without `hass`.
"""

import re
from collections.abc import Iterable


def _present(value: str | None) -> str | None:
    """`value` unless it is `None` or blank -- the registry stores an
    entity with no name of its own as either, so both mean "absent"."""
    return value if value is not None and value.strip() != "" else None


def resolve_socket_name(
    *,
    entity_name: str | None,
    entity_original_name_unprefixed: str | None,
    entity_original_name: str | None,
    has_entity_name: bool,
    device_name_by_user: str | None,
    device_name: str | None,
) -> str | None:
    """The name HA shows for the switch entity, else the device's name.

    The entity's own precedence is the one HA uses for its display entry
    (`RegistryEntry._as_display_dict` in the installed package): a rename
    in HA (`entity_name`), then `original_name_unprefixed`, then
    `original_name`. A single-socket device's switch has none of these:
    with `has_entity_name` set, HA names it after the device, so the
    device's name (the user's own, else the integration's) is offered. A
    switch without `has_entity_name` and without a name has nothing to
    offer, and the result is `None`.
    """
    for candidate in (entity_name, entity_original_name_unprefixed, entity_original_name):
        if (found := _present(candidate)) is not None:
            return found
    if not has_entity_name:
        return None
    return _present(device_name_by_user) or _present(device_name)


def is_default_socket_name(name: str, rules: Iterable[re.Pattern[str]]) -> bool:
    """Whether `name` is one its integration hands a Socket before anyone
    renames it (a pattern's `sockets.default_name`, #394), so an Appliance
    made from it would only carry that placeholder. Each rule must match
    the whole name: a user's own name that merely starts with a default,
    such as `Tapo P304M_4 UNASSIGNED`, is not one. No rules means nothing
    is a default."""
    return any(rule.fullmatch(name) for rule in rules)
