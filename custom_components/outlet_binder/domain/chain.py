"""Chains of devices plugged into one another (#421).

A device's parent is the owner of the socket it is plugged into, and
`parent_via_socket` is the one place that says so. Every function that needs
a parent takes it as a plain callable from a device id to its parent's id (or
`None`), so the walk has no `hass` and no database: the operations and the
read model build the callable from where they read the plug and the socket's
owner, and a BDD scenario builds it from a dict.
"""

from collections.abc import Callable, Iterator

from .identifiers import DeviceId, HaAreaId, SocketId

ParentOf = Callable[[DeviceId], DeviceId | None]


def parent_via_socket(
    *,
    plug_of: Callable[[DeviceId], SocketId | None],
    owner_of: Callable[[SocketId], DeviceId | None],
) -> ParentOf:
    """The parent of a device: the owner of the socket it is plugged into.

    `plug_of` gives the socket a device is plugged into (`None` when it is
    plugged into nothing or is not known), and `owner_of` the device that
    owns a socket (`None` when it is not known). Either `None` ends the chain
    there, so a dangling id cannot raise.
    """

    def parent_of(device_id: DeviceId) -> DeviceId | None:
        socket_id = plug_of(device_id)
        return owner_of(socket_id) if socket_id is not None else None

    return parent_of


def ancestors(*, start: DeviceId, parent_of: ParentOf) -> Iterator[DeviceId]:
    """`start`, then its parent, and so on, each device once.

    Stops at a device with no parent, at an id `parent_of` cannot resolve
    (it returns `None`, as for a dangling plug), and at a repeat, so a loop
    in corrupt data ends the walk instead of running forever.
    """
    seen: set[DeviceId] = set()
    current: DeviceId | None = start
    while current is not None and current not in seen:
        seen.add(current)
        yield current
        current = parent_of(current)


def would_loop(*, device_id: DeviceId, host_id: DeviceId, parent_of: ParentOf) -> bool:
    """True when plugging `device_id` into a socket of `host_id` would make
    the device its own ancestor: it is the host, or somewhere above it.

    This is the authority: `_plug` calls it and refuses a loop. The panel
    runs a copy of the rule (`hangingFrom` in
    frontend/src/outlet-binder-panel/link-state.ts) so its plug-in lists never
    offer a loop it would only be refused. tests/fixtures/chain_loops.json
    holds the two to the same answers.
    """
    return device_id in ancestors(start=host_id, parent_of=parent_of)


def area_source(
    *,
    device_id: DeviceId,
    own_area_of: Callable[[DeviceId], HaAreaId | None],
    parent_of: ParentOf,
) -> DeviceId | None:
    """The first device on `device_id` or above it that has an area of its
    own, or `None`.

    Takes areas only: a note never inherits, and the function has no note
    parameter to make it so.
    """
    for candidate in ancestors(start=device_id, parent_of=parent_of):
        if own_area_of(candidate) is not None:
            return candidate
    return None


def effective_area(
    *,
    device_id: DeviceId,
    own_area_of: Callable[[DeviceId], HaAreaId | None],
    parent_of: ParentOf,
) -> HaAreaId | None:
    """The area of `area_source`, or `None`: the rule is stated once, there."""
    source = area_source(device_id=device_id, own_area_of=own_area_of, parent_of=parent_of)
    return own_area_of(source) if source is not None else None
