# AGENTS.md

## Scope

These instructions apply to the entire repository unless a closer `AGENTS.md` provides more specific rules.

## Working principles

- Preserve existing user changes and avoid unrelated edits.
- Make the smallest change that fully solves the request.
- Reuse existing code and tools before adding abstractions or dependencies.
- Fix the root cause after checking relevant callers and neighboring code.
- Keep generated output, secrets, and machine-specific files out of version control.

## Project index

<!-- Replace every TODO when starting a project. List only useful entry points. -->

- Purpose: TODO
- Main application: `TODO`
- Tests: `TODO`
- Configuration: `TODO`
- Documentation: `TODO`

## Commands

<!-- Use exact commands that work from the repository root. Remove unused rows. -->

- Install: `TODO`
- Run: `TODO`
- Test: `TODO`
- Lint/format: `TODO`
- Build: `TODO`

Do not guess a missing command. Inspect the repository configuration first; if it remains unknown, report that verification could not be run.

## Command execution

- Treat a change, build, or fix request as authorization for all safe, reversible, project-local subtasks and checks needed to complete it; do not request separate confirmation for each step.
- Run read-only inspection and project-local setup, tests, linters, formatters, type checks, and builds without asking for confirmation.
- Create ordinary project-local caches, temporary files, build output, and test artifacts required by those checks without asking.
- Install dependencies already declared by the project when required to run its checks, provided this does not require system-wide changes.
- Do not pause for confirmation merely because a safe check needs additional tool permissions; use the platform approval flow only when the environment technically requires it.
- Ask before system-wide installation, accessing undeclared external services, using credentials, or operating outside the project workspace.

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
- Do not push commits or branches to any remote unless the user explicitly requests it.
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

## Further documentation

<!-- Link detailed documents; do not duplicate them here. Remove this section if unused. -->

- Architecture: `TODO`
- Development guide: `TODO`
- Deployment/operations: `TODO`
