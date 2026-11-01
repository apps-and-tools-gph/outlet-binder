"""How many dumb sockets an Unmanaged Outlet has, and what changing it removes (#422).

An Unmanaged Outlet always has at least one socket and never fewer than it has plugs
in. Its sockets are interchangeable (D4), so resizing it removes free ones
and nothing records which one a plug used. Plugging into a full Unmanaged Outlet
grows it on its own (D5); this module is only the count a user sets by hand.

Dependency-free: no `hass`, no persistence. Every function takes keyword
arguments only, so two integers cannot be transposed.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from .identifiers import SocketId


class SocketCountError(ValueError):
    """A requested socket count the Unmanaged Outlet cannot have.

    A `ValueError` subclass but not a `NotFoundError`: nothing is missing, so
    `_run_write`'s generic `ValueError` branch maps it to
    `ERR_HOME_ASSISTANT_ERROR` with the message intact.
    """


@dataclass(frozen=True)
class Resize:
    """What a resize does: the free sockets to remove, or how many to add.
    At most one of the two is non-empty."""

    remove: tuple[SocketId, ...]
    add: int


def check_count(*, name: str, requested: int, in_use: int) -> None:
    """Raise `SocketCountError` unless `requested` is at least 1 and at least
    `in_use`. `name` is the Unmanaged Outlet's, for the message."""
    if requested < 1:
        raise SocketCountError("A Wall Socket needs at least one socket")
    if requested < in_use:
        raise SocketCountError(
            f"'{name}' has {in_use} sockets in use; its socket count cannot be below {in_use}"
        )


def plan_resize(*, sockets: Sequence[tuple[SocketId, bool]], requested: int) -> Resize:
    """The change that gives an Unmanaged Outlet `requested` sockets.

    `sockets` is each socket's id and whether a plug is in it, lowest
    position first. Lowering removes free sockets from the highest position
    down and never an occupied one; if there are too few free ones the count
    is below the number in use, which `check_count` refuses, so this raises
    `SocketCountError` rather than return a plan that cannot be carried out.
    """
    surplus = len(sockets) - requested
    if surplus <= 0:
        return Resize(remove=(), add=-surplus)
    free = [socket_id for socket_id, occupied in sockets if not occupied]
    if len(free) < surplus:
        raise SocketCountError(f"Cannot remove {surplus} sockets when only {len(free)} are free")
    return Resize(remove=tuple(reversed(free))[:surplus], add=0)
