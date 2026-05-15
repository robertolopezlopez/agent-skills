# github-pr-comment-analysis

The `github-pr-comment-analysis` skill analyzes actionable unresolved GitHub pull request comments.

## Optional artifact input

This skill can start from a local GitHub bootstrap artifact such as:

- `review_pr_<PR>.md`
- `analysis_pr_<PR>.md`

When an artifact is provided, the skill:

- reads it first for context and prior assumptions
- then refreshes live PR context through `github`
- keeps `github` as the source of truth for PR identity, comment state, and normalized threads

This is additive only. Existing workflows that start directly from `github`, a PR number, or a PR URL continue to work the same way.

Artifacts reused by this skill should follow the shared schema in `../ARTIFACTS.md`.

When rerun on the same PR, this skill may preserve local learned sections such as:

- `## Follow-up Findings`
- `## Improvement Candidates`

for still-relevant grouped issues while refreshing live PR comment state through `github`.
