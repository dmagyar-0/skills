#!/usr/bin/env python3
"""Check an SDLC artifact (intent.md, spec.md or plan.md) against its template.

Usage:  python3 check_artifact.py path/to/intent.md [more files...]

Exit code 0 when every file passes, 1 otherwise. Standard library only.
The artifact type is taken from the file name (intent.md, spec.md, plan.md).

This file is copied identically into sdlc-intent, sdlc-spec and sdlc-plan so each
skill folder stays self-contained. Edit all copies together.
"""
import re
import sys
from pathlib import Path

RULES = {
    "intent": {
        "title": "Intent:",
        "fields": ["Author", "Date", "Status", "Source"],
        "statuses": ["draft", "accepted", "rejected"],
        "sections": [
            "Problem",
            "Proposed outcome",
            "Affected users and systems",
            "Constraints",
            "Out of scope",
            "What success looks like",
            "Open questions",
        ],
    },
    "spec": {
        "title": "Spec:",
        "fields": ["Intent", "Author", "Date", "Status"],
        "statuses": ["draft", "approved", "rejected"],
        "sections": [
            "Summary",
            "Requirements",
            "Design",
            "Acceptance criteria",
            "Policies applied",
            "Areas of concern",
            "Open questions",
            "Out of scope",
        ],
    },
    "plan": {
        "title": "Plan:",
        "fields": ["Intent", "Spec", "Author", "Date", "Status"],
        "statuses": ["draft", "accepted", "superseded"],
        "sections": [
            "Files that change",
            "Order of work",
            "Risks",
            "Alternatives considered",
            "Proof",
            "Deviations from plan",
        ],
    },
}

PLACEHOLDER = re.compile(r"<[a-z][a-z0-9 _/|.,-]{0,60}>")
INLINE_CODE = re.compile(r"`[^`]*`")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def strip_code(lines):
    """Drop fenced code blocks so their contents are not checked."""
    out, fenced = [], False
    for line in lines:
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def check(path):
    errors = []
    kind = path.stem.lower().rsplit("-", 1)[-1]  # "example-spec" counts as spec
    if kind not in RULES:
        return ["file name must be intent.md, spec.md or plan.md"]
    rule = RULES[kind]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read file: {exc}"]
    lines = strip_code(text.splitlines())

    # Title
    first = next((l for l in lines if l.strip()), "")
    if not first.startswith("# " + rule["title"]):
        errors.append(f'first line must start with "# {rule["title"]} <title>"')

    # Metadata fields: "Field: value" lines before the first "## " heading.
    header = []
    for line in lines:
        if line.startswith("## "):
            break
        header.append(line)
    fields = {}
    for line in header:
        m = re.match(r"^([A-Z][A-Za-z ]+):\s*(.*)$", line.strip())
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    for name in rule["fields"]:
        if not fields.get(name):
            errors.append(f'missing metadata line "{name}: ..." above the first section')
    status = fields.get("Status", "").lower().rstrip(".")
    if status and status not in rule["statuses"]:
        errors.append(f'Status must be one of {", ".join(rule["statuses"])} (found "{status}")')
    if fields.get("Date") and not DATE.match(fields["Date"]):
        errors.append("Date must be YYYY-MM-DD")
    for name in ("Intent", "Spec"):
        if name in rule["fields"] and fields.get(name):
            target = (path.parent / fields[name]).resolve()
            if not target.exists():
                errors.append(f'{name}: points to "{fields[name]}", which does not exist next to this file')

    # Sections present, in order, and not empty.
    headings = [(i, l[3:].strip()) for i, l in enumerate(lines) if l.startswith("## ")]
    names = [h for _, h in headings]
    for section in rule["sections"]:
        if section not in names:
            errors.append(f'missing section "## {section}"')
    present = [s for s in rule["sections"] if s in names]
    if present != [n for n in names if n in rule["sections"]]:
        errors.append("sections are out of order; keep the template order")
    for idx, (start, name) in enumerate(headings):
        end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        body = [l for l in lines[start + 1:end] if l.strip()]
        if name in rule["sections"] and not body:
            errors.append(f'section "## {name}" is empty (write "None." if there is nothing)')

    # Leftover template placeholders such as <title> or <name>.
    for n, line in enumerate(lines, 1):
        m = PLACEHOLDER.search(INLINE_CODE.sub("", line))
        if m:
            errors.append(f'leftover placeholder {m.group(0)} in: "{line.strip()[:70]}"')
            break
    return errors


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    failed = False
    for arg in argv[1:]:
        path = Path(arg)
        errors = check(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
