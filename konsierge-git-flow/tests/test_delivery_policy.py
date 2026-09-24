import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
POLICY = SKILL / "scripts/delivery-policy"
VALIDATOR = SKILL / "scripts/validate-commit-message"


class DeliveryPolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="konsierge-policy-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        KONSIERGE_GIT_FLOW_SKILL_DIR=str(SKILL))
        self.env.pop("KONSIERGE_BRANCH_OVERRIDE", None)
        self.git("init", "-b", "master")
        self.git("config", "user.name", "Policy Test")
        self.git("config", "user.email", "policy@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "konsierge.commitPolicy", "true")
        self.git("config", "core.hooksPath", os.devnull)
        self.commit("base", "base")
        self.git("branch", "dev")
        self.git("branch", "KON-11419")
        self.remote = self.root / "remote.git"
        self.git("init", "--bare", str(self.remote))
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "origin", "dev", "master")

    def run_cmd(self, args, *, ok=True, stdin=None, cwd=None):
        result = subprocess.run([str(x) for x in args], cwd=cwd or self.repo,
                                env=self.env, text=True, input=stdin, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def git(self, *args, **kwargs):
        return self.run_cmd(["git", *args], **kwargs)

    def commit(self, filename, content):
        (self.repo / filename).write_text(content)
        self.git("add", filename)
        self.git("commit", "-m", "KON-11419: change " + filename)

    def validator(self, subject, ok=True, cwd=None):
        message = self.root / "message"
        message.write_text(subject + "\n")
        return self.run_cmd(["bash", VALIDATOR, message], ok=ok, cwd=cwd)

    def policy(self, *args, **kwargs):
        return self.run_cmd(["python3", POLICY, *args], **kwargs)

    def merge(self, source):
        self.git("-c", "core.editor=true", "merge", "--no-ff", "--no-commit", source)

    def outgoing(self, target="dev", **kwargs):
        tip = self.git("rev-parse", target).stdout.strip()
        old = self.git("rev-parse", "origin/" + target).stdout.strip()
        line = f"refs/heads/{target} {tip} refs/heads/{target} {old}\n"
        return self.policy("check-push", "origin", str(self.remote), stdin=line, **kwargs)

    def task_change(self):
        self.git("switch", "KON-11419")
        self.commit("feature", "feature")

    def test_direct_task_merges_pass(self):
        self.task_change()
        for branch, subject in [("dev", "Merge branch 'KON-11419' into dev"),
                                ("master", "Merge branch 'KON-11419'")]:
            self.git("switch", branch)
            self.merge("KON-11419")
            self.validator(subject)
            self.git("commit", "-m", subject)
            self.outgoing(branch)

    def test_descriptive_source_and_temporary_destination_fail(self):
        self.task_change()
        self.git("branch", "KON-11419-description")
        self.git("switch", "dev")
        self.merge("KON-11419-description")
        self.validator("Merge branch 'KON-11419-description' into dev", ok=False)
        self.git("merge", "--abort")
        self.git("switch", "-c", "KON-11419-crm-completion-master", "master")
        self.merge("KON-11419")
        self.validator("Merge branch 'KON-11419' into KON-11419-crm-completion-master", ok=False)

    def test_nested_invalid_merge_is_rejected_before_push(self):
        self.task_change()
        self.git("switch", "-c", "KON-11419-crm-completion-master", "master")
        self.merge("KON-11419")
        self.git("commit", "-m", "Merge branch 'KON-11419' into KON-11419-crm-completion-master")
        self.git("switch", "KON-11419")
        self.git("merge", "--ff-only", "KON-11419-crm-completion-master")
        self.git("switch", "dev")
        self.merge("KON-11419")
        self.git("commit", "-m", "Merge branch 'KON-11419' into dev")
        result = self.outgoing(ok=False)
        self.assertIn("crm-completion-master", result.stderr)
        self.git("push", "origin", "dev")
        # Published legacy history does not prevent subsequent normal delivery.
        self.git("switch", "master")
        self.git("merge", "--ff-only", "dev")
        self.outgoing("master")

    def test_dev_suffix_requires_real_conflict_and_rejects_master(self):
        self.git("switch", "KON-11419")
        self.commit("base", "task")
        task_sha = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("switch", "dev")
        self.commit("base", "dev")
        self.git("branch", "KON-11419-dev")
        self.policy("record-dev-conflict", "KON-11419", ok=False)
        self.git("merge", "--no-ff", "KON-11419", ok=False)
        self.policy("record-dev-conflict", "KON-11419")
        self.git("merge", "--abort")
        self.git("switch", "KON-11419-dev")
        self.git("cherry-pick", task_sha, ok=False)
        (self.repo / "base").write_text("resolved")
        self.git("add", "base")
        self.git("-c", "core.editor=true", "cherry-pick", "--continue")
        self.git("switch", "dev")
        self.merge("KON-11419-dev")
        self.validator("Merge branch 'KON-11419-dev' into dev")
        self.git("commit", "-m", "Merge branch 'KON-11419-dev' into dev")
        self.outgoing()
        self.git("switch", "master")
        self.merge("KON-11419-dev")
        self.validator("Merge branch 'KON-11419-dev'", ok=False)
        self.git("merge", "--abort")
        self.git("switch", "KON-11419")
        self.commit("later", "later")
        self.outgoing(ok=False)

    def test_existing_dev_suffix_without_conflict_is_rejected(self):
        self.task_change()
        self.git("branch", "KON-11419-dev")
        self.git("switch", "dev")
        self.merge("KON-11419-dev")
        self.validator("Merge branch 'KON-11419-dev' into dev", ok=False)

    def test_linked_worktree_may_only_commit_to_temporary_branch(self):
        worktree = self.root / "worktree"
        self.git("worktree", "add", str(worktree), "KON-11419")
        self.validator("KON-11419: test", ok=False, cwd=worktree)
        self.git("switch", "-c", "KON-11419-implementation", cwd=worktree)
        self.validator("KON-11419: test", cwd=worktree)
        self.git("switch", "-c", "KON-11419-dev", cwd=worktree)
        self.validator("KON-11419: test", ok=False, cwd=worktree)

    def test_push_dispatcher_preserves_local_hook_stdin_and_blocks_task_push(self):
        hooks = self.root / "hooks"
        hooks.mkdir()
        shutil.copy2(SKILL / "hooks/commit-msg", hooks / "pre-push")
        self.git("config", "core.hooksPath", str(hooks))
        local_hook = self.repo / ".git/hooks/pre-push"
        local_hook.write_text('#!/bin/sh\ncat > .git/push-input\n')
        local_hook.chmod(0o755)
        self.git("switch", "dev")
        self.commit("change", "change")
        self.git("push", "origin", "dev")
        self.assertIn("refs/heads/dev", (self.repo / ".git/push-input").read_text())
        self.git("push", "origin", "KON-11419", ok=False)
        self.git("config", "konsierge.commitPolicy", "false")
        self.git("push", "origin", "KON-11419")
        self.assertIn("refs/heads/KON-11419", (self.repo / ".git/push-input").read_text())

    def test_push_rejects_multiple_targets_aliases_deletion_and_rewrite(self):
        tip = self.git("rev-parse", "HEAD").stdout.strip()
        line = f"refs/heads/dev {tip} refs/heads/dev {tip}\n"
        self.policy("check-push", "origin", str(self.remote), stdin=line * 2, ok=False)
        self.policy("check-push", "origin", str(self.remote),
                    stdin=line.replace("refs/heads/dev", "refs/heads/KON-11419", 1), ok=False)
        self.policy("check-push", "origin", str(self.remote),
                    stdin=f"(delete) {'0' * 40} refs/heads/dev {tip}\n", ok=False)
        self.git("switch", "dev")
        self.commit("later", "later")
        ahead = self.git("rev-parse", "HEAD").stdout.strip()
        self.policy("check-push", "origin", str(self.remote),
                    stdin=f"refs/heads/dev {tip} refs/heads/dev {ahead}\n", ok=False)

    def test_installer_is_idempotent_and_preserves_custom_hooks(self):
        hooks = self.root / "installed-hooks"
        self.env["KONSIERGE_GIT_HOOKS_DIR"] = str(hooks)
        self.env["GIT_CONFIG_GLOBAL"] = str(self.root / "global.gitconfig")
        installer = SKILL / "scripts/install-global-commit-hook"
        self.run_cmd(["bash", installer])
        self.run_cmd(["bash", installer])
        self.assertEqual((hooks / "pre-push").read_bytes(), (SKILL / "hooks/commit-msg").read_bytes())
        (hooks / "pre-push").write_text("#!/bin/sh\nexit 17\n")
        self.run_cmd(["bash", installer], ok=False)
        self.assertEqual((hooks / "pre-push").read_text(), "#!/bin/sh\nexit 17\n")


if __name__ == "__main__":
    unittest.main()
