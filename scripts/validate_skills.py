#!/usr/bin/env python3
"""Validate skill frontmatter and local Markdown links in a skill catalog."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)?(`{3,}|~{3,})")
FRONTMATTER_PATTERN = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def skill_directories(catalog_root: Path) -> list[Path]:
    """Find catalog skills at the root and in the reserved .system namespace."""
    candidates = list(catalog_root.iterdir())
    system_root = catalog_root / ".system"
    if system_root.is_dir():
        candidates.extend(system_root.iterdir())
    return sorted(
        (path for path in candidates if (path / "SKILL.md").is_file()),
        key=lambda path: str(path),
    )


def markdown_lines(content: str):
    """Yield source lines outside fenced code blocks."""
    fence_char = None
    fence_size = 0
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = FENCE_PATTERN.match(line)
        if match:
            marker = match.group(1)
            if fence_char is None:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = None, 0
            continue
        if fence_char is None:
            yield line_number, line


def broken_links(skill_file: Path) -> list[str]:
    """Return unresolved relative Markdown link targets with source locations."""
    errors = []
    content = skill_file.read_text(encoding="utf-8")
    for line_number, line in markdown_lines(content):
        for match in LINK_PATTERN.finditer(line):
            destination = match.group(1).strip()
            if destination.startswith("<") and ">" in destination:
                destination = destination[1 : destination.index(">")]
            else:
                destination = destination.split(maxsplit=1)[0]

            if not destination or destination.startswith("#") or destination.startswith("//"):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination):
                continue

            path_part = unquote(destination.split("#", maxsplit=1)[0].split("?", maxsplit=1)[0])
            if not path_part:
                continue
            target = (skill_file.parent / path_part).resolve()
            if not target.exists():
                errors.append(f"{skill_file}:{line_number}: broken local link: {destination}")
    return errors


def frontmatter_errors(skill_file: Path) -> list[str]:
    """Check skill frontmatter shape and required metadata."""
    content = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return ["missing or malformed YAML frontmatter"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        return [f"invalid YAML frontmatter: {error}"]
    if not isinstance(frontmatter, dict):
        return ["frontmatter must be a YAML mapping"]

    errors = []
    unexpected_keys = set(frontmatter) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        errors.append(f"unsupported frontmatter keys: {', '.join(sorted(unexpected_keys))}")

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("missing or invalid 'name'")
    elif (
        len(name.strip()) > MAX_SKILL_NAME_LENGTH
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip())
    ):
        errors.append("'name' must be lowercase hyphen-case, at most 64 characters")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("missing or invalid 'description'")
    elif len(description.strip()) > MAX_DESCRIPTION_LENGTH:
        errors.append("'description' exceeds 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("'description' cannot contain angle brackets")
    elif description.strip().startswith("[TODO:"):
        errors.append("'description' contains an unfinished TODO placeholder")

    body = content[match.end() :]
    if any(
        re.fullmatch(r" {0,3}\[TODO:[^\n]*\][ \t]*", line)
        for _, line in markdown_lines(body)
    ):
        errors.append("skill instructions contain an unfinished TODO placeholder")
    return errors


def validate_catalog(catalog_root: Path) -> int:
    skills = skill_directories(catalog_root)
    if not skills:
        print(f"FAIL: no SKILL.md files found in {catalog_root}", file=sys.stderr)
        return 1

    errors = []
    for skill_directory in skills:
        skill_file = skill_directory / "SKILL.md"
        errors.extend(
            f"{skill_file}: {error}" for error in frontmatter_errors(skill_file)
        )
        errors.extend(broken_links(skill_file))

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"Failed: {len(errors)} issue(s) across {len(skills)} skills.", file=sys.stderr)
        return 1

    print(f"Valid: {len(skills)} skills; frontmatter and local Markdown links pass.")
    return 0


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}):
        print(f"Usage: {Path(sys.argv[0]).name} [catalog-root]")
        return 0 if len(sys.argv) == 2 else 2
    catalog_root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parent.parent
    if not catalog_root.is_dir():
        print(f"FAIL: catalog root not found: {catalog_root}", file=sys.stderr)
        return 1
    return validate_catalog(catalog_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
