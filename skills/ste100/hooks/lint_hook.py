#!/usr/bin/env python
"""Advisory writing checks for Claude Code hooks. Never blocks.

PostToolUse (Write|Edit on a .md file): lint the file with
skills/ste100/scripts/ste-lint.py and, when it has violations, print the
offending text and line number for each hit (capped at MAX_HOOK_HITS) to
stderr and exit 2 so the model sees it. Exit 2 on PostToolUse is advisory:
the tool already ran. Agent-internal Markdown, such as memory files under
the Claude configuration directory, is skipped. The writing rules do not
govern it, and a summary of its violations only spends tokens. Set
ASD_STE100_LINT_EXCLUDE to skip more paths.

Stop: read `last_assistant_message`, check the reply register (no headers,
bullets, bold, or em-dashes), and return a systemMessage only when the reply
breaks it. Always exit 0, so the session never loops.
"""
import fnmatch
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LINTER = HERE.parent / "scripts" / "ste-lint.py"
SLOP = HERE.parent / "slop.tsv"

MAX_HOOK_HITS = 12
CLAUDE_DIR = ".claude"
OPENERS = re.compile(
    r"^\s*(certainly|great question|you're absolutely right|sure[,!]|"
    r"absolutely[,!])", re.I,
)
CLOSERS = re.compile(r"(\b(?:i\s+)?hope this helps\b|let me know if|feel free to)", re.I)


def _run_linter(path):
    try:
        r = subprocess.run(
            [sys.executable, str(LINTER), str(path)],
            capture_output=True, text=True, timeout=15,
        )
        return (r.stdout + r.stderr)
    except (subprocess.TimeoutExpired, OSError):
        return ""


def _parse_findings(output):
    """Pull (line, rule, message) tuples out of ste-lint.py text output."""
    findings = []
    for line in output.splitlines():
        m = re.match(
            r"^\S+:(\d+):\d+ (\S+):\s+(.+)$", line.strip(),
        )
        if m:
            findings.append((int(m.group(1)), m.group(2), m.group(3)))
    return findings


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    return re.sub(r"`[^`]*`", " ", text)


def absolute(path, cwd=None):
    """Make the path absolute. The harness can send it relative to the session directory."""
    return pathlib.Path(cwd or ".", pathlib.Path(path).expanduser()).absolute()


def variants(path):
    """The path as written and the path with symlinks resolved. An exclusion matches either form.

    A symlink hides a directory name in both directions. `notes.md` can point into `.claude`,
    and `.claude` itself can point at a dotfiles repository. Both forms must miss for the
    file to reach the linter.
    """
    return {pathlib.Path(os.path.normpath(path)), path.resolve()}


def excluded(target):
    """True for agent-internal Markdown and for the paths the user excludes."""
    config_dirs = variants(absolute(os.environ.get("CLAUDE_CONFIG_DIR") or f"~/{CLAUDE_DIR}"))
    raw = os.environ.get("ASD_STE100_LINT_EXCLUDE", "").split(os.pathsep)
    patterns = [os.path.expanduser(p) for p in raw if p]
    for form in variants(target):
        if CLAUDE_DIR in form.parts or any(form.is_relative_to(d) for d in config_dirs):
            return True
        if any(fnmatch.fnmatch(str(form), p) for p in patterns):
            return True
    return False


def post_tool_use(event):
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(".md"):
        return 0
    target = absolute(path, event.get("cwd"))
    if excluded(target):
        return 0
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return 0
    output = _run_linter(str(target))
    findings = _parse_findings(output)
    if not findings:
        return 0
    lines = [f"asd-ste100: {target.name} has {len(findings)} STE violation(s)."]
    for lineno, rule, msg in findings[:MAX_HOOK_HITS]:
        lines.append(f"  line {lineno}, {rule}: {msg}")
    if len(findings) > MAX_HOOK_HITS:
        lines.append(f"  and {len(findings) - MAX_HOOK_HITS} more hit(s).")
    lines.append("Fix these hits in the file you just wrote, then continue.")
    sys.stderr.write("\n".join(lines) + "\n")
    return 2


def slop_words():
    words = set()
    if SLOP.exists():
        with open(SLOP) as f:
            for line in f:
                w = line.strip().lower()
                if w and not w.startswith("#"):
                    words.add(w)
    return words


def stop(event):
    reply = event.get("last_assistant_message") or ""
    problems = []
    stripped = strip_code(reply)
    if "—" in stripped or "–" in stripped:
        problems.append("em-dash")
    if "**" in stripped or "__" in stripped:
        problems.append("bold span")
    if re.search(r"(?m)^#{1,6} ", stripped):
        problems.append("header")
    if re.search(r"(?m)^[-*+] ", stripped):
        problems.append("list item")
    if OPENERS.search(reply):
        problems.append("a filler opener")
    if CLOSERS.search(reply):
        problems.append("a filler closer")
    found = [w for w in stripped.lower().split() if w in slop_words()]
    if found:
        problems.append(f"{len(found)} slop word(s)")
    if problems:
        print(json.dumps({
            "systemMessage": (
                "asd-ste100 reply check: " + "; ".join(problems)
                + ". Answer in prose."
            ),
        }))
    return 0


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    try:
        name = event.get("hook_event_name", "")
        if name == "PostToolUse":
            return post_tool_use(event)
        if name == "Stop":
            return stop(event)
    except Exception:  # noqa: BLE001  advisory hook: a crash must never block or loop the session
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
