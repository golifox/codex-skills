from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "install.py"
START = "<!-- repository-knowledge:start -->"
END = "<!-- repository-knowledge:end -->"


class InstallTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        subprocess.run(
            ["git", "init", "-q", str(self.root)], check=True, capture_output=True
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_installer(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def load_installer(self):
        spec = importlib.util.spec_from_file_location("knowledge_install", SCRIPT)
        if spec is None or spec.loader is None:
            self.fail(f"cannot load {SCRIPT}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def tree_digest(self) -> str:
        digest = hashlib.sha256()
        for path in sorted(self.root.rglob("*")):
            if ".git" in path.relative_to(self.root).parts or not path.is_file():
                continue
            digest.update(path.relative_to(self.root).as_posix().encode())
            digest.update(path.read_bytes())
            digest.update(str(path.stat().st_mode & 0o777).encode())
        return digest.hexdigest()

    def test_dry_run_lists_creates_without_writing(self) -> None:
        result = self.run_installer()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CREATE .repository-knowledge.json", result.stdout)
        self.assertIn("CREATE bin/docs-lint", result.stdout)
        self.assertEqual(self.tree_digest(), hashlib.sha256().hexdigest())

    def test_apply_creates_required_tree_and_executable_linter(self) -> None:
        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = {
            "AGENTS.md",
            ".repository-knowledge.json",
            "docs/index.md",
            "docs/tags.md",
            "docs/repository-knowledge.md",
            "docs/sources/index.md",
            "docs/sources/manifest.json",
            "bin/docs-lint",
        }
        self.assertTrue(
            expected.issubset(
                {
                    path.relative_to(self.root).as_posix()
                    for path in self.root.rglob("*")
                    if path.is_file()
                }
            )
        )
        self.assertTrue(os.access(self.root / "bin/docs-lint", os.X_OK))
        self.assertEqual(
            (self.root / "docs/repository-knowledge.md").read_bytes(),
            (SKILL_ROOT / "assets/repository-knowledge.md").read_bytes(),
        )

    def test_installed_protocol_matches_canonical_reference(self) -> None:
        self.assertEqual(
            (SKILL_ROOT / "assets/repository-knowledge.md").read_bytes(),
            (SKILL_ROOT / "references/protocol.ru.md").read_bytes(),
        )

    def test_second_apply_has_no_changes(self) -> None:
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        before = self.tree_digest()

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, self.tree_digest())
        self.assertIn("No changes", result.stdout)

    def test_existing_agents_content_is_preserved(self) -> None:
        original = "# Local instructions\n\nKeep this text.\n"
        self.write(self.root / "AGENTS.md", original)

        self.assertEqual(self.run_installer("--apply").returncode, 0)

        content = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith(original))
        self.assertIn(START, content)
        self.assertIn(END, content)

    def test_managed_block_is_updated_without_touching_surrounding_text(self) -> None:
        original = f"before\n{START}\nold\n{END}\nafter\n"
        self.write(self.root / "docs/index.md", original)

        self.assertEqual(self.run_installer("--apply").returncode, 0)

        content = (self.root / "docs/index.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("before\n"))
        self.assertTrue(content.endswith("after\n"))
        self.assertNotIn("\nold\n", content)
        self.assertEqual(content.count(START), 1)
        self.assertEqual(content.count(END), 1)

    def test_divergent_owned_file_blocks_all_apply(self) -> None:
        self.write(self.root / "docs/repository-knowledge.md", "local content\n")
        before = self.tree_digest()

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(before, self.tree_digest())
        self.assertIn("CONFLICT docs/repository-knowledge.md", result.stdout)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_modified_manifest_is_preserved_on_reapply(self) -> None:
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        manifest = self.root / "docs/sources/manifest.json"
        changed = '{"version": 1, "sources": [{"kind": "fixture"}]}\n'
        self.write(manifest, changed)

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(manifest.read_text(encoding="utf-8"), changed)

    def test_malformed_managed_block_blocks_all_apply(self) -> None:
        self.write(self.root / "AGENTS.md", f"local\n{START}\nunterminated\n")
        before = self.tree_digest()

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, self.tree_digest())

    def test_existing_docs_are_not_moved_or_rewritten(self) -> None:
        legacy = self.root / "docs/provider/original.pdf"
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(b"provider bytes\x00\xff")
        before = legacy.read_bytes()

        self.assertEqual(self.run_installer("--apply").returncode, 0)

        self.assertEqual(legacy.read_bytes(), before)
        self.assertTrue(legacy.exists())

    def test_symlink_target_outside_repository_is_a_conflict(self) -> None:
        outside_directory = Path(tempfile.mkdtemp())
        self.addCleanup(
            lambda: outside_directory.rmdir() if outside_directory.exists() else None
        )
        (self.root / "docs").symlink_to(outside_directory, target_is_directory=True)

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(any(outside_directory.iterdir()))
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_non_directory_parent_blocks_all_apply(self) -> None:
        self.write(self.root / "docs", "not a directory\n")
        before = self.tree_digest()

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(before, self.tree_digest())
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_identical_linter_is_made_executable(self) -> None:
        linter = self.root / "bin/docs-lint"
        linter.parent.mkdir(parents=True)
        linter.write_bytes((SKILL_ROOT / "scripts/docs_lint.py").read_bytes())
        linter.chmod(0o644)

        result = self.run_installer("--apply")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.access(linter, os.X_OK))
        self.assertEqual(
            linter.read_bytes(),
            (SKILL_ROOT / "scripts/docs_lint.py").read_bytes(),
        )

    def test_plan_api_reports_conflicts(self) -> None:
        self.write(self.root / "docs/repository-knowledge.md", "divergent\n")

        plan = self.load_installer().plan_install(self.root, SKILL_ROOT)

        self.assertEqual(len(plan.conflicts), 1)
        self.assertEqual(plan.conflicts[0].path, "docs/repository-knowledge.md")


if __name__ == "__main__":
    unittest.main()
