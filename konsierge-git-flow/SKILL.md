---
name: konsierge-git-flow
description: "Use for every Git delivery task in a Konsierge repository, including isolated worktree implementation, commit transfer to the task branch, target integration, pushes, and conditional deployment verification."
---

# Konsierge Git Flow

Treat this as the standing delivery workflow for Konsierge repositories.

This skill owns worktree isolation, branch topology, commit transfer, target integration, pushes, cleanup, and delivery evidence. For commit-message selection and formatting, use [`konsierge-commit-conventions`](../konsierge-commit-conventions/SKILL.md). That skill generates text only; this skill controls when and where the commit is created.

The global commit hook first identifies the repository. Repositories with any remote hosted exactly at `gitlab.konsierge.com`, or repositories explicitly configured with `git config konsierge.commitPolicy true`, use the KON rules below. Other repositories keep unrestricted branch names and require Conventional Commit subjects such as `feat: add export` or `fix(api): reject invalid input`; real Git merge and revert operations retain their generated subjects.

The global `pre-push` dispatcher validates all newly published merge commits, permits only an existing matching `dev` or `master` target, and preserves stdin for repository-local hooks. Published remote history is excluded from this validation.

The global hook directory dispatches every standard Git hook back to an executable repository-local `.git/hooks/<hook>` when one exists. The global `commit-msg` policy runs first and then chains the repository-local `commit-msg`, so enabling policy enforcement must not silently disable existing project hooks.

A repository-local `core.hooksPath` overrides Git's global value before any global hook can run. Before every commit, inspect `git config --local --get core.hooksPath`. When it is set, do not commit or push until that hook manager invokes both the Konsierge commit validator and the delivery `pre-push` validator, preserving repository hooks and stdin. This is an agent-side fail-closed preflight because Git provides no higher-precedence client-side hook. Never claim that the global installation covers a repository with an unintegrated local override.

## Hard Rules

- Keep one persistent task branch: use the ticket branch named by the request or current context, for example `KON-1234`; when none exists, use `KON-0000`. `KON-1234` is an example, not a fixed branch name.
- Create every new linked worktree under `~/dev/konsierge/worktrees`, using a collision-resistant path such as `~/dev/konsierge/worktrees/<repository>-<branch>`. Expand `~` to the current user's home before calling Git and create the shared parent directory when it is absent. Never create new Konsierge worktrees in `/tmp`, inside a repository-local `.worktrees` directory, or in sibling `*.worktrees` directories. Existing worktrees outside the shared directory may be inspected or cleaned up, but do not relocate them implicitly.
- Perform implementation in a separate linked worktree on a temporary descriptive branch such as `KON-1234-authorization-implementation`. Create the implementation commits there, then cherry-pick them in order into the persistent task branch. Never merge the temporary branch into the task branch.
- Temporary worktree branches are session-owned safety refs, not delivery branches. Never push or merge them. Remove their worktrees immediately after verified cherry-pick into the persistent task branch, before target integration or deployment. Preserve any unique work.
- Check out persistent task branches, exact `KON-<number>-dev` integration branches, `dev`, and `master` only in the main checkout. Linked worktrees may use only temporary descriptive implementation branches. Serialize transfer and delivery; never evade a dirty or busy main checkout by occupying these branches in another worktree.
- Never create merge commits in temporary branches or task branches. Synchronize task branches by fast-forward, and transfer implementation or conflict-specific work with cherry-pick.
- Treat the `contracts` tree as out-of-scope by default. When the user did not explicitly ask to change contracts, ignore `contracts` completely: do not mention it in status/final reports, do not include it in staging, commits, or application checks. Worktree removal still requires checking that every submodule contains no unique data; preserve any such data.
- Never commit task work directly to `dev` or `master`.
- Never push persistent task branches, temporary worktree branches, or their `-dev` delivery branches under any circumstance.
- By default, merge the persistent task branch locally into every delivery target that exists on `origin`: both `dev` and `master`, only `dev`, or only `master`.
- Use the split topology only after an actual direct `KON-<number>` -> `dev` merge conflict for the current task tip has been recorded. An existing `-dev` branch alone never enables the exception. The only allowed suffix is exactly `-dev`: merge `KON-<number>-dev` into `dev` and the persistent task branch into `master`.
- Treat `KON-<number>-dev` only as a local conflict integration branch. Base it on the conflicted current `dev` tip, apply task changes with cherry-pick, and never merge another branch into it or deliver it to `master`.
- Push only the delivery targets that exist on `origin`, after their local merges and checks succeed. If only `dev` exists, push only `dev`. If only `master` exists, push only `master`. Stop and ask for direction when neither exists.
- When both targets exist, always push them sequentially: push `dev`, require its successful staging deployment, then push `master` and require its successful production deployment. Never push both targets together or start their pipelines concurrently; their parallel test jobs share temporary database infrastructure and can delete each other's databases.
- Monitor pipelines and deployments only when the user explicitly requests monitoring or when both `dev` and `master` are being pushed. For a single-target push, verify the remote SHA and task-commit containment, but do not monitor its deployment unless explicitly requested.
- Never force-push, rebase, or rewrite `dev` or `master`.
- Keep every merge commit message generated by Git. Never pass `-m`/`--message` to `git merge` or edit the default merge message.
- Merge only the persistent local named task-branch ref matching `^KON-[0-9]+$`, or the recorded conflict exception matching `^KON-[0-9]+-dev$` into `dev`. Never merge a temporary worktree branch, `FETCH_HEAD`, a raw commit SHA, a filesystem path, or a repository URL into a delivery branch.
- Before pushing, validate every newly published merge commit, including nested merges. Subjects may only be Git-generated merges from `KON-<number>` into `dev`/`master`, or the recorded exact `-dev` exception into `dev`. Reject descriptive suffixes, merge targets other than `dev`/`master`, octopus merges, paths, URLs, raw SHAs, and `FETCH_HEAD`. Git normally omits `into master`; keep that generated form. Never rename an invalid merge subject to disguise its topology.
- When deployment monitoring is required, treat delivery as incomplete until GitLab MCP confirms every monitored target's exact pushed SHA deployed successfully to its environment.

## Prepare

1. Read repository instructions and inspect all worktrees, branches, status, staged/unstaged diffs, upstreams, recent subjects, and remote target state.
   Also inspect `git config --local --get core.hooksPath`; stop if a local override does not invoke the global commit policy.
2. Preserve unrelated and pre-existing changes. Do not switch branches with an unresolved dirty worktree. The persistent task branch must be available in the clean main checkout before commit transfer; if it is checked out with unrelated changes, preserve them and stop before cherry-picking.
3. Run `git fetch origin --prune` before starting and determine whether `dev`, `master`, or both exist on the remote. Resolve the persistent task branch from the request or current context; otherwise use `KON-0000`. If the matching `origin/KON-<number>` exists, create the local task branch from it or fast-forward the existing local branch to include it. A locally ahead branch is valid; divergence requires explicit reconciliation without an automatic merge or reset. If no remote task exists, preserve the local task branch or create it from the repository's established base. If the base is genuinely ambiguous, ask.
4. Create a separate linked implementation worktree from the current persistent task branch tip under `~/dev/konsierge/worktrees`, for example `~/dev/konsierge/worktrees/travelmart-KON-1234-authorization-implementation`. Its temporary branch must match `KON-[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*` and describe the work clearly. Do not use detached HEAD.
5. From the main repository root, copy its local `.env` into the new worktree before setup or tests: `cp .env <worktree-path>/.env`. Do not create a placeholder when the main checkout has no `.env`, and never commit the copied file.
6. If `.gitmodules` declares the `contracts` submodule, initialize it in the new worktree with `git submodule update --init --recursive contracts`, then run `bin/contracts-update` from the worktree root before running tests. This setup does not make `contracts` part of the task scope; do not stage or commit it unless the user explicitly requested contract changes.

## Implement and Transfer Commits

1. Implement and verify the requested work only in the separate implementation worktree.
2. Build atomic commits on its temporary descriptive branch using [`konsierge-commit-conventions`](../konsierge-commit-conventions/SKILL.md). Nearby repository history remains authoritative when it establishes a more specific convention.
3. Confirm the implementation worktree is clean and relevant checks pass. Record the ordered source commit SHAs.
4. Run `git fetch origin --prune` again immediately before transfer. In the clean main checkout, switch to the persistent task branch, fast-forward it from its matching remote when present, and confirm its expected tip. Stop on divergence or unexpected local commits. Cherry-pick every source commit in order. Record the `source SHA -> task SHA` mapping because cherry-pick normally changes commit IDs.
5. Run relevant checks on the persistent task branch. Use `git cherry <task-branch> <temporary-branch>` or stable patch IDs to prove every source commit is patch-equivalent to a task-branch commit; no source commit may remain marked `+`.
6. Do not push either branch. Complete implementation-worktree cleanup now, including when no merge or push was requested. Retain the source-to-task SHA mapping in the task report. Delivery continues from the persistent task branch; a pipeline failure is not a reason to retain the implementation checkout.

## Merge Locally

Fetch `origin` again immediately before merging. First check which delivery targets exist. An existing `-dev` branch does not select split delivery. Apply the steps below only to existing target branches; skip every step for an absent target.

### Default topology

Always try direct delivery from the persistent task branch first, unless a direct conflict for this exact task tip and compatible dev base has already been recorded:

1. Switch to `dev`, fast-forward it to `origin/dev`, merge the persistent task branch with the repository's established merge style, and run relevant checks.
2. Switch to `master`, fast-forward it to `origin/master`, merge the same persistent task branch, and run relevant checks.
3. On a direct dev conflict, follow the split topology below. Stop on master conflicts, failed checks, non-fast-forward target state, or unexpected commits. Do not push a partial delivery.

### Split `-dev` topology

Use this path only after a direct task-to-`dev` conflict. A pre-existing split branch is insufficient.

1. While the direct merge is still unresolved on `dev`, record its actual state:

   ```sh
   python3 ~/.codex/skills/konsierge-git-flow/scripts/delivery-policy record-dev-conflict KON-11419
   ```

   This records the current task SHA and dev SHA under the repository's common Git directory. The validator requires `MERGE_HEAD` to match the task tip and unmerged files to exist. Keep this record through push verification; a changed task tip requires a new direct conflict.
2. Abort that session-owned conflicted merge, returning to the clean dev tip. In the main checkout, create exactly `KON-11419-dev` from that dev tip. If an old branch exists, inspect and preserve its unique work before reusing the name; never reset it blindly or import its merge history.
3. Cherry-pick only task changes missing from dev, resolve their conflicts, and verify the result. Do not merge `origin/dev` or another branch into `KON-11419-dev`. Conflict-specific edits belong here; use an implementation worktree plus cherry-pick if additional coding is needed.
4. Switch back to `dev`, confirm it still includes the recorded base and current `origin/dev`, then merge the named `KON-11419-dev` branch. The hook checks the recorded conflict and source ref. If origin advances incompatibly, repeat integration against the new base.
5. Fast-forward local `master` to `origin/master` and merge the persistent `KON-11419`. Never merge the split branch or dev history into master.

Prefer explicit merge commits when that matches the repository history:

```sh
# Default topology and `master` in split topology
GIT_MERGE_AUTOEDIT=no git merge --no-ff KON-0000

# `dev` in split topology
GIT_MERGE_AUTOEDIT=no git merge --no-ff KON-0000-dev
```

`GIT_MERGE_AUTOEDIT=no` only suppresses the editor; it preserves Git's default merge message. Do not replace it with a custom message.

Never use `git merge FETCH_HEAD` in the delivery branch: Git can expose a source filesystem path in the generated merge subject. Commit transfer from the implementation worktree belongs in the persistent task branch and uses cherry-pick, not merge.

## Push Targets

When both local target branches are correct and verified, deliver sequentially:

1. Fetch `origin` and confirm local `dev` still descends from the current `origin/dev`.
2. Push only `dev`:

   ```sh
   git push origin dev
   ```

3. Monitor the exact pushed `dev` SHA and require `deploy_staging` to succeed. Stop on any failed, canceled, skipped, or blocked job; do not push `master` while the staging pipeline is unfinished or unsuccessful.
4. Fetch `origin` again and confirm local `master` still descends from the current `origin/master`.
5. Push only `master`:

   ```sh
   git push origin master
   ```

6. Monitor the exact pushed `master` SHA and require `deploy_production` to succeed.

When only one target exists, fetch `origin`, confirm the local target still descends from its remote counterpart, push only that target, and verify its remote SHA plus task-commit containment. Do not monitor its pipeline or deployment unless the user explicitly requested monitoring.

Never include the persistent task branch or temporary worktree branch in a push refspec. Never use one atomic or multi-ref push for `dev` and `master`. If either remote target advanced, fetch, reconcile locally, rerun affected checks, then retry or report the blocker.

Verify every pushed remote target SHA and task-commit containment after the push.

## Monitor Deployments When Required

Enter this section only when the user explicitly requests deployment monitoring or both `dev` and `master` are being pushed. Otherwise finish after remote SHA and containment verification; implementation-worktree cleanup must already be complete.

Use GitLab MCP to verify deployments. Resolve `project_id` from the `origin` URL; do not ask for it when it is available locally. Activate the `pipelines` and `ci` tool categories with `discover_tools` when their tools are not already available.

Monitor each pushed target before pushing the next one:

| Branch | Environment |
| --- | --- |
| `dev` | staging |
| `master` | production |

1. Call `list_pipelines` with the branch and exact SHA. Select only the pipeline for that SHA; never substitute an older successful pipeline.
2. Poll `get_pipeline` while the pipeline is non-terminal. Recheck at progressively longer intervals instead of rapid polling.
3. Call `list_pipeline_jobs` and identify the deployment job for the expected environment from its name, stage, and environment metadata. Require that exact job to finish with `success`; pipeline success alone is not deployment proof.
4. When GitLab exposes environment/deployment records, resolve them with `list_environments` and `list_deployments`, then confirm with `get_deployment` that the matching environment, branch, and SHA succeeded. If the project does not create deployment records, use the successful exact-SHA deployment job as the proof.
5. Continue until every monitored deployment succeeds. Treat `failed`, `canceled`, `skipped`, or blocked `manual` deployment jobs as unsuccessful. Do not retry, play, cancel, or otherwise mutate a pipeline unless the user explicitly requests it.

On failure, inspect the failed deployment job with `get_pipeline_job` or `get_pipeline_job_output` and report the pipeline, job, environment, SHA, status, URL, and concise failure evidence. Do not claim delivery succeeded.

## Clean Up the Implementation Worktree

Cleanup is part of commit transfer. Perform it immediately after cherry-picks and task-branch checks succeed, before merging, pushing, or monitoring deployment. Run a final worktree audit on every exit path; if unique work prevents removal, report the exact path, size, and reason instead of silently retaining it.

1. Recheck the recorded `source SHA -> task SHA` mapping and prove the temporary branch has no patch absent from the persistent task branch. Stop when `git cherry <task-branch> <temporary-branch>` contains any `+` entry.
2. Confirm tracked, untracked, ignored files, and initialized submodules contain no unique work. Classify copied `.env`, caches, dependencies, and build output explicitly; ordinary `git status` does not show all of these. Preserve unique files. Do not let routine generated files silently prevent cleanup: remove only verified reproducible session artifacts, and deinitialize clean submodules where needed before worktree removal. If Git still refuses removal because the worktree contains submodules, report that exact blocker; never silently mark cleanup complete or force-remove a dirty worktree.
3. Remove the exact session-owned implementation worktree without force, then prune only stale metadata for verified absent directories. Before removing older worktrees, establish that they are inactive and all work is preserved; age alone is insufficient.
4. Delete only its exact temporary branch. Because cherry-pick changes ancestry, first repoint the no-longer-checked-out temporary branch to the persistent task branch with `git branch --force <temporary-branch> <task-branch>`, then delete it with `git branch -d <temporary-branch>`. Do not use `git branch -D`.
5. Verify the temporary worktree path and branch are gone, and no linked worktree occupies a persistent task, split, dev, or master branch. For an inactive legacy worktree that must remain, preserve its HEAD on a unique descriptive temporary branch to release the permanent branch. Never change an active neighboring session's checkout.
6. Report remaining worktrees with their size and retention reason. `git worktree prune` only removes stale registration; it does not delete existing checkout directories or reclaim their contents.

Report the persistent task branch, source-to-task SHA mapping, merge commits for existing targets, remote SHAs, checks, pushes, and final worktree state. When monitoring was required, also report each monitored pipeline/job or deployment ID, URL, and final status.
