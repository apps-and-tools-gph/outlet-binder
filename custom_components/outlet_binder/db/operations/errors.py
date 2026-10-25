"""Shared db/operations/ exception types.

A single place for the exceptions every operations-layer write can raise,
so websocket_api.py's error mapping (docs/LLD.md §13) has actual types to
dispatch on instead of inferring meaning from a bare `ValueError`'s
message text.
"""


class NotFoundError(ValueError):
    """A referenced row -- CO, Unmanaged Outlet, Appliance, CO Socket, ...
    -- does not exist.

    A `ValueError` subclass so existing `pytest.raises(ValueError, ...)`
    assertions keep matching, but its own type lets websocket_api.py's
    `_run_write` map "that row doesn't exist" to HA's `ERR_NOT_FOUND`
    specifically, distinct from any other domain error a future write
    command might raise as a plain `ValueError`.
    """


class DuplicateError(ValueError):
    """A write would violate a uniqueness constraint -- an Appliance's
    normalised (name, type), or a CO's or an Unmanaged Outlet's normalised name,
    already exists (issue #185, db/sql/devices.py's
    `ux_devices_appliance_name_type_norm`, `ux_devices_co_name_norm` and
    `ux_devices_uo_name_norm`).

    A `ValueError` subclass for the same reason as `NotFoundError`:
    existing `pytest.raises(ValueError, ...)` assertions keep matching,
    while its own type lets a caller distinguish it from any other domain
    error a write might raise. `websocket_api.py`'s `_run_write` needs no
    change for this one -- its existing generic `ValueError` branch already
    maps to `ERR_HOME_ASSISTANT_ERROR` with the message intact.
    """


class WrongKindError(NotFoundError):
    """A row exists, but it is a device of a different kind than the
    operation accepts -- an Appliance id given where a CO is wanted, say.

    A `NotFoundError` subclass carrying the same message as the not-found
    case, so `websocket_api.py`'s `_run_write` and `failed_entry` treat the
    two alike and the wire cannot tell them apart.
    """


class LoopError(ValueError):
    """A plug would make a device its own ancestor (#421).

    A `ValueError` subclass but not a `NotFoundError`: nothing is missing, so
    `_run_write`'s generic `ValueError` branch maps it to
    `ERR_HOME_ASSISTANT_ERROR` with the message intact, and the edit
    session's replay catches it by name.
    """


class FixedDeviceError(ValueError):
    """A plug was asked of a device that has none (#422).

    An FCO, and an Unmanaged Outlet, are fixed in place: `devices.has_plug` is
    0 and the database refuses them a plug as well. A `ValueError` subclass
    but not a `NotFoundError`: the device exists and is the right kind, it
    just cannot be plugged in, so `_run_write`'s generic `ValueError` branch
    maps it to `ERR_HOME_ASSISTANT_ERROR` with the message intact, and the
    edit session's replay catches it by name.
    """
