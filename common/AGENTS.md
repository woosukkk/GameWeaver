# AGENTS.md

## Scope

These instructions apply to the entire repository unless a closer `AGENTS.md` provides more specific rules.

## Working principles

- Preserve existing user changes and avoid unrelated edits.
- Make the smallest change that fully solves the request.
- Reuse existing code and tools before adding abstractions or dependencies.
- Fix the root cause after checking relevant callers and neighboring code.
- Keep generated output, secrets, and machine-specific files out of version control.

## Command execution

- Treat a change, build, or fix request as authorization for every safe, reversible, in-scope subtask needed to complete it.
- Execute read-only inspection, project-local edits and setup, declared dependency installation, tests, linters, formatters, type checks, builds, and ordinary temporary or generated artifacts without asking the user "Should I proceed?" or requesting confirmation in chat.
- If the platform technically requires approval for an otherwise authorized action, submit the narrow platform approval directly. Group related operations and request a reusable, narrowly scoped command rule when supported instead of interrupting the user repeatedly.
- Ask before system-wide installation, undeclared external-service access, credential use not already authorized for the task, destructive or irreversible actions, purchases, deployment, release, or material expansion of scope.
- Read project-specific entry points and exact commands from `README.md`. If a value is still `TODO`, inspect project configuration rather than guessing; report only what remains unverifiable.

## Git workflow

- Inspect Git status before editing and preserve unrelated work.
- Follow `CONTRIBUTING.md` as the source of truth for branch, commit, issue, and pull request conventions.
- Before starting a feature or bug fix, search open issues for the same work. Reuse a matching issue; if none exists, create one from the appropriate template. Keep one issue per feature or bug, not one issue per push or commit.
- Include the issue number in the branch name, such as `feature/123-user-login` or `hotfix/123-login-error`.
- Never commit directly to `main` or `develop`.
- Create `feature/<issue-number>-<short-name>` from `develop` for normal work and `hotfix/<issue-number>-<short-name>` from `main` for urgent release fixes, without asking for confirmation.
- After completing and validating a requested change, create a focused commit containing only the task-related files.
- Choose the commit message without asking. Use `<type>: <subject>` with the appropriate type defined in `CONTRIBUTING.md` and an accurate summary of the completed task.
- Add `Refs #<issue-number>` to the commit body and feature-to-`develop` pull request. Use `Closes #<issue-number>` only in a pull request targeting `main` so the issue closes with the stable release.
- Put the implementation summary and validation results in the pull request. Do not duplicate GitHub's commit history with an issue comment for every push; comment only for a meaningful decision, blocker, or status change.
- Do not push commits or branches to a remote until the user explicitly authorizes a push for the current task.
- Push authorization is task-scoped. Once granted, it also authorizes the normal publishing steps for that task: push the relevant branch, create or update its pull request, link the tracked issue, set PR metadata, and inspect resulting checks without asking again.
- Push authorization does not authorize merging a pull request, force-pushing, deploying, publishing a release, deleting remote data, or closing unrelated issues. Obtain explicit authorization for those actions.
- Do not amend existing commits, force-push, rebase shared history, or otherwise rewrite history unless explicitly requested.

## Collaboration

- Make safe, reversible, in-scope decisions without interrupting the user for confirmation.
- Ask only when a missing decision would materially change the result, require new authority, or risk irreversible impact.
- For longer work, provide concise progress updates with assumptions, findings, and blockers.
- Lead the final response with the outcome, then summarize verification and any remaining limitations.
- Treat corrections and new constraints from the user as authoritative for the current task.

## Conventions

<!-- Add only rules that cannot be inferred from code, formatter, linter, or tests. -->

- Follow established patterns in the nearest relevant code.
- Keep public behavior backward-compatible unless the request requires a breaking change.
- Add comments only when they explain a non-obvious decision or constraint.

## Preferred tools

- Use the approved catalog under `tools/` when it is included in the project.
- Apply Ponytail principles to coding tasks.
- Use Code Review Graph when repository-scale review or impact analysis justifies its setup cost.
- Prefer PDF Inspector when the project needs local PDF classification or text extraction.
- For frontend design, use Anthropic Frontend Design for initial direction and Taste Skill for refinement.
- Do not install a conditional tool until the current project has its stated need.

## Validation

- Start with the smallest relevant check, then run the broader affected suite when practical.
- Add or update a focused test when behavior changes or a bug is fixed.
- Run the configured formatter or linter instead of restating its rules here.
- Report what was verified and any checks that could not be run.

## Safety

- Never commit credentials, tokens, private keys, or populated `.env` files.
- Do not delete data, deploy, or change external services unless explicitly requested.
- Treat migrations, authentication, authorization, payments, and destructive operations as high-risk changes requiring targeted verification.
