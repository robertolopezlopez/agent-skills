# github-pr-comment-analysis

The `github-pr-comment-analysis` skill analyzes actionable unresolved GitHub pull request comments **inside the main PR artifact** (`review_pr_<PR>.md` by default, or `analysis_pr_<PR>.md` when that is the working file).

See `SKILL.md`.

## Transport

Fetch and normalize PR context per synced **`GITHUB-ACCESS.md`** (`agent_config.py --github-access-policy`) using **`gh`** / **`gh api`**.

## Optional artifact input

Start from `review_pr_<PR>.md` or `analysis_pr_<PR>.md`:

- read first for framing
- refresh live PR context via **`gh`** per **`GITHUB-ACCESS.md`**
- upsert grouped threads under `## Grouped unresolved comments` with stable `### issue_*` subsections—no separate work-plan or per-issue files for new runs

Artifacts follow `../ARTIFACTS.md`. Legacy split files (`work_plan_pr_*`, etc.) should be merged into the main artifact when encountered.
