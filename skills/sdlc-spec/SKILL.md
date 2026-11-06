---
name: sdlc-spec
description: Turn an accepted intent.md into spec.md, the requirements and design spec of the AI-native SDLC (Design stage). Use when the user says "write the spec", "design this intent", "intent is accepted", or points at an intent/<slug>/intent.md. Applies the team's policy skills and steering (security, compliance, API, UX, brand), flags areas of concern, validates, and stops for product owner approval.
license: MIT
metadata:
  stage: design
  version: "0.1.0"
---

# Write spec.md from an accepted intent

You produce `intent/<slug>/spec.md` next to the intent: what will be built and how, in
enough detail that an engineer can plan against it. The product owner reviews it; you
write it. You do **not** write code or an implementation plan here.

## Steps

1. **Find the intent.** Use the path the user gave, or list `intent/*/intent.md` and ask
   which one. Read it fully.

2. **Check the gate.** The intent's `Status:` must be `accepted`.
   - If it says `draft`: ask "Has the product owner accepted this intent?" Continue only
     on a clear yes, and then change its status line to `Status: accepted`.
   - If it says `rejected`: stop and say so.

3. **Load the policies.** Find every policy that applies and read it before designing:
   - other skills in `.claude/skills/` or `.kiro/skills/` whose description mentions
     security, compliance, privacy, API, UX, brand, accessibility or architecture;
   - the project instructions: `CLAUDE.md`, `AGENTS.md` and `.kiro/steering/*.md` if present.
   For each policy skill, record its name and version. Version = the `metadata.version`
   in its frontmatter, otherwise the output of
   `git log -1 --format=%h -- <skill-folder>`, otherwise "uncommitted".

4. **Read the code that the intent touches.** Look at the systems named under
   "Affected users and systems" so the design fits the existing codebase. Read only;
   change nothing.

5. **Write the spec.** Copy `assets/spec-template.md` from this skill's folder to
   `intent/<slug>/spec.md` and fill every section. `references/example-spec.md` shows the
   expected depth. Rules:
   - Number requirements (R1, R2 …, NFR1 …). Each must be testable.
   - Every acceptance criterion names something that can be checked (a test, a response,
     a screenshot, a metric).
   - Carry every open question from the intent forward: answer it or keep it open.
   - **Areas of concern:** add a row whenever you cannot satisfy a policy, two policies
     conflict, the intent is ambiguous, or the risk is high (PII, money, auth, data loss,
     migrations). Name the policy and who should decide. Do not resolve conflicts silently.
   - Keep the design at component and interface level. File-by-file detail belongs in plan.md.

6. **Validate.** Run the checker from this skill's folder
   (`.claude/skills/sdlc-spec` or `.kiro/skills/sdlc-spec`):
   `python3 <skill-folder>/scripts/check_artifact.py intent/<slug>/spec.md`
   Fix every problem and repeat until it prints `OK`.

7. **Summarise for the product owner** in chat: the requirements in one line each, then
   the areas of concern, highest severity first. Ask them to resolve each concern with
   its policy owner.

8. **Commit** (when the user wants it): `git add intent/<slug>/spec.md intent/<slug>/intent.md`,
   message `spec: <title>`. Do not push or open a merge request unless asked.

9. **STOP.** Tell the user the product owner approves by setting `Status: approved` and
   merging (consulting a tech lead for high-risk changes), and that the next step is
   `/sdlc-plan`. Do not start planning in this session unless the user says it is approved.

## Before you finish, confirm

- [ ] The intent was accepted before you started.
- [ ] Every applicable policy is listed under "Policies applied" with a version.
- [ ] Every intent open question is answered or carried forward.
- [ ] Concerns are listed, not silently resolved.
- [ ] The checker prints `OK`, and you stopped for approval.
