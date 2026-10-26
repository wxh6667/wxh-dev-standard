#!/usr/bin/env python3
"""Read-only checks for installed wxh configuration; never repairs or fetches."""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Doctor:
    def __init__(self, home: Path, skip_repo: bool = False):
        self.home = home
        self.skip_repo = skip_repo
        self.instructions = load("sync-global-instructions.py")
        self.skills = load("sync-skills.py")
        self.claude = load("sync-claude-hooks.py")
        self.zcode = load("sync-zcode.py")
        self.claude.CLAUDE_DIR = home / ".claude"
        self.zcode.HOOK_TARGET = home / ".zcode/hooks/gate-commit-trellis.py"
        self.zcode.AGENT_LINKS = {
            home / ".agents/references": ROOT / "references",
            home / ".agents/templates": ROOT / "templates",
        }
        self.failures = self.warnings = 0

    def report(self, severity: str, message: str) -> None:
        if severity == "FAIL":
            self.failures += 1
        elif severity == "WARN":
            self.warnings += 1
        print(f"[{severity}] {message}")

    def read_json(self, path: Path) -> dict | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.report("FAIL", f"cannot read valid JSON {path}: {exc}")
            return None
        if not isinstance(value, dict):
            self.report("FAIL", f"not a JSON object: {path}")
            return None
        return value

    def check_repo(self) -> None:
        if self.skip_repo:
            self.report("INFO", "cached repository check skipped")
            return
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(ROOT), "status", "--porcelain=v1", "--branch"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            self.report("WARN", f"cached repository status unavailable: {result.stderr.strip()}")
            return
        for line in result.stdout.splitlines():
            self.report("WARN" if not line.startswith("##") else "INFO", f"cached git {line}")

    def check_file(self, source: Path, target: Path, label: str) -> None:
        if not target.exists() and not target.is_symlink():
            self.report("INFO", f"{label} not installed: {target}")
        elif not target.is_file() or target.read_bytes() != source.read_bytes():
            self.report("FAIL", f"{label} differs from source: {target}")

    def check_instructions(self) -> None:
        for name, (source, target) in self.instructions.TARGETS.items():
            if not target.parent.exists():
                self.report("INFO", f"{name} host not installed")
            else:
                self.check_file(source, target, f"{name} instructions")

    def check_skills(self) -> None:
        for label, directory in (("Codex/shared", self.home / ".agents/skills"), ("Claude", self.home / ".claude/skills")):
            if not directory.exists():
                self.report("INFO", f"{label} skill directory not installed")
                continue
            for source in self.skills.skill_dirs():
                link = directory / source.name
                if not self.skills.same_target(link, source):
                    self.report("FAIL", f"{label} skill link missing or wrong: {source.name}")

    def check_claude(self) -> None:
        directory = self.home / ".claude"
        if not directory.exists():
            self.report("INFO", "Claude host not installed")
            return
        path = directory / "settings.json"
        if not path.exists():
            self.report("FAIL", f"Claude settings missing: {path}")
            return
        settings = self.read_json(path)
        for name in self.claude.HOOK_MANIFEST:
            self.check_file(ROOT / "hooks" / name, directory / "hooks" / name, f"Claude hook {name}")
        if settings is None:
            return
        merged = copy.deepcopy(settings)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                for name in self.claude.HOOK_MANIFEST:
                    self.claude.register_settings(name, merged)
                self.claude.sync_permissions(merged)
                self.claude.sync_sandbox(merged)
                self.claude.sync_skill_overrides(merged)
                self.claude.sync_settings_keys(merged)
                self.claude.sync_statusline(merged)
        except SystemExit as exc:
            self.report("FAIL", f"Claude settings invalid: {exc}")
            return
        if merged != settings:
            self.report("WARN", "Claude settings have missing baseline entries or redundant permissions")
        statusline = settings.get("statusLine")
        if statusline is not None and not self.claude.is_wxh_statusline(statusline):
            self.report("INFO", "Claude uses a user-owned statusLine")
        for name, mode in settings.get("skillOverrides", {}).items():
            if name in self.claude.SKILL_OVERRIDES_BASELINE and mode != self.claude.SKILL_OVERRIDES_BASELINE[name]:
                self.report("INFO", f"preserving user skill choice: {name}")

    def check_zcode(self) -> None:
        directory = self.home / ".zcode"
        if not directory.exists():
            self.report("INFO", "ZCode host not installed")
            return
        for conflict in self.zcode.agent_link_conflicts():
            self.report("FAIL", f"ZCode shared link conflict: {conflict}")
        path = directory / "cli/config.json"
        config = self.read_json(path) if path.exists() else None
        if config is not None:
            merged = copy.deepcopy(config)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.zcode.merge_hooks(merged)
            except SystemExit as exc:
                self.report("FAIL", f"ZCode settings invalid: {exc}")
            else:
                if merged != config:
                    self.report("FAIL", "ZCode hook registration missing or stale")
        hook = directory / "hooks/gate-commit-trellis.py"
        if not hook.is_file():
            self.report("FAIL", "ZCode adapted hook missing")

    @staticmethod
    def direct_serena(entry: dict) -> bool:
        return (
            entry.get("command") == "serena"
            and isinstance(entry.get("args"), list)
            and all(isinstance(arg, str) for arg in entry["args"])
            and entry["args"] == ["start-mcp-server", "--context=claude-code", "--project-from-cwd"]
        )

    def compare_mcp(self, config_path: Path, servers: dict | None, baseline: dict) -> None:
        if servers is None:
            self.report("WARN", f"MCP configuration unavailable: {config_path}")
            return
        for name, expected in baseline.items():
            if not isinstance(servers, dict):
                self.report("FAIL", f"MCP servers must be an object: {config_path}")
                return
            actual = servers.get(name)
            if actual is None:
                self.report("FAIL", f"MCP server missing: {name} in {config_path}")
                continue
            if not isinstance(actual, dict):
                self.report("FAIL", f"MCP server invalid: {name} in {config_path}")
                continue
            if self.direct_serena(actual) and name == "serena":
                self.report("WARN", f"Serena uses documented direct-binary local override in {config_path}")
            else:
                differences = []
                for key in ("command", "args"):
                    if actual.get(key) != expected.get(key):
                        differences.append(key)
            expected_env = expected.get("env", {})
            actual_env = actual.get("env", {})
            expected_keys = set(expected_env)
            for key, value in expected_env.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}") and value[2:-1] not in os.environ:
                    expected_keys.discard(key)
            # A configured private value replaces a template placeholder without drift.
            if set(actual_env) == set(expected_env) if isinstance(actual_env, dict) else False:
                expected_keys = set(actual_env)
            if not isinstance(actual_env, dict) or set(actual_env) != expected_keys:
                differences.append("env key names")
            if differences:
                self.report("FAIL", f"MCP server {name} differs in {', '.join(differences)}: {config_path}")

    def check_mcp(self) -> None:
        baseline = json.loads((ROOT / "mcp/claude.mcp.example.json").read_text(encoding="utf-8"))["mcpServers"]
        baseline = {name: self.zcode.clean_env(entry) for name, entry in copy.deepcopy(baseline).items()}
        path = self.home / ".claude.json"
        if (self.home / ".claude").exists():
            config = self.read_json(path) if path.exists() else None
            servers = config.get("mcpServers") if config else None
            self.compare_mcp(path, servers, baseline)
        zpath = self.home / ".zcode/cli/config.json"
        if zpath.parent.exists():
            config = self.read_json(zpath) if zpath.exists() else None
            mcp = config.get("mcp", {}) if config else None
            servers = mcp.get("servers") if isinstance(mcp, dict) else None
            self.compare_mcp(zpath, servers, baseline)

    def check_sandbox_dependencies(self) -> None:
        if os.name != "nt":
            for command in ("bwrap", "socat"):
                if shutil.which(command) is None:
                    self.report("WARN", f"sandbox dependency missing: {command}; runtime isolation not verified")

    def check_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate-skills.py")],
            capture_output=True, text=True, check=False, env=dict(os.environ, PYTHONIOENCODING="utf-8"),
        )
        output = (result.stdout + result.stderr).strip()
        self.report("OK" if result.returncode == 0 else "FAIL", f"skill validation: {output}")

    def run(self) -> int:
        self.check_repo()
        self.check_instructions()
        self.check_skills()
        self.check_claude()
        self.check_zcode()
        self.check_mcp()
        self.check_sandbox_dependencies()
        self.check_validation()
        print(f"Summary: {self.failures} failure(s), {self.warnings} warning(s); read-only, cached repository state")
        return 1 if self.failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-repo", action="store_true")
    args = parser.parse_args()
    return Doctor(Path.home(), args.skip_repo).run()


if __name__ == "__main__":
    raise SystemExit(main())
