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

A database whose `user_version` is newer than the newest migration here is
refused before anything is written (`SchemaTooNewError`): older code on a
schema it does not know can fail at random or write wrong data.

A migration with `rebuilds_tables` follows SQLite's 12-step procedure
(sqlite.org/lang_altertable.html, section 7). Foreign keys go off before the
transaction, because the pragma does nothing inside one. `foreign_key_check`
runs before the commit, and any row it returns rolls the migration back and
restores the backup. Foreign keys come back on after the commit. On failure
nothing more runs on the connection once it is closed; a new connection from
db/session.py's `connect` has them on again.
"""

import shutil
import sqlite3
from collections.abc import Sequence
from pathlib import Path

from .schema import MIGRATIONS, Migration
from .sql import pragma, transaction

BACKUP_SUFFIX = ".pre-migration.bak"


class MigrationError(Exception):
    """A migration step failed; the database was restored from backup."""


class SchemaTooNewError(MigrationError):
    """The database is newer than this code; nothing was changed."""

    def __init__(self, database_version: int, latest_version: int) -> None:
        # Both ints go to Exception.__init__, so `args` rebuilds the error when
        # it is copied or pickled; `__str__` supplies the message.
        super().__init__(database_version, latest_version)
        self.database_version = database_version
        self.latest_version = latest_version

    def __str__(self) -> str:
        return (
            f"The database is at schema version {self.database_version}, but this"
            f" version of Outlet & Appliance Binding only knows versions up to"
            f" {self.latest_version}. Install the newer version again, or restore a"
            f" backup of the database."
        )


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


def _apply_steps(conn: sqlite3.Connection, migration: Migration) -> None:
    for step in migration.steps:
        step(conn)
    pragma.set_user_version(conn, migration.version)


def _run_migration(conn: sqlite3.Connection, migration: Migration) -> None:
    if not migration.rebuilds_tables:
        with transaction.immediate(conn):
            _apply_steps(conn, migration)
        return

    pragma.disable_foreign_keys(conn)
    if pragma.foreign_keys_enabled(conn):
        # Dropping a referenced table with enforcement on cascades away the rows
        # that reference it, and `foreign_key_check` then finds nothing wrong.
        raise sqlite3.OperationalError("foreign keys could not be turned off for a table rebuild")
    with transaction.immediate(conn):
        _apply_steps(conn, migration)
        violations = pragma.foreign_key_violations(conn)
        if violations:
            # Raised inside the transaction so it rolls back. IntegrityError
            # because that is what a dangling reference is.
            raise sqlite3.IntegrityError(
                f"Migration to version {migration.version} left dangling"
                f" foreign keys: {violations[:5]}"
            )
    pragma.enable_foreign_keys(conn)


def apply_pending_migrations(conn: sqlite3.Connection, db_path: Path) -> int:
    """Apply any migrations in `MIGRATIONS` newer than the database's current
    user_version.

    Returns how many it applied (0 when the database was already current),
    which db/session.py uses to decide whether a staged edit session is still
    safe to keep.

    `conn` must already be open against `db_path` (same file, same
    connection the caller will keep using afterwards). Raises
    `SchemaTooNewError` for a database newer than the code, before a backup
    is written. Raises `MigrationError` if any migration step fails; the
    database file is restored to its pre-migration state before the error
    propagates.
    """
    return apply_migrations(conn, db_path, migrations=MIGRATIONS)


def apply_migrations(
    conn: sqlite3.Connection, db_path: Path, *, migrations: Sequence[Migration]
) -> int:
    """`apply_pending_migrations` for a given list, which must not be empty.

    Production never calls this directly: the snapshot tool and its guards use
    it to build the schema as of an earlier version.
    """
    if not migrations:
        raise ValueError("there are no migrations to apply")
    current_version: int = pragma.get_user_version(conn)
    latest_version = migrations[-1].version
    if current_version > latest_version:
        raise SchemaTooNewError(current_version, latest_version)
    pending: list[Migration] = [m for m in migrations if m.version > current_version]
    if not pending:
        return 0

    _write_backup(db_path)

    try:
        for migration in pending:
            _run_migration(conn, migration)
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
    return len(pending)
