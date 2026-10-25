"""The transaction-control statements: BEGIN IMMEDIATE, COMMIT, ROLLBACK."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def immediate(conn: sqlite3.Connection) -> Generator[None]:
    """Run a block inside one `BEGIN IMMEDIATE` transaction.

    COMMITs if the block completes, ROLLBACKs if anything at all escapes
    it. `BEGIN IMMEDIATE` rather than plain `BEGIN` is deliberate: it takes
    the write lock up front, so two concurrent writers queue on
    `busy_timeout` instead of one failing late at COMMIT (docs/LLD.md's
    concurrency section).

    Ends the transaction with raw "COMMIT"/"ROLLBACK" *statements*, never
    the Connection.commit()/.rollback() methods. Under the `autocommit=True`
    connections this project opens (db/session.py's `connect`), those
    methods silently no-op against a manually-opened transaction -- and,
    worse, the same connection still reads back its own uncommitted rows,
    so a test that writes and reads on one connection would keep passing
    while nothing was ever persisted. Do not "simplify" this to
    `conn.commit()`.

    Catches BaseException, not Exception, deliberately: a KeyboardInterrupt
    or a cancelled task must still release the write lock rather than leave
    this connection holding it for the rest of its life.

    Never nested. SQLite has no nested transactions -- a second BEGIN
    raises OperationalError -- so this raises RuntimeError up front with a
    clearer message. Only db/operations/ may call this; db/sql/ modules
    never open a transaction of their own.
    """
    if conn.in_transaction:
        raise RuntimeError(
            "A transaction is already open on this connection. SQLite has no"
            " nested transactions: db/sql/ modules must never open one, and"
            " db/operations/ must not nest them."
        )
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
