"""The PRAGMA statements that configure a connection or track schema version.

PRAGMA cannot take a bound parameter, so the setters below interpolate.
Every value they interpolate is either this project's own static data
(a migration version from core/db/schema.py) or an int the caller controls --
never anything user-supplied. The setters take `int`, so a string cannot
reach the statement in the first place.
"""

import sqlite3


def enable_foreign_keys(conn: sqlite3.Connection) -> None:
    """Turn on foreign-key enforcement, which SQLite leaves off by default.

    Per-connection, not stored in the database file, so every connection
    must do this -- which is why core/db/session.py's `connect` is the only
    sanctioned way to open one. core/db/migrate.py turns it off around a table
    rebuild and back on after the commit.
    """
    conn.execute("PRAGMA foreign_keys = ON")


def disable_foreign_keys(conn: sqlite3.Connection) -> None:
    """Turn foreign-key enforcement off for a table rebuild.

    SQLite ignores this inside a transaction, so core/db/migrate.py calls it
    before `BEGIN IMMEDIATE`: dropping the old table would otherwise delete
    the rows that other tables reference. See sqlite.org/lang_altertable.html,
    section 7.
    """
    conn.execute("PRAGMA foreign_keys = OFF")


def foreign_keys_enabled(conn: sqlite3.Connection) -> bool:
    (enabled,) = conn.execute("PRAGMA foreign_keys").fetchone()
    return bool(enabled)


def foreign_key_violations(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """Every row whose foreign key points at nothing, as (table, parent table).
    Reads the whole database whether or not enforcement is on."""
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [(row["table"], row["parent"]) for row in rows]


def integrity_problems(conn: sqlite3.Connection) -> list[str]:
    """What `PRAGMA integrity_check` reports; empty when the database is sound."""
    messages = [row[0] for row in conn.execute("PRAGMA integrity_check").fetchall()]
    return [] if messages == ["ok"] else messages


def set_busy_timeout(conn: sqlite3.Connection, milliseconds: int) -> None:
    """Wait rather than fail immediately when another connection holds the
    write lock -- lets a concurrent `BEGIN IMMEDIATE` queue briefly instead
    of raising. See docs/LLD.md's concurrency section."""
    conn.execute(f"PRAGMA busy_timeout = {int(milliseconds)}")


def get_user_version(conn: sqlite3.Connection) -> int:
    """The database's schema version, as tracked by core/db/migrate.py.

    SQLite's own `user_version` field: 0 on a freshly created file, which
    is exactly what the migration runner needs it to be.
    """
    (version,) = conn.execute("PRAGMA user_version").fetchone()
    return version


def set_user_version(conn: sqlite3.Connection, version: int) -> None:
    """Record that migrations up to `version` have been applied."""
    conn.execute(f"PRAGMA user_version = {int(version)}")
