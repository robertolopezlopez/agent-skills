---
name: branch-change-reviewer
description: Review the current branch against a target Git branch, defaulting to origin/main, and write review findings to a Markdown output file whose default name is based on the current branch, such as review_feature-branch.md. Use when Codex is asked to review a branch diff without writing code, especially to assess code style, architecture, testing, regressions, and whether changes are worth raising as comments.
---

# Branch Change Reviewer

Review changes against a target branch. Default to `origin/main`. Do not write code. Write the review to both the screen and a Markdown file. Focus on code style, architecture, testing, and possible regressions.

## Inputs

- Accept an optional target branch.
- If the user provides a target branch, use it.
- If the user does not provide one, use `origin/main`.
- Accept an optional output file name.
- Accept an optional local workflow artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md` as additional review context.
- If the user provides an output file, use it.
- If the user does not provide one, use a name like `review_feature-branch.md` based on the current branch name.

## Inspect the repository first

- Run `git status --short --branch`.
- Determine the current branch name for the default output filename.
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

## Review standards

Focus on comments worth raising. Do not pad the review with praise or trivial observations.

- Prioritize bugs, possible regressions, architectural drift, weak abstractions, missing or incorrect tests, and code style issues that reduce maintainability.
- Check whether changed logic could break existing callers, data flows, contracts, edge cases, or previously covered behavior even when the diff looks locally correct.
- Treat testing gaps as findings when behavior changed without adequate coverage.
- Call out architecture issues when the change conflicts with existing patterns, duplicates logic, weakens boundaries, or increases coupling.
- Call out code style issues when they materially affect readability, consistency, or future maintenance.
- Prefer concrete, actionable comments tied to specific files and lines when possible.
- If no meaningful findings exist, say so clearly.

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

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for context and prior reviewer concerns
- reuse its links, assumptions, and open questions to focus the review
- keep the actual branch diff and surrounding code as the source of truth for findings
- if you update the same artifact, preserve the shared core sections from `../ARTIFACTS.md`

This is additive only and does not replace the normal diff-based review workflow.
