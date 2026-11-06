# AI-Native SDLC skills: research and build plan

Source: *The AI-Native SDLC Playbook* (Anthropic, Louis Claxton), 54 pages.
Goal: a set of Claude Code skills (plus the agents, hooks and templates they need)
that run the playbook's loop, and that work on **Sonnet 4.6** as well as newer models.

Research date: 2026-11-06. Star counts were read from the GitHub search API that day.

---

## 1. What the playbook actually asks for

Each stage ends by committing an artifact to git, and the next stage starts by reading it.

```
intent.md --accepted--> spec.md --approved--> plan.md --accepted--> diff+tests --> PR+findings --merged--> pipeline
    ^                                                                                                   |
    +--------------- breached control band / ticket / channel message writes a new intent.md <----------+
```

| Stage | Play | Artifact | Human gate | Kind of control |
|---|---|---|---|---|
| 1 Plan | Capture intent | `intent/<slug>/intent.md` | Product owner merges or closes it | Skill (template) |
| 2 Design | Requirements and design | `spec.md` next to the intent | Product owner signs off; flagged concerns go to policy owners | Skill plus **policy skills** |
| 3 Build | Plan mode | `plan.md` | Engineer (or tech lead if high risk) accepts | Skill plus plan mode |
| 3 Build | CLAUDE.md | `CLAUDE.md` | Code owners in PR | File (not a skill) |
| 3 Build | Skills as institutional knowledge | `.claude/skills/*` | Policy owner signs off changes | Skills |
| 3 Build | Hooks as guardrails | `.claude/settings.json`, `.claude/hooks/*` | none (deterministic) | Hooks |
| 3 Build | Parallel sessions and subagents | `.claude/agents/*.md` | n/a | Subagents, worktrees |
| 4 Test | Feedback loop | test output pasted in the session/PR | Code owner | CLAUDE.md block, skill, hook (test lock) |
| 4 Test | Continuous evals | `evals/*.json`, CI workflow | Config-change owner | CI plus skill to author evals |
| 5 Deploy | AI PR review | `REVIEW.md`, PR findings | Code owner via branch protection | Skill or action |
| 5 Deploy | Hooks as approval gates | `production-gate.sh`, managed settings | Release manager | Hooks |
| 5 Deploy | CI/CD | pipeline steps using `claude -p` | Branch protection | CI config plus prompts |
| 6 Maintain | Closing the loop | `bands.yaml`, detection script, new `intent.md` | Service owner triage | Deterministic script plus skill |
| 6 Maintain | Claude Tag on call | `lessons/*.md` | Channel | Product feature (likely unavailable) |

The playbook's own rule of thumb (p. 25): *write a skill for institutional knowledge
that must be applied consistently; don't write a skill for things that belong in
CLAUDE.md or a prompt.* And (p. 26): *a skill is advisory; a policy that must always
hold needs a hook or a review pass behind it.* So the deliverable is a **plugin**
(skills + agents + hooks + templates), not skills alone.

---

## 2. Existing work (research)

### 2a. Repos that implement this exact playbook (all low credibility so far)

| Repo | Stars | License | Notes |
|---|---:|---|---|
| bashebr/ai-native-sdlc | 94 | MIT | One big `ai-native-sdlc` skill (151 lines) + ~500 lines of references, 13 Python scripts, every template (intent/spec/plan/REVIEW/bands/production-gate/managed-settings). Adds an "agent org" (CEO/CTO roles) that is **not** in the playbook. Good reference material; too monolithic to adopt. |
| TsCarpe/claude-sdlc-skills | 66 | MIT | Requirement intake, adversarial gate, test, release check. Java/Chinese-enterprise specific; ships evals per skill (nice pattern). |
| ghiaog123/ai-native-sdlc | 11 | ? | Plugin, six stages, one artifact each. |
| OBaruch/ai-native-sdlc-template | 4 | ? | Repo template. |
| bibutikoley/ai-sdlc-claude | 3 | ? | 14 slash commands + hooks. |
| JHashimoto0518/ai-native-sdlc-playbook-sample | 1 | ? | Worked example carried through the stages. |

Verdict: nothing here has enough adoption to trust as-is. Read bashebr's templates for
ideas (MIT, attribute if you copy).

### 2b. High-credibility building blocks (adopt or borrow)

| Repo | Stars | License | Covers which play |
|---|---:|---|---|
| obra/superpowers | 313k | MIT | brainstorming (≈ intent capture), writing-plans / executing-plans (plan mode), test-driven-development + verification-before-completion (feedback loop), requesting/receiving-code-review, using-git-worktrees + dispatching-parallel-agents, systematic-debugging, writing-skills. Strong discipline, but its own artifact names/paths and a "must invoke skills before anything" bootstrap skill. |
| anthropics/skills | 188k | Apache-2.0 (skill-creator) | `skill-creator`: authoring + eval harness for our own skills. |
| github/spec-kit | 148k | MIT | /constitution, /specify, /clarify, /plan, /tasks, /analyze, /implement. Closest to intent→spec→plan; needs its CLI and uses its own file layout. |
| Fission-AI/OpenSpec | 74k | MIT | Spec-driven change proposals. Same family as spec-kit. |
| bmad-code-org/BMAD-METHOD | 55k | custom | Full agile persona method. Much heavier than the playbook. |
| anthropics/claude-plugins-official | 46k | Apache-2.0 | `code-review`, `pr-review-toolkit` (review play), `hookify` (hooks play), `claude-md-management` (CLAUDE.md play), `code-simplifier` (subagent), `feature-dev`, `commit-commands`, `skill-creator`. |
| wshobson/agents | 42k | MIT | Large catalogue of subagents/commands; pick-and-choose. |
| anthropics/claude-code-action | 9.8k | MIT | @claude in PRs, CI review, `claude -p` in pipelines (Deploy, CI/CD, evals). |
| automazeio/ccpm | 8.4k | MIT | GitHub Issues + worktrees for parallel agents. |

Directories: ComposioHQ/awesome-claude-skills (79k), hesreallyhim/awesome-claude-code (57k).

### 2c. Conclusion

* No credible package implements **this** playbook's artifact chain end to end.
* The individual plays are well covered by trusted sources (superpowers, official
  plugins, spec-kit, claude-code-action).
* Recommended path: **build a thin, playbook-shaped plugin of our own** that owns the
  artifact chain and the gates, and lean on official plugins / superpowers ideas for
  generic engineering discipline. Vendoring (copying with attribution) is safer than
  installing from public marketplaces if work restricts `strictKnownMarketplaces`.

---

## 3. Proposed skill set

Naming: `sdlc-*` so they group together and are easy to call as `/sdlc-...`.

### Skills (advisory, what Claude should do)

| # | Skill | Stage / play | Trigger | Reads → writes | Reuse |
|---|---|---|---|---|---|
| 0 | `sdlc-workflow` | All (router) | "where are we", "next step", any mention of intent/spec/plan | detects which artifacts exist → tells you the next skill and the gate | new |
| 1 | `sdlc-intent` | 1 Plan | new idea, ticket, "write an intent" | conversation / ticket / incident evidence → `intent/<slug>/intent.md` | superpowers brainstorming (question style) |
| 2 | `sdlc-spec` | 2 Design | accepted intent | intent.md + org policy skills → `spec.md` with **Areas of concern** and **Policy skills applied (versions)** | spec-kit /specify + /clarify ideas |
| 3 | `sdlc-plan` | 3 Build (plan mode) | approved spec, "plan this" | intent+spec+codebase → `plan.md` (files, order, risks, alternatives rejected, proof, parallelisable tasks) | superpowers writing-plans |
| 4 | `sdlc-verify` | 4 Test (feedback loop) | before saying "done", bug fix | runs CLAUDE.md verify commands, failing-test-first for bugs, never edit tests during a fix | superpowers TDD + verification-before-completion |
| 5 | `sdlc-review` | 5 Deploy (PR review) | "review this PR/diff" | diff + REVIEW.md + spec.md + plan.md → findings ranked Important/Nit, plan-vs-diff drift, CLAUDE.md feedback | official code-review / pr-review-toolkit |
| 6 | `sdlc-address-review` | 5 Deploy (babysit) | "address review comments", "get PR green" | unresolved comments + failing checks → fixes until only code-owner approval is left | superpowers receiving-code-review |
| 7 | `sdlc-evals` | 4 Test (continuous evals) | "add an eval", after incident fix | real task or incident → `evals/<id>.json` + check | new (skill-creator eval format as reference) |
| 8 | `sdlc-diagnose` | 6 Maintain | band breach, alert, incident | evidence (read-only) → diagnosis → new `intent.md` (incident variant) + `lessons/*.md` + suggested eval | systematic-debugging ideas |
| 9 | `sdlc-bootstrap` | setup (one-time) | "set up the SDLC in this repo" | repo → `intent/`, templates, CLAUDE.md sections, REVIEW.md, hooks, agents, CI examples | new |
| P | `policy-*` (template + 1 example) | 2 Design / 3 Build | domain specific | policy source of truth → skill | playbook's `secure-api-review` example |

Policy skills (security, API conventions, brand/UX, compliance) are **your organisation's
content**. We ship a template and one worked example; policy owners fill the rest.

### Not skills (shipped in the same plugin)

* **Templates** (`templates/`): intent.md, intent (incident variant), spec.md, plan.md,
  CLAUDE.md skeleton with "Verifying your work" and "Things Claude gets wrong", REVIEW.md,
  bands.yaml, eval case JSON.
* **Subagents** (`agents/`): `verifier` (runs app, checks against plan.md, report only),
  `researcher` (explores codebase, returns summary). Code simplifier: reuse official plugin.
* **Hooks** (`hooks/`, wired via settings): protected paths; format/lint after edit;
  secret scan on edit; **test-file lock** during fix tasks; **plan-sync** check at commit;
  **production gate**. Each prints *why* it blocked and how to get approval.
* **CI examples** (`ci/`): agent-evals workflow, PR review with claude-code-action,
  failed-build triage step, scheduled band detection.
* **Deterministic scripts** (`scripts/`, stdlib Python): `validate_artifact.py`
  (required headings present, status field, links to parent artifact),
  `check_plan_sync.py`, `detect_bands.py`.

---

## 4. Designing for Sonnet 4.6

Skills are model-agnostic, but these choices keep them reliable on a smaller model:

1. **Short SKILL.md** (target ≤ 120 lines). Detail lives in `references/` and is read only
   when a step says so (progressive disclosure keeps context small).
2. **Numbered imperative steps** with explicit inputs, outputs and file paths. No "use
   your judgement to decide the structure": copy the template from `templates/`.
3. **Explicit STOP lines at every gate**: "Stop. Ask the product owner to accept. Do not
   write spec.md in this session until they say so."
4. **A closing checklist** in each skill ("before you finish, confirm: …").
5. **Push correctness into scripts and hooks.** `validate_artifact.py` checks the
   artifact instead of the model self-grading; hooks enforce what must always hold.
6. **Trigger-friendly descriptions** naming file names and verbs ("intent.md", "spec",
   "plan", "review this PR"), and every skill is also callable as `/sdlc-…`, so you never
   depend on auto-triggering.
7. **Single-session path first.** Subagents / parallel worktrees are optional
   accelerators, never required for a skill to work.
8. **No dependency on preview products** (Claude Design, Claude Tag, managed Code Review,
   auto mode, Cowork). Where the playbook uses them, the skill states the fallback.
9. **No model pinned in skills.** CI examples take the model from a variable so evals can
   run on Sonnet 4.6 and newer models side by side.
10. **Eval every skill on Sonnet 4.6** (3–5 prompts each, with skill-creator) before
    calling it done.

---

## 5. Build order (follows the playbook dependency graph, entry points first)

| Phase | Deliver | Why first | Done when |
|---|---|---|---|
| 0 | Repo layout as a plugin + marketplace manifest; templates; `validate_artifact.py`; README | Everything else references templates | `/plugin marketplace add` installs it; templates validate |
| 1 | `sdlc-intent`, `sdlc-bootstrap` (CLAUDE.md + intent home), `sdlc-verify`, build hooks | All are entry points (no prerequisites) | Sonnet 4.6 produces a valid intent.md from 3 different idea prompts |
| 2 | `sdlc-spec` + policy template + one example policy, `sdlc-plan`, `verifier` agent | Depend on intent / CLAUDE.md | Worked example (claims status) goes intent → spec → plan with concerns flagged |
| 3 | `sdlc-review` + REVIEW.md, `sdlc-address-review`, production gate + plan-sync hooks | Depend on CLAUDE.md, spec, plan | Review flags a deliberate plan-vs-diff drift and a seeded security issue |
| 4 | `sdlc-evals` + CI workflow, `sdlc-diagnose` + bands.yaml + `detect_bands.py` | Depend on everything above | Synthetic breach produces an incident intent.md that `sdlc-spec` accepts |
| 5 | `sdlc-workflow` router, docs, eval suite for the skills themselves | Needs the others to exist | Router correctly names the next step for each artifact state |

For each skill: draft from the playbook page → write 3–5 trigger/behaviour evals →
run on Sonnet 4.6 → tighten wording → commit.

---

## 6. Decisions (2026-11-06)

1. **No plugin.** Must work in Claude Code *and* Kiro. Both support the open Agent Skills
   format (`SKILL.md` with `name` + `description`; `scripts/`, `references/`, `assets/`;
   auto-selection by description or `/name`). Skills live in this repo under `skills/`
   and `install.sh` copies them to `.claude/skills/` and/or `.kiro/skills/` of a project.
   Frontmatter is limited to the portable keys: name, description, license, compatibility,
   metadata. No Claude-only keys, hooks or subagents in the starter set.
2. **Intents live in the product repos**, one folder per change: `intent/<slug>/` with
   `intent.md`, `spec.md`, `plan.md`. The merge request is the approval record.
3. **GitLab CI** is guidance only: see `docs/gitlab-ci.md` for what stays out of skills
   and where CI, CODEOWNERS, approval rules and protected environments plug in.
4. **Start small.** Phase 1 = `sdlc-intent`, `sdlc-spec`, `sdlc-plan`, `sdlc-verify` plus
   a stdlib artifact checker. Everything else in section 3 is backlog.

## 7. Status

Done (phase 1): the four skills above, templates, worked examples (claims status),
`check_artifact.py`, `install.sh`, `tests/check_repo.py`, GitLab guidance.

Not yet done: trying the skills on a real repo with Sonnet 4.6 in Claude Code and in Kiro
(trigger reliability + output quality), then `sdlc-review` + `REVIEW.md` as the next step.
