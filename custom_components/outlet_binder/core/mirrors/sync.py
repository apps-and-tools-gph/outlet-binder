"""Keeps the OB entities that mirror a socket's facilities in step with the
database and HA's registries (#187).

One coordinator serves every mirror platform (sensor.py, binary_sensor.py,
button.py, number.py, select.py, switch.py). Each platform registers its
`async_add_entities`; every registration and every `SIGNAL_SWITCHES_CHANGED`
runs one sync, which is idempotent, so a domain's entities are created as its
platform registers and a second sync changes nothing. One lock keeps two syncs
from overlapping: the read runs on an executor thread, and an older read must
not be applied after a newer one.

A sync works out the whole set once (domain/appliance_mirrors.py) and each
domain applies its own part: it removes registry entries the set no longer
wants, adopts the current name and source of those it has, and adds the rest.
Nothing here prunes a domain whose platform has not registered. The `switch`
domain also holds switch.py's PCO plugs, which its platform hands over as
`sync_plugs`: the same sync, on the same read and under the same lock, prunes
the domain and adds the plugs, so a plug cannot be pruned by a read older than
the one that made it. The prune keeps the plugs' entries
(`plug_switch_unique_ids`).

An entity id that cannot be renamed back to what the name gives, because another
entity holds it, is logged once and again only if it clears and returns.

HA's registries decide what a socket gives (an entity enabled or disabled, a
device renamed), so `async_listen` also syncs on their events, after a short
quiet period. An event about one of our own entities is ignored: a sync causes
those, and a second one would find nothing to change.
"""

import asyncio
import logging
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN, ENTITY_ID_PREFIX
from ..db.operations.state import get_full_state
from ..db.session import connection as db_connection
from ..domain.appliance_mirrors import desired_mirrors
from ..domain.device_switch import plug_switch_unique_ids
from ..domain.discovery import CoPattern
from ..domain.facilities import (
    FacilityClash,
    FacilityGap,
    SocketFacilities,
    gap_issue_id,
    gap_placeholders,
    stale_gap_issue_ids,
)
from ..domain.facility_rules import StandardFacility
from ..domain.identifiers import FacilityName
from ..entity_slug import mirror_entity_id, reslug
from ..issue_ids import existing_issue_ids
from .entities import MIRROR_CLASSES, MirrorEntity
from .sources import facilities_by_socket

_LOGGER = logging.getLogger(__name__)

# What switch.py hands over to keep the CO plugs: the state just read, and where
# to put the entity ids it could not rename.
SyncPlugs = Callable[[dict[str, Any], set[tuple[str, str]]], None]

# A device being set up gives a burst of registry events; one sync follows
# this many seconds after the last.
REGISTRY_QUIET_SECONDS = 1.0


class MirrorSync:
    def __init__(
        self,
        hass: HomeAssistant,
        *,
        db_path: Path,
        patterns: tuple[CoPattern, ...],
        standard: Mapping[FacilityName, StandardFacility],
    ) -> None:
        self._hass = hass
        self._db_path = db_path
        self._patterns = patterns
        self._standard = standard
        self._adders: dict[str, AddEntitiesCallback] = {}
        # Keyed by (domain, unique_id): two facilities of one Appliance can end
        # alike in different domains, and HA keeps entities apart by domain.
        self._entities: dict[tuple[str, str], MirrorEntity] = {}
        self._sync_plugs: SyncPlugs | None = None
        # The clashes the last sync logged, so a lasting one is logged once.
        self._reported_clashes: set[tuple[str, FacilityClash]] = set()
        self._reported_renames: set[tuple[str, str]] = set()
        # The gaps the last sync logged, so a lasting one is logged once.
        self._reported_gaps: set[FacilityGap] = set()
        self._lock = asyncio.Lock()

    async def async_register(
        self,
        domain: str,
        add_entities: AddEntitiesCallback,
        *,
        sync_plugs: SyncPlugs | None = None,
    ) -> None:
        self._adders[domain] = add_entities
        if sync_plugs is not None:
            self._sync_plugs = sync_plugs
        await self.async_sync()

    async def async_sync(self, *_args: Any) -> None:
        async with self._lock:
            state = await self._hass.async_add_executor_job(self._read_state)
            self._apply(state)

    @callback
    def async_listen(self) -> Callable[[], None]:
        """Sync after HA's entity and device registries change. Returns what
        stops it."""
        debouncer = Debouncer(
            self._hass,
            _LOGGER,
            cooldown=REGISTRY_QUIET_SECONDS,
            immediate=False,
            function=self.async_sync,
        )

        @callback
        def entity_changed(event: Event[er.EventEntityRegistryUpdatedData]) -> None:
            entry = er.async_get(self._hass).async_get(event.data["entity_id"])
            if entry is None or entry.platform != DOMAIN:
                debouncer.async_schedule_call()

        @callback
        def device_changed(_event: Event[dr.EventDeviceRegistryUpdatedData]) -> None:
            debouncer.async_schedule_call()

        unsubscribe_entities = self._hass.bus.async_listen(
            er.EVENT_ENTITY_REGISTRY_UPDATED, entity_changed
        )
        unsubscribe_devices = self._hass.bus.async_listen(
            dr.EVENT_DEVICE_REGISTRY_UPDATED, device_changed
        )

        @callback
        def stop() -> None:
            unsubscribe_entities()
            unsubscribe_devices()
            debouncer.async_shutdown()

        return stop

    def _read_state(self) -> dict[str, Any]:
        with db_connection(self._db_path) as conn:
            return get_full_state(conn)

    def _state_of(self, entity_registry: er.EntityRegistry, source: str) -> State | None:
        entry = entity_registry.async_get(source)
        return self._hass.states.get(entry.entity_id) if entry is not None else None

    def _log_new_clashes(self, facilities: Mapping[str, SocketFacilities]) -> None:
        clashes = {
            (socket_id, clash) for socket_id, found in facilities.items() for clash in found.clashes
        }
        for socket_id, clash in sorted(clashes - self._reported_clashes):
            _LOGGER.warning(
                "Outlet & Appliance Binding: socket %s gives %s.%s from more than one "
                "entity, so it has no mirror.",
                socket_id,
                clash.domain,
                clash.id_suffix,
            )
        self._reported_clashes = clashes

    @callback
    def _report_gaps(self, facilities: Mapping[str, SocketFacilities]) -> None:
        """One Repairs issue and one log line per integration and id the
        sockets in use have no rule for. An issue goes when a later sync no longer
        meets its id, as the near-miss issues do (#356)."""
        gaps = {gap for found in facilities.values() for gap in found.gaps}
        for issue_id in stale_gap_issue_ids(gaps, existing=existing_issue_ids(self._hass)):
            ir.async_delete_issue(self._hass, DOMAIN, issue_id)
        for gap in sorted(gaps):
            ir.async_create_issue(
                self._hass,
                DOMAIN,
                gap_issue_id(gap),
                is_fixable=False,
                is_persistent=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=gap.kind.translation_key,
                translation_placeholders=gap_placeholders(gap),
            )
        for gap in sorted(gaps - self._reported_gaps):
            _LOGGER.warning(
                "Outlet & Appliance Binding: %s %s.%s %s, so its entity has only the vendor name.",
                gap.integration_domain,
                gap.domain,
                gap.key,
                gap.kind.log_reason,
            )
        self._reported_gaps = gaps

    def _log_new_rename_clashes(self, clashes: set[tuple[str, str]]) -> None:
        for entity_id, expected in sorted(clashes - self._reported_renames):
            _LOGGER.warning(
                "Outlet & Appliance Binding: couldn't rename %s to %s -- %s is already "
                "registered to a different entity. Rename or remove the conflicting "
                "entity to clear this -- if two devices swapped names, rename one of "
                "them to something else, wait for a sync, then rename it to what you "
                "wanted.",
                entity_id,
                expected,
                expected,
            )
        self._reported_renames = clashes

    @callback
    def _apply(self, state: dict[str, Any]) -> None:
        facilities = facilities_by_socket(
            self._hass,
            state,
            patterns=self._patterns,
            standard=self._standard,
        )
        self._log_new_clashes(facilities)
        self._report_gaps(facilities)
        specs = [
            spec
            for spec in desired_mirrors(
                appliances=state["appliances"],
                facilities_by_socket=facilities,
                entity_id_prefix=ENTITY_ID_PREFIX,
            )
            if spec.domain in self._adders
        ]
        wanted = {(spec.domain, spec.unique_id) for spec in specs}
        # switch.py's PCO plugs share the `switch` domain with the mirrors.
        wanted.update(
            ("switch", unique_id)
            for unique_id in plug_switch_unique_ids(
                cos=state["cos"], entity_id_prefix=ENTITY_ID_PREFIX
            ).values()
        )
        entity_registry = er.async_get(self._hass)

        # A currently loaded entity's removal cascades from the registry event.
        for entry in list(entity_registry.entities.values()):
            if (
                entry.platform == DOMAIN
                and entry.domain in self._adders
                and (entry.domain, entry.unique_id) not in wanted
            ):
                entity_registry.async_remove(entry.entity_id)
        for key in [key for key in self._entities if key not in wanted]:
            del self._entities[key]

        rename_clashes: set[tuple[str, str]] = set()
        # Before the mirrors are built: a source that makes one raise must not
        # stop the plugs being kept.
        if self._sync_plugs is not None:
            self._sync_plugs(state, rename_clashes)

        added: dict[str, dict[tuple[str, str], MirrorEntity]] = {}
        for spec in specs:
            key = (spec.domain, spec.unique_id)
            existing = self._entities.get(key)
            if existing is not None:
                existing.async_update_spec(spec)
                expected = mirror_entity_id(
                    domain=spec.domain,
                    appliance_label=spec.appliance_label,
                    id_suffix=spec.id_suffix,
                )
                reslug(entity_registry, existing.entity_id, expected, rename_clashes)
                continue
            entity = MIRROR_CLASSES[spec.domain](spec, self._state_of(entity_registry, spec.source))
            added.setdefault(spec.domain, {})[key] = entity
        # Recorded only once added: an entity recorded but never added would be
        # taken for one that exists, and no later sync would add it.
        for domain, entities in added.items():
            self._adders[domain](list(entities.values()))
            self._entities.update(entities)
        self._log_new_rename_clashes(rename_clashes)
