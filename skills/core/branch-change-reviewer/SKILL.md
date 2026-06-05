---
name: branch-change-reviewer
description: Review the current branch against a target Git branch, defaulting to origin/main, and write review findings to a Markdown output file under `$ARTIFACTS/<meaningful_id>/` (default basename `review_<sanitized-branch>.md`; legacy root-level review files remain valid). Use when Codex is asked to review a branch diff without writing code, especially to assess code style, architecture, testing, regressions, and whether changes are worth raising as comments.
---

# Branch Change Reviewer

Review changes against a target branch. Default to `origin/main`. Do not write code. Write the review to both the screen and a Markdown file. Focus on code style, architecture, testing, and possible regressions.

## When to Use

Use this skill when the user wants:

- a branch diff reviewed without changing code
- review comments focused on regressions, architecture, testing, or maintainability
- a written review artifact for the current branch against a target branch

## When Not to Use

Do not use this skill when:

- the user wants code changes, fixes, or implementation work
- the task is primarily MR transport access or comment grouping
- the task is repository investigation rather than branch-diff review

## Inputs

- Accept an optional target branch.
- If the user provides a target branch, use it.
- If the user does not provide one, use `origin/main`.
- Accept an optional output file path (absolute or relative).
- Accept an optional local workflow artifact such as `$ARTIFACTS/…/task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md` as additional review context.
- If the user provides an output file, use it.
- If the user does not provide one, write under `$ARTIFACTS/<meaningful_id>/` per repository `ARTIFACTS.md`:
  - default basename: `review_<sanitized-branch>.md` from the current branch name (e.g. `feature/foo-bar` → `$ARTIFACTS/feature-foo-bar/review_feature-foo-bar.md`)
  - default `meaningful_id`: tracker key from a provided task artifact when present; else the same sanitized branch slug
- **Legacy:** an existing root-level `review_<branch>.md` (or other user path) already present remains valid—open and extend it instead of relocating unless the user asks to migrate.

## Inspect the repository first

- Run `git status --short --branch`.
- Determine the current branch name and resolve the default output path under `$ARTIFACTS/<meaningful_id>/` (or an existing legacy review file when already present).
- Refresh the target branch with `git fetch` before reviewing.
- Keep any existing user changes intact.
- Do not modify code, tests, or configuration as part of this skill.

## Gather the review scope

- Compare the current branch against the target branch with the narrowest useful diff.
- Review committed changes first.
- If uncommitted changes are present and appear relevant to the user's request, include them explicitly in the review scope.
- Read the changed files and any adjacent files needed to understand architecture, call sites, and test coverage.
- Read repo guidance such as `AGENTS.md`, `README`, `Makefile`, `pyproject.toml`, `package.json`, CI config, or test configuration when they affect the review standard.
- If a local workflow artifact is provided, read it first and reuse its scope, links, assumptions, and open questions as review context, while keeping the branch diff as the source of truth.
- if prior review artifacts for the same branch or area exist (under `$ARTIFACTS/…/` or legacy root-level paths), preserve durable learned sections such as `Recurring Findings`, `Missed In Prior Review`, or `Repo-Specific Review Heuristics` when they still match the current diff and surrounding code.

## Review standards

Focus on comments worth raising. Do not pad the review with praise or trivial observations.

- Prioritize bugs, possible regressions, architectural drift, weak abstractions, missing or incorrect tests, and code style issues that reduce maintainability.
- Check whether changed logic could break existing callers, data flows, contracts, edge cases, or previously covered behavior even when the diff looks locally correct.
- Treat testing gaps as findings when behavior changed without adequate coverage.
- Call out architecture issues when the change conflicts with existing patterns, duplicates logic, weakens boundaries, or increases coupling.
- Call out code style issues when they materially affect readability, consistency, or future maintenance.
- Prefer concrete, actionable comments tied to specific files and lines when possible.
- When a risk was missed in a prior review and is now visible in the diff or surrounding code, record it once in `Missed In Prior Review` with the signal that should have been checked earlier.
- If no meaningful findings exist, say so clearly.

## Validation

- Review committed changes first, expanding to uncommitted changes only when relevant to the request.
- Keep findings grounded in the live diff and surrounding code.
- Prefer concrete file and line references when available.
- Keep the report concise and ordered by severity.

## Output format

Write the same review content to both the screen and the output file.

- Start with `Findings`.
- List findings ordered by severity.
- For each finding, include:
  - severity
  - file and line reference when available
  - concise explanation of the issue
  - why it matters
  - what should change or what should be verified
- After findings, include `Open Questions` only if they materially affect the review.
- Include optional learned sections such as `Recurring Findings`, `Missed In Prior Review`, or `Repo-Specific Review Heuristics` when they are evidence-backed and useful for future reviews of the same area.
- End with a short `Summary` stating:
  - which branch was reviewed against which target branch
  - whether the target branch was user-provided or defaulted
  - which output file was written
  - whether there were any findings

## Writing rules

- Do not write code.
- Do not apply fixes.
- Do not rewrite the user's files.
- Do not invent issues without evidence from the diff and surrounding code.
- Do not let minor style points drown out architectural or testing risks.
- Keep the report concise, technical, and reviewer-oriented.

## File writing rules

- Always create or overwrite the requested output file with the full review text.
- Use Markdown.
- If there are no findings, still create the file and state that no review comments were warranted.

## Outputs / Artifacts

This skill should produce:

- an on-screen review summary
- a Markdown review file such as `$ARTIFACTS/<meaningful_id>/review_<sanitized-branch>.md` for new runs (legacy root-level `review_<branch>.md` paths remain valid when already in use)

The review should include:

- findings ordered by severity
- open questions when materially relevant
- short summary of review scope and result

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for context and prior reviewer concerns
- reuse its links, assumptions, and open questions to focus the review
- keep the actual branch diff and surrounding code as the source of truth for findings
- if you update the same artifact, preserve the shared core sections from `../ARTIFACTS.md`

This is additive only and does not replace the normal diff-based review workflow.

## Companion Skills

Common pairings:

- local workflow artifacts such as `$ARTIFACTS/…/task_<issue>.md` or `review_mr_<MR>.md` for extra review context
- repository-specific contributor or analysis skills only after the review is complete and the user asks for follow-on changes

## Self-Improving Behavior

When rerunning review for the same branch, MR, or code area:

- read any existing review artifact first (under `$ARTIFACTS/…/` by preference, or a legacy root-level file when that is where prior work lives)
- preserve durable learned sections such as `## Recurring Findings`, `## Missed In Prior Review`, and `## Repo-Specific Review Heuristics` when they still match the current diff and surrounding code
- refresh findings from the live diff and current code before concluding
- promote repeated confirmed review themes into short heuristics, preferably phrased like `when code changes X, verify Y`
- demote, mark stale, or remove heuristics contradicted by new code or evidence

This makes the review artifact more useful across reruns without replacing the normal evidence-based review flow.

## Safety Notes

- Do not write code or apply fixes as part of this skill.
- Keep existing user changes intact.
- Do not invent issues without evidence from the diff and surrounding code.
