"""Checks device pattern files from the command line:

    uv run --frozen python -m \\
        custom_components.outlet_binder.device_identification.validate_patterns <path>

Checks one device pattern file, or every pattern file under a patterns
root directory, using pattern_loader.py's own rules -- never a copy of
them (#373). Needs `homeassistant` importable: pattern_loader.py imports
it, and so does the integration's `__init__.py`, which importing any
module under custom_components.outlet_binder runs first.
The JSON Schema alone (`device_patterns_schema.yaml`)
is the piece that needs no dev environment -- this command is not that.

Exits non-zero if any file was skipped. A warning (today only the
unique_id_suffixes + exclude_unique_id_suffixes combination) is printed
but does not affect the exit code, since the loader still loads such a
file.
"""

import argparse
import logging
import sys
from pathlib import Path

from .pattern_loader import LoadResult, iter_pattern_files, process_pattern_path


def _report(pattern_id: str, result: LoadResult) -> bool:
    """Prints one file's outcome and returns whether it counts as ok
    (loaded, with or without a warning) rather than skipped."""
    for warning in result.warnings:
        print(f"{pattern_id}: warning: {warning}")
    if result.skip_reason is not None:
        print(f"{pattern_id}: skipped: {result.skip_reason}")
        return False
    print(f"{pattern_id}: ok")
    return True


def _validate_directory(directory: Path) -> bool:
    ok = True
    for pattern_id, result in iter_pattern_files(directory):
        ok &= _report(pattern_id, result)
    return ok


def _validate_single_file(path: Path) -> bool:
    """The file's patterns root is taken as four levels up
    (integration_domain/Manufacturer/Model/HwVersion-SwVersion.yaml), so
    its integration domain is read from its path, the same as at load
    time."""
    if len(path.parents) < 4:
        print(
            f"{path}: not a valid pattern file path -- expected at least"
            " <root>/integration_domain/Manufacturer/Model/HwVersion-SwVersion.yaml",
            file=sys.stderr,
        )
        return False
    directory = path.parents[3]
    pattern_id, result = process_pattern_path(path, directory)
    return _report(pattern_id, result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate outlet_binder device pattern files against pattern_loader.py's rules."
    )
    parser.add_argument(
        "path",
        type=Path,
        help=(
            "A patterns root directory (integration_domain/Manufacturer/Model/... layout),"
            " or a single pattern file."
        ),
    )
    args = parser.parse_args(argv)

    # Surfaces warnings the loader's own logger emits on stderr --
    # otherwise silent, since a standalone script has no handler configured
    # for HA's logger the way HA itself does.
    logging.basicConfig(level=logging.WARNING)

    # Resolved so single-file mode's "four levels up" is always sensible,
    # whether the user passed a relative or absolute path.
    path: Path = args.path.resolve()
    if not path.exists():
        print(f"{path}: no such file or directory", file=sys.stderr)
        return 2

    ok = _validate_directory(path) if path.is_dir() else _validate_single_file(path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
