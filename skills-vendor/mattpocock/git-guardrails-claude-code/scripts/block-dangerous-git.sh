#!/usr/bin/env bash
# Direct-command workflow guard. Does not inspect script bodies or dynamic wrappers.
exec python3 -c '
import json
from pathlib import Path
import shlex
import sys

# Set False in the installed copy when only destructive operations are blocked.
BLOCK_ALL_PUSH = True
try:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str):
        raise ValueError("command must be a string")
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    segments = [[]]
    for token in lexer:
        if token and all(c in ";&|()\n" for c in token):
            segments.append([])
        else:
            segments[-1].append(token)
except (ValueError, AttributeError) as error:
    print("Git guard could not inspect input: " + str(error), file=sys.stderr)
    sys.exit(2)

for words in segments:
    if words and words[0] == "env":
        words = words[1:]
    while words and "=" in words[0] and words[0].split("=", 1)[0].isidentifier():
        words = words[1:]
    if not words or Path(words[0]).name != "git":
        continue
    i = 1
    while i < len(words) and words[i].startswith("-"):
        i += 2 if words[i] in {"-C", "-c", "--git-dir", "--work-tree"} else 1
    if i >= len(words):
        continue
    operation, args = words[i], words[i+1:]
    dangerous = (
        operation == "push" and (BLOCK_ALL_PUSH or any(a.startswith("--force") or (a.startswith("-") and not a.startswith("--") and "f" in a[1:]) for a in args))
        or operation == "reset" and "--hard" in args
        or operation == "clean" and any(a == "--force" or (a.startswith("-") and not a.startswith("--") and "f" in a[1:]) for a in args)
        or operation == "branch" and ("-D" in args or ("--delete" in args and "--force" in args))
        or operation in {"checkout", "restore"} and "." in args
    )
    if dangerous:
        print("BLOCKED: git " + operation + " is disabled by the configured workflow policy.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
'
