# AI Constraint Cleanup Reference

Use with `skills/agent-config-cleanup/SKILL.md` when a workstation/server has accumulated overlapping agent rules and Skills.

## Linux/macOS discovery

Run read-only discovery first and only for paths that exist:

```bash
printf 'HOME=%s\n' "$HOME"
for p in \
  "$HOME/.agents" \
  "$HOME/.claude" \
  "$HOME/.codex" \
  "$HOME/.cursor" \
  "$HOME/.config"; do
  [ -e "$p" ] && { echo "===== $p ====="; find "$p" -maxdepth 3 -type f -printf '%p\n' 2>/dev/null | sort; }
done

find . -maxdepth 4 -type f \
  \( -name 'AGENTS.md' -o -name 'CLAUDE.md' -o -name 'SKILL.md' -o -name '*.mdc' -o -name '*rules*' \) \
  -print 2>/dev/null | sort
```

For suspicious duplicate text rules, compare filenames/content before removal:

```bash
find "$HOME/.agents" "$HOME/.claude" "$HOME/.codex" . \
  -type f \( -name '*.md' -o -name '*.mdc' \) -size -2M \
  -exec sha256sum {} + 2>/dev/null | sort
```

Do not include credential stores, session databases, SSH keys or opaque binary tool state in content dumps.

## Windows PowerShell discovery

```powershell
$paths = @(
  "$HOME\.agents",
  "$HOME\.claude",
  "$HOME\.codex",
  "$HOME\.cursor"
)
foreach ($p in $paths) {
  if (Test-Path $p) {
    Write-Host "===== $p ====="
    Get-ChildItem $p -Recurse -File -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty FullName
  }
}

Get-ChildItem . -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -in @('AGENTS.md','CLAUDE.md','SKILL.md') -or $_.Extension -eq '.mdc' } |
  Select-Object -ExpandProperty FullName
```

## Classification hints

**Global keep:** short stable preferences such as preferred deployment approach or response/work style.

**Skill:** multi-step reusable workflows: project intake, debugging, Git isolation, Docker/CNB build, deployment, delivery, cleanup.

**Project-local:** project architecture, commands, business rules, CodeGraph/Trellis project config/index pointers, repo-specific AGENTS instructions.

**Remove candidate:** identical copies, older superseded prompts, generated exports, rules referring to tools no longer installed, or instructions fully covered by a canonical Skill.

Before deletion, make a timestamped backup of hand-written configuration being changed. Do not blindly back up credential/session caches into a public repository.

## Verification

After consolidation, open at least one real project and verify: the coding agent starts, expected Skills are discoverable, CodeGraph/Trellis project context still works or can be reinitialized, and there is no obvious contradictory duplicate rule being loaded from both global and project scope.
