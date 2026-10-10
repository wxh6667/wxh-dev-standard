#!/usr/bin/env python3
"""Check discovery fields, invocation consistency and concrete Markdown links.

This lightweight check does not replace a host's full YAML/schema validation.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def collect(source: Path) -> list[Path]:
    if not source.is_dir():
        return []
    if (source / "SKILL.md").is_file():
        return [source]
    return sorted(p for p in source.iterdir() if p.is_dir())


def field(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*(.*)$", frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value in {">", "|", ">-", "|-"}:
        lines = []
        for line in frontmatter[match.end():].splitlines():
            if line and not line[0].isspace():
                break
            if line.strip():
                lines.append(line.strip())
        return " ".join(lines)
    return value.strip(" \t'\"")


def validate(root: Path = ROOT) -> tuple[int, list[str]]:
    errors = []
    directories = collect(root / "skills")
    vendor = root / "skills-vendor"
    if vendor.is_dir():
        for group in sorted(p for p in vendor.iterdir() if p.is_dir()):
            directories.extend(collect(group))
    names = set()
    count = 0
    for directory in sorted(directories):
        skill = directory / "SKILL.md"
        label = str(skill.relative_to(root))
        if not skill.is_file():
            errors.append(f"{label}: missing SKILL.md")
            continue
        count += 1
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{label}: missing YAML frontmatter")
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            errors.append(f"{label}: unclosed YAML frontmatter")
            continue
        frontmatter = text[4:end]
        name = field(frontmatter, "name")
        description = field(frontmatter, "description")
        if name != directory.name or not name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append(f"{label}: name must match directory and use lowercase hyphenated words")
        if name in names:
            errors.append(f"{label}: duplicate skill name {name}")
        names.add(name)
        if not description:
            errors.append(f"{label}: missing description")
        elif len(description) > 1024:
            errors.append(f"{label}: description exceeds 1024 characters (ZCode/Agent Skills limit)")
        disabled = field(frontmatter, "disable-model-invocation")
        if disabled not in {None, "true", "false"}:
            errors.append(f"{label}: disable-model-invocation must be true or false")
        metadata = directory / "agents" / "openai.yaml"
        if metadata.is_file():
            meta = metadata.read_text(encoding="utf-8")
            policy = re.search(r"(?m)^[ \t]*allow_implicit_invocation:[ \t]*(\S+)[ \t]*$", meta)
            if policy and policy.group(1) not in {"true", "false"}:
                errors.append(f"{metadata.relative_to(root)}: invalid invocation boolean")
            elif (disabled == "true") != bool(policy and policy.group(1) == "false"):
                errors.append(f"{label}: Claude and Codex explicit invocation settings disagree")
        elif disabled == "true":
            errors.append(f"{label}: explicit invocation needs agents/openai.yaml for Codex")

        # Check literal links in instructions, not examples inside fenced code.
        body = re.sub(r"(?ms)^(```|~~~).*?^\1[^\n]*$", "", text[end + 5:])
        body = re.sub(r"(`+).*?\1", "", body, flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
            target = target.strip().split(" ", 1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("#"):
                continue
            path = unquote(parsed.path)
            if not path or any(char in path for char in "<>{}*"):
                continue
            if not (directory / path).exists():
                errors.append(f"{label}: missing local link {path}")
    if count == 0:
        errors.append("no skills found")
    return count, errors


def main() -> int:
    count, errors = validate()
    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: validated {count} skills; names, descriptions, invocation policy and Markdown links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
