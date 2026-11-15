# Format for YAML device patterns

## Table of Contents

- [Quick reference](#quick-reference)
- [Directory and filename structure](#directory-and-filename-structure)
- [Hardware/firmware version matching](#hardwarefirmware-version-matching)
- [Pattern content schema](#pattern-content-schema)
- [Role-matching fields](#role-matching-fields)
- [Vocabulary files](#vocabulary-files)
- [When a pattern does not match](#when-a-pattern-does-not-match)
- [What gets recorded](#what-gets-recorded)
- [Comments in a pattern file](#comments-in-a-pattern-file)
- [Template](#template)

## Quick reference

Every key, its type, whether it's required, and what it means, generated
directly from [`schemas/device_pattern_schema.yaml`][pattern-schema] (issue #374) -- this is
also what an editor checks against live via each pattern file's
`# yaml-language-server: $schema=...` modeline. This table is mechanically
regenerated (`uv run --frozen python -m
custom_components.outlet_binder.core.device_identification.generate_pattern_reference`); the sections
below it are hand-written and hold the rationale, worked examples and
version-matching rules a schema description can't carry on its own.

<!-- BEGIN GENERATED: custom_components/outlet_binder/core/device_identification/generate_pattern_reference.py -- do not hand-edit below -->

### Device pattern file

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `device` | object | required | Whole-device concerns: whether the device has a plug of its own, and its whole-device on/off switch if it has one. |
| `device.kind` | `PLUG_IN` or `FIXED` | required | PLUG_IN if the device has a plug of its own and can be moved between outlets (a smart plug or power strip); FIXED if it has no plug and stays where it is installed (a smart wall outlet). Always written out, since nothing guesses it. |
| `device.all_on_off` | [role](#role) | optional | Identifies a whole-device master on/off switch, if the device has one (e.g. a multi-socket power strip's single strip-wide switch), distinct from any individual socket's own on_off. No default; most devices don't have one. |
| `device.facilities` | object of lists of [host_entity](#host_entity) | optional | This model's own device-level entities, laid over its integration's entries for this model alone (#211). An entry whose integration_name the integration's file has replaces that entry whole, recognition and meaning together; any other adds an entity. Each states its own `unique_id_suffix`. They exist only at the CO level, such as the restart button or the Wi-Fi signal; a CO Socket has no such facility, so an Appliance never mirrors them. They play no part in matching a device. Omit it if the model uses the integration's entries. |
| `sockets` | object | required | Everything about deriving this device's individual CO Sockets. |
| `sockets.count` | integer | required | How many CO Sockets this device has. A whole number written without a decimal point (3, not 3.0) -- pattern_loader.py rejects 3.0 at load, since a plain `type: integer` accepts any zero-fractional-part number per the JSON Schema spec, but a standard schema-aware editor may not (issue #339). |
| `sockets.child_models` | list of string | optional | The model string(s) this device's own per-socket child HA devices report, if any (a hub-plus-children device, e.g. a Tapo P304M power strip). Folded into the parent device's entity list before matching. |
| `sockets.default_name` | string | optional | A regular expression, matched against a Socket's whole name, for the names this device's integration gives its Sockets before anyone renames them (e.g. `Tapo P304M_\d+`). The "Appliances from Socket names" dialog reads it to leave such Sockets out; it plays no part in matching a device. Omit it if the device has no such names. |
| `sockets.on_off` | [role](#role) | required | Per-socket role identifying the entity that turns one socket on/off. The only match-blocking role: it must resolve to exactly `count` entities or the whole device fails to match. |
| `sockets.monitoring` | [role](#role) | optional | Per-socket role identifying a socket's usage-tracking entity, if any. Best-effort: silently unresolved if absent/ambiguous, never a reason to reject the device. No default -- a pattern declares it explicitly whenever the device has one. |
| `sockets.facilities` | object of lists of [socket_facility](#socket_facility) | optional | This model's own socket entities, laid over its integration's entries for this model alone (#211). An entry whose integration_name the integration's file has replaces that entry whole, recognition and meaning together; any other adds an entity. Each states its own `unique_id_suffix`, and, to be an OB facility, a `facility_name`. An Appliance mirrors them. They play no part in matching a device. Omit it if the model uses the integration's entries. |

### role

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `domain` | string | required | The HA entity domain to match, e.g. switch, sensor, binary_sensor. |
| `device_class` | string | optional | The entity's device_class/original_device_class, e.g. power, connectivity. Also disambiguates one specific entity among several that otherwise match the same domain. |
| `exclude_unique_id_suffixes` | list of string | optional | Entities whose unique_id ends with any of these are excluded from matching. |
| `unique_id_suffixes` | list of string | optional | Ordered list of suffixes, one per socket position (index 0 -> socket position 1, etc.), each matched against the full, literal unique_id via endswith. on_off/monitoring only, never all_on_off. Mutually exclusive with exclude_unique_id_suffixes. |
| `identified_by` | [identified_by](#identified_by) | optional | Confirms an entity's identity exactly from HA's own identifier data instead of guessing it from a unique_id suffix (issue #341). |

### host_entity

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `integration_name` | string | required | The entity's name in this file: the `<name>` in `<integration>_<name>`, e.g. `rssi`. |
| `unique_id_suffix` | string | required | What the entity's `unique_id` ends with, compared literally. It must name one entity of the device, not a kind of entity. |
| `device_class` | string | optional | An HA device class the entity must also have, as well as the ending. Optional: the ending alone recognises the entity. |

### socket_facility

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `facility_name` | string | optional | The facility's key (`ha_` or `ob_`, then lowercase words); it must be in OB's facility vocabulary, in this domain. When the facility's entity id ending differs from `integration_name`, an Appliance gets two entities for it, one under each name. Without it the entity is offered as `<integration>_<integration_name>` only. |
| `integration_name` | string | required | The entity's name in this file: the `<name>` in `<integration>_<name>`, e.g. `current_consumption`. |
| `unique_id_suffix` | string | required | What the entity's `unique_id` ends with, compared literally. It must name one entity of the device, not a kind of entity. |
| `device_class` | string | optional | An HA device class the entity must also have, as well as the ending. Optional: the ending alone recognises the entity. |

### identified_by

| Key | Type | Required | Meaning |
| --- | --- | --- | --- |
| `device` | `self` or `child` | required | self compares against the matched device's own identifiers; child compares against the identifiers of any of its folded children (needs sockets.child_models). |
| `identifier` | string | required | A template over {unique_id}, or over {unique_id_stem} when unique_id_suffix is set (exactly one of the two is required), and {parent_identifier} (device: child only) -- see device_patterns/README.md. |
| `unique_id_suffix` | string | optional | What the entity's unique_id ends with, compared literally. When set, identifier uses {unique_id_stem} (the unique_id without this ending) instead of {unique_id} -- see device_patterns/README.md. |

<!-- END GENERATED -->

## Directory and filename structure

- integration_domain/
  - vocabulary_and_defaults.yaml (optional; see [Vocabulary files](#vocabulary-files))
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
`core/domain/discovery.py`'s `CoPattern` docstring for the full rationale.

The filename is either the bare sentinel `any.yaml` (no constraint on
either axis) or `HwVersion-SwVersion.yaml`, each half one of `any`, a
floor, or an exact pin — see
[Hardware/firmware version matching](#hardwarefirmware-version-matching)
below for the full grammar and when to use which. `sw_version` is parsed
but not currently enforced in matching — see `core/domain/discovery.py`'s
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
revisions from discovery: a KP105 pattern pinned to `2.0` left real `1.0`
KP105 units undiscovered. A higher rung that fails its
shape check is skipped for a lower one and logged; see
[When a pattern does not match](#when-a-pattern-does-not-match).

A device reporting a missing or unparseable version is treated as
version zero — it can never silently drop out of discovery because its
version string was odd or absent, and it still matches the `any`
pattern. Version strings are parsed leniently for a device (anything
unrecognisable becomes zero) but **strictly** for a pattern filename
token — a typo'd pin is a hard error at load time (logged and the whole
file skipped), never a silent "matches everything". See
`core/domain/versions.py` for the exact parsing/comparison rules and
`core/domain/discovery.py`'s `candidate_patterns` for how multiple patterns
under one model are ordered and selected.

Given `any`, `1.0` and `2.5` patterns under one model:

```text
device hw="1.0"   -> tries 1.0, then any
device hw="2.5"   -> tries 2.5, then 1.0, then any
device hw="3.1"   -> tries 2.5, then 1.0, then any (2.5 is the highest floor it still satisfies)
device hw=None    -> tries any only
device hw="Rev A" -> tries any only (unparseable -- treated as version zero)
```

A pattern file is a complete description of its version. A file for a later
hardware version lists that version's extra entities itself, in
`device.facilities` and `sockets.facilities`, each with its own
`unique_id_suffix`; nothing in the integration's
[vocabulary file](#vocabulary-files) or in `any.yaml` has to change for it.

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
    — see `core/domain/discovery.py`'s `group_device_families`. Structural
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
  (`core/domain/discovery.py`) resolves the two roles independently and then
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
  - `identifier` (required, string): a template over three placeholders:
    `{unique_id}` (the entity's), `{unique_id_stem}` (the entity's with
    `unique_id_suffix` taken off its end) and `{parent_identifier}` (one
    of the matched device's own identifiers; `child` only). A rule uses
    exactly one of `{unique_id}` and `{unique_id_stem}`: `{unique_id_stem}`
    if and only if `unique_id_suffix` is set. Anything else in braces is
    rejected at load time. Device-specific detail, such as the `_`
    between the two, is written here in the YAML.
  - `unique_id_suffix` (optional, non-empty string): what the entity's
    `unique_id` ends with, compared literally. It is for a device whose
    identifier is a leading part of every one of its entities'
    `unique_id`s, so that only the ending tells one entity from another.
    With it, an entity is accepted only if its `unique_id` ends with the
    suffix and has at least one character before it (the stem), and the
    device holds the identifier built from that stem. An entity whose
    `unique_id` does not end with it is not accepted. The suffix is text,
    never a template, and may hold any character. It is not the role's
    `unique_id_suffixes`: that lists one ending per socket and sets their
    order, while this one states a single ending and confirms identity.
    Because an entity must end with both, a role that lists
    `unique_id_suffixes` must have each entry end with the stated ending or
    be ended by it, and, when the role has no `unique_id_suffixes`, the
    stated ending must not end with any `exclude_unique_id_suffixes` entry
    (with `unique_id_suffixes` the exclude list is ignored); otherwise the
    pattern could never match and is refused at load. An empty ending is
    refused.

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
  A Matter plug needs `unique_id_suffix`: its device identifier is
  `deviceid_<fabric>-<node>-MatterNodeDevice`, and every entity's
  `unique_id` on that device starts with the same
  `<fabric>-<node>-MatterNodeDevice`, so the switch is told from the
  device's other entities only by its ending:

  ```yaml
  on_off:
    domain: switch
    identified_by:
      device: self
      unique_id_suffix: "-1-MatterPlug-6-0"
      identifier: "deviceid_{unique_id_stem}"
  ```

  Read aloud: the switch's `unique_id` ends with `-1-MatterPlug-6-0`, and
  the device's identifier is `deviceid_` followed by the rest of it. The
  ending includes the entity's endpoint id, so one literal ending
  describes one model's switch, not every Matter device.
  Missing facts fail closed: a device with no identifiers, or an entity
  with no `unique_id`, matches nothing and shows up as a near-miss rather
  than a wrong CO.

## Vocabulary files

A CO Socket's _facilities_ are the entities on the socket's own HA device, plus
its `on_off` entity. An Appliance plugged into the socket gets one OB entity
for each, named after the Appliance and the facility, so an automation that
uses it survives the Appliance being moved to another socket. Nothing is
stored: the facilities are read from HA's registries when they are needed.

**The socket's own device** comes from the `on_off` role's `identified_by`,
which already says how the device names its sockets. With `device: self`, the
socket's device is the matched device's own. With `device: child`, it is the
one folded child whose identifier is the template filled in for the socket's
`on_off` entity. No child, or more than one, means no device, and the socket
has only its On/Off entity. Nothing matches by substring.

**An integration's `vocabulary_and_defaults.yaml`** sits directly in its folder,
beside the Manufacturer folders. It lists every entity the integration offers
for the devices OB has patterns for, by the HA domain of the entity, how OB
recognises each, and what OB makes of it. The names OB gives them come from OB's
facility list, `core/device_identification/ob_facility_vocabulary.yaml`, which groups the
facilities by their HA domain and gives each a key, the `entity_id_name` its
entity id ends with, and a display name. It is checked against
`schemas/ob_facility_vocabulary_schema.yaml`. A key is `ha_<name>` when HA itself
defines the name (a device class name: `ha_power`, `ha_voltage`, ...) and
`ob_<name>` when the name is OB's own (`ob_overheated`, ...), so a key never
equals an HA or an integration word. A facility has one domain whichever
integration it comes from, so a mapping to a facility in another domain is
refused: the Appliance's entity id would otherwise change with the socket it is
plugged into.

Each entry's key is its _name_: the `<name>` in `<integration>_<name>`, written
by a person, so it is the same in every language and never changes with the
integration. The entry states the facts that recognise the entity, and OB
matches an entity on those facts alone (the entity registry's `translation_key`
is not read):

- `unique_id_suffix` (required): what the entity's `unique_id` ends with,
  compared literally. It must name one entity of the device, not a kind of
  entity: a device class alone is too loose, since a strip can have several
  sensors of one class.
- `device_class` (optional): an HA device class the entity must also have, read
  as the registry's `device_class`, else its `original_device_class`.

Beside the facts is the entry's optional default:

- `socket: <facility>`: a CO Socket has the entity, and an Appliance mirrors
  it as that facility, a key from OB's facility vocabulary (`ha_power`, `ob_overheated`,
  ...).
- `device: true`: the entity exists only at the CO level, on the plug itself
  (restart, LED, signal strength, a whole-strip total). A CO Socket has no such
  facility, so an Appliance never mirrors it. Where the plug and its socket are
  one HA device, every plug-level entity needs this, or it raises the Repairs
  issue below. `socket` and `device` together are refused.
- nothing: the integration offers the entity and OB has no name for it. The
  Appliance gets the entity as `<integration>_<name>`, and that is the intended
  result, not a fault.

```yaml
vocabulary:
  sensor:
    current_consumption:
      unique_id_suffix: _current_power_w
      socket: ha_power
    rssi:
      unique_id_suffix: _rssi
      device: true
    humidity:
      unique_id_suffix: _humidity
      device_class: humidity
```

The file is checked against `schemas/vocabulary_and_defaults_schema.yaml`, and
then by `facility_loader.py` for what a schema cannot say: every `socket`
facility is in OB's facility vocabulary and in the facility's domain, `on_off` is never
mapped (it is the pattern's role, and its domain must be the one OB's facility vocabulary gives it), no
facility is mapped from two entries, no name repeats under one domain (a repeated
YAML key is refused, not read as the last one), and **no entity could satisfy
two entries**: two entries in one domain overlap when one's ending ends with the
other's (equal endings included) and their device classes are equal or one is
absent. That check is why an entity has at most one entry and the resolver needs
no precedence rule. `validate_patterns` checks it too. The pattern loader skips
it, because only `<integration>/vocabulary_and_defaults.yaml` is a vocabulary
file.

**Which OB entities an entity gets**, for an enabled entity of the integration
on the socket's device:

| Case | OB entities |
| --- | --- |
| Entry with `socket`, the facility's `entity_id_name` differs from the name (`current_consumption` → `power`) | `sensor.ob_<appliance>_power` and `sensor.ob_<appliance>_tplink_current_consumption` |
| Entry with `socket`, the facility's `entity_id_name` equals the name (`voltage`) | `sensor.ob_<appliance>_voltage` only |
| Entry with no default (`humidity`) | `sensor.ob_<appliance>_tplink_humidity` only |
| Entry with `device: true`, or a disabled entity, or another integration's entity | none |
| No entry recognises it | none, and a Repairs issue |
| The `on_off` role | `switch.ob_<appliance>_on_off` only |

If two sources would give the same entity id, neither is offered.

**An unlisted entity** (an enabled entity of the integration on a socket's
device that no entry recognises) gets no OB entity: OB does not invent a name
for something nobody has looked at. So that nothing goes missing silently, OB
raises one Repairs issue for it, keyed by its entity registry id, describing it
by its facts (its HA entity id, domain and device class) and naming nothing. It
is raised only for a socket an Appliance is plugged into, and clears when the
entity is listed, disabled or no longer met.

**A model's own entries** go in its pattern file: `device.facilities` lists
device-level entities, and `sockets.facilities` lists socket entities, each as a
list of entries that states its own `unique_id_suffix` (and `device_class` if
needed). A socket entry may add a `facility_name`; without one the entity is
offered as `<integration>_<name>`. An entry whose `integration_name` the
integration's file has replaces that entry whole, for that model alone: nothing
is merged field by field. Any other name adds an entity. The loader works out
each model's final entries once, when the pattern loads: the integration's
entries, then the model's own, and refuses the result if two overlap.

A later hardware version gets an additional pattern file beside `any.yaml`
(a hardware floor such as `1.5-any.yaml`), complete on its own: it does not build
on `any.yaml`, which is not edited. Its `device.facilities` and
`sockets.facilities` list that version's extra entities, each with its own
`unique_id_suffix`, so nothing in the integration's file has to change for it.
The software half of the filename is reserved for firmware-specific files, such
as `any-1.5.yaml`. It is parsed but not matched yet, so until it is, only the
hardware half selects a pattern and such a file is not chosen over `any.yaml`.

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
ignored** at discovery: an LED switch, a signal-strength sensor, all three of
a KP115's competing "energy" sensors, a P304M child's "auto off enabled"
switch. None of them is recorded anywhere. They are read live from HA's
registries, not from anything stored, when an Appliance's entities are worked
out (see [Vocabulary files](#vocabulary-files)).

There is no socket-level versus device-level distinction to reason about.
A feature that needs a device's other entities reads HA's entity registry
live by `co_id`/`co_socket_id` — the same way `manufacturer`/`model` are
read.

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
# yaml-language-server: $schema=../../../../schemas/device_pattern_schema.yaml
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

[pattern-schema]: ../schemas/device_pattern_schema.yaml
