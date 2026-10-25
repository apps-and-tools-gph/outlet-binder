"""Reading the schema back out of SQLite: sqlite_master and the PRAGMAs.

Used by db/migrate.py, by docs/database/generate_er.py to build the ER
diagram from the real schema, and by the tests that check both. Before
this module existed the same PRAGMAs were hand-written in each of those
places, with results unpacked by positional index (`row[3]` for notnull),
so the four copies could drift.

PRAGMA cannot bind an identifier, so the table/index name has to be
interpolated. Every function that does so validates the name first --
that check is the reason this is the only place in the project allowed to
interpolate one.
"""

import re
import sqlite3
from dataclasses import dataclass

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(name: str) -> str:
    """Reject anything that isn't a plain SQLite identifier.

    PRAGMA takes no bound parameters, so callers below interpolate this
    return value directly into a statement. Everything reaching it today
    is this project's own static data, but validating here means that
    stays true even if a caller ever passes something it read at runtime.
    """
    if not _IDENTIFIER.match(name):
        raise ValueError(f"Not a valid SQLite identifier: {name!r}")
    return name


@dataclass(frozen=True)
class Column:
    """One row of `PRAGMA table_xinfo`.

    `hidden` is `0` for an ordinary column, `2` for a `VIRTUAL` generated
    column, `3` for a `STORED` one -- only `table_xinfo` exposes this;
    `table_info` (used before issue #185) silently omits generated columns
    entirely, which is what let them go undocumented in `er.md` with no
    way for the drift guard to catch it.
    """

    name: str
    sqlite_type: str
    notnull: bool
    is_primary_key: bool
    hidden: int = 0


@dataclass(frozen=True)
class ForeignKey:
    """One row of `PRAGMA foreign_key_list`: `column` REFERENCES
    `references_table`(`references_column`)."""

    column: str
    references_table: str
    references_column: str


@dataclass(frozen=True)
class Index:
    """One row of `PRAGMA index_list`.

    `origin` is SQLite's own code for how the index came about: "u" for a
    standalone UNIQUE constraint, "pk" for a primary key's own index, "c"
    for an explicit CREATE INDEX.

    `partial` is true for a `CREATE UNIQUE INDEX ... WHERE ...` index --
    e.g. `ux_plug_log_open_device`, which only guarantees at most
    one *currently-open* row per device, not uniqueness across the whole
    log table. `unique and partial` is a real, narrower invariant than
    `unique` alone, and callers that mean "this column is unique across
    the whole table" (docs/database/generate_er.py's `UK` tag) must check
    it -- issue #185 found `partial` unchecked there, which would have
    mislabelled three pre-existing partial indexes as full uniqueness the
    moment origin `"c"` started being considered at all.
    """

    name: str
    unique: bool
    origin: str
    partial: bool


def table_names(conn: sqlite3.Connection) -> set[str]:
    """Every real table, excluding SQLite's own internal `sqlite_*` ones."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row["name"] for row in rows}


def columns(conn: sqlite3.Connection, table: str) -> list[Column]:
    """Every column of `table`, in declared order -- generated columns
    included (`table_xinfo`, not `table_info`, which omits them)."""
    rows = conn.execute(f"PRAGMA table_xinfo({_identifier(table)})").fetchall()
    return [
        Column(
            name=row["name"],
            sqlite_type=row["type"],
            notnull=bool(row["notnull"]),
            is_primary_key=bool(row["pk"]),
            hidden=row["hidden"],
        )
        for row in rows
    ]


def foreign_keys(conn: sqlite3.Connection, table: str) -> list[ForeignKey]:
    """Every DB-enforced foreign key declared on `table`."""
    rows = conn.execute(f"PRAGMA foreign_key_list({_identifier(table)})").fetchall()
    return [
        ForeignKey(
            column=row["from"],
            references_table=row["table"],
            references_column=row["to"],
        )
        for row in rows
    ]


def indexes(conn: sqlite3.Connection, table: str) -> list[Index]:
    """Every index on `table`, including those SQLite created implicitly."""
    rows = conn.execute(f"PRAGMA index_list({_identifier(table)})").fetchall()
    return [
        Index(
            name=row["name"],
            unique=bool(row["unique"]),
            origin=row["origin"],
            partial=bool(row["partial"]),
        )
        for row in rows
    ]


def index_columns(conn: sqlite3.Connection, index_name: str) -> list[str]:
    """The column names an index covers, in index order."""
    rows = conn.execute(f"PRAGMA index_info({_identifier(index_name)})").fetchall()
    return [row["name"] for row in rows]
