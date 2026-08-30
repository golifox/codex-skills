#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
TAG_PATTERN = re.compile(
    r"@tag:[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*"
)
TAG_CANDIDATE_PATTERN = re.compile(r"@tag:[^\s<>\"'`)]+")
TAG_REGISTRY_PATTERN = re.compile(
    r"^-\s+`(?P<tag>@tag:[^`]+)`.+?owner:\s*\[[^\]]+\]\((?P<owner>[^)]+)\)",
    re.MULTILINE,
)
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".bundle",
    ".cache",
    ".idea",
    ".vscode",
    "coverage",
    "log",
    "node_modules",
    "tmp",
    "vendor",
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, order=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


def load_json(path: Path, issues: list[Issue], code: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        issues.append(Issue("error", code, str(path), str(error)))
        return None


def validate_required_files(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> None:
    docs_root = Path(str(config.get("docs_root", "docs")))
    manifest = Path(
        str(config.get("sources_manifest", docs_root / "sources/manifest.json"))
    )
    required = (
        Path("AGENTS.md"),
        docs_root / "index.md",
        docs_root / "tags.md",
        docs_root / "repository-knowledge.md",
        docs_root / "sources/index.md",
        manifest,
        Path("bin/docs-lint"),
    )
    for relative_path in required:
        if not (root / relative_path).is_file():
            issues.append(
                Issue(
                    "error",
                    "missing-required-file",
                    relative_path.as_posix(),
                    "required protocol file is missing",
                )
            )


def configured_paths(config: dict[str, Any], key: str) -> tuple[Path, ...]:
    value = config.get(key, [])
    if not isinstance(value, list):
        return ()
    return tuple(Path(item) for item in value if isinstance(item, str))


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def relative_name(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def path_matches(path: Path, candidates: tuple[Path, ...]) -> bool:
    return any(path == candidate or is_within(path, candidate) for candidate in candidates)


def managed_markdown_paths(
    root: Path, config: dict[str, Any]
) -> tuple[set[Path], set[Path], Path]:
    docs_root = (root / str(config.get("docs_root", "docs"))).resolve()
    managed_roots = tuple(
        (root / path).resolve() for path in configured_paths(config, "managed_roots")
    )
    excluded = tuple(
        (root / path).resolve() for path in configured_paths(config, "excluded_paths")
    )
    core = {
        docs_root / "index.md",
        docs_root / "tags.md",
        docs_root / "repository-knowledge.md",
        docs_root / "sources/index.md",
    }
    managed: set[Path] = set()
    unmanaged: set[Path] = set()
    if not docs_root.is_dir():
        return managed, unmanaged, docs_root
    for path in docs_root.rglob("*.md"):
        resolved = path.resolve()
        if not is_within(resolved, root):
            continue
        if path_matches(resolved, excluded):
            continue
        if resolved in core or path_matches(resolved, managed_roots):
            managed.add(resolved)
        elif not is_within(resolved, docs_root / "sources"):
            unmanaged.add(resolved)
    return managed, unmanaged, docs_root


def markdown_targets(page: Path, root: Path) -> list[Path]:
    try:
        content = page.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    targets: list[Path] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(content):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        raw_target = raw_target.split(maxsplit=1)[0]
        parsed = urlsplit(raw_target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if parsed.path.startswith("/"):
            continue
        target = (page.parent / unquote(parsed.path)).resolve()
        if target.is_dir():
            target = target / "index.md"
        targets.append(target)
    return targets


def validate_markdown(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> None:
    managed, _, docs_root = managed_markdown_paths(root, config)
    if docs_root.is_dir():
        for path in docs_root.rglob("*.md"):
            if path.is_symlink() and not is_within(path.resolve(), root):
                issues.append(
                    Issue(
                        "error",
                        "unsafe-path",
                        path.relative_to(root).as_posix(),
                        "managed documentation symlink resolves outside the repository",
                    )
                )
    graph: dict[Path, set[Path]] = {page: set() for page in managed}
    for page in managed:
        for target in markdown_targets(page, root):
            if not is_within(target, root) or not target.exists():
                issues.append(
                    Issue(
                        "error",
                        "broken-link",
                        relative_name(root, page),
                        f"relative link target does not exist: {target}",
                    )
                )
                continue
            if target in managed:
                graph[page].add(target)

    entrypoint = docs_root / "index.md"
    reachable: set[Path] = set()
    pending = [entrypoint] if entrypoint in managed else []
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(graph.get(current, ()))
    for page in sorted(managed - reachable):
        issues.append(
            Issue(
                "error",
                "orphan-page",
                relative_name(root, page),
                "managed page is not reachable from docs/index.md",
            )
        )


def validate_unmanaged_docs(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> None:
    _, unmanaged, _ = managed_markdown_paths(root, config)
    for page in sorted(unmanaged):
        issues.append(
            Issue(
                "warning",
                "unmanaged-documentation",
                relative_name(root, page),
                "document is outside the protocol-managed roots",
            )
        )


def read_text(path: Path) -> str | None:
    try:
        content = path.read_bytes()
    except OSError:
        return None
    if b"\0" in content:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def tag_candidates(content: str) -> set[str]:
    return set(TAG_CANDIDATE_PATTERN.findall(content))


def source_text_paths(
    root: Path, config: dict[str, Any], docs_root: Path
) -> list[Path]:
    excluded = tuple(
        (root / path).resolve() for path in configured_paths(config, "excluded_paths")
    )
    ignored_files = {
        (root / ".repository-knowledge.json").resolve(),
        (root / "bin/docs-lint").resolve(),
    }
    paths: list[Path] = []
    candidates = repository_paths(root, include_untracked=True)
    if candidates is None:
        candidates = [path.resolve() for path in root.rglob("*")]
    for path in candidates:
        if not path.is_file() or path.is_symlink():
            continue
        resolved = path.resolve()
        if not is_within(resolved, root):
            continue
        relative_parts = resolved.relative_to(root).parts
        if any(part in IGNORED_DIRECTORY_NAMES for part in relative_parts):
            continue
        if is_within(resolved, docs_root) or path_matches(resolved, excluded):
            continue
        if resolved in ignored_files or resolved.suffix.lower() == ".md":
            continue
        paths.append(resolved)
    return paths


def validate_knowledge_tag_position(
    root: Path, path: Path, content: str, issues: list[Issue]
) -> None:
    if "knowledge-tags:" not in content:
        return
    first_content_line = next(
        (line.strip() for line in content.splitlines() if line.strip()), ""
    )
    if not (
        first_content_line.startswith("<!-- knowledge-tags:")
        and first_content_line.endswith("-->")
    ):
        issues.append(
            Issue(
                "error",
                "misplaced-knowledge-tags",
                relative_name(root, path),
                "knowledge-tags must be the first non-blank line",
            )
        )


def validate_tags(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> None:
    managed, _, docs_root = managed_markdown_paths(root, config)
    registry_path = docs_root / "tags.md"
    registry_content = read_text(registry_path) or ""
    registry_entries = list(TAG_REGISTRY_PATTERN.finditer(registry_content))
    registered: dict[str, int] = {}
    for entry in registry_entries:
        tag = entry.group("tag")
        registered[tag] = registered.get(tag, 0) + 1
        if TAG_PATTERN.fullmatch(tag) is None:
            issues.append(
                Issue(
                    "error",
                    "invalid-tag",
                    relative_name(root, registry_path),
                    f"invalid registry tag: {tag}",
                )
            )
    for tag, count in registered.items():
        if count > 1:
            issues.append(
                Issue(
                    "error",
                    "duplicate-tag",
                    relative_name(root, registry_path),
                    f"tag is registered {count} times: {tag}",
                )
            )

    documentation_usage: dict[str, set[Path]] = {}
    ignored_markdown = {
        registry_path.resolve(),
        (docs_root / "repository-knowledge.md").resolve(),
    }
    for path in managed:
        content = read_text(path)
        if content is None:
            continue
        validate_knowledge_tag_position(root, path, content, issues)
        if path in ignored_markdown:
            continue
        for candidate in tag_candidates(content):
            if TAG_PATTERN.fullmatch(candidate) is None:
                issues.append(
                    Issue(
                        "error",
                        "invalid-tag",
                        relative_name(root, path),
                        f"invalid tag token: {candidate}",
                    )
                )
                continue
            documentation_usage.setdefault(candidate, set()).add(path)

    code_usage: dict[str, set[Path]] = {}
    for path in source_text_paths(root, config, docs_root):
        content = read_text(path)
        if content is None:
            continue
        for candidate in tag_candidates(content):
            if TAG_PATTERN.fullmatch(candidate) is None:
                issues.append(
                    Issue(
                        "error",
                        "invalid-tag",
                        relative_name(root, path),
                        f"invalid tag token: {candidate}",
                    )
                )
                continue
            code_usage.setdefault(candidate, set()).add(path)

    used_tags = set(documentation_usage) | set(code_usage)
    for tag in sorted(used_tags - set(registered)):
        paths = documentation_usage.get(tag, set()) | code_usage.get(tag, set())
        issues.append(
            Issue(
                "error",
                "unregistered-tag",
                relative_name(root, min(paths)),
                f"tag is used but not registered: {tag}",
            )
        )
    for tag in sorted(registered):
        in_docs = bool(documentation_usage.get(tag))
        in_code = bool(code_usage.get(tag))
        if in_docs != in_code:
            issues.append(
                Issue(
                    "error",
                    "one-sided-tag",
                    relative_name(root, registry_path),
                    f"tag must occur in both documentation and code: {tag}",
                )
            )
        elif not in_docs:
            issues.append(
                Issue(
                    "warning",
                    "unused-tag",
                    relative_name(root, registry_path),
                    f"registered tag has no usage: {tag}",
                )
            )


def safe_repository_path(root: Path, value: object) -> Path | None:
    if not isinstance(value, str):
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return None
    resolved = (root / candidate).resolve()
    return resolved if is_within(resolved, root) else None


def validate_config(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> bool:
    messages: list[str] = []
    if config.get("version") != 1:
        messages.append("version must be 1")
    docs_root = safe_repository_path(root, config.get("docs_root"))
    if docs_root is None:
        messages.append("docs_root must be a relative path inside the repository")
    manifest_path = safe_repository_path(root, config.get("sources_manifest"))
    if manifest_path is None:
        messages.append(
            "sources_manifest must be a relative path inside the repository"
        )
    for key in ("managed_roots", "excluded_paths"):
        value = config.get(key)
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            messages.append(f"{key} must be an array of relative paths")
            continue
        for item in value:
            resolved = safe_repository_path(root, item)
            if resolved is None:
                messages.append(f"{key} contains a path outside the repository: {item}")
            elif key == "managed_roots" and docs_root is not None and not is_within(
                resolved, docs_root
            ):
                messages.append(f"managed root must be inside docs_root: {item}")
    for message in messages:
        issues.append(
            Issue(
                "error",
                "invalid-config",
                ".repository-knowledge.json",
                message,
            )
        )
    return not messages


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_paths(root: Path, *, include_untracked: bool) -> list[Path] | None:
    command = ["git", "-C", str(root), "ls-files"]
    if include_untracked:
        command.extend(["--cached", "--others", "--exclude-standard"])
    command.append("-z")
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return [(root / name).resolve() for name in names if name]


def tracked_paths(root: Path) -> list[Path] | None:
    return repository_paths(root, include_untracked=False)


def validate_snapshot(
    root: Path,
    entry: dict[str, Any],
    issues: list[Issue],
) -> tuple[str | None, str | None]:
    required_fields = {
        "id",
        "path",
        "provider",
        "version",
        "sha256",
        "distribution",
    }
    missing_fields = sorted(required_fields - set(entry))
    display_path = str(entry.get("path", "docs/sources/manifest.json"))
    if missing_fields:
        issues.append(
            Issue(
                "error",
                "invalid-source-entry",
                display_path,
                f"provider snapshot is missing: {', '.join(missing_fields)}",
            )
        )
        return None, None
    for field in ("id", "path", "provider", "version"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(
                Issue(
                    "error",
                    "invalid-source-entry",
                    display_path,
                    f"{field} must be a non-empty string",
                )
            )
    source_path = safe_repository_path(root, entry.get("path"))
    if source_path is None or not source_path.is_file():
        issues.append(
            Issue(
                "error",
                "missing-source-file",
                display_path,
                "provider snapshot path is missing or outside the repository",
            )
        )
        return str(entry.get("id")), str(entry.get("version"))
    expected_hash = entry.get("sha256")
    if not isinstance(expected_hash, str) or SHA256_PATTERN.fullmatch(
        expected_hash
    ) is None:
        issues.append(
            Issue(
                "error",
                "invalid-source-entry",
                display_path,
                "sha256 must contain 64 lowercase hexadecimal characters",
            )
        )
    elif file_sha256(source_path) != expected_hash:
        issues.append(
            Issue(
                "error",
                "snapshot-hash-mismatch",
                display_path,
                "provider snapshot bytes differ from the manifest",
            )
        )
    distribution = entry.get("distribution")
    if distribution not in {"internal", "restricted", "public"}:
        issues.append(
            Issue(
                "error",
                "invalid-source-entry",
                display_path,
                "distribution must be internal, restricted, or public",
            )
        )
    elif distribution == "restricted":
        issues.append(
            Issue(
                "warning",
                "restricted-source",
                display_path,
                "verify that this snapshot is not published outside its allowed scope",
            )
        )
    return str(entry.get("id")), str(entry.get("version"))


def validate_sources(
    root: Path, config: dict[str, Any], issues: list[Issue]
) -> None:
    manifest_path = safe_repository_path(root, config.get("sources_manifest"))
    if manifest_path is None:
        issues.append(
            Issue(
                "error",
                "invalid-config",
                ".repository-knowledge.json",
                "sources_manifest must stay inside the repository",
            )
        )
        return
    manifest = load_json(manifest_path, issues, "invalid-source-manifest")
    if manifest is None:
        return
    if not isinstance(manifest, dict) or not isinstance(
        manifest.get("sources"), list
    ):
        issues.append(
            Issue(
                "error",
                "invalid-source-manifest",
                relative_name(root, manifest_path),
                "manifest must be an object with a sources array",
            )
        )
        return

    entries = [entry for entry in manifest["sources"] if isinstance(entry, dict)]
    if len(entries) != len(manifest["sources"]):
        issues.append(
            Issue(
                "error",
                "invalid-source-entry",
                relative_name(root, manifest_path),
                "every source entry must be a JSON object",
            )
        )
    snapshots: dict[str, tuple[str, str]] = {}
    classified_synthetic: set[str] = set()
    derived_entries: list[dict[str, Any]] = []
    for entry in entries:
        kind = entry.get("kind")
        if kind == "provider-snapshot":
            source_id, version = validate_snapshot(root, entry, issues)
            if source_id is not None and version is not None:
                if source_id in snapshots:
                    issues.append(
                        Issue(
                            "error",
                            "duplicate-source-id",
                            str(entry.get("path", relative_name(root, manifest_path))),
                            f"source id is duplicated: {source_id}",
                        )
                    )
                snapshots[source_id] = (version, str(entry.get("path")))
        elif kind == "provider-derived":
            derived_entries.append(entry)
        elif kind == "synthetic-fixture":
            fixture_path = safe_repository_path(root, entry.get("path"))
            if entry.get("synthetic") is not True or fixture_path is None:
                issues.append(
                    Issue(
                        "error",
                        "invalid-source-entry",
                        str(entry.get("path", relative_name(root, manifest_path))),
                        "synthetic fixture requires synthetic: true and a safe path",
                    )
                )
            elif not fixture_path.is_file():
                issues.append(
                    Issue(
                        "error",
                        "missing-source-file",
                        str(entry.get("path")),
                        "synthetic fixture path does not exist",
                    )
                )
            else:
                classified_synthetic.add(relative_name(root, fixture_path).casefold())
        else:
            issues.append(
                Issue(
                    "error",
                    "invalid-source-kind",
                    str(entry.get("path", relative_name(root, manifest_path))),
                    f"unsupported source kind: {kind}",
                )
            )

    for entry in derived_entries:
        display_path = str(entry.get("path", relative_name(root, manifest_path)))
        derived_path = safe_repository_path(root, entry.get("path"))
        if derived_path is None or not derived_path.is_file():
            issues.append(
                Issue(
                    "error",
                    "missing-source-file",
                    display_path,
                    "provider-derived document is missing or outside the repository",
                )
            )
        source_id = entry.get("source")
        if not isinstance(source_id, str) or source_id not in snapshots:
            issues.append(
                Issue(
                    "warning",
                    "missing-derived-source",
                    display_path,
                    f"provider-derived document references unknown source: {source_id}",
                )
            )
            continue
        snapshot_version = snapshots[source_id][0]
        if entry.get("source_version") != snapshot_version:
            issues.append(
                Issue(
                    "warning",
                    "source-version-mismatch",
                    display_path,
                    f"derived source version {entry.get('source_version')} differs from {snapshot_version}",
                )
            )

    credential_candidates = tracked_paths(root)
    if credential_candidates is None:
        credential_candidates = [path.resolve() for path in root.rglob("*")]
    for path in credential_candidates:
        if not path.is_file() or path.is_symlink():
            continue
        resolved = path.resolve()
        if not is_within(resolved, root):
            continue
        parts = resolved.relative_to(root).parts
        if any(part in IGNORED_DIRECTORY_NAMES for part in parts):
            continue
        relative = relative_name(root, resolved)
        if "dari" in resolved.name.casefold() and resolved.suffix.casefold() == ".csv":
            if relative.casefold() not in classified_synthetic:
                issues.append(
                    Issue(
                        "error",
                        "unclassified-credential-file",
                        relative,
                        "DARI-like CSV must not be tracked unless explicitly synthetic",
                    )
                )


def lint_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    config = load_json(
        root / ".repository-knowledge.json", issues, "invalid-config"
    )
    if not isinstance(config, dict):
        if config is not None:
            issues.append(
                Issue(
                    "error",
                    "invalid-config",
                    ".repository-knowledge.json",
                    "configuration must be a JSON object",
                )
            )
        return sorted(set(issues))
    if not validate_config(root, config, issues):
        return sorted(set(issues))
    validate_required_files(root, config, issues)
    validate_markdown(root, config, issues)
    validate_tags(root, config, issues)
    validate_sources(root, config, issues)
    validate_unmanaged_docs(root, config, issues)
    return sorted(set(issues))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint repository knowledge")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args(argv)
    issues = lint_repository(arguments.root)
    for issue in issues:
        print(
            f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}"
        )
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
