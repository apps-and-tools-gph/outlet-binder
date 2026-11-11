"""The schema migration manifest -- which DDL runs, in what order.

Contains no SQL itself. Each migration's DDL is a module of literal SQL in
db/sql/migrations/ (`m0001_initial.py` for Migration 1), in the order its
statements run; this module records which migrations exist and what each runs.

Each Migration is applied as one atomic transaction and bumps
`PRAGMA user_version` to its own version number in the same transaction --
see db/migrate.py.

`PRAGMA foreign_keys = ON` is set once per connection in db/session.py,
not here: it cannot be changed inside a transaction, so it can't be a
migration step. The runner alone turns it off, outside the transaction, for a
migration with `rebuilds_tables` (db/migrate.py).

The schema is frozen (`SCHEMA_FROZEN`): each change is a new migration, never
an edit to an existing one (docs/MIGRATIONS.md).
"""

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from .sql.migrations import m0001_initial, sql_step

type MigrationStep = Callable[[sqlite3.Connection], None]


@dataclass(frozen=True)
class Migration:
    """One versioned, atomically-applied schema change."""

    version: int
    steps: tuple[MigrationStep, ...]
    # True when a step drops and recreates a table that others reference, so
    # the runner follows SQLite's 12-step rebuild procedure (foreign keys off
    # outside the transaction, `foreign_key_check` before the commit).
    rebuilds_tables: bool = False


# Every migration on `main` is frozen: tests/test_frozen_migrations_guard.py
# refuses an edit to one, and a schema change is a new migration
# (docs/MIGRATIONS.md).
SCHEMA_FROZEN: bool = True

_MIGRATION_1_INITIAL_SCHEMA: Migration = Migration(
    version=1,
    steps=tuple(sql_step(statement) for statement in m0001_initial.STATEMENTS),
)

MIGRATIONS: tuple[Migration, ...] = (_MIGRATION_1_INITIAL_SCHEMA,)
