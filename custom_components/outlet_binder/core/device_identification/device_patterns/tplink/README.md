# tplink

Every pattern under this folder is verified against a real device's actual
HA registry entries, not guessed.

This folder is the HA `tplink` integration's domain: a device matches a
pattern here only if its config entry belongs to `tplink`, whatever
manufacturer string it reports. The integration (python-kasa) hardcodes
`manufacturer="TP-Link"` in `homeassistant/components/tplink/entity.py` for
every product line it supports — Kasa, Tapo, Deco, etc. — regardless of
retail brand, so every pattern here sits under `TP-Link/`.

A device reported by a different integration never matches a pattern here,
even if it also says `manufacturer="TP-Link"` and the same model. It belongs
in that integration's own folder next to this one.
`tests/test_tplink_manufacturer_assumption.py` is a separate guard: it
checks that HA's `tplink` integration still hardcodes that manufacturer
string.
