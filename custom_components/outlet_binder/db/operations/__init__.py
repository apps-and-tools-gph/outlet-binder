"""Persistence operations: transactions and cross-concept sequencing.

Contains no SQL text -- every statement it runs comes from a named
function in db/sql/. What lives here is the part that is *not* a fact
about any single concept: the transaction boundary, the order writes
happen in, and the validation that raises before any of them do.

Every operation here is cross-concept, which is exactly why none of them
could live in a db/sql/ module. Deleting a CO closes history rows
belonging to the Plugged Into concept; plugging an Appliance in validates
against the Appliance and CO Socket concepts first. Those are rules about
an operation, not facts about a table -- and pushing them down into
db/sql/ would make its modules import each other, which is what the split
exists to prevent.

Modules here never import one another either. Each takes what it needs
straight from db/sql/.

The edit-session engine (issue #189) needs to call four of these whole
operations by name to replay staged commands, which would break this
rule from the inside -- so it lives one layer up, at db/edit_session.py,
the same place websocket_api.py already calls them from today. See that
module's own docstring.
"""
