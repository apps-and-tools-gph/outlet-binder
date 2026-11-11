"""Whether a staged edit session survives an upgrade. Pure, like the rest of domain/.

Staged commands are replayed by command name and payload key, which a release
can change, or what a command does, with no schema change at all. Only a check
of the version that opened the session catches that. What is lost by
discarding is uncommitted staging, and an upgrade in the middle of a session
is rare.
"""


def should_discard_session(
    *,
    entry_count: int,
    opened_by_version: str | None,
    running_version: str,
    migrations_applied: int,
) -> bool:
    """True when the session's staged entries must be thrown away at setup.

    A session is open when the log has entries; the `edit_session` row alone
    says nothing, because it is never deleted. It is discarded when another OB
    version opened it (an entry with no recorded version counts as another), or
    when any migration ran in this setup: dev deploys to the test instance keep
    the manifest version, so a branch migration that rewrites ids would
    otherwise run under a session whose version still matches.
    """
    if entry_count == 0:
        return False
    return opened_by_version != running_version or migrations_applied > 0
