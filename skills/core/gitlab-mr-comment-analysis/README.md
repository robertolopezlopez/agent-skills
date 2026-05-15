# gitlab-mr-comment-analysis

The `gitlab-mr-comment-analysis` skill analyzes actionable unresolved GitLab merge request comments **inside the main MR artifact** (`review_mr_<MR>.md` by default, or `analysis_mr_<MR>.md` when that is the working file).

See `SKILL.md`.

## Optional artifact input

Start from `review_mr_<MR>.md` or `analysis_mr_<MR>.md`:

- read first for framing
- refresh live MR context through `gitlab`
- upsert grouped threads under `## Grouped unresolved comments` with stable `### issue_*` subsections—no separate work-plan or per-issue files for new runs

Artifacts follow `../ARTIFACTS.md`. Legacy split files (`work_plan_mr_*`, etc.) should be merged into the main artifact when encountered.
