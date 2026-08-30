#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


START_MARKER = "<!-- repository-knowledge:start -->"
END_MARKER = "<!-- repository-knowledge:end -->"

MARKER_FILES = {
    "AGENTS.md": "agents-section.md",
    "docs/index.md": "docs-index.md",
    "docs/tags.md": "tags.md",
}

OWNED_FILES = {
    ".repository-knowledge.json": "assets/repository-knowledge.json",
    "docs/repository-knowledge.md": "assets/repository-knowledge.md",
    "docs/sources/index.md": "assets/sources-index.md",
    "docs/sources/manifest.json": "assets/sources-manifest.json",
    "bin/docs-lint": "scripts/docs_lint.py",
}


@dataclass(frozen=True)
class Action:
    path: str
    operation: str
    content: bytes | None = None


@dataclass(frozen=True)
class InstallPlan:
    root: Path
    actions: tuple[Action, ...]

    @property
    def conflicts(self) -> tuple[Action, ...]:
        return tuple(
            action for action in self.actions if action.operation == "conflict"
        )


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def is_git_repository(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return False
    if result.returncode != 0:
        return False
    try:
        top_level = Path(result.stdout.strip()).resolve()
    except (OSError, RuntimeError):
        return False
    return top_level == root


def target_is_safe(root: Path, relative_path: str) -> bool:
    target = root / relative_path
    try:
        parent = target.parent.resolve()
    except (OSError, RuntimeError):
        return False
    if not is_within(parent, root):
        return False
    if target.is_symlink():
        return False
    return True


def conflict(path: str) -> Action:
    return Action(path, "conflict")


def plan_owned_file(
    root: Path, skill_root: Path, relative_path: str, asset_path: str
) -> Action:
    target = root / relative_path
    asset = skill_root / asset_path
    if not target_is_safe(root, relative_path) or not asset.is_file():
        return conflict(relative_path)
    try:
        expected = asset.read_bytes()
    except OSError:
        return conflict(relative_path)
    if not target.exists():
        return Action(relative_path, "create", expected)
    if not target.is_file():
        return conflict(relative_path)
    try:
        current = target.read_bytes()
    except OSError:
        return conflict(relative_path)
    if current == expected:
        return Action(relative_path, "unchanged")
    return conflict(relative_path)


def insert_block(current: str, block: str) -> str:
    if not current:
        return block
    separator = "\n" if current.endswith("\n") else "\n\n"
    return current + separator + block


def plan_marker_file(
    root: Path, skill_root: Path, relative_path: str, asset_name: str
) -> Action:
    target = root / relative_path
    asset = skill_root / "assets" / asset_name
    if not target_is_safe(root, relative_path) or not asset.is_file():
        return conflict(relative_path)
    try:
        block = asset.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return conflict(relative_path)
    if block.count(START_MARKER) != 1 or block.count(END_MARKER) != 1:
        return conflict(relative_path)
    if block.index(START_MARKER) > block.index(END_MARKER):
        return conflict(relative_path)
    if not target.exists():
        return Action(relative_path, "create", block.encode("utf-8"))
    if not target.is_file():
        return conflict(relative_path)
    try:
        current = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return conflict(relative_path)

    start_count = current.count(START_MARKER)
    end_count = current.count(END_MARKER)
    if start_count == 0 and end_count == 0:
        updated = insert_block(current, block)
        return Action(relative_path, "insert-block", updated.encode("utf-8"))
    if start_count != 1 or end_count != 1:
        return conflict(relative_path)
    start = current.index(START_MARKER)
    end = current.index(END_MARKER)
    if start > end:
        return conflict(relative_path)
    end += len(END_MARKER)
    updated = current[:start] + block.rstrip("\n") + current[end:]
    if updated == current:
        return Action(relative_path, "unchanged")
    return Action(relative_path, "update-block", updated.encode("utf-8"))


def plan_install(repo: Path, skill_root: Path) -> InstallPlan:
    root = repo.resolve()
    skill_root = skill_root.resolve()
    if not root.is_dir() or not is_git_repository(root):
        return InstallPlan(root, (conflict("."),))

    actions = [
        plan_marker_file(root, skill_root, path, asset)
        for path, asset in MARKER_FILES.items()
    ]
    actions.extend(
        plan_owned_file(root, skill_root, path, asset)
        for path, asset in OWNED_FILES.items()
    )
    return InstallPlan(root, tuple(actions))


def write_atomic(path: Path, content: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            os.fchmod(temporary.fileno(), mode)
        temporary_path.replace(path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def apply_plan(plan: InstallPlan) -> None:
    if plan.conflicts:
        raise ValueError("cannot apply an install plan with conflicts")
    for action in plan.actions:
        if action.operation == "unchanged":
            continue
        if action.content is None:
            raise ValueError(f"missing content for {action.path}")
        target = plan.root / action.path
        if target.exists():
            mode = target.stat().st_mode & 0o777
        elif action.path == "bin/docs-lint":
            mode = 0o755
        else:
            mode = 0o644
        write_atomic(target, action.content, mode)


def print_plan(plan: InstallPlan) -> None:
    changed = False
    for action in plan.actions:
        if action.operation == "unchanged":
            continue
        changed = True
        print(f"{action.operation.upper()} {action.path}")
    if not changed:
        print("No changes")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install the Konsierge repository knowledge protocol"
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args(argv)

    skill_root = Path(__file__).resolve().parents[1]
    plan = plan_install(arguments.repo, skill_root)
    print_plan(plan)
    if plan.conflicts:
        return 2
    if arguments.apply:
        apply_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
