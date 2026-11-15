# matter

The pattern under this folder is verified against the real device's actual HA
registry entries, not guessed.

This folder is the HA `matter` integration's domain: a device matches a
pattern here only if its config entry belongs to `matter`.

The manufacturer and model folders are the strings the device reports to HA,
read from the registry: `IKEA of Sweden` and `GRILLPLATS Plug` for the
GRILLPLATS.
