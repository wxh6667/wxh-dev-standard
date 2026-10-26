#!/usr/bin/env python3
"""Check discovery fields, invocation consistency and concrete Markdown links."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


def collect(source: Path) -> list[Path]:
    if not source.is_dir():
        return []
    if (source / "SKILL.md").is_file():
        return [source]
    return sorted(p for p in source.iterdir() if p.is_dir())


def parse_yaml(text: str, label: str, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: YAML must be an object")
        return None
    return value


def validate(root: Path = ROOT) -> tuple[int, list[str]]:
    if yaml is None:
        return 0, ["PyYAML is required; install requirements-dev.txt"]
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
        frontmatter = parse_yaml(text[4:end], label, errors)
        if frontmatter is None:
            continue
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not isinstance(name, str) or name != directory.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append(f"{label}: name must be a string matching the directory in lowercase hyphenated words")
            name = None
        if name in names:
            errors.append(f"{label}: duplicate skill name {name}")
        if name is not None:
            names.add(name)
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{label}: description must be a non-empty string")
        elif len(description) > 1024:
            errors.append(f"{label}: description exceeds 1024 characters (ZCode/Agent Skills limit)")
        disabled = frontmatter.get("disable-model-invocation")
        if disabled is not None and not isinstance(disabled, bool):
            errors.append(f"{label}: disable-model-invocation must be a YAML boolean")
        metadata = directory / "agents" / "openai.yaml"
        policy = None
        if metadata.is_file():
            meta = parse_yaml(metadata.read_text(encoding="utf-8"), str(metadata.relative_to(root)), errors)
            if meta is not None:
                policy_section = meta.get("policy", {})
                if not isinstance(policy_section, dict):
                    errors.append(f"{metadata.relative_to(root)}: policy must be an object")
                else:
                    policy = policy_section.get("allow_implicit_invocation")
                if policy is not None and not isinstance(policy, bool):
                    errors.append(f"{metadata.relative_to(root)}: allow_implicit_invocation must be a YAML boolean")
                    policy = None
            if disabled is True and policy is None:
                errors.append(f"{label}: Codex metadata must set allow_implicit_invocation: false")
            elif policy is not None and (disabled is True) != (policy is False):
                errors.append(f"{label}: Claude and Codex explicit invocation settings disagree")
        elif disabled is True:
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
