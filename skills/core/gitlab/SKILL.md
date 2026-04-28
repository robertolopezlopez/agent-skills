---
name: gitlab
description: Fetch and inspect GitLab merge requests and their discussions. Use when given an MR IID or URL and asked to fetch merge request details, read comments or discussion threads, inspect structured discussion data, extract the MR IID from a URL, auto-detect the repository project path or numeric project ID via the `git` skill, or prepare normalized GitLab MR context for a companion skill. Prefer GitLab MCP when available, with `glab` and `glab api` as fallback transport.
---

# GitLab Merge Request Access

Use this skill from a GitLab repository root when the user wants merge request data fetched or inspected.
This skill is the source of truth for GitLab MR identity, links, discussion fetch, and thread-status normalization for companion skills.

## When to Use

Use this skill when the user wants to:

- fetch or inspect a GitLab merge request
- read merge request comments or discussions
- inspect structured discussion state
- bootstrap a local MR artifact
- prepare normalized MR context for a companion skill

## When Not to Use

Do not use this skill when:

- the task is general local Git repository inspection only; use `git`
- the task is primarily comment grouping or review planning; use `gitlab-mr-comment-analysis` after this skill
- the task is primarily repository-specific technical analysis or code changes; use the appropriate overlay after this skill
- the repository is not hosted on GitLab

## First Read

- Read the repository `AGENTS.md` before running commands.
- Prefer GitLab MCP for MR overview, comments, discussions, and structured metadata when a GitLab MCP server is configured in the session.
- Fall back to `glab mr view` for MR overview and comments when GitLab MCP is unavailable or cannot provide the needed data.
- Fall back to `glab api` when structured discussion data is needed and GitLab MCP is unavailable or insufficient.
- Use the `git` skill first when a fallback `glab api` call needs the repository project path or numeric project ID.
- Pair this skill with a repository-specific or workflow-specific companion skill when the user wants deeper technical analysis, implementation planning, or code changes.

## Inputs

Accept, in order of preference:

- MR context that is already known from prior `gitlab` usage
- an MR IID like `123`
- an MR URL that contains the IID
- no explicit MR input, when the current repository context can be used to infer or verify the target MR

If the user did not provide an MR IID or MR URL, try to verify or discover the target MR from available context before asking the user:

- use GitLab MCP when the current checkout, branch context, or repository metadata is enough to identify the MR
- otherwise fall back to `glab`
- use the `git` skill to resolve repository identity when fallback GitLab API context is needed first

Ask the user for an MR IID or MR URL only after those verification or discovery paths fail.

Extract the IID first and use that single value consistently in commands, filenames, and reporting.

For HTTP MR links, parse these fields from the URL:

- host
- project path
- MR IID

Canonical MR URL shape:

```text
https://<host>/<group>/<subgroup>/<repo>/-/merge_requests/<MR>
```

Example:

```text
https://example.com/group/project/-/merge_requests/123
```

Resolves to:

- host: `example.com`
- project path: `guided-experience/private-service`
- encoded project path: `guided-experience%2Fprivate-service`
- MR IID: `123`

## Companion Skills

Use this skill as the transport and normalization layer.

Common pairings:

- `git` for repository identity or GitLab project resolution in fallback mode
- `gitlab-mr-comment-analysis` for unresolved comment grouping and reporting
- repository-specific overlay skills for deeper technical analysis or proposed changes

## Workflow

1. Start in the target repository root.
2. If MR context is already known from prior `gitlab` usage, reuse it.
3. If no MR IID or MR URL was provided, try to verify or discover the target MR from the current repository context:
   - prefer GitLab MCP when local branch, checkout, or repository context can identify the MR
   - otherwise use `glab`
   - use the `git` skill first when fallback repository identity must be resolved before a GitLab lookup
4. If the input is an MR URL, parse host, project path, and MR IID from the link first.
5. Extract the MR IID once and reuse it consistently as `mr_iid`.
6. If the task needs fallback `glab api` with a project identifier, use the `git` skill to resolve repository identity first:
   - ask the `git` skill for the repository host, project path, encoded project path, and numeric GitLab project ID when available
7. When the task started from an MR URL, prefer the parsed host and project path from the URL when calling GitLab MCP, or the parsed host and encoded project path when using fallback `glab api`, if there is no reliable local repository context.
8. If no MR can be verified or discovered from local context, ask the user for an MR IID or MR URL.
9. Read the MR overview and comments with GitLab MCP when available.
10. If GitLab MCP is unavailable or does not expose the needed fields, fall back to `glab mr view <MR> --comments`.
11. If needed, inspect structured discussion data with GitLab MCP first, then fall back to `glab api`.
12. Normalize and preserve:
   - `mr_iid`
   - `mr_link`
   - `project_id` when available
   - `encoded_project_path` when `project_id` is not available
   - direct comment links when available
13. Distinguish and record per thread:
   - actionable unresolved thread vs resolved thread
   - human comment vs system note
   - actionable review comment vs non-actionable chatter
14. When the follow-on task needs unresolved comments only, exclude resolved threads.
15. When the follow-on task needs comment status, note whether:
   - the author is still waiting on a reply
   - you have already replied and are waiting for author feedback, including `answered_waiting_for_author_feedback`
16. Keep GitLab-specific fetch, discussion, link-handling, and normalization logic here. Leave grouping, reporting scaffolds, and repository-specific technical analysis to companion skills.

17. When the user explicitly asks to bootstrap a local artifact for the MR, keep the existing fetch behavior and additionally:
   - fetch MR JSON with GitLab MCP when possible, otherwise with fallback `glab api`
   - run `scripts/bootstrap_gitlab_artifact.py`
   - return the local artifact path and suggested next action
18. Keep artifact bootstrap optional and additive so existing companion skills can keep using the same `gitlab` context contract unchanged.
19. Return normalized MR context for downstream skills.
20. When rerunning similar MR fetch or inspection work, preserve durable learned sections such as `Transport Notes`, `Project Resolution Fallbacks`, and `Discussion Shape Oddities` when they still match the current host, project, and transport behavior.

## Transport Preference

Preferred order:

1. GitLab MCP for MR overview, discussions, notes, and structured metadata
2. `glab mr view` for overview and comment fallback
3. `glab api` for structured fallback when MCP is unavailable or insufficient

Use the same normalized output contract regardless of transport so companion skills do not care whether the data came from GitLab MCP or fallback `glab`.

## Fallback Command Pattern

Preferred fallback MR overview and comments fetch:

```bash
glab mr view <MR> --comments
```

Fallback MR verification or discovery from current checkout when the user did not supply an MR explicitly:

```bash
glab mr view --comments
```

Fallback structured discussion fetch when needed:

```bash
glab api /projects/:id/merge_requests/<MR>/discussions
```

Resolve project identity first through the `git` skill.

When starting from an MR HTTP link and no local repository context is needed, use the parsed URL values directly in fallback mode:

```bash
glab api --hostname <host> /projects/<encoded_project_path>/merge_requests/<MR>/discussions
```

Prefer these explicit fallback patterns after resolving identity:

When `project_id` is present:

```bash
glab api /projects/<project_id>/merge_requests/<MR>/discussions
glab api /projects/<project_id>/merge_requests/<MR>/notes
glab api /projects/<project_id>/merge_requests/<MR>
```

When `project_id` is not present, fall back to `encoded_project_path`:

```bash
glab api /projects/<encoded_project_path>/merge_requests/<MR>/discussions
glab api /projects/<encoded_project_path>/merge_requests/<MR>/notes
glab api /projects/<encoded_project_path>/merge_requests/<MR>
```

Optional fallback artifact bootstrap after fetching MR JSON:

```bash
glab api /projects/<project_id>/merge_requests/<MR> > /tmp/mr_<MR>.json
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR>
```

When using `encoded_project_path` instead of `project_id`:

```bash
glab api /projects/<encoded_project_path>/merge_requests/<MR> > /tmp/mr_<MR>.json
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR>
```

Decision rule:

- if the `git` skill returns `project_id`, use it in `/projects/<project_id>/...`
- otherwise use `encoded_project_path` in `/projects/<encoded_project_path>/...`

If the repo is not hosted on GitLab, stop and report that the remote host is not a GitLab instance instead of calling GitLab MCP or fallback `glab api`.

## Notes

- Prefer GitLab MCP first when available, then `glab mr view`, then `glab api` only when structured fallback data is needed.
- Extract the MR IID once and reuse it consistently.
- Prefer the `git` skill for fallback repository/project identity instead of manually inferring it from `git remote -v`.
- Use the numeric project ID when available; otherwise use the resolved project path consistently.
- Do not assume resolved comments are actionable unless the user asks for them.
- Companion skills should consume this skill's normalized MR context instead of redoing fetch, identity-resolution, link-handling, or classification logic.
- Artifact bootstrap is optional and must not change the existing MR context contract consumed by dependent skills.
- Keep GitLab transport selection and discussion inspection logic in this skill; let overlays add workflow-specific outputs and repository-specific conclusions.
- When a transport path or thread shape proves unusual, record it once in `Transport Notes`, `Project Resolution Fallbacks`, or `Discussion Shape Oddities` with the smallest useful explanation.

## Validation

- Prefer GitLab MCP first when available.
- Keep the same normalized MR context contract regardless of transport.
- Verify that `mr_iid`, `mr_link`, and project identity fields stay consistent across fallback commands.
- Exclude resolved threads only when the downstream task calls for unresolved comments only.

## Outputs / Artifacts

This skill should return normalized MR context for downstream skills, including when available:

- `mr_iid`
- `mr_link`
- project identity fields such as `project_id` or `encoded_project_path`
- thread status and comment links
- transport notes that matter for reruns

When artifact bootstrap is requested, this skill may also write:

- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

## Safety Notes

- Stop and report when the remote host is not a GitLab instance.
- Keep GitLab transport and normalization logic here; do not duplicate it in companion skills.
- Do not let artifact bootstrap change the normalized MR context contract used by downstream skills.

## Self-Improving Behavior

When rerunning GitLab MR fetch or inspection for the same host, project, or MR family:

- preserve durable learned sections such as `## Transport Notes`, `## Project Resolution Fallbacks`, and `## Discussion Shape Oddities` when they still match the current host, project, and transport behavior
- refresh conclusions from live GitLab MCP or fallback `glab` output before reusing them
- promote repeated confirmed observations into short transport heuristics, preferably phrased like `when MCP lacks X, fall back to Y`
- demote, mark stale, or remove heuristics contradicted by new transport behavior or updated API output

## Artifact Bootstrap

When the user explicitly asks to create a local artifact from an MR, create either:

- `review_mr_<MR>.md` for normal review work
- `analysis_mr_<MR>.md` for investigation-heavy work

Recommended flow:

1. resolve the MR IID with the normal workflow
2. fetch MR JSON with GitLab MCP when possible, otherwise with fallback `glab api`
3. run `scripts/bootstrap_gitlab_artifact.py`
4. let the bootstrap helper validate the generated artifact against the shared schema
5. if a local review artifact already exists, preserve local sections such as `Follow-up Findings` and `Improvement Candidates` while refreshing GitLab-derived sections from live MR data
6. write the artifact using the shared section order documented in `../ARTIFACTS.md`
7. report the artifact path and next suggested action

Example requests:

- `Use gitlab to bootstrap an artifact for MR 123`
- `Use gitlab to fetch MR 123 and fill review_mr_123.md`
- `Bootstrap a local review artifact from https://example.com/group/project/-/merge_requests/123`
