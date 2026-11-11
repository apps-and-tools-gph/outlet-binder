# Outlet & Appliance Binding

A Home Assistant custom integration that separates an appliance (for example
_Living Room Lamp_) from the smart plug currently controlling it, so that
automations and dashboards keep working when the plug is swapped or moved.

## Table of contents

- [What it does](#what-it-does)
- [Requirements](#requirements)
- [Installing through HACS](#installing-through-hacs)
- [Setting it up](#setting-it-up)
- [Using it](#using-it)
- [Upgrading and downgrading](#upgrading-and-downgrading)
- [Not yet implemented](#not-yet-implemented)
- [Reporting a problem](#reporting-a-problem)
- [Licence](#licence)

## What it does

An automation that switches a lamp usually names the smart plug the lamp is
plugged into. Move the lamp to another plug and the automation breaks.

Outlet & Appliance Binding gives each appliance its own permanent `switch`
entity. You point your automations at that entity. When you plug the
appliance into a different socket, you tell the integration once, and it
repoints the switch to the new socket. The automations need no change.

It sits on top of the integrations you already use for your smart plugs
(Tapo, Kasa, Matter and so on). It does not talk to plug hardware itself.

## Requirements

- Home Assistant 2026.9.0 or later
- [HACS][hacs]

## Installing through HACS

Until this repository is listed in HACS, add it as a custom repository:

1. In HACS, open the menu (the three dots, top right) and choose
   **Custom repositories**.
1. Enter `https://github.com/apps-and-tools-gph/outlet-binder` as the
   repository.
1. Choose **Integration** as the type, then click **Add**.
1. Find _Outlet & Appliance Binding_ in HACS, download it and restart Home
   Assistant.

## Setting it up

1. In Home Assistant, go to **Settings**, then **Devices & services**.
1. Choose **Add integration** and search for _Outlet & Appliance Binding_.
1. Confirm. There is nothing to configure to get started, and only one
   instance can exist.

An **Outlet Binder** entry then appears in the sidebar.

## Using it

Open **Outlet Binder** from the sidebar. The panel is where you manage:

- **Wall Sockets**: ordinary outlets that are not switchable. They are for
  your own record-keeping and are never an automation target.
- **Smart Devices**: the smart plugs and outlets the integration found in
  Home Assistant, each with its sockets.
- **Appliances**: the things you plug in. Each one gets its permanent
  `switch` entity.

To plug an appliance in, or move it, use the panel's link dialogs. Only
administrators can make changes.

The integration's **Configure** button (on its card in **Devices &
services**) chooses how plug and unplug operations are applied:

- **Batch**: plug operations are staged, and take effect when you commit
  them. Undo and redo step through the staged operations.
- **Immediate**: each change is written as soon as you make it.

## Upgrading and downgrading

When an update changes how the integration stores its data, it upgrades its
database the first time Home Assistant starts with the new version. Before it
does, it saves a copy of the database as `outlet_binder.db.pre-migration.bak`
beside it, in the Home Assistant configuration directory, and puts the copy
back if the upgrade fails.

If you had staged changes in the panel that you had not committed, the upgrade
discards them, and a Repairs notice titled _Staged changes discarded after an
upgrade_ says so. Nothing already committed is changed. Make the staged
changes again if you still want them.

Going back to an older version is refused when the database has already been
upgraded: the integration will not load, and says which versions are involved.
To go back, stop Home Assistant, replace `outlet_binder.db` with a copy of
`outlet_binder.db.pre-migration.bak`, install the older version and start
Home Assistant again. The copy is the database as it was before the upgrade,
so anything you changed in the integration since is lost, and each later
upgrade replaces the copy. Or install the newer version again.

## Not yet implemented

- Power monitoring. Appliances can be switched on and off, but their usage
  is not reported yet.

## Reporting a problem

Open an issue in this repository's issue tracker.

## Licence

Released under the GNU General Public License, version 3. See the
`LICENSE` file.

[hacs]: https://hacs.xyz
