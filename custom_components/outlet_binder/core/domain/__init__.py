"""Dependency-free domain logic for the Outlet & Appliance Binding integration.

No `hass` argument anywhere in this package, deliberately — see the
"Testable domain logic" design principle in docs/HLD.md and docs/LLD.md's
individual sections. This is what lets domain-behaviour BDD scenarios
exercise these functions directly, without pulling in HA test fixtures.
tests/test_domain_import_guard.py fails if a module here imports anything
but the stdlib and this package, or needs Home Assistant to import, even
indirectly.
"""
