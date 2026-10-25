"""One distinct type per identifier, so a mix-up is a type error.

A bare `str` for every id would mean nothing stopped a device registry
id being passed where an entity registry id belongs, or an Appliance id where a
Unmanaged Outlet id belongs. The sharpest case is in domain/discovery.py:
`DiscoveredEntity` carries HA's dotted
`entity_id` and its immutable registry `id` as adjacent fields, and it is
the registry `id` that gets persisted. Picking the other one would store a
plausible-looking value that keeps working until a user renames the entity
months later -- a silent wrong result from a one-word edit. See the
"The toolchain, not the reviewer, prevents mistakes" rule in the global
CLAUDE.md.

Two relationships are expressed here, and the difference between them is
deliberate:

- **The three device kinds nest** on `DeviceId`. A `UoId`, a `CoId`
  and an `ApplianceId` each *is* a device id, so the generic plug operation
  takes a `DeviceId` and every kind widens to it for free; going the other
  way needs an explicit `CoId(...)`, which makes each narrowing a visible
  construction site. Two kinds still cannot be swapped for each other, since
  they are siblings under `DeviceId`.
- **`SocketId` is separate.** A socket is not a device, and a device id
  passed where a socket id belongs is the transposition worth preventing.

A CO's id and a smart socket's id are Home Assistant's own registry ids,
because HA's key is their identity. A `CoId` is therefore *not* an
`HaDeviceRegistryId`: a type has one parent, and the parent here is
`DeviceId`. Discovery builds a `CoId` from an HA device registry id at one
named site, and the few calls back into HA unwrap it explicitly.

Nesting costs a double wrap when building from a literal:
`CoId(DeviceId("co1"))`, since `CoId` takes a `DeviceId` and not a
`str`. Narrowing from an already-typed value
stays a single wrap, so the cost falls on test fixtures rather than
production code, and tests/conftest.py absorbs it in named constants.

`NewType` is a static-only construct: each of these erases to `str` at
runtime, and `CoId("nonsense")` is legal. This module closes the
*transposition* class of mistake, not the malformed-value class. It also
buys nothing where the input is already `Any` -- which is why db/sql/'s row
mappers do not wrap what they read (see db/sql/__init__.py).
"""

from typing import NewType

# Home Assistant's own identifiers, as HA hands them to us.
HaDeviceRegistryId = NewType("HaDeviceRegistryId", str)
HaEntityRegistryId = NewType("HaEntityRegistryId", str)
HaEntityDottedId = NewType("HaEntityDottedId", str)  # "switch.living_room_lamp"
HaAreaId = NewType("HaAreaId", str)

# A device is an Unmanaged Outlet, a CO or an Appliance. Each kind nests on
# `DeviceId`, so an operation that names a kind takes that kind and a mix-up
# is a type error, while the generic plug operation takes `DeviceId`.
DeviceId = NewType("DeviceId", str)
UoId = NewType("UoId", DeviceId)
CoId = NewType("CoId", DeviceId)
ApplianceId = NewType("ApplianceId", DeviceId)

# The prefix an app-generated id carries for its kind. A CO's id is HA's raw
# registry id and has none. The database `CHECK`s on `devices` and `sockets`
# are built from these, so the SQL and the code that mints an id cannot drift.
UO_ID_PREFIX = "uo_"
APPLIANCE_ID_PREFIX = "ap_"
DUMB_SOCKET_ID_PREFIX = "sk_"

# A socket belongs to a device. Separate from `DeviceId` on purpose.
SocketId = NewType("SocketId", str)

# Not an identifier -- nothing above names a *thing*, this names a *when*.
# It closes the same class of mistake for the one remaining bare-`str`
# boundary in the codebase: every `now`/`created_at`/`updated_at`/
# `plugged_at`/`unplugged_at` parameter in db/sql/ and db/operations/ used
# to accept any string at all, so a `name` or `alias` variable handed to a
# `now=` keyword by mistake type-checked identically to a real timestamp.
# `Timestamp` forces the same explicit, visible construction the id types
# already force. It does not distinguish *which* timestamp a value is --
# `created_at` and `updated_at` are both simply `Timestamp`, so swapping
# them with each other is not what this closes (that would need
# `field(kw_only=True)` on the dataclass instead, a separate and
# deliberately unaddressed risk) -- only that some plain string cannot
# drift into a timestamp slot unnoticed.
Timestamp = NewType("Timestamp", str)
