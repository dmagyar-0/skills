#!/usr/bin/env python3
"""Self-test for this repository. Run: python3 tests/check_repo.py

Checks that every skill follows the portable Agent Skills format (works in Claude Code
and Kiro), that the copies of check_artifact.py are identical, that the worked examples
pass the checker, and that the templates still fail it (they contain placeholders).
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata"}
problems = []


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    keys, values = [], {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:  # top-level key (no indentation)
            keys.append(km.group(1))
            values[km.group(1)] = km.group(2).strip()
    return keys, values


for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    md = skill / "SKILL.md"
    if not md.exists():
        problems.append(f"{skill.name}: missing SKILL.md")
        continue
    text = md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        problems.append(f"{skill.name}: SKILL.md has no YAML frontmatter")
        continue
    keys, values = fm
    extra = set(keys) - ALLOWED_KEYS
    if extra:
        problems.append(f"{skill.name}: non-portable frontmatter keys {sorted(extra)}")
    if values.get("name") != skill.name:
        problems.append(f"{skill.name}: name must equal folder name")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", values.get("name", "")):
        problems.append(f"{skill.name}: name must be lowercase letters, digits, hyphens, max 64")
    desc = values.get("description", "")
    if not desc or len(desc) > 1024:
        problems.append(f"{skill.name}: description missing or over 1024 characters")
    lines = text.count("\n")
    if lines > 150:
        problems.append(f"{skill.name}: SKILL.md is {lines} lines; keep it short for smaller models")
    # Files the SKILL.md refers to must exist.
    for ref in re.findall(r"`((?:assets|references|scripts)/[^`\s]+)`", text):
        if not (skill / ref).exists():
            problems.append(f"{skill.name}: SKILL.md refers to {ref}, which does not exist")

checkers = sorted(SKILLS.glob("*/scripts/check_artifact.py"))
if len({c.read_bytes() for c in checkers}) > 1:
    problems.append("copies of check_artifact.py differ: " + ", ".join(str(c.relative_to(ROOT)) for c in checkers))
checker = checkers[0]

# Worked examples must pass when laid out as a real change folder.
with tempfile.TemporaryDirectory() as tmp:
    change = Path(tmp) / "intent" / "claims-status-self-service"
    change.mkdir(parents=True)
    for kind, skill in (("intent", "sdlc-intent"), ("spec", "sdlc-spec"), ("plan", "sdlc-plan")):
        shutil.copy(SKILLS / skill / "references" / f"example-{kind}.md", change / f"{kind}.md")
    r = subprocess.run([sys.executable, "-I", str(checker), *map(str, sorted(change.glob("*.md")))],
                       capture_output=True, text=True)
    if r.returncode != 0:
        problems.append("worked examples fail the checker:\n" + r.stdout)

    # Templates must fail (placeholders left), proving the checker catches unfilled files.
    for kind, skill in (("intent", "sdlc-intent"), ("spec", "sdlc-spec"), ("plan", "sdlc-plan")):
        t = change / f"{kind}.md"
        shutil.copy(SKILLS / skill / "assets" / f"{kind}-template.md", t)
        r = subprocess.run([sys.executable, "-I", str(checker), str(t)], capture_output=True, text=True)
        if r.returncode == 0:
            problems.append(f"{kind}-template.md passes the checker; placeholders are not detected")

if problems:
    print("FAIL")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print(f"OK: {len(list(SKILLS.iterdir()))} skills, {len(checkers)} identical checkers, examples pass, templates rejected")
