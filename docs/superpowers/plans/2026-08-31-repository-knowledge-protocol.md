# Repository Knowledge Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a Russian-language repository knowledge protocol, deterministic local linter, safe installer skill, and separate migration skill in `golifox/codex-skills`.

**Architecture:** The installer owns one canonical protocol and copies or inserts small managed artifacts into a target repository without moving existing documentation. A Python 3 stdlib linter validates managed knowledge, tags, links, source manifests, and immutable provider snapshots; migration remains a separately invoked, approval-gated agent workflow.

**Tech Stack:** Markdown, Python 3 stdlib (`argparse`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`, `unittest`), Codex skill metadata, Git.

**Spec:** `docs/superpowers/specs/2026-08-31-repository-knowledge-protocol-design.md`

## Global Constraints

- Do not modify target repositories or `.gitlab-ci.yml` while building the skills.
- Use only Python 3 standard-library modules in installer, linter, and tests.
- Preserve existing files; update only explicitly marked managed blocks.
- Never classify an external file as provider-supplied, public, safe, or immutable without evidence.
- Never add real credentials, PII, DARI pools, provider secrets, or copied restricted source material to fixtures.
- Keep protocol prose canonical in `install-repository-knowledge/references/protocol.ru.md`; generated target protocol content comes from that file.
- Work and commit only on `KON-0000`; never push the feature branch.
- The repository has only the `master` delivery target. Push `master` only after all checks and local merge succeed.

## File Map

- `install-repository-knowledge/scripts/docs_lint.py` — standalone linter copied to target `bin/docs-lint`.
- `install-repository-knowledge/tests/test_docs_lint.py` — linter unit and MirPass-like fixture coverage.
- `install-repository-knowledge/scripts/install.py` — dry-run/apply installer with conflict detection and managed blocks.
- `install-repository-knowledge/tests/test_install.py` — fresh, existing-file, conflict, and idempotence tests.
- `install-repository-knowledge/references/protocol.ru.md` — canonical normative protocol.
- `install-repository-knowledge/assets/*.md|*.json` — initial managed blocks and machine-readable defaults.
- `install-repository-knowledge/SKILL.md` — discovery and installation workflow.
- `install-repository-knowledge/agents/openai.yaml` — UI metadata.
- `migrate-repository-knowledge/SKILL.md` — approval-gated migration workflow.
- `migrate-repository-knowledge/agents/openai.yaml` — UI metadata.

---

### Task 1: Deterministic repository knowledge linter

**Files:**
- Create: `install-repository-knowledge/scripts/docs_lint.py`
- Create: `install-repository-knowledge/tests/test_docs_lint.py`

**Interfaces:**
- Consumes: repository root containing `.repository-knowledge.json`.
- Produces: `Issue(severity: str, code: str, path: str, message: str)`, `lint_repository(root: Path) -> list[Issue]`, and CLI exit status `1` when any issue has severity `error`, otherwise `0`.

- [ ] **Step 1: Add fixture helpers and a passing minimal-repository test**

Create a `unittest.TestCase` that imports the script with `importlib.util`, creates files under `tempfile.TemporaryDirectory`, and writes this minimal contract:

```python
def make_repository(self, root: Path) -> None:
    self.write(root / "AGENTS.md", "Read [docs](docs/index.md).\n")
    self.write(root / ".repository-knowledge.json", json.dumps({
        "version": 1,
        "docs_root": "docs",
        "managed_roots": ["docs/domains"],
        "excluded_paths": [],
        "sources_manifest": "docs/sources/manifest.json",
    }))
    self.write(root / "docs/index.md", "- [Orders](domains/orders.md) — Orders.\n")
    self.write(root / "docs/tags.md", (
        "- `@tag:orders/creation` — Order creation — "
        "owner: [Orders](domains/orders.md)\n"
    ))
    self.write(root / "docs/repository-knowledge.md", "# Protocol\n")
    self.write(root / "docs/sources/index.md", "# Sources\n")
    self.write(root / "docs/sources/manifest.json", '{"version": 1, "sources": []}\n')
    self.write(root / "bin/docs-lint", "#!/usr/bin/env python3\n")
    self.write(root / "docs/domains/orders.md", (
        "<!-- knowledge-tags: @tag:orders/creation -->\n# Orders\n"
    ))
    self.write(root / "app/services/create_order.rb", (
        "# @tag:orders/creation\nclass CreateOrder\nend\n"
    ))
```

Assert `lint_repository(root) == []`.

- [ ] **Step 2: Run the minimal test and verify RED**

Run:

```bash
python3 -m unittest install-repository-knowledge/tests/test_docs_lint.py -v
```

Expected: import or attribute failure because `docs_lint.py` does not exist.

- [ ] **Step 3: Implement configuration, issue reporting, and required-file checks**

Implement:

```python
@dataclass(frozen=True, order=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


def lint_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    config = load_json(root / ".repository-knowledge.json", issues, "invalid-config")
    if config is None:
        return sorted(issues)
    validate_required_files(root, config, issues)
    validate_markdown(root, config, issues)
    validate_tags(root, config, issues)
    validate_sources(root, config, issues)
    validate_unmanaged_docs(root, config, issues)
    return sorted(set(issues))
```

Require `AGENTS.md`, `docs/index.md`, `docs/tags.md`,
`docs/repository-knowledge.md`, `docs/sources/index.md`, the configured source
manifest, and `bin/docs-lint`.

- [ ] **Step 4: Add RED tests for links, reachability, and unmanaged docs**

Add focused tests asserting these codes:

```python
self.assertCodes(root, "broken-link")
self.assertCodes(root, "orphan-page")
self.assertWarningCodes(root, "unmanaged-documentation")
```

Use one fixture mutation per test: a missing relative target, an unlinked file
inside `managed_roots`, and a Markdown file outside managed roots.

- [ ] **Step 5: Implement managed Markdown graph validation**

Parse ordinary inline Markdown links, ignore `http:`, `https:`, `mailto:`, pure
anchors, and images, strip URL fragments, percent-decode paths, and resolve
relative to the containing page. Build a graph of managed Markdown pages and
traverse it from `docs/index.md`; emit `orphan-page` only for managed pages.
Emit `unmanaged-documentation` as a warning for Markdown outside core files,
managed roots, excluded paths, and `docs/sources/`.

- [ ] **Step 6: Add RED tests for tag registry and dual-sided usage**

Cover invalid slug, unregistered usage, duplicate registry entry, docs-only
usage, code-only usage, misplaced `knowledge-tags`, and an unused registered
tag. Assert errors for the first six and a warning for the last:

```python
cases = {
    "@tag:Bad_Tag": "invalid-tag",
    "@tag:unknown": "unregistered-tag",
}
```

- [ ] **Step 7: Implement tag validation**

Accept only:

```python
TAG_PATTERN = re.compile(r"@tag:[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*")
```

Parse registry entries beginning with a backticked token and containing
`owner: [label](relative-path)`. Count occurrences separately in managed
Markdown and non-doc text files. Exclude `.git`, common build/cache directories,
the registry definition itself, source snapshots, and configured exclusions.

- [ ] **Step 8: Add RED tests for source manifests and credentials**

Add a MirPass-like fixture with:

```json
{
  "version": 1,
  "sources": [
    {
      "id": "nspk-api-1.0",
      "path": "docs/mir-pass.json",
      "kind": "provider-snapshot",
      "provider": "АО НСПК",
      "version": "1.0",
      "sha256": "<fixture sha256>",
      "distribution": "restricted",
      "derived_documents": ["docs/mir-pass.md"]
    },
    {
      "path": "docs/mir-pass.md",
      "kind": "provider-derived",
      "source": "nspk-api-1.0",
      "source_version": "1.0",
      "status": "current"
    },
    {
      "path": "docs/attachments/0000_Dari_example.csv",
      "kind": "synthetic-fixture",
      "synthetic": true
    }
  ]
}
```

Cover changed SHA, missing source, source-version mismatch, an unclassified
tracked DARI-like file, and a safely classified synthetic fixture.

- [ ] **Step 9: Implement source and credential-like validation**

Validate required fields by `kind`, stream SHA-256 reads, warn for
`distribution: restricted`, error on changed hash, warn on derived mismatch or
unknown source, and error on credential-like filenames unless classified as
`synthetic-fixture` with `synthetic: true`. Never read binary contents looking
for secrets.

- [ ] **Step 10: Implement the CLI and run the complete linter suite GREEN**

CLI contract:

```bash
python3 install-repository-knowledge/scripts/docs_lint.py --root /path/to/repo
```

Print stable lines as `ERROR code path: message` or
`WARNING code path: message`, followed by counts. Run:

```bash
python3 -m unittest install-repository-knowledge/tests/test_docs_lint.py -v
```

Expected: all tests pass.

- [ ] **Step 11: Review Task 1 and commit**

Run `git diff --check`, inspect only the two Task 1 files, correct confirmed
issues, rerun tests, then commit:

```bash
git add install-repository-knowledge/scripts/docs_lint.py \
  install-repository-knowledge/tests/test_docs_lint.py
git commit -m "KON-0000: add repository knowledge linter"
```

---

### Task 2: Safe idempotent installer and target assets

**Files:**
- Create: `install-repository-knowledge/scripts/install.py`
- Create: `install-repository-knowledge/tests/test_install.py`
- Create: `install-repository-knowledge/assets/agents-section.md`
- Create: `install-repository-knowledge/assets/docs-index.md`
- Create: `install-repository-knowledge/assets/tags.md`
- Create: `install-repository-knowledge/assets/sources-index.md`
- Create: `install-repository-knowledge/assets/sources-manifest.json`
- Create: `install-repository-knowledge/assets/repository-knowledge.json`

**Interfaces:**
- Consumes: `--repo PATH`, assets adjacent to the script, and canonical protocol/linter files from the skill.
- Produces: `plan_install(repo: Path, skill_root: Path) -> InstallPlan`, dry-run text, and `--apply` mutations only when no conflict exists.

- [ ] **Step 1: Write RED tests for fresh dry-run and apply**

Assert default invocation makes no changes and lists creates; `--apply` creates
the required tree, copies the protocol to `docs/repository-knowledge.md`, copies
the linter to `bin/docs-lint`, and sets its executable bit.

- [ ] **Step 2: Write RED tests for existing files, conflicts, and idempotence**

Cover five named cases: `test_second_apply_has_no_changes` compares a complete
tree digest before and after the second apply;
`test_existing_agents_content_is_preserved` checks text on both sides of the
inserted block; `test_managed_block_is_updated_without_touching_surrounding_text`
starts with an older valid block; `test_divergent_owned_file_blocks_all_apply`
asserts exit `2` and an unchanged tree; and
`test_existing_docs_are_not_moved_or_rewritten` compares inode-independent
Add `test_symlink_target_outside_repository_is_a_conflict`: an owned target path
that resolves through a symlink beyond the repository root must block all
writes.

Expected initial result: import or attribute failure.

- [ ] **Step 3: Define assets and managed block markers**

Use these exact markers in `AGENTS.md`, `docs/index.md`, and `docs/tags.md`:

```text
<!-- repository-knowledge:start -->
<!-- repository-knowledge:end -->
```

The AGENTS block requires reading `docs/index.md` and
`docs/repository-knowledge.md`. The docs-index block links protocol, tags, and
sources. The tags block documents the registry entry format without adding a
fake tag.

Default config:

```json
{
  "version": 1,
  "docs_root": "docs",
  "managed_roots": [],
  "excluded_paths": [],
  "sources_manifest": "docs/sources/manifest.json"
}
```

Default manifest is `{"version": 1, "sources": []}`.

- [ ] **Step 4: Implement planning and all-or-nothing conflict detection**

Define immutable dataclasses:

```python
@dataclass(frozen=True)
class Action:
    path: str
    operation: str  # create, insert-block, update-block, unchanged, conflict
    content: bytes | None = None

@dataclass(frozen=True)
class InstallPlan:
    root: Path
    actions: tuple[Action, ...]

    @property
    def conflicts(self) -> tuple[Action, ...]:
        return tuple(action for action in self.actions if action.operation == "conflict")
```

Owned files are created only when absent and accepted only when byte-identical.
Marker-managed files preserve all content outside one well-formed block.
Multiple, nested, or half-present markers are conflicts. Any conflict prevents
all writes.

- [ ] **Step 5: Implement atomic application and CLI**

Write each changed file to a sibling temporary file, preserve the existing mode
when replacing a marker-managed file, use `Path.replace`, and set
`bin/docs-lint` executable. CLI defaults to dry-run; `--apply` is required for
mutation. Stable exit codes: `0` success/no conflicts, `2` conflict or invalid
repository.

- [ ] **Step 6: Run installer tests GREEN and execute a temporary end-to-end install**

Run:

```bash
python3 -m unittest install-repository-knowledge/tests/test_install.py -v
fixture="$(mktemp -d /tmp/repository-knowledge.XXXXXX)"
git -C "$fixture" init -q
python3 install-repository-knowledge/scripts/install.py --repo "$fixture"
python3 install-repository-knowledge/scripts/install.py --repo "$fixture" --apply
"$fixture/bin/docs-lint" --root "$fixture"
python3 install-repository-knowledge/scripts/install.py --repo "$fixture" --apply
git -C "$fixture" status --short
```

Expected: tests pass, linter exits `0` with only allowed warnings, and the second
apply reports no changes.

- [ ] **Step 7: Review Task 2 and commit**

Run `git diff --check`, inspect installer safety and exact owned paths, rerun both
test modules, then commit:

```bash
git add install-repository-knowledge/assets \
  install-repository-knowledge/scripts/install.py \
  install-repository-knowledge/tests/test_install.py
git commit -m "KON-0000: add safe knowledge protocol installer"
```

---

### Task 3: Canonical protocol and installation skill

**Files:**
- Create: `install-repository-knowledge/references/protocol.ru.md`
- Create: `install-repository-knowledge/SKILL.md`
- Create: `install-repository-knowledge/agents/openai.yaml`
- Create: `install-repository-knowledge/assets/repository-knowledge.md`

**Interfaces:**
- Consumes: installer and linter from Tasks 1–2.
- Produces: discoverable `$install-repository-knowledge` skill and the canonical protocol copied into target repositories.

- [ ] **Step 1: Write the canonical Russian protocol**

Translate every normative requirement from the approved spec into concise
operational rules. Include: source-of-truth order, domain-first sections,
semantic indexes, tag syntax, same-change updates, unmanaged documentation,
provider classification, manifest fields, distribution/security gate,
runtime-bound path protection, and the boundary between installation and
migration.

- [ ] **Step 2: Make the installed protocol asset byte-identical to the canonical reference**

Copy the canonical file to
`install-repository-knowledge/assets/repository-knowledge.md` and add a test in
`test_install.py` asserting byte equality. This prevents drift between skill
guidance and target output.

- [ ] **Step 3: Create a concise installation skill**

The `SKILL.md` description activates only for installing or checking this
protocol, not for migrating existing documentation. Its workflow must:

1. read repository instructions and Git state;
2. run installer dry-run;
3. report conflicts without overwriting;
4. run `--apply` only within user-authorized scope;
5. run installed linter;
6. report warnings as migration candidates;
7. never change CI, move existing docs, commit, push, or publish without the
   corresponding explicit request.

- [ ] **Step 4: Add UI metadata and validate the skill**

Use:

```yaml
interface:
  display_name: "Install Repository Knowledge"
  short_description: "Install the Konsierge repository knowledge protocol"
```

Run:

```bash
python3 .system/skill-creator/scripts/quick_validate.py install-repository-knowledge
python3 -m unittest discover -s install-repository-knowledge/tests -p 'test_*.py' -v
```

Expected: skill valid and all tests pass.

- [ ] **Step 5: Review Task 3 and commit**

Compare protocol reference, installed asset, and approved spec; remove duplicated
generic agent advice; rerun validation/tests; then commit:

```bash
git add install-repository-knowledge/SKILL.md \
  install-repository-knowledge/agents/openai.yaml \
  install-repository-knowledge/references/protocol.ru.md \
  install-repository-knowledge/assets/repository-knowledge.md \
  install-repository-knowledge/tests/test_install.py
git commit -m "KON-0000: add repository knowledge installation skill"
```

---

### Task 4: Approval-gated migration skill

**Files:**
- Create: `migrate-repository-knowledge/SKILL.md`
- Create: `migrate-repository-knowledge/agents/openai.yaml`

**Interfaces:**
- Consumes: target repository's installed `docs/repository-knowledge.md`, `.repository-knowledge.json`, and linter.
- Produces: migration inventory, user-approved migration map, small safe migration batches, and linter evidence.

- [ ] **Step 1: Write the migration skill with a hard approval boundary**

The skill must distinguish:

- unmanaged project knowledge eligible for movement;
- provider snapshots eligible only for catalog/manifest metadata;
- provider-derived pages requiring source/version mapping;
- runtime/tool-bound contracts whose paths cannot move without consumer changes;
- synthetic fixtures requiring secret/PII review;
- root files required by tooling.

It first outputs a concrete table
`old path | class | target path or keep | owner page | tags | required updates`
and must stop before mutation until the user approves that map.

- [ ] **Step 2: Encode migration and safety behavior**

After approval, require small batches using `git mv`, link repair, index/tag
updates, manifest changes, and a linter run per batch. Preserve dirty/unrelated
changes. Do not alter snapshots, duplicate restricted text, infer provenance,
modify CI, commit, push, or deploy beyond the current explicit authorization.

- [ ] **Step 3: Add UI metadata and validate both skills**

Use:

```yaml
interface:
  display_name: "Migrate Repository Knowledge"
  short_description: "Migrate existing docs into the Konsierge knowledge protocol"
```

Run:

```bash
python3 .system/skill-creator/scripts/quick_validate.py migrate-repository-knowledge
python3 .system/skill-creator/scripts/quick_validate.py install-repository-knowledge
```

Expected: both skills valid.

- [ ] **Step 4: Review Task 4 and commit**

Verify the migration skill cannot be mistaken for the installer and includes an
explicit provider/source decision before any movement. Commit:

```bash
git add migrate-repository-knowledge
git commit -m "KON-0000: add repository knowledge migration skill"
```

---

### Task 5: Full verification, independent review, and GitLab delivery

**Files:**
- Modify only confirmed findings in files created by Tasks 1–4.
- Update: `docs/superpowers/plans/2026-08-31-repository-knowledge-protocol.md` checkboxes as tasks complete.

**Interfaces:**
- Consumes: all implementation commits.
- Produces: verified clean feature branch, local merge into `master`, pushed exact master SHA.

- [ ] **Step 1: Run full deterministic verification**

```bash
python3 -m unittest discover -s install-repository-knowledge/tests -p 'test_*.py' -v
python3 .system/skill-creator/scripts/quick_validate.py install-repository-knowledge
python3 .system/skill-creator/scripts/quick_validate.py migrate-repository-knowledge
git diff --check origin/master...HEAD
```

Expected: all tests pass, both skills valid, and no whitespace errors.

- [ ] **Step 2: Run isolated installation and MirPass-like source smoke**

Create a temporary Git repository, install twice, run the linter, then add a
small provider snapshot plus correct hash, provider-derived Markdown, local
OpenAPI path, and synthetic DARI fixture. Run the linter again and require exit
`0`; mutate the snapshot and require exit `1` with `snapshot-hash-mismatch`.

- [ ] **Step 3: Review the complete diff against the spec**

Check every spec section has implementation evidence. Focus on mutation safety,
path traversal, symlinks, binary handling, Markdown-link parsing, source rights,
credential-like filenames, marker corruption, idempotence, and accidental CI
changes. Fix only confirmed findings and rerun Step 1.

- [ ] **Step 4: Commit final confirmed fixes and completed plan state**

If review changes exist, commit them atomically. Mark completed plan tasks,
stage the plan only, and commit:

```bash
git add docs/superpowers/plans/2026-08-31-repository-knowledge-protocol.md
git commit -m "KON-0000: record repository knowledge implementation"
```

- [ ] **Step 5: Merge locally into the only remote target**

```bash
git fetch origin --prune
git switch master
git merge --ff-only origin/master
GIT_MERGE_AUTOEDIT=no git merge --no-ff KON-0000
```

Stop on remote advancement, conflicts, unexpected commits, or failed checks.
Rerun Step 1 on merged `master`.

- [ ] **Step 6: Push only master and verify exact SHA**

```bash
git push origin master
remote_sha="$(git ls-remote origin refs/heads/master | awk '{print $1}')"
local_sha="$(git rev-parse master)"
test "$remote_sha" = "$local_sha"
git merge-base --is-ancestor f47fc1f master
```

Because only one target exists and deployment monitoring was not requested,
verify remote SHA and feature containment without pipeline monitoring.

- [ ] **Step 7: Report delivery evidence**

Report feature commits, merge commit, remote master SHA, tests, skill validation,
temporary-fixture smoke, absence of CI changes, and final worktree status.
