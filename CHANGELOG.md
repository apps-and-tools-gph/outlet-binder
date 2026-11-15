# Changelog

## [Unreleased]

## [0.4.0] - 2026-11-15

### Added

- Support for smart plugs added to Home Assistant through Matter, starting with the IKEA GRILLPLATS. It is discovered with one socket, and its Appliance gets On/Off, Power, Energy, Voltage, Current, Apparent power, Reactive power, Frequency and Power factor.
- Four new readings an Appliance can show: apparent power, reactive power, frequency and power factor.

### Changed

- When a plug has a reading or control the app does not yet know, the Appliance no longer gets an entity for it under the integration's own name. The Repairs warning stays, and the plug, its sockets and every known reading are unaffected.

## [0.3.1] - 2026-11-13

The integration now lists its category, Plugs & switches, and names the organisation as its code owner. Nothing changes in how it works.

## [0.3.0] - 2026-11-11

First beta drop.

## [0.2.0] - 2026-11-01

Second alpha drop.

## [0.1.1] - 2026-10-25

Initial alpha drop.
