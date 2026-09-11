#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
errors = []
count = 0

for directory in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    skill = directory / "SKILL.md"
    if not skill.exists():
        errors.append(f"{directory.relative_to(ROOT)}: missing SKILL.md")
        continue

    count += 1
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{skill.relative_to(ROOT)}: missing YAML frontmatter")
        continue

    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{skill.relative_to(ROOT)}: unclosed YAML frontmatter")
        continue

    frontmatter = text[4:end]
    name_match = re.search(r"(?m)^name:\s*(.+?)\s*$", frontmatter)
    desc_match = re.search(r"(?m)^description:\s*(.+?)\s*$", frontmatter)
    if not name_match:
        errors.append(f"{skill.relative_to(ROOT)}: missing name")
    elif name_match.group(1).strip(" '\"") != directory.name:
        errors.append(
            f"{skill.relative_to(ROOT)}: name must match directory ({directory.name})"
        )
    if not desc_match or not desc_match.group(1).strip(" '\""):
        errors.append(f"{skill.relative_to(ROOT)}: missing description")

    openai_meta = directory / "agents" / "openai.yaml"
    if openai_meta.exists():
        meta = openai_meta.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", meta, re.I):
            errors.append(
                f"{openai_meta.relative_to(ROOT)}: implicit invocation is disabled; this global library expects automatic matching"
            )

if count == 0:
    errors.append("no skills found")

if errors:
    print("Skill validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"OK: validated {count} skills; implicit invocation policy is compatible")
