"""The schema migration manifest -- which DDL runs, in what order.

Contains no SQL itself. Each step is a named function in the db/sql/
concept module that owns the table, so a column change touches one file
rather than two; this module records only the ordering, which is not
derivable from the concept modules alone (a table must exist before
another references it).

Each Migration is applied as one atomic transaction and bumps
`PRAGMA user_version` to its own version number in the same transaction --
see db/migrate.py.

`PRAGMA foreign_keys = ON` is set once per connection in db/session.py,
not here: it cannot be changed inside a transaction, so it can't be a
migration step.

Migration 1 is rewritten in place rather than superseded by a new one when
the schema changes -- a deliberate, repeated exception to the "each
migration is its own immutable, already-applied step" policy (docs/LLD.md
§12), safe only because no real installed base exists yet to protect
(pre-release, test-instance-only). See CHANGELOG.md for the history of
what's changed.
"""

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from .sql import devices, edit_session, plug_log, sockets

type MigrationStep = Callable[[sqlite3.Connection], None]


@dataclass(frozen=True)
class Migration:
    """One versioned, atomically-applied schema change."""

    version: int
    steps: tuple[MigrationStep, ...]


_MIGRATION_1_INITIAL_SCHEMA: Migration = Migration(
    version=1,
    steps=(
        # `devices` and `sockets` reference each other (a socket's owner, a
        # device's plug); SQLite looks a foreign key's parent up only when a
        # row is written, so the order between the two does not matter.
        devices.create_table,
        devices.create_co_name_index,
        devices.create_uo_name_index,
        devices.create_appliance_name_type_index,
        sockets.create_table,
        plug_log.create_table,
        plug_log.create_open_device_index,
        plug_log.create_open_socket_index,
        # No FK dependency on anything above -- edit_log's payload is an
        # opaque JSON blob of ids, not typed columns (issue #189).
        edit_session.create_log_table,
        edit_session.create_session_table,
    ),
)

MIGRATIONS: tuple[Migration, ...] = (_MIGRATION_1_INITIAL_SCHEMA,)
