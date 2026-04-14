---
name: gitlab
description: Fetch and inspect GitLab merge requests and their discussions. Use when given an MR IID or URL and asked to fetch merge request details with `glab`, read comments or discussion threads, inspect structured discussion data with `glab api`, extract the MR IID from a URL, auto-detect the repository project path or numeric project ID via the `git` skill, or prepare normalized GitLab MR context for a companion skill.
---

# GitLab Merge Request Access

Use this skill from a GitLab repository root when the user wants merge request data fetched or inspected.
This skill is the source of truth for GitLab MR identity, links, discussion fetch, and thread-status normalization for companion skills.

## First Read

- Read the repository `AGENTS.md` before running commands.
- Use `glab` to fetch the merge request overview and its comment threads.
- Use `glab api` when structured discussion data is needed.
- Use the `git` skill first when a `glab api` call needs the repository project path or numeric project ID.
- Pair this skill with a repository-specific or workflow-specific companion skill when the user wants deeper technical analysis, implementation planning, or code changes.

## Inputs

Accept, in order of preference:

- MR context that is already known from prior `gitlab` usage
- an MR IID like `123`
- an MR URL that contains the IID
- no explicit MR input, when the current repository context can be used to infer or verify the target MR

If the user did not provide an MR IID or MR URL, try to verify or discover the target MR from available context before asking the user:

- use `glab` when the current checkout or branch context is enough to identify the MR
- use the `git` skill to resolve repository identity when GitLab project context is needed first

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

## Workflow

1. Start in the target repository root.
2. If MR context is already known from prior `gitlab` usage, reuse it.
3. If no MR IID or MR URL was provided, try to verify or discover the target MR from the current repository context:
   - use `glab` when local branch or checkout context can identify the MR
   - use the `git` skill first when repository identity must be resolved before a GitLab lookup
4. If the input is an MR URL, parse host, project path, and MR IID from the link first.
5. Extract the MR IID once and reuse it consistently as `mr_iid`.
6. If the task needs `glab api` with a project identifier, use the `git` skill to resolve repository identity first:
   - ask the `git` skill for the repository host, project path, encoded project path, and numeric GitLab project ID when available
7. When the task started from an MR URL, prefer the parsed host and encoded project path from the URL if there is no reliable local repository context.
8. If no MR can be verified or discovered from local context, ask the user for an MR IID or MR URL.
9. Read the MR overview and comments with `glab mr view <MR> --comments`.
10. If needed, inspect structured discussion data for the same MR with `glab api`.
11. Normalize and preserve:
   - `mr_iid`
   - `mr_link`
   - `project_id` when available
   - `encoded_project_path` when `project_id` is not available
   - direct comment links when available
12. Distinguish and record per thread:
   - actionable unresolved thread vs resolved thread
   - human comment vs system note
   - actionable review comment vs non-actionable chatter
13. When the follow-on task needs unresolved comments only, exclude resolved threads.
14. When the follow-on task needs comment status, note whether:
   - the author is still waiting on a reply
   - you have already replied and are waiting for author feedback, including `answered_waiting_for_author_feedback`
15. Keep GitLab-specific fetch, discussion, link-handling, and normalization logic here. Leave grouping, reporting scaffolds, and repository-specific technical analysis to companion skills.
16. Return normalized MR context for downstream skills.

## Command Pattern

Preferred MR overview and comments fetch:

```bash
glab mr view <MR> --comments
```

MR verification or discovery from current checkout when the user did not supply an MR explicitly:

```bash
glab mr view --comments
```

Structured discussion fetch when needed:

```bash
glab api /projects/:id/merge_requests/<MR>/discussions
```

Resolve project identity first through the `git` skill.

When starting from an MR HTTP link and no local repository context is needed, use the parsed URL values directly:

```bash
glab api --hostname <host> /projects/<encoded_project_path>/merge_requests/<MR>/discussions
```

Prefer these explicit patterns after resolving identity:

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

Decision rule:

- if the `git` skill returns `project_id`, use it in `/projects/<project_id>/...`
- otherwise use `encoded_project_path` in `/projects/<encoded_project_path>/...`

If the repo is not hosted on GitLab, stop and report that the remote host is not a GitLab instance instead of calling `glab api`.

## Notes

- Prefer `glab mr view` first, then use `glab api` only when structured discussion data is needed.
- Extract the MR IID once and reuse it consistently.
- Prefer the `git` skill for repository/project identity instead of manually inferring it from `git remote -v`.
- Use the numeric project ID when available; otherwise use the resolved project path consistently.
- Do not assume resolved comments are actionable unless the user asks for them.
- Companion skills should consume this skill's normalized MR context instead of redoing fetch, identity-resolution, link-handling, or classification logic.
- Keep GitLab transport and discussion inspection logic in this skill; let overlays add workflow-specific outputs and repository-specific conclusions.
