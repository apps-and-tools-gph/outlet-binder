"""Reading this integration's Repairs issues, for the code that prunes a family of
them (the near-miss devices, the facility gaps)."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN


def existing_issue_ids(hass: HomeAssistant) -> frozenset[str]:
    """The id of every Repairs issue `outlet_binder` has raised."""
    return frozenset(
        issue_id for (issue_domain, issue_id) in ir.async_get(hass).issues if issue_domain == DOMAIN
    )
