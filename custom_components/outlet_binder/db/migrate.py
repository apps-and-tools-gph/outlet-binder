"""Schema migration runner for the Outlet & Appliance Binding integration.

Applies the DDL steps db/schema.py lists, in order, tracked via SQLite's
native `PRAGMA user_version`. Writes a rolling pre-migration backup before
touching anything, and restores it if any step fails, rather than leaving a
half-migrated database file in place — this is irreplaceable personal-home
state with no ops team behind it. See docs/LLD.md §12.

Requires `conn` to have been opened with `autocommit=True` (see
db/session.py's `connect`). Transactions are taken via
db/sql/transaction.py's `immediate`, which issues raw
"BEGIN IMMEDIATE"/"COMMIT"/"ROLLBACK" statements rather than the
Connection.commit()/.rollback() methods -- those do not affect a
manually-opened transaction under autocommit=True.

A migration step is an arbitrary callable, so any exception is
reachable; both the per-migration rollback (`immediate`) and the
backup restore below are deliberately broad enough to cover that.
"""

import shutil
import sqlite3
from pathlib import Path

from .schema import MIGRATIONS, Migration
from .sql import pragma, transaction

BACKUP_SUFFIX = ".pre-migration.bak"


class MigrationError(Exception):
    """A migration step failed; the database was restored from backup."""


def _backup_path(db_path: Path) -> Path:
    return db_path.with_name(db_path.name + BACKUP_SUFFIX)


def _write_backup(db_path: Path) -> None:
    """Write a rolling pre-migration backup, overwriting any previous one.

    This is a migration-attempt safety net, not the user-facing
    export/restore feature from docs/LLD.md §14 (separate, later work) — it
    exists only so a failed migration can be undone automatically.
    """
    backup_conn = sqlite3.connect(_backup_path(db_path))
    try:
        source_conn = sqlite3.connect(db_path)
        try:
            source_conn.backup(backup_conn)
        finally:
            source_conn.close()
    finally:
        backup_conn.close()


def _restore_backup(db_path: Path) -> None:
    shutil.copyfile(_backup_path(db_path), db_path)


def apply_pending_migrations(conn: sqlite3.Connection, db_path: Path) -> None:
    """Apply any migrations newer than the database's current user_version.

    `conn` must already be open against `db_path` (same file, same
    connection the caller will keep using afterwards). Raises
    `MigrationError` if any migration step fails; the database file is
    restored to its pre-migration state before the error propagates.
    """
    current_version: int = pragma.get_user_version(conn)
    pending: list[Migration] = [m for m in MIGRATIONS if m.version > current_version]
    if not pending:
        return

    _write_backup(db_path)

    try:
        for migration in pending:
            with transaction.immediate(conn):
                for step in migration.steps:
                    step(conn)
                pragma.set_user_version(conn, migration.version)
    except Exception as err:
        # Deliberately `Exception`, not `sqlite3.Error`. A step is a
        # Callable[[Connection], None], so it can raise anything -- a future
        # data migration that reads rows and transforms them in Python could
        # raise KeyError or ValueError as easily as sqlite3.Error.
        # transaction.immediate would roll that step back, but without this
        # breadth the restore below would never run: an earlier migration in
        # the same batch would stay committed with its user_version bump, and
        # the caller would see the raw error rather than MigrationError --
        # exactly the half-migrated file this module exists to prevent.
        #
        # Not BaseException: a KeyboardInterrupt should propagate untouched
        # rather than be reported as a migration failure. That leaves a
        # genuine (narrow) gap -- an interrupt between two migrations skips
        # the restore -- accepted rather than swallowing interrupts.
        conn.close()
        _restore_backup(db_path)
        raise MigrationError(
            f"Migration to version {migration.version} failed; "
            "database restored from pre-migration backup."
        ) from err
