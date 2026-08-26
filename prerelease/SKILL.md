---
name: prerelease
description: Prepare a repository for release by applying Semantic Versioning and changelog updates to Ruby gems, running every available verification check, validating built gem artifacts, and producing a commit message through the commit-message skill. Use when asked to prepare a release or prerelease, bump a gem version, update release metadata, run release checks, or make a project release-ready; for non-gem projects, run the verification gate and suggest a commit message without changing version metadata.
---

# Prerelease

Prepare the current worktree for release. Verify the real artifact, then provide one ready-to-use commit message.

## Boundaries

- Read repository instructions before acting.
- Preserve unrelated and pre-existing worktree changes.
- Do not stage, commit, tag, push, publish, deploy, or create a release unless the user explicitly requests that action.
- Do not install new tools or update unrelated dependencies merely to satisfy a check.
- Never hide, skip, or weaken a failing check. Mark the release as not ready when a required check fails.

## 1. Inspect the Repository

Collect before editing:

- repository root and local instruction files;
- current branch, status, staged and unstaged diffs;
- recent commit subjects and latest release tag;
- build manifests, CI configuration, test commands, lint commands, and release files.

Treat a project as a Ruby gem when it contains a relevant `*.gemspec`. If several gems are present and the target is ambiguous, ask one focused question before changing versions.

## 2. Prepare a Ruby Gem

Use the version requested by the user when explicit. Otherwise choose the smallest valid Semantic Versioning bump from changes since the last released version:

- `MAJOR`: incompatible public API, configuration, protocol, or runtime behavior;
- `MINOR`: backward-compatible public functionality;
- `PATCH`: backward-compatible fixes, internal refactors, documentation, or release metadata.

For `0.x` gems, follow the repository's established release convention. If compatibility or bump level remains genuinely ambiguous, explain the proposed bump and ask before editing.

Update every release source of truth that represents the current gem version, commonly:

- the version constant;
- a literal gemspec version, when present;
- the local gem entry in a lockfile;
- exact version expectations in specs;
- current-version documentation or packaging metadata.

Do not replace historical changelog versions or unrelated dependency versions.

Add a new changelog section at the top using the repository's existing format and current date. Derive concise entries from the actual diff and commits since the previous release. Describe user-visible behavior first; describe an internal refactor only when it is the release content.

## 3. Handle a Non-Gem Project

Do not bump versions or edit changelogs automatically. Run the complete available verification gate against the current changes, then produce a commit message.

Only change non-gem release metadata when the user explicitly asks for it or the repository has a clear documented prerelease workflow.

## 4. Run the Verification Gate

Discover commands from the repository instead of assuming a stack. Run every relevant check already provided by the project, including when present:

- tests;
- lint and static analysis;
- formatting checks;
- type checks;
- build or package tasks;
- security or dependency audits configured by the repository;
- `git diff --check`.

Prefer the project's aggregate check task, then run any important check it does not include. Do not run duplicate commands without a reason.

For a Ruby gem, also:

1. Load the gem and assert the expected version through its public entrypoint.
2. Run the available RSpec, RuboCop, Rake, and audit tasks.
3. Build the gem with the repository's package task, normally `bundle exec rake build`.
4. Inspect the built `.gem` specification and confirm its name and version.
5. Confirm the package contains the changed runtime files expected for the release.

If a check fails because of the release edits, fix the release edits and rerun it. If the failure is pre-existing or outside the requested scope, preserve it, report exact evidence, and mark readiness as blocked.

## 5. Generate the Commit Message

After the final diff and checks are known, load and follow the `commit-message` skill.

- Inspect the live branch, recent subjects, status, and complete diff.
- Generate one paste-ready commit subject matching repository convention.
- Add a body only when required for a breaking change, migration, security risk, revert, or manual deployment step.
- Do not create the commit unless explicitly requested.

## 6. Report Readiness

Lead with `ready` or `not ready`. Include only:

- selected version and SemVer rationale for a gem;
- changelog entry and release files changed;
- exact checks run and pass/fail summaries;
- built artifact name and validation result for a gem;
- remaining blockers or unverified checks;
- the commit message in a paste-ready code block;
- explicit confirmation that commit, tag, push, and publish were not performed.
