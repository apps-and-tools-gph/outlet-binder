"""The one place SQL statement text may appear.

Every SQL statement in this project lives in this package, as a named,
callable Python function, grouped by the domain concept it belongs to --
so that "how does a plug move at the database level?"
is answered by opening exactly one module. A history log lives with the
concept it records rather than in a module of its own, because a log is
that concept's history, not a separate idea.

Two rules keep the import graph acyclic, and both are load-bearing:

- **Modules here never import one another.** A statement that spans two
  concepts is not a fact about either one -- it is a rule about an
  *operation*, and it belongs one layer up, in db/operations/. This is
  what stops `devices` and `sockets` needing each other in both
  directions (plugging a device in validates the socket; deleting a device
  closes the log row of each of its sockets).
- **Modules here never open a transaction.** Transaction boundaries
  belong to db/operations/ alone. Several functions here are called both
  standalone under autocommit and from inside an operation's
  transaction, so opening one would break the second case.

Every function here takes a connection obtained from db/session.py's
`connect`/`connection`. That is the only path that sets
`row_factory = sqlite3.Row`, which every row mapper in this package
depends on for name-based access.

The row mappers hand those values straight into typed dataclass fields
without wrapping them. `sqlite3.Row.__getitem__` returns `Any`, so the id
types (domain/identifiers.py) are *not* checked here, and wrapping each
value would look like enforcement while being none -- worse, for a
nullable column it would claim a value is present when it is `NULL`,
because `NewType` erases to identity. What actually guards this boundary
is that every SELECT names its columns rather than using a wildcard, so
a statement and the mapper consuming its rows can be read against each
other; tests/test_sql_layer_guard.py fails if that slips -- bluntly
enough that it flagged this very paragraph's first draft. The mistake
worth catching here is naming the wrong column, and no type reaches a
string-to-string mapping.

Tests may call into this package directly, but only for schema-invariant
probes (proving a PK or UNIQUE constraint fires) and history-log
assertions. Behavioural tests go through db/operations/, or they are not
exercising the path production uses.
"""
