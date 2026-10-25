"""SQLite bootstrap for the Outlet & Appliance Binding integration.

Opens (creating if needed) the SQLite database and brings its schema up to
date via db/migrate.py on every integration setup. Uses the stdlib
`sqlite3` module via the executor rather than declaring a SQLAlchemy
dependency: Home Assistant core (via Recorder) already pins its own
SQLAlchemy version, and a second application-level pin risks conflicting
with it — see docs/LLD.md §12 for why this is a standing decision, not a
placeholder.
"""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from homeassistant.core import HomeAssistant

from .migrate import apply_pending_migrations
from .sql import pragma

DB_FILENAME = "outlet_binder.db"
BUSY_TIMEOUT_MS = 5000


def get_db_path(hass: HomeAssistant) -> Path:
    return Path(hass.config.path(DB_FILENAME))


def connect(db_path: Path) -> sqlite3.Connection:
    """Open a connection to the integration's SQLite database.

    The caller owns the connection and must close it -- prefer `connection`
    below, which does that for you. Every read and write path in this
    integration must obtain its connection here, so that the autocommit
    mode, `row_factory` and PRAGMAs set below are guaranteed to be in
    force; each db/sql/ module's row mapping depends on `sqlite3.Row`.
    """
    # autocommit=True (real PEP 249-style autocommit, not sqlite3's legacy
    # implicit-transaction mode) gives full manual control over transactions
    # via raw "BEGIN IMMEDIATE"/"COMMIT"/"ROLLBACK" statements — required for
    # the migration runner (db/migrate.py) and the Plugged Into swap
    # (db/sql/transaction.py) to get atomicity right per docs/LLD.md's
    # concurrency section.
    #
    # Gotcha, on this project's own Python 3.14 sqlite3: once
    # a transaction is opened with a raw "BEGIN" statement, the Connection's
    # own .commit()/.rollback() *methods* do NOT affect it — they silently
    # no-op (Connection.in_transaction stays True, nothing rolls back).
    # Always end a manually-opened transaction with a raw "COMMIT"/"ROLLBACK"
    # statement via conn.execute(...), never the .commit()/.rollback()
    # methods, anywhere a transaction was opened this way.
    conn = sqlite3.connect(db_path, autocommit=True)
    conn.row_factory = sqlite3.Row
    pragma.enable_foreign_keys(conn)
    # Lets a concurrent BEGIN IMMEDIATE (db/operations/plug.py's
    # plug) wait for a few seconds rather than fail immediately if another
    # call briefly holds the write lock — per docs/LLD.md's concurrency
    # section. No further concurrency machinery is warranted at this
    # project's stated scale (fewer than 50 objects in normal use).
    pragma.set_busy_timeout(conn, BUSY_TIMEOUT_MS)
    return conn


@contextmanager
def connection(db_path: Path) -> Generator[sqlite3.Connection]:
    """`connect`, closed on the way out -- the preferred entry point.

    Callers should not hand-roll the open / try / `finally: conn.close()`
    dance around `connect`; use this instead.
    """
    conn = connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


async def async_bootstrap(hass: HomeAssistant) -> None:
    """Ensure the SQLite database exists, is reachable, and is up to date.

    Raises db.migrate.MigrationError if a schema migration fails — callers
    (see __init__.py's async_setup_entry) should treat that as a permanent
    setup failure (ConfigEntryError), not something to retry.
    """
    db_path = get_db_path(hass)

    def _init() -> None:
        with connection(db_path) as conn:
            apply_pending_migrations(conn, db_path)

    await hass.async_add_executor_job(_init)
