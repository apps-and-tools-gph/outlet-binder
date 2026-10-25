"""Generates the "Quick reference" table in
custom_components/outlet_binder/device_identification/device_patterns/README.md directly
from device_patterns_schema.yaml (#374) -- the schema is the single source of
truth for the pattern format; this only renders it as prose, it never
re-derives or duplicates the rules themselves.

Deliberately narrower than "generate the whole file": the README's
rationale, worked examples and version-matching tables are more than a
description can hold and aren't mechanically derivable from the schema
alone, so they stay hand-written. What *is* mechanically regenerated is
the whole "Quick reference" table region -- everything strictly between
the `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` marker lines
(the convention docs/database/generate_er.py uses).

A role ($defs.role) is shared by device.all_on_off, sockets.on_off and
sockets.monitoring -- rather than repeating its fields three times, it's
rendered once in its own table and the three referencing keys just link
to it, the same deduplication the schema itself makes via $ref.

Run manually after a schema change to regenerate the table in place:

    uv run --frozen python -m \\
        custom_components.outlet_binder.device_identification.generate_pattern_reference
"""

import re
from pathlib import Path

from homeassistant.util.yaml import load_yaml_dict

from .pattern_loader import PATTERN_SCHEMA_PATH, PATTERNS_DIR

# Imported (not redefined) from pattern_loader.py: a second, independent
# path constant here is exactly the drift risk #372 exists to eliminate for
# the schema's own content -- it shouldn't reappear for the path to it.
README_PATH = PATTERNS_DIR / "README.md"

_BEGIN_MARKER = (
    "<!-- BEGIN GENERATED:"
    " custom_components/outlet_binder/device_identification/generate_pattern_reference.py"
    " -- do not hand-edit below -->"
)
_END_MARKER = "<!-- END GENERATED -->"


def type_label(subschema: dict) -> str:
    if "enum" in subschema:
        return " or ".join(f"`{value}`" for value in subschema["enum"])
    schema_type = subschema.get("type")
    if schema_type == "array":
        item_type = subschema.get("items", {}).get("type", "any")
        return f"list of {item_type}"
    if isinstance(schema_type, str):
        return schema_type
    return "any"


def _direct_refs(schema: dict) -> list[str]:
    """$defs names $ref'd anywhere in schema's own reachable properties
    -- recursing into a plain (non-$ref) nested object the same way
    rows_for_object does, in declaration order, deduplicated."""
    names: list[str] = []
    for subschema in schema.get("properties", {}).values():
        ref = subschema.get("$ref")
        if ref is not None:
            name = ref.rsplit("/", 1)[-1]
            if name not in names:
                names.append(name)
        elif subschema.get("type") == "object":
            names += [name for name in _direct_refs(subschema) if name not in names]
    return names


def all_referenced_defs(schema: dict, defs: dict) -> list[str]:
    """Every $defs name reachable from schema, transitively (a $def can
    itself $ref another -- role refs identified_by), in first-seen
    order, so the table documents exactly what this schema uses, and
    deterministically."""
    ordered: list[str] = []
    queue = list(_direct_refs(schema))
    while queue:
        name = queue.pop(0)
        if name in ordered:
            continue
        ordered.append(name)
        queue += [n for n in _direct_refs(defs[name]) if n not in ordered]
    return ordered


def rows_for_object(schema: dict, *, prefix: str = "") -> list[tuple[str, str, str, str]]:
    """One (key, type, required, meaning) row per key in schema's own
    properties, recursing into a nested object that ISN'T a $ref (its
    keys are inlined here, dotted under prefix, since they only ever
    mean one thing in this one place -- e.g. sockets.count). A $ref
    stops the recursion instead: $ref is JSON Schema's own "define once,
    use many" mechanism, so that def gets its own table (see
    all_referenced_defs), documented once rather than inlined at every
    place that references it."""
    required = set(schema.get("required", ()))
    rows = []
    for name, subschema in schema.get("properties", {}).items():
        key = f"{prefix}.{name}" if prefix else name
        is_required = "required" if name in required else "optional"
        description = " ".join(subschema.get("description", "").split())
        ref = subschema.get("$ref")
        if ref is not None:
            def_name = ref.rsplit("/", 1)[-1]
            rows.append((f"`{key}`", f"[{def_name}](#{def_name})", is_required, description))
        elif subschema.get("type") == "object":
            rows.append((f"`{key}`", "object", is_required, description))
            rows += rows_for_object(subschema, prefix=key)
        else:
            rows.append((f"`{key}`", type_label(subschema), is_required, description))
    return rows


def render_table(rows: list[tuple[str, str, str, str]]) -> str:
    lines = ["| Key | Type | Required | Meaning |", "| --- | --- | --- | --- |"]
    lines += [
        f"| {key} | {type_text} | {required} | {meaning} |"
        for key, type_text, required, meaning in rows
    ]
    return "\n".join(lines)


def render_generated_region() -> str:
    """The full new content for the marker interior -- pure (only reads
    the two schema files, no README I/O), so it can be unit-tested
    directly."""
    pattern_schema = load_yaml_dict(PATTERN_SCHEMA_PATH)
    defs = pattern_schema.get("$defs", {})

    sections = [("Device pattern file", rows_for_object(pattern_schema))]
    sections += [
        (name, rows_for_object(defs[name])) for name in all_referenced_defs(pattern_schema, defs)
    ]

    return "\n\n".join(f"### {title}\n\n{render_table(rows)}" for title, rows in sections)


def _marker_span(markdown_text: str) -> tuple[int, int]:
    """(index just after _BEGIN_MARKER, index of _END_MARKER) in
    markdown_text -- validates there is exactly one of each marker, in
    order. Raises ValueError naming the exact marker strings otherwise:
    a broken marker pair must fail loudly rather than silently losing
    the ability to regenerate the table at all."""
    begin_count = markdown_text.count(_BEGIN_MARKER)
    end_count = markdown_text.count(_END_MARKER)
    if begin_count != 1 or end_count != 1:
        raise ValueError(
            f"expected exactly one {_BEGIN_MARKER!r} and one {_END_MARKER!r} marker in"
            f" {README_PATH} (found {begin_count} of the first, {end_count} of the second)"
        )
    begin_index = markdown_text.index(_BEGIN_MARKER) + len(_BEGIN_MARKER)
    end_index = markdown_text.index(_END_MARKER)
    if end_index < begin_index:
        raise ValueError(
            f"{_END_MARKER!r} appears before {_BEGIN_MARKER!r} in {README_PATH} -- the"
            " generated-region markers are out of order."
        )
    return begin_index, end_index


def extract_generated_region(markdown_text: str) -> str:
    """The text strictly between the generated-region markers."""
    begin_index, end_index = _marker_span(markdown_text)
    return markdown_text[begin_index:end_index].strip("\n")


def replace_generated_region(markdown_text: str, new_region_body: str) -> str:
    """markdown_text with the generated-region markers' interior replaced
    by new_region_body; everything outside the markers (headings,
    rationale, worked examples) is untouched."""
    begin_index, end_index = _marker_span(markdown_text)
    return f"{markdown_text[:begin_index]}\n\n{new_region_body}\n\n{markdown_text[end_index:]}"


_MODELINE_RE = re.compile(r"^# yaml-language-server: \$schema=(\S+)\s*$")


def modeline_schema_path(yaml_path: Path) -> Path | None:
    """The schema path a yaml-language-server modeline on yaml_path's
    first line resolves to (yaml-language-server itself resolves a
    modeline's relative path from the YAML file's own location), or
    None if the first line isn't such a modeline at all."""
    with yaml_path.open(encoding="utf-8") as f:
        first_line = f.readline()
    match = _MODELINE_RE.match(first_line.rstrip("\n"))
    if match is None:
        return None
    return (yaml_path.parent / match.group(1)).resolve()


def main() -> None:
    old_text = README_PATH.read_text()
    extract_generated_region(old_text)  # loud failure if the marker pair is broken
    new_region = render_generated_region()
    new_text = replace_generated_region(old_text, new_region)
    if new_text == old_text:
        print(f"{README_PATH} already up to date.")
        return
    README_PATH.write_text(new_text)
    print(f"Regenerated {README_PATH}.")


if __name__ == "__main__":
    main()
