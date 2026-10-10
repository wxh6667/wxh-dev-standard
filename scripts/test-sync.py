#!/usr/bin/env python3
"""Regression checks use temporary files; never touch installed agent settings."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_shared_instruction_semantics(self):
        expected = (ROOT / "AGENTS.md").read_text().split("\n", 1)[1]
        for relative in ("CLAUDE.md", "zcode/AGENTS.md"):
            self.assertEqual((ROOT / relative).read_text().split("\n", 1)[1], expected)

    def test_claude_choices_and_idempotence(self):
        module = load("scripts/sync-claude-hooks.py")
        settings = {"permissions": {"defaultMode": "default", "ask": ["Bash(custom:*)"], "allow": ["Read"]},
                    "skillOverrides": {"cloudflare": "on", "app-shell-ui": "off"}, "model": "custom"}
        module.sync_permissions(settings)
        module.sync_skill_overrides(settings)
        self.assertEqual(settings["permissions"]["defaultMode"], "default")
        self.assertIn("Bash(custom:*)", settings["permissions"]["ask"])
        self.assertEqual(settings["permissions"]["allow"], ["Read"])
        self.assertEqual(settings["skillOverrides"]["cloudflare"], "on")
        self.assertEqual(settings["skillOverrides"]["app-shell-ui"], "off")
        self.assertEqual(settings["model"], "custom")
        before = copy.deepcopy(settings)
        module.sync_permissions(settings)
        module.sync_skill_overrides(settings)
        self.assertEqual(settings, before)

    def test_claude_mixed_hooks_and_ownership(self):
        module = load("scripts/sync-claude-hooks.py")
        name = "gate-commit-trellis.py"
        own = module.wanted_group(name)
        own["hooks"][0]["timeout"] = 1
        user = {"type": "command", "command": "python3 /user/gate-commit-trellis.py"}
        own["hooks"].append(user)
        own["user_field"] = "keep"
        settings = {"hooks": {"PreToolUse": [own]}}
        module.register_settings(name, settings)
        self.assertEqual(len(settings["hooks"]["PreToolUse"]), 1)
        self.assertEqual(own["hooks"][1], user)
        self.assertEqual(own["user_field"], "keep")
        self.assertEqual(own["hooks"][0]["timeout"], 15)
        before = copy.deepcopy(settings)
        module.register_settings(name, settings)
        self.assertEqual(settings, before)
        custom = {"statusLine": {"type": "command", "command": "bash /user/statusline.sh"}}
        before = copy.deepcopy(custom)
        module.sync_statusline(custom)
        self.assertEqual(custom, before)

    def test_invalid_settings_are_rejected(self):
        module = load("scripts/sync-claude-hooks.py")
        for value in ({"permissions": []}, {"permissions": {"ask": "custom"}}, {"permissions": {"ask": [1]}}):
            with self.assertRaises(SystemExit):
                module.sync_permissions(value)
        with self.assertRaises(SystemExit):
            module.sync_skill_overrides({"skillOverrides": []})
        for value in ({"hooks": []}, {"hooks": {"PreToolUse": {"user_value": "keep"}}}):
            before = copy.deepcopy(value)
            with self.assertRaises(SystemExit):
                module.register_settings("gate-commit-trellis.py", value)
            self.assertEqual(value, before)

    def test_zcode_mixed_hooks_and_disabled_setting(self):
        module = load("scripts/sync-zcode.py")
        own = module.wanted_hook_group()
        own["hooks"][0]["timeout"] = 1
        user = {"type": "command", "command": "python3 /user/gate-commit-trellis.py"}
        own["hooks"].append(user)
        own["user_field"] = "keep"
        config = {"hooks": {"enabled": False, "events": {"PreToolUse": [own]}}}
        module.merge_hooks(config)
        self.assertFalse(config["hooks"]["enabled"])
        self.assertEqual(own["hooks"][1], user)
        self.assertEqual(own["user_field"], "keep")
        self.assertEqual(own["hooks"][0]["timeout"], 15)
        before = copy.deepcopy(config)
        module.merge_hooks(config)
        self.assertEqual(config, before)

    def test_instruction_sync_does_not_write_through_symlink(self):
        module = load("scripts/sync-global-instructions.py")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = directory / "source.md"
            outside = directory / "user.md"
            target = directory / "AGENTS.md"
            source.write_text("new rules")
            outside.write_text("user rules")
            target.symlink_to(outside)
            module.TARGETS = {"test": (source, target)}
            module.sync_one("test")
            self.assertEqual(outside.read_text(), "user rules")
            self.assertEqual(target.read_text(), "new rules")
            self.assertFalse(target.is_symlink())
            self.assertEqual(len(list(directory.glob("AGENTS.md.bak-wxh-*"))), 1)

    def test_gate_direct_commands_and_query_failure(self):
        gate = load("hooks/gate-commit-trellis.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            scripts = root / ".trellis/scripts"
            scripts.mkdir(parents=True)
            task = scripts / "task.py"
            task.write_text('print(\'{"current_task": null}\')')
            subdir = root / "src"
            subdir.mkdir()
            other = root / "ordinary"
            other.mkdir()
            (other / ".git").mkdir()
            self.assertEqual(gate.trellis_root(subdir), root)
            self.assertIsNone(gate.trellis_root(other))
            self.assertEqual(gate.commit_contexts("(cd ordinary); git commit", str(root))[0][0], root)
            self.assertEqual(gate.commit_contexts("cd ordinary | cat; git commit", str(root))[0][0], root)
            self.assertEqual(gate.commit_contexts("cd ordinary && git commit", str(root))[0][0], other)
            for command in ("git commit -m change", "pwd\ngit commit -m change", f"git -C {root} commit -m change", "git commit -m no-trellis"):
                payload = {"tool_name": "Bash", "cwd": str(subdir), "tool_input": {"command": command}}
                result = subprocess.run([sys.executable, str(ROOT / "hooks/gate-commit-trellis.py")], input=json.dumps(payload), capture_output=True, text=True)
                self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertEqual(gate.commit_contexts('echo "git commit"', str(root)), [])
            self.assertTrue(gate.commit_contexts("WXH_TRELLIS_BYPASS=1 git commit", str(root))[0][1])
            task.write_text('print(\'{"current_task": {"dir": "active"}}\')')
            self.assertEqual(gate.active_task_state(str(root)), "has")
            task.write_text('print(\'{}\')')
            self.assertEqual(gate.active_task_state(str(root)), "unknown")
            task.write_text('raise SystemExit(1)')
            self.assertEqual(gate.active_task_state(str(root)), "unknown")

    def test_four_host_installation_in_temporary_home(self):
        with tempfile.TemporaryDirectory(prefix="wxh home ") as tmp:
            home = Path(tmp)
            env = dict(os.environ, HOME=tmp)
            commands = [
                ["scripts/sync-global-instructions.py", "--all"],
                ["scripts/sync-skills.py", "--all"],
                ["scripts/sync-claude-hooks.py"],
                ["scripts/sync-zcode.py"],
            ]
            for command in commands:
                result = subprocess.run([sys.executable, str(ROOT / command[0]), *command[1:]], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            for relative, source in ((".codex/AGENTS.md", "AGENTS.md"), (".claude/CLAUDE.md", "CLAUDE.md"), (".pi/agent/AGENTS.md", "AGENTS.md"), (".zcode/AGENTS.md", "zcode/AGENTS.md")):
                self.assertEqual((home / relative).read_bytes(), (ROOT / source).read_bytes())
            for relative in (".agents/skills", ".claude/skills"):
                self.assertEqual(len(list((home / relative).iterdir())), 68)
                for skill in (home / relative).iterdir():
                    self.assertTrue(skill.is_symlink())
                    self.assertTrue((skill / "SKILL.md").is_file())
            adapted = (home / ".zcode/hooks/gate-commit-trellis.py").read_text()
            self.assertIn("sys.exit(2)", adapted)
            self.assertNotIn('"hookSpecificOutput"', adapted)
            project = home / "project"
            (project / ".git").mkdir(parents=True)
            scripts = project / ".trellis/scripts"
            scripts.mkdir(parents=True)
            (scripts / "task.py").write_text('print(\'{"current_task": null}\')')
            payload = {"tool_name": "Bash", "cwd": str(project), "tool_input": {"command": "git commit"}}
            result = subprocess.run([sys.executable, str(home / ".zcode/hooks/gate-commit-trellis.py")], input=json.dumps(payload), capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("Trellis", result.stderr)
            before = {path: path.read_bytes() for path in (home / ".claude/settings.json", home / ".zcode/cli/config.json")}
            for command in commands:
                result = subprocess.run([sys.executable, str(ROOT / command[0]), *command[1:]], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            for path, data in before.items():
                self.assertEqual(path.read_bytes(), data)

    def test_settings_symlinks_are_preserved(self):
        for script, relative in (("sync-claude-hooks.py", ".claude/settings.json"), ("sync-zcode.py", ".zcode/cli/config.json")):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                external = home / "external.json"
                external.write_text('{"user_field": "keep"}')
                target = home / relative
                target.parent.mkdir(parents=True)
                target.symlink_to(external)
                result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("symlink", result.stderr)
                self.assertEqual(external.read_text(), '{"user_field": "keep"}')
                self.assertTrue(target.is_symlink())

    def test_validator_reports_real_failures(self):
        module = load("scripts/validate-skills.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills/example"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: example\n---\n[required](missing.md)\n")
            count, errors = module.validate(root)
            self.assertEqual(count, 1)
            self.assertTrue(any("missing local link" in error for error in errors))
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: " + "x" * 1025 + "\n---\n")
            self.assertTrue(any("1024" in error for error in module.validate(root)[1]))
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: example\ndisable-model-invocation: true\n---\n")
            self.assertTrue(any("openai.yaml" in error for error in module.validate(root)[1]))

    def test_git_guard_checks_commands_not_quoted_text(self):
        script = ROOT / "skills-vendor/mattpocock/git-guardrails-claude-code/scripts/block-dangerous-git.sh"
        blocked = ("git -C /tmp push", "git clean -df", "pwd\ngit reset --hard", "git restore --worktree .")
        allowed = ('echo "git push"', 'git commit -m "git push"', "git status", "git checkout main")
        for command in blocked + allowed:
            result = subprocess.run(["bash", str(script)], input=json.dumps({"tool_input": {"command": command}}), capture_output=True, text=True)
            self.assertEqual(result.returncode, 2 if command in blocked else 0, command)
            self.assertNotIn(command, result.stderr)

    def test_wizard_reports_failed_writes_as_incomplete(self):
        source = (ROOT / "skills-vendor/mattpocock/wizard/template.sh").read_text()
        library = source[:source.index("# STAGES: author")]
        fixture = library + '''
gh() {
  if [[ "$1" == auth ]]; then return 0; fi
  printf 'fixture write denied\n' >&2
  return 7
}
set_secret TEST_NAME fixture
set_var TEST_NAME fixture
finish
'''
        result = subprocess.run(["bash", "-c", fixture], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Setup incomplete", result.stdout)
        self.assertIn("secret write failed", result.stdout)
        self.assertIn("variable write failed", result.stdout)
        self.assertIn("fixture write denied", result.stderr)
        self.assertNotIn("Setup complete", result.stdout)


if __name__ == "__main__":
    unittest.main()
