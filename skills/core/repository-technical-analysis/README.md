# repository-technical-analysis

Use this skill for evidence-first investigation work across repositories.

## Optional Artifact Input

This skill can start from a local workflow artifact such as:

- `task_<issue>.md`
- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`
- `analysis_<relevant_name>.md`

When rerunning analysis for the same problem, read the existing analysis artifact first and preserve local learned sections such as:

- `## Follow-up Findings`
- `## Improvement Candidates`
- optional `## Root Cause Lessons`

while refreshing evidence-backed sections from current code, logs, tests, and reproductions.

Artifacts reused or updated by this skill should follow the shared schema in `../ARTIFACTS.md` when applicable.
