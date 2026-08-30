from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "docs_lint.py"


class DocsLintTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.make_repository(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, path: Path, content: str | bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")

    def make_repository(self, root: Path) -> None:
        self.write(root / "AGENTS.md", "Read [docs](docs/index.md).\n")
        self.write(
            root / ".repository-knowledge.json",
            json.dumps(
                {
                    "version": 1,
                    "docs_root": "docs",
                    "managed_roots": ["docs/domains"],
                    "excluded_paths": [],
                    "sources_manifest": "docs/sources/manifest.json",
                }
            ),
        )
        self.write(
            root / "docs/index.md",
            "- [Protocol](repository-knowledge.md) — Protocol.\n"
            "- [Tags](tags.md) — Tags.\n"
            "- [Sources](sources/index.md) — Sources.\n"
            "- [Orders](domains/orders.md) — Orders.\n",
        )
        self.write(
            root / "docs/tags.md",
            "- `@tag:orders/creation` — Order creation — "
            "owner: [Orders](domains/orders.md)\n",
        )
        self.write(root / "docs/repository-knowledge.md", "# Protocol\n")
        self.write(root / "docs/sources/index.md", "# Sources\n")
        self.write(
            root / "docs/sources/manifest.json",
            '{"version": 1, "sources": []}\n',
        )
        self.write(
            root / "docs/domains/orders.md",
            "<!-- knowledge-tags: @tag:orders/creation -->\n# Orders\n",
        )
        self.write(
            root / "app/services/create_order.rb",
            "# @tag:orders/creation\nclass CreateOrder\nend\n",
        )
        self.write(root / "bin/docs-lint", "#!/usr/bin/env python3\n")

    def load_linter(self):
        spec = importlib.util.spec_from_file_location("docs_lint", SCRIPT)
        if spec is None or spec.loader is None:
            self.fail(f"cannot load {SCRIPT}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_minimal_repository_is_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root)],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 error(s), 0 warning(s)", result.stdout)

    def issue_codes(self) -> set[str]:
        return {issue.code for issue in self.load_linter().lint_repository(self.root)}

    def issues_for(self, code: str):
        return [
            issue
            for issue in self.load_linter().lint_repository(self.root)
            if issue.code == code
        ]

    def test_invalid_configuration_is_an_error(self) -> None:
        self.write(self.root / ".repository-knowledge.json", "not-json\n")

        self.assertIn("invalid-config", self.issue_codes())

    def test_invalid_configuration_shape_is_an_error(self) -> None:
        self.write(
            self.root / ".repository-knowledge.json",
            json.dumps(
                {
                    "version": 2,
                    "docs_root": "../docs",
                    "managed_roots": "docs/domains",
                    "excluded_paths": [],
                    "sources_manifest": "/tmp/manifest.json",
                }
            ),
        )

        self.assertIn("invalid-config", self.issue_codes())

    def rewrite_config(self, **changes) -> None:
        config = json.loads(
            (self.root / ".repository-knowledge.json").read_text(encoding="utf-8")
        )
        config.update(changes)
        self.write(self.root / ".repository-knowledge.json", json.dumps(config))

    def test_unsupported_protocol_version_is_an_error(self) -> None:
        self.rewrite_config(version=2)

        self.assertIn("invalid-config", self.issue_codes())

    def test_managed_roots_must_be_an_array(self) -> None:
        self.rewrite_config(managed_roots="docs/domains")

        self.assertIn("invalid-config", self.issue_codes())

    def test_configuration_paths_must_stay_inside_repository(self) -> None:
        self.rewrite_config(docs_root="../outside")

        self.assertIn("invalid-config", self.issue_codes())

    def test_managed_markdown_symlink_outside_repository_is_an_error(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        (self.root / "docs/domains/outside.md").symlink_to(outside)

        self.assertIn("unsafe-path", self.issue_codes())

    def test_missing_required_file_is_an_error(self) -> None:
        (self.root / "docs/tags.md").unlink()

        self.assertIn("missing-required-file", self.issue_codes())

    def test_missing_relative_markdown_target_is_an_error(self) -> None:
        self.write(
            self.root / "docs/domains/orders.md",
            "<!-- knowledge-tags: @tag:orders/creation -->\n"
            "# Orders\n"
            "[Missing](missing.md)\n",
        )

        self.assertIn("broken-link", self.issue_codes())

    def test_unlinked_managed_page_is_an_error(self) -> None:
        self.write(self.root / "docs/domains/orphan.md", "# Orphan\n")

        self.assertIn("orphan-page", self.issue_codes())

    def test_unmanaged_document_is_a_warning(self) -> None:
        self.write(self.root / "docs/legacy.md", "# Legacy\n")

        issues = self.issues_for("unmanaged-documentation")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "warning")
        self.assertEqual(issues[0].path, "docs/legacy.md")

    def register_tag(self, tag: str) -> None:
        tags_path = self.root / "docs/tags.md"
        with tags_path.open("a", encoding="utf-8") as tags:
            tags.write(
                f"- `{tag}` — Fixture tag — "
                "owner: [Orders](domains/orders.md)\n"
            )

    def test_invalid_tag_slug_is_an_error(self) -> None:
        self.write(
            self.root / "docs/domains/orders.md",
            "<!-- knowledge-tags: @tag:Bad_Tag -->\n# Orders\n",
        )

        self.assertIn("invalid-tag", self.issue_codes())

    def test_unregistered_tag_is_an_error(self) -> None:
        with (self.root / "docs/domains/orders.md").open(
            "a", encoding="utf-8"
        ) as page:
            page.write("@tag:orders/retry\n")
        with (self.root / "app/services/create_order.rb").open(
            "a", encoding="utf-8"
        ) as source:
            source.write("# @tag:orders/retry\n")

        self.assertIn("unregistered-tag", self.issue_codes())

    def test_duplicate_registry_entry_is_an_error(self) -> None:
        self.register_tag("@tag:orders/creation")

        self.assertIn("duplicate-tag", self.issue_codes())

    def test_tag_used_only_in_documentation_is_an_error(self) -> None:
        self.register_tag("@tag:orders/retry")
        with (self.root / "docs/domains/orders.md").open(
            "a", encoding="utf-8"
        ) as page:
            page.write("@tag:orders/retry\n")

        self.assertIn("one-sided-tag", self.issue_codes())

    def test_tag_used_only_in_code_is_an_error(self) -> None:
        self.register_tag("@tag:orders/retry")
        with (self.root / "app/services/create_order.rb").open(
            "a", encoding="utf-8"
        ) as source:
            source.write("# @tag:orders/retry\n")

        self.assertIn("one-sided-tag", self.issue_codes())

    def test_knowledge_tags_after_heading_is_an_error(self) -> None:
        self.write(
            self.root / "docs/domains/orders.md",
            "# Orders\n<!-- knowledge-tags: @tag:orders/creation -->\n",
        )

        self.assertIn("misplaced-knowledge-tags", self.issue_codes())

    def test_unused_registered_tag_is_a_warning(self) -> None:
        self.register_tag("@tag:orders/retry")

        issues = self.issues_for("unused-tag")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "warning")

    def write_manifest(self, sources: list[dict]) -> None:
        self.write(
            self.root / "docs/sources/manifest.json",
            json.dumps({"version": 1, "sources": sources}, ensure_ascii=False),
        )

    def track(self, path: Path) -> None:
        if not (self.root / ".git").exists():
            subprocess.run(
                ["git", "init", "-q", str(self.root)],
                check=True,
                capture_output=True,
            )
        subprocess.run(
            ["git", "-C", str(self.root), "add", "--", str(path)],
            check=True,
            capture_output=True,
        )

    def add_provider_snapshot(self, sha256: str) -> None:
        self.write(self.root / "docs/mir-pass.json", '{"openapi":"3.0.3"}\n')
        self.write_manifest(
            [
                {
                    "id": "nspk-api-1.0",
                    "path": "docs/mir-pass.json",
                    "kind": "provider-snapshot",
                    "provider": "АО НСПК",
                    "version": "1.0",
                    "sha256": sha256,
                    "distribution": "restricted",
                    "obtained_from": "provider portal",
                    "obtained_at": "2026-08-31",
                    "derived_documents": [],
                }
            ]
        )

    def test_valid_restricted_snapshot_is_pinned_with_a_warning(self) -> None:
        self.add_provider_snapshot(
            "8ab4580cee6d59c31fc6e21d4fe0f6596b2239a5da41e6ca4aef844903b92483"
        )

        issues = self.load_linter().lint_repository(self.root)

        self.assertFalse([issue for issue in issues if issue.severity == "error"])
        self.assertIn("restricted-source", {issue.code for issue in issues})

    def test_changed_snapshot_hash_is_an_error(self) -> None:
        self.add_provider_snapshot("0" * 64)

        self.assertIn("snapshot-hash-mismatch", self.issue_codes())

    def test_snapshot_metadata_must_be_nonempty_strings(self) -> None:
        self.write(self.root / "docs/source.json", "{}\n")
        self.write_manifest(
            [
                {
                    "id": "",
                    "path": "docs/source.json",
                    "kind": "provider-snapshot",
                    "provider": "",
                    "version": "",
                    "sha256": "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
                    "distribution": "internal",
                    "obtained_from": "unknown",
                    "obtained_at": "unknown",
                }
            ]
        )

        self.assertIn("invalid-source-entry", self.issue_codes())

    def test_snapshot_requires_explicit_provenance(self) -> None:
        self.write(self.root / "docs/source.json", "{}\n")
        self.write_manifest(
            [
                {
                    "id": "provider-api-1.0",
                    "path": "docs/source.json",
                    "kind": "provider-snapshot",
                    "provider": "Provider",
                    "version": "1.0",
                    "sha256": "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
                    "distribution": "internal",
                }
            ]
        )

        self.assertIn("invalid-source-entry", self.issue_codes())

    def test_derived_document_with_unknown_source_is_a_warning(self) -> None:
        self.write(self.root / "docs/mir-pass.md", "# Generated API\n")
        self.write_manifest(
            [
                {
                    "path": "docs/mir-pass.md",
                    "kind": "provider-derived",
                    "source": "missing-source",
                    "source_version": "1.0",
                    "status": "current",
                }
            ]
        )

        issues = self.issues_for("missing-derived-source")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "warning")

    def test_derived_document_source_version_mismatch_is_a_warning(self) -> None:
        self.write(self.root / "docs/source.json", "{}\n")
        self.write(self.root / "docs/derived.md", "# Derived\n")
        self.write_manifest(
            [
                {
                    "id": "provider-api-2.0",
                    "path": "docs/source.json",
                    "kind": "provider-snapshot",
                    "provider": "Provider",
                    "version": "2.0",
                    "sha256": "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
                    "distribution": "internal",
                    "obtained_from": "provider portal",
                    "obtained_at": "2026-08-31",
                    "derived_documents": ["docs/derived.md"],
                },
                {
                    "path": "docs/derived.md",
                    "kind": "provider-derived",
                    "source": "provider-api-2.0",
                    "source_version": "1.0",
                    "status": "source-version-mismatch",
                },
            ]
        )

        issues = self.issues_for("source-version-mismatch")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "warning")

    def test_derived_document_requires_status_and_source_version(self) -> None:
        self.write(self.root / "docs/derived.md", "# Derived\n")
        self.write_manifest(
            [
                {
                    "path": "docs/derived.md",
                    "kind": "provider-derived",
                    "source": "missing",
                    "source_version": "",
                    "status": "invented",
                }
            ]
        )

        self.assertIn("invalid-source-entry", self.issue_codes())

    def test_source_manifest_version_must_be_one(self) -> None:
        self.write(
            self.root / "docs/sources/manifest.json",
            json.dumps({"version": 2, "sources": []}),
        )

        self.assertIn("invalid-source-manifest", self.issue_codes())

    def test_unclassified_dari_like_file_is_an_error(self) -> None:
        path = self.root / "docs/attachments/0000_Dari_credentials.csv"
        self.write(path, "real-looking-data\n")
        self.track(path)

        self.assertIn("unclassified-credential-file", self.issue_codes())

    def test_ignored_dari_like_file_is_not_reported(self) -> None:
        path = self.root / "docs/attachments/0000_Dari_local.csv"
        self.write(path, "local-untracked-data\n")
        self.write(self.root / ".gitignore", "*Dari*.csv\n")
        self.track(self.root / "AGENTS.md")

        self.assertNotIn("unclassified-credential-file", self.issue_codes())

    def test_ignored_source_file_is_not_scanned_for_tags(self) -> None:
        self.write(self.root / ".env.local", "@tag:Invalid_Tag\n")
        self.write(self.root / ".gitignore", ".env.local\n")
        self.track(self.root / "AGENTS.md")

        self.assertNotIn("invalid-tag", self.issue_codes())

    def test_explicit_synthetic_dari_fixture_is_allowed(self) -> None:
        path = self.root / "docs/attachments/0000_Dari_example.csv"
        self.write(path, "synthetic-data\n")
        self.track(path)
        self.write_manifest(
            [
                {
                    "path": "docs/attachments/0000_Dari_example.csv",
                    "kind": "synthetic-fixture",
                    "synthetic": True,
                }
            ]
        )

        self.assertNotIn("unclassified-credential-file", self.issue_codes())

    def test_synthetic_fixture_path_must_exist(self) -> None:
        self.write_manifest(
            [
                {
                    "path": "docs/attachments/missing.csv",
                    "kind": "synthetic-fixture",
                    "synthetic": True,
                }
            ]
        )

        self.assertIn("missing-source-file", self.issue_codes())


if __name__ == "__main__":
    unittest.main()
