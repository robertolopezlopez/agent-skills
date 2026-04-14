# gitlab-mr-comment-analysis

The `gitlab-mr-comment-analysis` skill analyzes actionable unresolved GitLab merge request comments.

## Optional artifact input

This skill can now start from a local GitLab bootstrap artifact such as:

- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

When an artifact is provided, the skill:

- reads it first for context and prior assumptions
- then refreshes live MR context through `gitlab`
- keeps `gitlab` as the source of truth for MR identity, comment state, and normalized threads

This is additive only. Existing workflows that start directly from `gitlab`, an MR IID, or an MR URL continue to work the same way.
