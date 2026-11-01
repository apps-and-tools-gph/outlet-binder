"""The database layer for the Outlet & Appliance Binding integration.

Everything that knows SQLite lives in this package. Every SQL statement
is in `sql/`, grouped by domain concept; `operations/` owns transactions
and cross-concept sequencing; `schema.py` is the SQL-free manifest naming
which DDL steps run in what order; `session.py` owns connections and
`migrate.py` the migration runner. No module outside this package opens a
connection for itself or executes SQL.

`connect`/`connection` are re-exported here so callers have one obvious
public entrance, and `Connection` lets them annotate a connection without
importing `sqlite3` for the type alone.
"""

import sqlite3

from .session import connect, connection

type Connection = sqlite3.Connection

__all__ = ["Connection", "connect", "connection"]
