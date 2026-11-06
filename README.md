# AI-native SDLC skills

Portable [Agent Skills](https://agentskills.io) that run the core of Anthropic's
*AI-Native SDLC Playbook* in **Claude Code** and **Kiro**: every stage writes a markdown
artifact into the repository, and the next stage starts by reading it.

```
idea / ticket / incident
   └─ /sdlc-intent ──> intent/<slug>/intent.md   (product owner accepts via MR)
        └─ /sdlc-spec ──> intent/<slug>/spec.md  (product owner approves via MR)
             └─ /sdlc-plan ──> intent/<slug>/plan.md  (engineer accepts, then implements)
                  └─ /sdlc-verify  build + test + lint before anything is called done
```

No plugin and no tool-specific features: each skill is a plain folder with `SKILL.md`,
a template, a worked example and (for the artifacts) a small Python checker.

## Skills

| Skill | Stage | Produces |
|---|---|---|
| `sdlc-intent` | Plan | `intent/<slug>/intent.md` from an interview, ticket or incident |
| `sdlc-spec` | Design | `intent/<slug>/spec.md` with policies applied and areas of concern flagged |
| `sdlc-plan` | Build | `intent/<slug>/plan.md` (files, order, risks, proof) before any code |
| `sdlc-verify` | Test | Verified build/test/lint output; failing-test-first for bugs |

## Install into a project

```bash
./install.sh /path/to/project both     # or: claude | kiro
```

This copies the skills to `.claude/skills/` and/or `.kiro/skills/` in the project. Commit
them there so the whole team uses the same version. Re-run to update.

Without bash (e.g. Windows), copy each `skills/sdlc-*` folder into the project's
`.claude/skills/` or `.kiro/skills/` folder by hand.

Requirements: `git`, and `python3` for the artifact checker (standard library only).

## Use

Call a skill by name (`/sdlc-intent`, `/sdlc-spec`, …) or just describe the task. Both tools
pick skills by their description. Each skill stops at its human gate and tells you the next step.

Where the artifacts live: one folder per change, `intent/<slug>/`, holding `intent.md`,
`spec.md` and `plan.md`. The merge request that merges each file is the approval record.

### Tool notes

- **Claude Code:** use plan mode while `/sdlc-plan` explores, then let it write `plan.md`.
- **Kiro:** run these from a normal chat, not Kiro's built-in spec mode. Kiro's spec mode
  writes its own `requirements.md`/`design.md`/`tasks.md`, which would duplicate the
  artifacts here. Skills placed in a custom Kiro agent need `skill://` resources added.
- **Policies:** `sdlc-spec` applies any other skill whose description mentions security,
  compliance, API, UX or brand, plus `CLAUDE.md`, `AGENTS.md` and `.kiro/steering/*.md`.
  Add your organisation's policies as skills to get them applied.

## Develop

```bash
python3 tests/check_repo.py
```

This checks that the frontmatter is portable (only `name`, `description`, `license`,
`compatibility`, `metadata`; name equals folder), that the checker copies are identical,
and that the worked examples pass while the bare templates fail.

`check_artifact.py` is deliberately copied into each artifact skill so every folder works
on its own. Edit all three copies together; the test fails if they drift.

See [docs/PLAN.md](docs/PLAN.md) for the research and roadmap, and
[docs/gitlab-ci.md](docs/gitlab-ci.md) for where GitLab CI fits.
