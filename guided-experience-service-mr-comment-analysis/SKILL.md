---
name: private-service-mr-comment-analysis
description: "Analyze private-service merge request comments by consuming grouped MR issues and adding private-service-specific technical analysis. Use when given an MR IID or URL and asked to analyze unresolved review comments in private-service, using repository-technical-analysis with private-service-technical-analysis for each grouped issue and private-service-contributor to add proposed changes."
---

# Guided Experience Service MR Comment Analysis

Use this skill from the `private-service` repository root when the user wants an MR analyzed comment-by-comment.
This skill consumes upstream GitLab MR context and grouped issue artifacts, then enriches them with private-service-specific technical analysis, verdicts, and proposed changes.

## First Read

- Read `AGENTS.md` before running commands.
- Read `gitlab` first to resolve normalized MR context, including MR identity, links, discussions, and thread status.
- Read `gitlab-mr-comment-analysis` next to convert that MR context into grouped actionable unresolved issues and reporting scaffolds.
- Treat `gitlab` and `gitlab-mr-comment-analysis` as the transport and normalization boundary. Consume their artifacts whether upstream data came from GitLab MCP or fallback `glab`.
- Use `repository-technical-analysis` together with `private-service-technical-analysis` for the actual technical analysis.
- After each technical analysis is complete, use `private-service-contributor` to add concrete proposed changes to the grouped-issue analysis file.
- Use `multi-spawn-agent` only when the user has explicitly authorized subagents or parallel agent work.

## Inputs

Accept, in order of preference:

- grouped issue context already prepared by `gitlab-mr-comment-analysis`
- MR context already resolved by `gitlab`
- or a raw MR IID / MR URL, which must first be resolved through `gitlab` and then grouped through `gitlab-mr-comment-analysis`

Prefer consuming existing upstream artifacts instead of repeating GitLab fetch or grouping work locally.
If the user provides `review_mr_<MR>.md` or `analysis_mr_<MR>.md`, treat it as preferred bootstrap context before continuing through the normal upstream GitLab analysis flow.

## Workflow

1. Start in the `private-service` repository root.
2. Check whether grouped issues are already available from `gitlab-mr-comment-analysis`.
3. If grouped issues are not available, check whether normalized MR context is already available from `gitlab`.
4. If only raw MR input is available, run the upstream `gitlab` → `gitlab-mr-comment-analysis` flow first.
5. Reuse upstream artifacts without recomputing them locally, including:
   - `mr_iid`
   - `mr_link`
   - project reference
   - direct comment links
   - actionable unresolved thread classification
   - reply status such as `answered_waiting_for_author_feedback`
   - stable grouped issue labels
   - grouped comment membership
   - analysis file paths
   - plan history and status tracking
   - without depending on whether upstream `gitlab` transport used GitLab MCP or fallback `glab`
6. For each grouped issue in `work_plan_mr_<MR>.md`, use `repository-technical-analysis` plus `private-service-technical-analysis` to inspect the relevant local code, tests, and nearby modules before concluding.
7. After the technical analysis is complete for a grouped issue, run `private-service-contributor` to add concrete proposed changes to the same analysis file.
8. If subagents are explicitly authorized, use `multi-spawn-agent` and spawn one worker per independent grouped issue or per small disjoint set of grouped issues.
9. If subagents are not authorized, analyze the grouped issues sequentially with the same file layout.
10. Enrich the upstream reporting artifacts with private-service-specific verdicts, repo-specific risks, prerequisites, blockers, and recommended next actions.
11. Finish with a concise on-screen report with 2-3 lines per analyzed grouped issue plus the path to its Markdown file.
12. When rerunning similar MR analysis, preserve durable repo-local learned sections such as `Reviewer Preference Notes`, `Common Service Fix Patterns`, `Environment Preconditions`, and `Thread Outcome` when they still match refreshed live MR context and local code evidence.

## Worker Requirements

Each grouped-issue analysis must:

- identify whether the comment appears valid, partially valid, outdated, or blocked by missing context
- inspect the relevant local code, tests, and nearby modules before concluding
- note missing prerequisites, environment gaps, or follow-up checks when they materially affect the conclusion
- record whether you have already replied and are waiting for feedback from the comment author
- only cover grouped issues assigned in `work_plan_mr_<MR>.md`
- write one Markdown file per assigned grouped issue
- after the technical analysis section is complete, use `private-service-contributor` sequentially in the same worker to add a proposed changes section to the same file

Use this per-issue file shape:

```text
analysis_mr_<MR>_issue_<NN>.md
```

Each file should contain:

1. MR and issue label
2. MR link
3. direct MR comment links when available
4. reply status, including `answered_waiting_for_author_feedback` when applicable
5. grouped comment summary
6. affected files or modules
7. technical analysis
8. verdict
9. proposed changes
10. recommended next action
11. confidence and open questions
12. optional reviewer preference notes
13. optional common service fix patterns
14. optional environment preconditions
15. optional thread outcome

## Parallel Worker Template

When subagents are allowed, use a `work_plan_mr_<MR>.md`-driven split like this:

```text
Use gitlab-mr-comment-analysis, multi-spawn-agent, repository-technical-analysis, private-service-technical-analysis, and private-service-contributor.

Read work_plan_mr_<MR>.md first.

Spawn N parallel worker agents with fork_context: true, where N is based on the number of independent actionable unresolved grouped issues.

For each worker:
- read work_plan_mr_<MR>.md
- use repository-technical-analysis and private-service-technical-analysis
- after the technical analysis is complete, use private-service-contributor sequentially in the same worker to update the same analysis file with proposed changes
- own exactly the grouped issues assigned in `work_plan_mr_<MR>.md`
- create the assigned analysis_mr_<MR>_issue_<NN>.md files
- do not modify other workers' analysis files
- return: summary, files changed, and validation run

After all workers finish:
- refresh the final report using the upstream `gitlab-mr-comment-analysis` reporting scaffold
- show a screen summary with 2-3 lines per grouped issue and the corresponding Markdown path
```

## Boundaries

- Do not run raw Git commands here for repository identity; consume the `git` skill through the upstream `gitlab` flow when needed.
- Do not parse MR URLs directly here; consume normalized MR context from `gitlab`.
- Do not run `glab` or `glab api` here; GitLab transport belongs to `gitlab`.
- Do not resolve GitLab project identity here; reuse the project reference supplied upstream.
- Do not regroup raw comments here when grouped issues already exist from `gitlab-mr-comment-analysis`.
- Do not redefine stale-file cleanup or consolidated report scaffolding here; reuse the upstream `gitlab-mr-comment-analysis` workflow.
- Reuse upstream MR identity, project reference, MR links, direct comment links, thread classification, reply/waiting status, grouped issue labels, and analysis file paths.
- Do not ask the user for an MR IID or URL until after attempting the upstream `gitlab` resolution flow.
- If MR context is still missing after that flow, then ask for the missing MR IID or URL.

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for task framing, assumptions, and prior open questions
- prefer upstream artifacts such as `work_plan_mr_<MR>.md` and `analysis_mr_<MR>.md` when they already exist
- refresh live MR context through upstream `gitlab` and `gitlab-mr-comment-analysis` flows before concluding
- preserve the shared core sections from `../ARTIFACTS.md` when enriching an existing bootstrap artifact

This is additive only and does not replace the existing upstream GitLab-driven workflow.
Keep repo-specific grouped-issue analysis and report enrichment transport-agnostic so upstream transport changes do not change local artifact contracts.

## Self-Improving Behavior

When rerunning MR comment analysis for the same MR or code area:

- read any existing grouped-issue analysis artifact first
- preserve durable repo-local learned sections such as `## Reviewer Preference Notes`, `## Common Service Fix Patterns`, `## Environment Preconditions`, and `## Thread Outcome` when they still match refreshed MR context and current code evidence
- refresh conclusions through the upstream `gitlab` and `gitlab-mr-comment-analysis` flows before reusing prior lessons
- promote repeated confirmed observations into short repo-local heuristics, preferably phrased like `when this reviewer flags X in private-service, verify Y first`
- demote, mark stale, or remove heuristics contradicted by updated thread state or local code evidence

This keeps grouped-issue analysis artifacts useful across reruns without replacing the upstream GitLab-driven workflow.

## Reporting

Follow and enrich the reporting structure produced by `gitlab-mr-comment-analysis`.
Make sure each per-issue analysis adds:

- a private-service-specific technical analysis
- a verdict grounded in local code and test inspection
- a proposed changes section produced with `private-service-contributor`
- any repo-specific prerequisites, environment gaps, blockers, or follow-up checks that materially affect the conclusion

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard commands
- `pyproject.toml` for pytest markers and project config
- `cicd/scripts/set_weaviate_config.sh` when analysis depends on production Weaviate settings
