# Format for YAML device patterns

## Table of Contents

- [Quick reference](#quick-reference)
- [Directory and filename structure](#directory-and-filename-structure)
- [Hardware/firmware version matching](#hardwarefirmware-version-matching)
- [Pattern content schema](#pattern-content-schema)
- [Role-matching fields](#role-matching-fields)
- [When a pattern does not match](#when-a-pattern-does-not-match)
- [What gets recorded](#what-gets-recorded)
- [Comments in a pattern file](#comments-in-a-pattern-file)
- [Template](#template)

## Quick reference

Every key, its type, whether it's required, and what it means, generated
directly from [`device_patterns_schema.yaml`][pattern-schema] (issue #374) -- this is
also what an editor checks against live via each pattern file's
`# yaml-language-server: $schema=...` modeline. This table is mechanically
regenerated (`uv run --frozen python -m
custom_components.outlet_binder.device_identification.generate_pattern_reference`); the sections
below it are hand-written and hold the rationale, worked examples and
version-matching rules a schema description can't carry on its own.

<!-- BEGIN GENERATED: custom_components/outlet_binder/device_identification/generate_pattern_reference.py -- do not hand-edit below -->

### Device pattern file

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `device` | object | required | Whole-device concerns: whether the device has a plug of its own, and its whole-device on/off switch if it has one. |
| `device.kind` | `PLUG_IN` or `FIXED` | required | PLUG_IN if the device has a plug of its own and can be moved between outlets (a smart plug or power strip); FIXED if it has no plug and stays where it is installed (a smart wall outlet). Always written out, since nothing guesses it. |
| `device.all_on_off` | [role](#role) | optional | Identifies a whole-device master on/off switch, if the device has one (e.g. a multi-socket power strip's single strip-wide switch), distinct from any individual socket's own on_off. No default; most devices don't have one. |
| `sockets` | object | required | Everything about deriving this device's individual CO Sockets. |
| `sockets.count` | integer | required | How many CO Sockets this device has. A whole number written without a decimal point (3, not 3.0) -- pattern_loader.py rejects 3.0 at load, since a plain `type: integer` accepts any zero-fractional-part number per the JSON Schema spec, but a standard schema-aware editor may not (issue #339). |
| `sockets.child_models` | list of string | optional | The model string(s) this device's own per-socket child HA devices report, if any (a hub-plus-children device, e.g. a Tapo P304M power strip). Folded into the parent device's entity list before matching. |
| `sockets.default_name` | string | optional | A regular expression, matched against a Socket's whole name, for the names this device's integration gives its Sockets before anyone renames them (e.g. `Tapo P304M_\d+`). The "Appliances from Socket names" dialog reads it to leave such Sockets out; it plays no part in matching a device. Omit it if the device has no such names. |
| `sockets.on_off` | [role](#role) | required | Per-socket role identifying the entity that turns one socket on/off. The only match-blocking role: it must resolve to exactly `count` entities or the whole device fails to match. |
| `sockets.monitoring` | [role](#role) | optional | Per-socket role identifying a socket's usage-tracking entity, if any. Best-effort: silently unresolved if absent/ambiguous, never a reason to reject the device. No default -- a pattern declares it explicitly whenever the device has one. |

### role

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `domain` | string | required | The HA entity domain to match, e.g. switch, sensor, binary_sensor. |
| `device_class` | string | optional | The entity's device_class/original_device_class, e.g. power, connectivity. Also disambiguates one specific entity among several that otherwise match the same domain. |
| `exclude_unique_id_suffixes` | list of string | optional | Entities whose unique_id ends with any of these are excluded from matching. |
| `unique_id_suffixes` | list of string | optional | Ordered list of suffixes, one per socket position (index 0 -> socket position 1, etc.), each matched against the full, literal unique_id via endswith. on_off/monitoring only, never all_on_off. Mutually exclusive with exclude_unique_id_suffixes. |
| `identified_by` | [identified_by](#identified_by) | optional | Confirms an entity's identity exactly from HA's own identifier data instead of guessing it from a unique_id suffix (issue #341). |

### identified_by

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `device` | `self` or `child` | required | self compares against the matched device's own identifiers; child compares against the identifiers of any of its folded children (needs sockets.child_models). |
| `identifier` | string | required | A template over {unique_id} (required) and {parent_identifier} (device: child only) -- see device_patterns/README.md. |

<!-- END GENERATED -->

## Directory and filename structure

- integration_domain/
  - Manufacturer/
    - Model/
      - HwVersion-SwVersion.yaml

**The top-level directory is the HA integration's domain** (e.g. `tplink`), and
it is a hard match condition: a device matches a pattern only if its config
entry (`DeviceEntry.config_entry_id` → `ConfigEntry.domain`) belongs to that
integration. The domain is HA's mandated record of which integration created
a device, unlike the domain element of a device's `identifiers`, which is
only a convention. The folder name must look like a domain (lowercase
letters, digits and underscores); the loader skips anything else, such as
`TP-Link/`, as a path error. Each integration folder's own README.md says
which integration it is and what that integration reports. A device
whose integration has no folder here is simply unknown.

**The second level ("Manufacturer") is whatever literal string that
integration puts in `DeviceEntry.manufacturer`** — not a verified,
device-intrinsic property, and not necessarily the retail brand. Because the
integration is already fixed by the level above, the string only has to be
unambiguous within that one integration, which controls what it reports. See
`domain/discovery.py`'s `CoPattern` docstring for the full rationale.

The filename is either the bare sentinel `any.yaml` (no constraint on
either axis) or `HwVersion-SwVersion.yaml`, each half one of `any`, a
floor, or an exact pin — see
[Hardware/firmware version matching](#hardwarefirmware-version-matching)
below for the full grammar and when to use which. `sw_version` is parsed
but not currently enforced in matching — see `domain/discovery.py`'s
`CoPattern` docstring for why.

A pattern file does not declare its integration domain: the path is the only
source of it, and the schema rejects a `device.integration_domain` key. There
is no per-folder config file.

## Hardware/firmware version matching

Each half of a `HwVersion-SwVersion.yaml` filename is one of three
constraint kinds (issue #136):

| Token | Meaning | When to use it | Example match |
| --- | --- | --- | --- |
| `any` | No constraint (floor zero) | The default. Use this unless you have a specific reason not to. | matches every device |
| `1.5` | Floor — `>= 1.5` | A revision genuinely diverged from here onward, and you've verified this and later revisions share the new entity shape. | `1.5`, `1.6`, `2.0`, `10.0` |
| `=2.0` | Exact — `== 2.0` | **Backstop only** — the ladder above cannot express this case (e.g. you know revision 2.0 alone needs different handling but don't yet know what the next revision will be called). | `2.0` and `2.0.0` only, never `2.1` |

**The ladder (`any`/floor) is the normal mechanism; `=` is an escape
hatch.** Reach for a floor before an exact pin, and reach for `any`
before either. A floor means "this version and everything after, until
a higher pin supersedes it" — not "only this exact string" — so an
unforeseen future hardware revision correctly inherits the nearest lower
floor's pattern rather than silently falling through to `any` with no
error. A pin that is too narrow silently excludes real units of other
revisions from discovery; the case that showed this is recorded in
[`DECISIONS.md`][decisions] (issue #135). A higher rung that fails its
shape check is skipped for a lower one and logged; see
[When a pattern does not match](#when-a-pattern-does-not-match).

A device reporting a missing or unparseable version is treated as
version zero — it can never silently drop out of discovery because its
version string was odd or absent, and it still matches the `any`
pattern. Version strings are parsed leniently for a device (anything
unrecognisable becomes zero) but **strictly** for a pattern filename
token — a typo'd pin is a hard error at load time (logged and the whole
file skipped), never a silent "matches everything". See
`domain/versions.py` for the exact parsing/comparison rules and
`domain/discovery.py`'s `candidate_patterns` for how multiple patterns
under one model are ordered and selected.

Given `any`, `1.0` and `2.5` patterns under one model:

```text
device hw="1.0"   -> tries 1.0, then any
device hw="2.5"   -> tries 2.5, then 1.0, then any
device hw="3.1"   -> tries 2.5, then 1.0, then any (2.5 is the highest floor it still satisfies)
device hw=None    -> tries any only
device hw="Rev A" -> tries any only (unparseable -- treated as version zero)
```

## Pattern content schema

A pattern file's content is a YAML mapping split into two top-level
blocks, both required — `device:` for whole-device concerns, `sockets:` for
everything about deriving individual CO Sockets:

- `device:` (required)
  - `kind` (required, `PLUG_IN` or `FIXED`) — whether the device has a plug
    of its own. `PLUG_IN` is a smart plug or power strip that can be moved
    between outlets; `FIXED` is a smart outlet with no plug that stays where
    it is installed. Discovery records either as a CO, and a `FIXED` one
    can never be plugged into anything. Always written out: nothing guesses
    it.
  - `all_on_off` (optional) — identifies a whole-device master on/off
    switch, if the device has one (e.g. a multi-socket power strip's
    single strip-wide switch), distinct from any individual socket's own
    `on_off`. No default; most devices don't have one.
- `sockets:` (required)
  - `count` (required, integer) — how many CO Sockets this device has.
  - `child_models` (optional, list of strings, default empty) — the
    model string(s) this device's own per-socket child HA devices
    report, if any (a hub-plus-children device, e.g. a Tapo P304M power
    strip). Folded into the parent device's entity list before matching
    — see `domain/discovery.py`'s `group_device_families`. Structural
    (which HA devices count as this device's children) rather than a
    role, but lives here since it only ever matters in
    service of "how many sockets, and which HA device is each one."
  - `default_name` (optional, a regular expression as a string) — the
    names this device's integration gives its Sockets before anyone
    renames them, e.g. `'Tapo P304M_\d+'`, matched against a Socket's
    whole name (a name that only starts with one, like
    `Tapo P304M_4 UNASSIGNED`, does not match). The "Appliances from
    Socket names" dialog leaves such Sockets out, since an Appliance made
    from one would only carry the placeholder. Plays no part in matching a
    device. Omit it if the device has no such names; an invalid regular
    expression logs and skips the file like any other malformed pattern.
  - `on_off` (required) — per-socket role identifying the entity that
    turns one socket on/off. The only match-blocking role: it must
    resolve to exactly `count` entities or the whole device fails to
    match, since it defines how many CO Sockets this device has at all.
    A pattern missing it is logged and skipped at load time, the same as
    any other malformed pattern.
  - `monitoring` (optional, per-socket) — identifies the one entity (if
    any) representing a socket's usage-tracking role, whatever it
    actually measures underneath. Best-effort: silently unresolved if
    absent/ambiguous, never a reason to reject the device. **No
    default** — a pattern declares it explicitly whenever the device has
    one (typically `{domain: sensor, device_class: power}`, see the
    KP115/P304M examples in this directory), same as `all_on_off` above.
    Deliberately not silently filled in by `pattern_loader.py`: a pattern
    file should fully explain its own matching behavior on its own,
    without a reader needing to know about a hidden default elsewhere.

Each of `on_off`/`monitoring`/`all_on_off`'s values is a role — see
[Role-matching fields](#role-matching-fields).

`on_off`/`monitoring`/`all_on_off` are the _only_ concepts a pattern
needs to name explicitly, and the only ones recorded at all — every other
entity a matched device exposes is ignored (see
[What gets recorded](#what-gets-recorded)), since nothing else needs
code-level identity.

## Role-matching fields

Each of `on_off`/`monitoring`/`all_on_off` is a role describing how to
find the entity/entities filling that slot:

- `domain` (required, string) — the HA entity domain to match, e.g.
  `switch`, `sensor`, `binary_sensor`.
- `device_class` (optional, string) — the entity's `device_class`/
  `original_device_class`, e.g. `power`, `connectivity`. Also
  disambiguates one specific entity among several that otherwise match
  the same `domain` (e.g. a device with a "power" sensor plus 3
  competing "energy" sensors — today's/this month's/total — where
  `device_class: power` alone selects the one entity wanted).
- `exclude_unique_id_suffixes` (optional, list of strings, default
  empty) — entities whose `unique_id` ends with any of these are
  excluded from matching (e.g. excluding an accessory LED-indicator
  switch that would otherwise ambiguously match alongside the real
  on/off switch).
- `unique_id_suffixes` (optional, ordered list of strings, default
  empty; `on_off`/`monitoring` only, not `all_on_off`) — each suffix
  positionally identifies one socket's entity, in the order given
  (index 0 → socket position 1, etc.), each required to match exactly
  one entity against the full, literal `unique_id` (via `endswith`, not
  a "positional segment" extraction). Used instead of the default rule
  (gather every matching entity, then sort by `entity_id`) when a
  device's `entity_id`s aren't reliably positional — verified against a
  real KP303, whose `entity_id`s are derived from arbitrary user-facing
  friendly names with no positional meaning at all, while its 3 socket
  switches' raw `unique_id`s reliably end `00`/`01`/`02`. Mutually
  exclusive with `exclude_unique_id_suffixes` (setting both logs a
  warning at load time but still loads the pattern) — see
  `device_patterns/tplink/TP-Link/KP303/any.yaml` for a worked example.

  A declared suffix isn't always the bare positional code itself: if a
  role's entities carry a vendor-appended feature-name segment after
  the code (verified against a real P304M, whose per-socket power
  sensor's `unique_id` is `<base><suffix>_current_power_w` — HA's
  tplink integration appends `_<feature key>` to every non-primary
  entity's `unique_id`), the declared suffix is the whole trailing
  string, e.g. `"00_current_power_w"`, not just `"00"` — see
  `device_patterns/tplink/TP-Link/P304M/any.yaml`.

  When a pattern declares both `on_off` and `monitoring`, the loader
  requires **both or neither** to set `unique_id_suffixes` (issue
  #235) — each with exactly `sockets.count` entries. `_match_pattern`
  (`domain/discovery.py`) resolves the two roles independently and then
  pairs them purely by index, so if only one role were suffix-ordered,
  index _i_ would only coincidentally mean the same physical socket in
  both. This is a structural check only — it can't prove the two
  declared orders actually agree with each other, only that both roles
  explicitly commit to a per-position declaration together; getting the
  order right is the same verified-against-hardware responsibility this
  file already places on a single role's own suffix list.
- `identified_by` (optional, mapping; any role) — confirms an entity's
  identity exactly from HA's own identifier data instead of guessing it
  from a `unique_id` suffix (issue #341). An entity is accepted only if
  the device has an identifier equal to `identifier`, a template filled
  in from that entity. It is a filter, never an ordering: it takes no
  part in the "both or neither" rule above, and `unique_id_suffixes`
  still sets socket position, over the entities it has confirmed.
  Only identifiers whose domain is the pattern's integration domain (its
  top-level folder) are compared.
  - `device` (required): `self` compares against the matched device's
    own identifiers; `child` compares against the identifiers of any of
    its folded children, so it needs `sockets.child_models`.
  - `identifier` (required, string): a template over two placeholders,
    `{unique_id}` (the entity's; required) and `{parent_identifier}` (one
    of the matched device's own identifiers; `child` only). Anything else
    in braces is rejected at load time. Device-specific detail, such as
    the `_` between the two, is written here in the YAML.

  On a KP303, the parent's identifier is its MAC, the master switch's
  `unique_id` is exactly that MAC, and each child's identifier is
  `<parent MAC>_<a socket switch's unique_id>` — so `tplink/TP-Link/KP303/any.yaml`
  confirms the master with `device: self`, `{unique_id}` and the sockets
  with `device: child`, `{parent_identifier}_{unique_id}`. A suffix alone
  cannot tell them apart when the MAC itself ends in `00`, `01` or `02`.
  A KP105 or KP115 needs only the `self` form: its real on/off switch's
  `unique_id` is exactly the device's own identifier (its MAC), while the
  LED switch's is not, so `identified_by: {device: self, identifier:
  "{unique_id}"}` picks the real switch however many accessory switches
  exist (issue #376). A P304M's socket switches use the `child` form
  without `{parent_identifier}`: each switch's `unique_id` equals its own
  child device's identifier exactly, so the identifier is just
  `{unique_id}`, unlike KP303's `<parent MAC>_<unique_id>`.
  Missing facts fail closed: a device with no identifiers, or an entity
  with no `unique_id`, matches nothing and shows up as a near-miss rather
  than a wrong CO.

## When a pattern does not match

A device whose integration, manufacturer and model match a pattern, but
which gets no CO, is a **near-miss** (issue #353). Every discovery pass writes one
warning to the Home Assistant log for it, naming the device and, for each
pattern tried as `pattern_id: reason`, why it failed: an hw_version the
pattern does not allow, or an `on_off` role that did not resolve — the
suffix that matched too many or too few entities, or the entity count
against `sockets.count`, with the entity ids found. Only `on_off` can
fail a match; `monitoring` and `all_on_off` are best-effort and never
appear in a reason. A device whose integration, manufacturer and model no
pattern names is simply unknown and logs nothing. The warning repeats on every pass
until the pattern is fixed; nothing is written for the device meanwhile.

A different case is not a near-miss: a higher-ranked pattern (a floor, or an
exact pin) whose `on_off` role did not resolve, so a lower-ranked one
matched instead. The device still gets its CO, and one warning containing
"fell back to pattern" names the pattern that matched and the higher-ranked
ones skipped (issue #146). It is logged once, when the CO is created; a
device that already has a CO is never matched again, so fixing the YAML
does not remap it.

Alongside the log warning, each near-miss also raises a Home Assistant
Repairs issue (Settings > System > Repairs, issue #356), naming the
device and the same per-pattern reasons. It clears automatically once the
pattern is fixed (or the device is otherwise no longer a near-miss) --
there is nothing to dismiss by hand.

## What gets recorded

Only the three roles. A matched device's `on_off` entity _is_ the CO
Socket's identity, `monitoring` and `all_on_off` are stored as pointers to
HA entity registry ids, and **every other entity the device exposes is
ignored**: an LED switch, a signal-strength sensor, all three of a KP115's
competing "energy" sensors, a P304M child's "auto off enabled" switch.
None of them is recorded anywhere.

There is no socket-level versus device-level distinction to reason about.
A feature that needs a device's other entities reads HA's entity registry
live by `co_id`/`co_socket_id` — the same way `manufacturer`/`model` are
read. The reasoning is in [`DECISIONS.md`][decisions].

## Comments in a pattern file

Keep a device pattern's comments to facts about _that device_: which
entities it exposes, and why a given exclude/suffix rule picks the ones it
does. Anything generic belongs elsewhere, or it goes stale in as many
copies as there are devices:

- How matching works at all — folding, role resolution, what gets recorded
  — belongs in this README.
- Anything shared by every device from one integration belongs in that
  integration folder's own README.md (see `tplink/README.md`).

## Template

Copy this into `<integration_domain>/<Manufacturer>/<Model>/any.yaml` (or
`<HwVersion>-<SwVersion>.yaml`, e.g. `1.5-any.yaml`, only once a
specific hardware revision is verified to need a different pattern —
see [Hardware/firmware version matching](#hardwarefirmware-version-matching))
and fill it in against a real, verified device — never guessed. Check it
against that device's actual HA registry entries, leaving out the disabled
ones: discovery never sees them (`_build_discovered_devices` passes
`include_disabled_entities=False`).

```yaml
# yaml-language-server: $schema=../../../../device_patterns_schema.yaml
device:
  kind: PLUG_IN # required -- PLUG_IN (has a plug) or FIXED (has none)
  # all_on_off: # optional -- only for a device with a whole-strip switch
  #   domain: switch
sockets:
  child_models: [] # optional -- only for hub-plus-children devices
  # default_name: 'Some default_\d+' # optional -- the unrenamed Socket names
  count: 1
  on_off: # required -- the only match-blocking role
    domain: switch
  # monitoring: # optional -- declare only if this device has one
  #   domain: sensor
  #   device_class: power
```

For a device whose `entity_id`s aren't reliably positional across
sockets, or whose entities need `identified_by` (or, where identity can't
be confirmed, `exclude_unique_id_suffixes`) disambiguation, see the real
examples in this directory. No shipped pattern uses
`exclude_unique_id_suffixes` now; it stays a supported option. Particularly
`tplink/TP-Link/KP115/any.yaml` (`device_class` disambiguation among
several sensors, plus `identified_by` picking the real switch over the LED
one),
`tplink/TP-Link/KP303/any.yaml` (`identified_by` confirming the master and
sockets, ordered `unique_id_suffixes`, and a device-level `all_on_off`), and `tplink/TP-Link/P304M/any.yaml` (`identified_by` confirming each socket
switch from its child's identifier, ordered `unique_id_suffixes` on _both_
`on_off` and `monitoring` together, the
latter feature-qualified since its sensors live on separate per-socket
child devices).

[decisions]: ../../../../docs/DECISIONS.md
[pattern-schema]: ../device_patterns_schema.yaml
