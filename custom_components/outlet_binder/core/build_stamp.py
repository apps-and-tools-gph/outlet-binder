"""The build stamp the panel shows in dialog titles in debug mode (#684).

`v<manifest version>`, plus `+<contents of the deployed-commit file>` when a
dev deploy left one beside this module (scripts/deploy/test-ha/lib/deploy-common.sh
writes it). That file is git-ignored, so a tag's tree never holds one and a
published install shows the version alone.
"""

from pathlib import Path

from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN

# Where a dev deploy leaves the file: beside this module. `async_setup` reads
# from here, and scripts/deploy/test-ha/lib/deploy-common.sh writes to the same
# place, so the read side names its folder once, in the module the file
# belongs beside (#699).
DEPLOYED_COMMIT_DIR = Path(__file__).parent
DEPLOYED_COMMIT_FILE = ".deployed-commit"

# Set once by `async_setup`, which runs once per HA run however often the
# config entry reloads, so the stamp names the code HA is running and not
# the files a later deploy left on disk.
BUILD_STAMP_KEY: HassKey[str | None] = HassKey(f"{DOMAIN}_build_stamp")


def read_deployed_commit(directory: Path) -> str | None:
    """The first line of `directory`'s deployed-commit file, or None when there
    is no such file or it is blank. Blocking: run it in an executor."""
    try:
        text = (directory / DEPLOYED_COMMIT_FILE).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    return first_line.strip() or None


def build_stamp(version: str | None, deployed_commit: str | None) -> str | None:
    """`v<version>` or `v<version>+<deployed_commit>`; None when the manifest
    has no version, since a hash alone does not say which release it follows."""
    if not version:
        return None
    return f"v{version}+{deployed_commit}" if deployed_commit else f"v{version}"
