# Skill Catalog Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce Codex startup context to a single curated source per custom skill, retain only proven specialized workflows, and replace CodeGraph with a minimal Codebase Memory MCP integration.

**Architecture:** Treat user skills, plugins, MCP servers, hooks, and agents as separate activation layers. Capture a baseline, make every removal recoverable through a dated archive and SHA-256 manifest, then verify each layer before proceeding. Keep `~/.codex/skills` authoritative; manage plugins through `codex plugin`; never edit generated plugin cache.

**Tech Stack:** Codex CLI, TOML, YAML/Markdown skills, Ruby validation scripts, zsh/RTK, npm through mise, MCP stdio, SHA-256.

**Spec:** `docs/superpowers/specs/2026-09-02-skill-catalog-refactor-design.md`

## Global Constraints

- Preserve all unrelated dirty paths and staging exactly as found.
- Do not edit `~/.codex/skills/.system` or plugin cache directly.
- Move every removed user-owned artifact into one dated archive before deleting its active path.
- Record original path and SHA-256 for every archived file.
- A narrow skill remains active only with evidence of at least one substantive user-requested use.
- Bulk reads during installation, validation, audits, or inherited session catalogs are not usage evidence.
- Keep `auto_index=false` and set `auto_watch=false` for Codebase Memory.
- Never print the full `~/.codex/config.toml`; it contains secrets. Use targeted parsers or redacted CLI output.
- Do not push, deploy, or mutate any Konsierge application repository.

---

### Task 1: Capture Baseline and Build the Decision Register

**Files:**
- Create: `docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md`
- Read: `~/.codex/config.toml`
- Read: `~/.codex/AGENTS.md`
- Read: `~/.codex/hooks.json`
- Read: `~/.codex/agents/*.toml`
- Read: `~/.codex/skills/**/SKILL.md`
- Read: `~/.agents/skills/**/SKILL.md`

**Interfaces:**
- Consumes: approved design and current machine state.
- Produces: a reviewed keep/merge/archive register with source, evidence, byte size, description size, and owner for every active skill.

- [ ] **Step 1: Record a redacted baseline**

Run:

```bash
rtk codex --version
rtk codex plugin list
rtk codex mcp list
rtk codebase-memory-mcp --version
rtk codebase-memory-mcp config list
rtk git status --short
```

Expected: CodeGraph, Codebase Memory, and codemem are visible as separate MCP entries; the actual Codebase Memory configuration values are recorded; no secret values are printed by `codex mcp list`.

- [ ] **Step 2: Inventory active skill sources**

Run a read-only Ruby inventory over these exact roots:

```bash
rtk ruby -rdigest -e 'roots=%w[/Users/david/.codex/skills /Users/david/.agents/skills /Users/david/.codex/plugins/cache]; roots.each{|root| Dir.glob("#{root}/**/SKILL.md").sort.each{|path| puts [path, File.size(path), Digest::SHA256.file(path).hexdigest].join("\t")}}'
```

Expected: each discovered path has a byte size and digest; exact duplicate digests are visible.

- [ ] **Step 3: Classify usage evidence**

For every custom skill, link evidence to the original user request or mark `no-substantive-use`. Do not use raw read counts alone. Record one of:

```text
keep: substantive user-requested use found
merge: useful unique rule, but trigger overlaps a retained skill
archive: no substantive use or byte-identical duplicate
managed-plugin: lifecycle belongs to codex plugin
system: immutable Codex-owned skill
```

Expected: every active skill has exactly one classification and an evidence note.

- [ ] **Step 4: Write the baseline report**

The report must contain:

```markdown
| Skill | Active source | Owner | Bytes | Decision | Evidence |
| --- | --- | --- | ---: | --- | --- |
```

Also record totals for active skill count, summed description bytes, custom skill count, enabled plugin count, MCP count, hook count, and agent count.

- [ ] **Step 5: Verify and commit only the report**

Run:

```bash
rtk rg -n 'T[B]D|T[O]DO|F[I]XME|no decision' docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md
rtk git diff --check -- docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md
rtk git add docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md
rtk git diff --cached --name-only
rtk git commit -m 'add: skill catalog baseline'
```

Expected: the placeholder scan returns no matches; the staged list contains only the baseline report.

---

### Task 2: Minimize Codebase Memory Integration

**Files:**
- Modify: `/Users/david/.codex/config.toml`
- Modify: `/Users/david/.codex/AGENTS.md`
- Modify: `/Users/david/.codex/hooks.json`
- Archive: `/Users/david/.agents/skills/codebase-memory/`
- Keep: `/Users/david/.codex/skills/codebase-memory/`
- Archive: `/Users/david/.codex/agents/codebase-memory.toml`
- Archive: `/Users/david/.codex/agents/codebase-memory-scout.toml`
- Archive: `/Users/david/.codex/agents/codebase-memory-auditor.toml`

**Interfaces:**
- Consumes: Task 1 baseline and Codebase Memory `0.10.8` binary.
- Produces: one MCP entry, one custom skill, no CBM global prompt block, no CBM hooks, and no CBM agents.

- [ ] **Step 1: Create the dated archive and manifest**

Create one explicit directory outside active roots:

```bash
skill_archive=/Users/david/.Trash/codex-skill-refactor-20260902
mkdir -p "$skill_archive/files"
```

Before moving a file, append a tab-separated row to `$skill_archive/manifest.tsv` containing:

```text
sha256<TAB>original_absolute_path<TAB>archived_relative_path<TAB>reason
```

Expected: archive path is exact and does not reuse a broad environment variable such as `HOME`.

- [ ] **Step 2: Archive installer-owned CBM extras**

Archive the duplicate skill and three agent TOML files. Preserve paths beneath `files/` so restoration cannot collide. Verify every copied file digest before removing its active original.

Expected: `/Users/david/.codex/skills/codebase-memory/SKILL.md` remains; `/Users/david/.agents/skills/codebase-memory/SKILL.md` does not.

- [ ] **Step 3: Remove only the marked CBM block from global instructions**

Delete the inclusive block between:

```text
<!-- codebase-memory-mcp:start -->
<!-- codebase-memory-mcp:end -->
```

Expected: all global instructions outside these markers remain byte-identical.

- [ ] **Step 4: Remove only CBM-owned hooks**

Parse `hooks.json` and remove entries whose command executable is exactly `/Users/david/.local/bin/codebase-memory-mcp` with argument `hook-augment`. Preserve ordering and every unrelated hook.

Expected: JSON parses successfully and no `hook-augment` command remains.

- [ ] **Step 5: Disable background indexing registration**

Run:

```bash
rtk codebase-memory-mcp config set auto_index false
rtk codebase-memory-mcp config set auto_watch false
rtk codebase-memory-mcp config list
```

Expected: `auto_index=false` and `auto_watch=false`.

- [ ] **Step 6: Verify the retained MCP entry without exposing config secrets**

Run:

```bash
rtk codex mcp get codebase-memory-mcp
rtk codebase-memory-mcp cli list_projects '{}'
```

Expected: executable is `/Users/david/.local/bin/codebase-memory-mcp`; CLI returns structured project data or an empty project list without startup failure.

---

### Task 3: Remove CodeGraph

**Files:**
- Modify: `/Users/david/.codex/config.toml`
- Remove through package manager: `@colbymchenry/codegraph@0.9.9`
- Preserve: user-owned plugin and MCP `codemem@codemem`
- Preserve: project-local `.codegraph/` and `.codegraph` ignore changes unless separately approved.

**Interfaces:**
- Consumes: verified Codebase Memory MCP from Task 2.
- Produces: no active CodeGraph; both user-approved `codebase-memory-mcp` and `codemem` remain.

- [ ] **Step 1: Prove Codebase Memory can index a disposable repository**

Run:

```bash
cbm_smoke_dir=$(mktemp -d /tmp/cbm-skill-refactor-smoke.XXXXXX)
rtk git -C "$cbm_smoke_dir" init
```

Create `$cbm_smoke_dir/smoke.rb` with `apply_patch`:

```ruby
def skill_refactor_smoke
  :ok
end
```

Then run:

```bash
rtk codebase-memory-mcp cli index_repository --repo-path "$cbm_smoke_dir" --name cbm-skill-refactor-smoke --mode fast --persistence false
rtk codebase-memory-mcp cli index_status --project cbm-skill-refactor-smoke
rtk codebase-memory-mcp cli search_graph --project cbm-skill-refactor-smoke --name-pattern skill_refactor_smoke
rtk codebase-memory-mcp cli check_index_coverage --project cbm-skill-refactor-smoke --paths '["smoke.rb"]'
```

Expected: index completes, the symbol is returned, and coverage reports no unexamined gap for the source file.

- [ ] **Step 2: Archive CodeGraph installation metadata**

Record in the archive manifest:

```text
package=@colbymchenry/codegraph
version=0.9.9
binary=/Users/david/.local/share/mise/installs/node/25.8.2/bin/codegraph
```

Do not copy or remove any project-local `.codegraph/` path.

- [ ] **Step 3: Remove the CodeGraph MCP block**

Edit only `[mcp_servers.codegraph]` and `[mcp_servers.codegraph.tools.codegraph_explore]` from `config.toml`. Parse TOML after the edit and verify unrelated MCP names are unchanged.

- [ ] **Step 4: Uninstall the exact CodeGraph npm package**

Run through the same mise Node installation that owns the binary:

```bash
rtk mise x node@25.8.2 -- npm uninstall -g @colbymchenry/codegraph
rtk which codegraph
```

Expected: uninstall succeeds and `which codegraph` returns not found.

- [ ] **Step 5: Verify configuration integrity**

Run a TOML parse without printing values, then `rtk codex doctor` and `rtk codex mcp list`.

Expected: no CodeGraph entry; both codemem and Codebase Memory remain enabled; no new configuration error.

---

### Task 4: Consolidate Custom Workflow Skills

**Files:**
- Move: `/Users/david/.agents/skills/context7-mcp/` -> `/Users/david/.codex/skills/context7-mcp/`
- Modify: retained `SKILL.md` and targeted `references/*.md` under `/Users/david/.codex/skills/`
- Archive: exact duplicates under `/Users/david/.agents/skills/`
- Archive after rule transfer: overlapping custom skill directories listed in the spec.

**Interfaces:**
- Consumes: Task 1 decision register.
- Produces: one active source per custom skill and one primary workflow per trigger family.

- [ ] **Step 1: Establish exact merge pairs from the approved spec**

Use this mapping:

```text
documentation-lookup -> context7-mcp
tdd-workflow -> test-driven-development
code-review-and-quality -> code-review
auditing-access-control -> security-and-hardening
planning-and-task-breakdown -> orchestrating-agent-work
spec-driven-development -> brainstorming
idea-refine -> interview-me
using-agent-skills -> orchestrating-agent-work
api-design -> openapi-design-first and api-documentation
coding-standards -> rails and code-review
```

Expected: every source has one destination; no source is archived before its unique rules are classified.

- [ ] **Step 2: Write characterization checks before merging**

For every destination, record its expected trigger boundary and required hard gates in the baseline report. Use exact phrases for mandatory behavior, especially approval gates, TDD, API contract reconciliation, security review, and Konsierge delivery boundaries.

Expected: a reviewer can compare pre/post trigger and invariant coverage without reading all prose.

- [ ] **Step 3: Transfer only unique rules**

Keep trigger metadata and minimal workflow in `SKILL.md`. Move detailed tables, examples, and long references into destination `references/` files. Do not broaden destination triggers merely to preserve generic catalog prose.

Expected: each destination has one clear responsibility; no two retained custom skills claim the same default trigger.

- [ ] **Step 4: Archive merged sources and legacy duplicates**

Move approved source directories into the dated archive after digest verification. Archive all remaining byte-identical `.agents/skills` copies.

Expected: `~/.agents/skills` contains no active duplicate; only explicitly retained non-duplicate content may remain until moved.

- [ ] **Step 5: Validate every retained custom skill**

Run for every immediate child containing `SKILL.md`:

```bash
rtk ruby -e 'Dir.glob("*/SKILL.md").sort.each{|path| dir=File.dirname(path); ok=system("python3", ".system/skill-creator/scripts/quick_validate.py", dir); abort("validation failed: #{dir}") unless ok}'
```

Expected: every retained custom skill prints `Skill is valid!`; exit status is zero.

- [ ] **Step 6: Commit only consolidated skill paths**

Stage an explicit path list from the decision register. Confirm no pre-existing dirty path is staged. Use a repository-style message:

```bash
rtk git commit -m 'refactor: consolidate overlapping skills'
```

---

### Task 5: Archive Unused Specialized Skills and Remove Unused Plugins

**Files:**
- Archive: only `archive` rows from the Task 1 decision register.
- Modify through CLI: Codex plugin installation state.
- Do not modify: plugin cache files directly.

**Interfaces:**
- Consumes: evidence-backed Task 1 register and completed consolidation.
- Produces: reduced custom catalog and reduced plugin-contributed catalog.

- [ ] **Step 1: Recheck every archive candidate**

Search session summaries and original user requests for substantive use. Promote a candidate from `archive` to `keep` only with a concrete task reference and record that reference.

Expected: no removal is justified only by age, name, or read count.

- [ ] **Step 2: Archive confirmed unused custom skills**

Use the approved candidate list in the spec. Digest, copy, verify, then remove each active path. Update `manifest.tsv` for every file.

Expected: all removed paths are recoverable and every manifest digest matches the archived copy.

- [ ] **Step 3: Remove unused installed plugins through the CLI**

After the Task 1 evidence review confirms the approved candidates are unused, run these exact selectors:

```bash
rtk codex plugin remove template-creator@openai-primary-runtime --json
rtk codex plugin remove sites@openai-bundled --json
rtk codex plugin remove visualize@openai-bundled --json
rtk codex plugin remove cc-safety-net@cc-marketplace --json
```

Candidates requiring evidence review include Template Creator, Sites, Visualize, and duplicate Safety Net installations. Browser, Chrome, superpowers, and any plugin with substantive use remain.

Expected: `codex plugin list` reports removed candidates as not installed; no manual cache deletion occurs.

- [ ] **Step 4: Commit tracked removals only**

Inspect `git diff --cached --name-status` before commit. Exclude all pre-existing dirty paths. Commit:

```bash
rtk git commit -m 'remove: unused skills'
```

---

### Task 6: Final Verification and Recovery Proof

**Files:**
- Modify: `docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md`
- Verify: `/Users/david/.Trash/codex-skill-refactor-20260902/manifest.tsv`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: exact before/after evidence and a tested recovery path.

- [ ] **Step 1: Validate archive integrity**

For each manifest file row, recompute SHA-256 for the archived path and compare it with the recorded digest.

Expected: zero missing files and zero digest mismatches.

- [ ] **Step 2: Repeat the baseline commands**

Run:

```bash
rtk codex plugin list
rtk codex mcp list
rtk codebase-memory-mcp config list
rtk git status --short
```

Expected: no CodeGraph, both codemem and Codebase Memory enabled, background indexing disabled, unrelated dirty paths unchanged.

- [ ] **Step 3: Restart Codex and inspect the effective catalog**

Start a fresh Codex session after restart. Capture the effective skill names and sources exposed to that session.

Expected: no `.agents` duplicate, no removed plugin skill, no duplicate `codebase-memory`, and no CodeGraph bootstrap instruction.

- [ ] **Step 4: Re-run Codebase Memory smoke in the fresh session**

Verify `tools/list` exposes 15 tools. Explicitly index a small repository and perform one structural search plus coverage check.

Expected: the MCP works without global CBM prompt injection, hooks, or custom graph agents.

- [ ] **Step 5: Test one recovery without reactivating it**

Copy one archived file into a temporary directory, verify its digest and original-path mapping, then remove only that temporary copy.

Expected: recovery instructions are sufficient and the active catalog remains unchanged.

- [ ] **Step 6: Record final metrics and commit verification evidence**

Add before/after counts and bytes, retained exceptions with evidence, verification commands, and exact final Git SHA to the audit report. Then run:

```bash
rtk git diff --check
rtk git add docs/superpowers/audits/2026-09-02-skill-catalog-baseline.md
rtk git diff --cached --name-only
rtk git commit -m 'add: skill catalog verification'
```

Expected: only the audit report is staged for the final evidence commit; all checks pass.
