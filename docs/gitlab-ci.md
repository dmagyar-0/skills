# Where GitLab CI plugs in

The skills cover what the agent does inside a session. Anything that must run on every
change, runs without a person, or must hold regardless of the agent belongs in GitLab
(CI jobs, protected branches, approval rules), **not** in a skill.

## Keep out of the skills

| Concern | Why not a skill | Put it in |
|---|---|---|
| Who may approve intent/spec/plan | A skill is advisory; approval must be enforced | Protected branches + **Merge request approval rules** / `CODEOWNERS` for `intent/**` (product owner) and code paths (code owners) |
| Artifact validation on every MR | Must run even if nobody used the skill | CI job running `check_artifact.py` (below) |
| Build, test and lint gate | Already the pipeline's job | Existing test stage; `sdlc-verify` only runs the same commands locally |
| Production deploy authorisation | Must be impossible to bypass | `environment: production` with **protected environments** / deployment approvals, `when: manual` |
| Secret scanning, SAST, dependency scanning | Deterministic tooling does it better | GitLab security templates |
| Running the agent headless (review, triage, evals) | Needs an API key, budget and a runner | Separate CI jobs (later phases) |
| Detecting production anomalies | The playbook says detection stays deterministic | Monitoring + scheduled pipeline (later phase) |

## Plug-in points, in adoption order

### 1. Validate artifacts on merge requests (start here)

Copy one checker into the project (e.g. `tools/check_artifact.py`, from any
`skills/sdlc-*/scripts/`) or reference the installed skill copy:

```yaml
sdlc:artifacts:
  stage: test
  image: python:3.12-slim
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes: ["intent/**/*.md"]
  variables:
    GIT_DEPTH: "0"   # the diff below needs the MR base commit
  script:
    - files=$(git diff --name-only --diff-filter=AM "$CI_MERGE_REQUEST_DIFF_BASE_SHA" HEAD -- 'intent/*/intent.md' 'intent/*/spec.md' 'intent/*/plan.md')
    - if [ -z "$files" ]; then echo "No artifacts changed"; exit 0; fi
    - python3 .claude/skills/sdlc-intent/scripts/check_artifact.py $files
```

Use `.kiro/skills/...` instead if the project only installs for Kiro.

### 2. Make the gates real

- `CODEOWNERS`: `/intent/ @product-owners` so a product owner must approve intent/spec MRs.
- Protected default branch, merge only via MR, at least one approval from code owners.
- Optional: an MR must change `intent/<slug>/plan.md` when it changes code tagged to that
  change (add later with a plan-sync check).

### 3. Keep the existing test pipeline as the source of truth

`sdlc-verify` runs the same `make test`-style commands as CI so failures are caught before
the MR. Keep those commands identical in the project instruction file and `.gitlab-ci.yml`.

### 4. Later: agent jobs (not part of the starter set)

- **MR review** on `merge_request_event` with a headless agent (`claude -p` or Kiro CLI) using a
  `REVIEW.md`; post findings as an MR note. Findings inform, approval rules decide.
- **Failed-pipeline triage** in a `when: on_failure` job: summarise the log into the MR.
- **Agent evals** when `CLAUDE.md`, `AGENTS.md`, `.kiro/**` or `.claude/**` change, and nightly.
- **Closing the loop**: a scheduled pipeline runs a deterministic band check and, on a breach,
  runs the agent read-only to draft an incident `intent.md` as an MR.

Each of these needs a masked CI variable for the model API key, a runner with network
access to the model endpoint, and no production credentials in the job.
