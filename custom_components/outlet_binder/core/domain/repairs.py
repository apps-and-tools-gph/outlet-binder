"""Pruning Repairs issues by id prefix. Pure, like the rest of domain/.

Each family of issues (a near-miss device, a facility gap) has its own id prefix,
so pruning one family's stale issues can never delete another family's.
"""

from collections.abc import Iterable


def stale_issue_ids(
    current: Iterable[str], *, prefix: str, existing: frozenset[str]
) -> frozenset[str]:
    """Every id in `existing` that starts with `prefix` and is not in `current`.
    An id outside the prefix is never returned, so `existing` need not be
    filtered first and this cannot prune an unrelated `outlet_binder` issue."""
    current_ids = set(current)
    return frozenset(
        issue_id
        for issue_id in existing
        if issue_id.startswith(prefix) and issue_id not in current_ids
    )
