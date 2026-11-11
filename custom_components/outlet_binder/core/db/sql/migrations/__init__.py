"""One module per migration, each holding that migration's DDL as literal SQL.

`sql_step` turns one statement into the step callable core/db/migrate.py runs.
"""

import sqlite3
from collections.abc import Callable


def sql_step(statement: str) -> Callable[[sqlite3.Connection], None]:
    """A migration step that runs `statement` as it is written."""

    def step(conn: sqlite3.Connection) -> None:
        conn.execute(statement)

    return step
