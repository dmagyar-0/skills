---
name: sdlc-intent
description: Capture a new idea, feature request, ticket or problem as intent.md, the first artifact of the AI-native SDLC (Plan stage). Use when someone describes something they want built or changed, says "write an intent", "capture this idea", "new feature", or pastes a ticket to turn into an intent. Interviews the originator, writes intent/<slug>/intent.md from the template, validates it, and stops for product owner acceptance.
license: MIT
metadata:
  stage: plan
  version: "0.1.0"
---

# Capture intent as intent.md

You turn an idea into `intent/<slug>/intent.md`: what is wanted, why, and under which
constraints, in the originator's own words. You do **not** design or plan the solution here.

## Steps

1. **Listen first.** Ask the originator to describe the problem in their own words if
   they have not already. Do not propose solutions.

2. **Interview until it is concrete.** Ask the questions an analyst would ask, two or
   three at a time, and wait for answers. Cover every item below before writing:
   - What can't be done today, and what does it cost (time, money, complaints)?
   - Who is affected? Which teams and which systems?
   - What does better look like? How would we measure it?
   - Constraints: security, data/PII, compliance, deadlines, technology.
   - What is explicitly out of scope?
   - Where did it come from: an idea, a ticket (get the ID), or an incident (get the ID)?
   If the originator does not know an answer, record it under Open questions. Do not invent one.

3. **Pick the slug and folder.** Slug = 2–5 lowercase words joined by hyphens
   (e.g. `claims-status-self-service`). Path: `intent/<slug>/intent.md` at the repository
   root. If that folder already exists, ask whether to update it or choose another slug.

4. **Write the file.** Copy `assets/intent-template.md` from this skill's folder and fill
   every section. Keep the originator's wording where possible. Set `Status: draft` and
   `Date:` to today (YYYY-MM-DD). For a reference of the expected depth, read
   `references/example-intent.md`.
   - Write "None." in a section that truly has nothing; never delete a section.
   - No solution design: no file names, endpoints or table names unless the originator
     stated them as a constraint.

5. **Validate.** Run the checker from this skill's folder (it is `.claude/skills/sdlc-intent`
   or `.kiro/skills/sdlc-intent`):
   `python3 <skill-folder>/scripts/check_artifact.py intent/<slug>/intent.md`
   Fix every reported problem and run it again until it prints `OK`.

6. **Read it back.** Show the originator the finished intent and ask: "Is anything
   misunderstood or missing?" Apply their corrections and validate again.

7. **Commit** (only when the originator is happy and the user wants you to commit):
   - Create a branch `intent/<slug>` if you are on the default branch.
   - `git add intent/<slug>/intent.md`
   - Commit message: `intent: <title>`.
   - Do not push or open a merge request unless asked.

8. **STOP.** Tell the user:
   - the path of the file;
   - that the product owner accepts it by setting `Status: accepted` in a merge request
     and merging it (or rejects by setting `Status: rejected` / closing the MR);
   - that the next step after acceptance is `/sdlc-spec`.
   Do not start the spec in this session unless the user says the intent is accepted.

## Incident or ticket source

When the input is an alert, incident or ticket instead of a person, do the same steps but
take answers from the evidence: put the evidence (metric, time window, error, ticket text)
under Problem, set `Source: incident <ID>` or `Source: ticket <ID>`, and list everything
you could not confirm under Open questions.

## Before you finish, confirm

- [ ] All seven sections are filled (or say "None.").
- [ ] `Status: draft`, today's date, author and source are set.
- [ ] The checker prints `OK`.
- [ ] The originator has read it back and agreed.
- [ ] You stopped and told the user how acceptance works.
