---
name: sdlc-plan
description: Turn an approved spec.md into plan.md, the implementation plan of the AI-native SDLC (Build stage), before any code is written. Use when the user says "plan this", "spec is approved", "how should we implement", or points at intent/<slug>/spec.md. Reads the codebase without changing it, names files, order of work, risks and proof, gets the engineer's acceptance, and keeps plan.md in sync during implementation.
license: MIT
metadata:
  stage: build
  version: "0.1.0"
---

# Write plan.md before writing code

You produce `intent/<slug>/plan.md`: which files change, in what order, what could break,
and what proves it works. Nothing is implemented until the engineer accepts the plan.

**Hard rule: until the engineer says the plan is accepted, the only file you may create or
edit is plan.md.** If your tool has a read-only planning mode (for example Claude Code plan
mode), use it for steps 1–4 and write plan.md once the user approves.

## Steps

1. **Read the inputs.** Read `intent/<slug>/intent.md` and `intent/<slug>/spec.md`, and the
   project instructions (`CLAUDE.md`, `AGENTS.md` or `.kiro/steering/*.md`). The spec's
   `Status:` must be `approved`. If it is `draft`, ask whether the product owner approved it.
   Continue only on a clear yes, and then set `Status: approved` in spec.md.
   With no spec at all, ask whether to plan from the intent alone and note that in the plan.

2. **Explore the code.** Find every file the change touches and the tests that cover them.
   Read; do not modify. Note the commands used to build and test.

3. **Draft the plan** using `assets/plan-template.md` from this skill's folder
   (`references/example-plan.md` shows the expected depth):
   - **Files that change:** every path, marked (new), (modified) or (deleted).
   - **Order of work:** small numbered steps; each ends in a state where the tests pass.
   - **Risks:** what this could break, and the riskiest step.
   - **Alternatives considered:** at least one approach you rejected, and why.
   - **Proof:** for each acceptance criterion in spec.md, the test, command or screenshot
     that proves it. Name exact test files and commands.
   - **Deviations from plan:** write "None yet."

4. **Interrogate it with the engineer.** Show the plan and answer these before asking for
   acceptance: What could this break? Which step is riskiest? What did you choose not to do?
   Revise until an engineer who never saw this conversation could implement it from the
   plan alone.

5. **Validate.** Run the checker from this skill's folder
   (`.claude/skills/sdlc-plan` or `.kiro/skills/sdlc-plan`):
   `python3 <skill-folder>/scripts/check_artifact.py intent/<slug>/plan.md`
   Fix every problem until it prints `OK`.

6. **STOP for acceptance.** Ask: "Do you accept this plan?" Routine changes are accepted
   by the engineer; high-risk ones (auth, money, PII, migrations, infrastructure) need a
   tech lead. On acceptance set `Status: accepted`, then commit plan.md (and spec.md if you
   changed its status) with message `plan: <title>`.

7. **Implement** only after acceptance, following the order of work.
   - After each step, run the project's tests (use `/sdlc-verify` if available).
   - **If you depart from the plan** (a different file, an extra step, a changed approach),
     update plan.md in the same commit: edit the affected section and add a line under
     "Deviations from plan" saying what changed and why.

## Before you finish planning, confirm

- [ ] No file other than plan.md (and status lines) was changed before acceptance.
- [ ] Every spec acceptance criterion has a matching line under Proof.
- [ ] At least one rejected alternative is recorded.
- [ ] The checker prints `OK`, and the engineer explicitly accepted.
