---
name: sdlc-verify
description: Verify your own work before saying a task is done, the feedback loop of the AI-native SDLC (Test stage). Use before reporting any implementation, bug fix or refactor as complete, before committing or opening a merge request, and whenever the user says "verify", "run the checks", "fix this bug" or "is it done". Runs the project's build, test and lint commands, writes a failing test first for bugs, never weakens tests, and pastes the real output.
license: MIT
metadata:
  stage: test
  version: "0.1.0"
---

# Verify before you say "done"

A task is done only when the project's own checks pass and you have shown their output.

## 1. Find the commands

Look, in this order, for a section named "Verifying your work" (or Commands / Testing) in
`CLAUDE.md`, `AGENTS.md`, `.kiro/steering/*.md`, then `README.md`, `Makefile`,
`package.json` scripts, or `.gitlab-ci.yml` test jobs.

If no single build, test and lint command is documented, tell the user and offer to add
the block from `assets/verification-block.md` (in this skill's folder) to their project
instruction file. Do not guess silently: say which commands you are using and where you
found them.

## 2. For a bug fix: failing test first

1. Write a test that reproduces the bug.
2. Run it and confirm it **fails for the expected reason**. Show the failure.
3. Commit that test on its own (message `test: reproduce <bug>`) if the user wants commits.
4. Fix the code. **Do not edit that test while fixing.** If you believe the test is wrong,
   stop and ask.

## 3. Run the loop

1. Run build, then tests, then lint, using the documented commands.
2. If anything fails, read the error, fix the **code**, and run again.
3. Repeat until everything passes. After three failed attempts on the same error, stop
   and report what you tried instead of continuing.
4. For UI work, if you have a browser or screenshot tool, compare the result with the
   mock or the spec and iterate. If you don't have one, say the visual check was not done.

## Never

- Skip, delete, comment out or loosen a test, or add a skip marker, to get a green run.
- Change test expectations to match new behaviour unless the spec or plan says the
  behaviour changes. If so, say so explicitly.
- Report "tests pass" without having run them in this session.
- Summarise output instead of showing it.

## 4. Report

End with a short report:

```
Verification
- Build: <command> -> <result>
- Test:  <command> -> <N passed, M failed>
- Lint:  <command> -> <result>
- Not checked: <anything you could not run, and why>
```

Paste the last lines of each command's real output under the report. If the change came
from a plan.md, also say whether each item under its "Proof" section is now satisfied.
