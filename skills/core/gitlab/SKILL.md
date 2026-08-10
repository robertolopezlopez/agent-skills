---
name: gitlab
description: Fetch and inspect GitLab merge requests and their discussions. Use when given an MR IID or URL and asked to fetch merge request details, read comments or discussion threads, inspect structured discussion data, extract the MR IID from a URL, auto-detect the repository project path or numeric project ID via synced GIT-ACCESS.md and resolve_repo_identity.py, or prepare normalized GitLab MR context for a companion skill. Prefer `glab` and `glab api`, then GitLab MCP when local tools are insufficient.
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

- the task is general local Git repository inspection only; use synced **`GIT-ACCESS.md`**
- the task is primarily comment grouping or review planning; use `gitlab-mr-comment-analysis` after this skill
- the task is primarily repository-specific technical analysis or code changes; use the appropriate overlay after this skill
- the repository is not hosted on GitLab

## First Read

- Read the repository `AGENTS.md` and `ARTIFACTS.md` (artifact directory conventions) before running commands.
- Read synced **`GIT-ACCESS.md`** (`agent_config.py --git-access-policy`) when a `glab api` call needs the repository project path or numeric project ID.
- Prefer `glab mr view` for MR overview and comments.
- Prefer `glab api` when structured discussion data is needed.
- Use GitLab MCP only when local `glab` access is missing or insufficient.
- Pair this skill with a repository-specific or workflow-specific companion skill when the user wants deeper technical analysis, implementation planning, or code changes.

## Inputs

Accept, in order of preference:

- MR context that is already known from prior `gitlab` usage
- an MR IID like `123`
- an MR URL that contains the IID
- no explicit MR input, when the current repository context can be used to infer or verify the target MR

If the user did not provide an MR IID or MR URL, try to verify or discover the target MR from available context before asking the user:

- use `glab` when the current checkout, branch context, or repository metadata is enough to identify the MR
- use synced **`GIT-ACCESS.md`** + **`git-repo-identity`** to resolve repository identity when GitLab API context is needed first
- use GitLab MCP only when local `glab` discovery fails or is insufficient

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
- project path: `guided-experience/guided-experience-service`
- encoded project path: `guided-experience%2Fguided-experience-service`
- MR IID: `123`

## Companion Skills

Use this skill as the transport and normalization layer.

Common pairings:

- synced **`GIT-ACCESS.md`** + **`git-repo-identity`** for repository identity or GitLab project resolution before `glab api`
- `gitlab-mr-comment-analysis` for unresolved comment grouping and reporting
- repository-specific overlay skills for deeper technical analysis or proposed changes

## Workflow

1. Start in the target repository root.
2. If MR context is already known from prior `gitlab` usage, reuse it.
3. If no MR IID or MR URL was provided, try to verify or discover the target MR from the current repository context:
   - use `glab` when local branch, checkout, or repository context can identify the MR
   - use synced **`GIT-ACCESS.md`** first when repository identity must be resolved before a GitLab lookup
   - use GitLab MCP only when local `glab` discovery fails or is insufficient
4. If the input is an MR URL, parse host, project path, and MR IID from the link first.
5. Extract the MR IID once and reuse it consistently as `mr_iid`.
6. If the task needs `glab api` with a project identifier, resolve repository identity per **`GIT-ACCESS.md`** first:
   - run **`git-repo-identity --json`** (or **`--fetch-id`**) for host, project path, encoded project path, and numeric GitLab project ID when available
7. When the task started from an MR URL, prefer the parsed host and encoded project path from the URL in `glab api` calls when there is no reliable local repository context.
8. If no MR can be verified or discovered from local context, ask the user for an MR IID or MR URL.
9. Read the MR overview and comments with `glab mr view <MR> --comments`.
10. If needed, inspect structured discussion data with `glab api`.
11. Use GitLab MCP only when local `glab` access is missing or insufficient.
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
   - resolve `meaningful_id` (default `mr-<MR>` unless a tracker key or repo rule applies; explicit user paths win)
   - fetch MR JSON with `glab api`, using GitLab MCP only when local `glab` access is missing or insufficient
   - run `scripts/bootstrap_gitlab_artifact.py` with `--output` under `$ARTIFACTS/<meaningful_id>/` when not overridden
   - return the local artifact path and suggested next action
18. Keep artifact bootstrap optional and additive so existing companion skills can keep using the same `gitlab` context contract unchanged.
19. Return normalized MR context for downstream skills.
20. When rerunning similar MR fetch or inspection work, preserve durable learned sections such as `Transport Notes`, `Project Resolution Fallbacks`, and `Discussion Shape Oddities` when they still match the current host, project, and transport behavior.

## Transport Preference

Preferred order:

1. **`GIT-ACCESS.md`** + **`git-repo-identity`** when repository or project identity is needed
2. `glab mr view` for overview and comments
3. `glab api` for structured discussions, notes, and MR JSON
4. GitLab MCP when local tools are missing or insufficient

Use the same normalized output contract regardless of transport so companion skills do not care whether the data came from local `glab` or GitLab MCP.

## API reference cache

Resolve **`$AGENT_CONFIG_HOME/api-docs/gitlab-api/`** with **`scripts/agent_config.py --api-docs-dir gitlab-api`**.

1. Read the cached `README.md` and endpoint notes when present.
2. On first use (or when stale), fetch or summarize [GitLab REST API](https://docs.gitlab.com/api/rest/) docs into that directory — especially merge request, discussion, and project endpoints used by `glab api`.
3. On later uses, consult the cache before re-downloading docs.

See **AGENTS.md** (REST API reference cache).

## Local Tool Commands

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

Resolve project identity first through synced **`GIT-ACCESS.md`**.

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

Optional artifact bootstrap after fetching MR JSON (default output under `$ARTIFACTS/mr-<MR>/` via external store; pass `--output` explicitly when the user or repo rules specify a different path):

```bash
glab api /projects/<project_id>/merge_requests/<MR> > /tmp/mr_<MR>.json
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR>
```

When using `encoded_project_path` instead of `project_id`:

```bash
glab api /projects/<encoded_project_path>/merge_requests/<MR> > /tmp/mr_<MR>.json
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR>
```

For investigation-heavy bootstrap, use `--type analysis`. To pin a path explicitly:

```bash
ARTIFACTS="$(python3 scripts/resolve_artifact_path.py --repo-artifacts-root)"
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR> --output "$ARTIFACTS/mr-<MR>/analysis_mr_<MR>.md"
```

Decision rule:

- if identity resolution returns `project_id`, use it in `/projects/<project_id>/...`
- otherwise use `encoded_project_path` in `/projects/<encoded_project_path>/...`

If the repo is not hosted on GitLab, stop and report that the remote host is not a GitLab instance instead of calling `glab api` or GitLab MCP.

## Notes

- Prefer local `glab mr view`, then `glab api`, then GitLab MCP only when local tools are insufficient.
- Extract the MR IID once and reuse it consistently.
- Prefer synced **`GIT-ACCESS.md`** + **`git-repo-identity`** for repository/project identity instead of manually inferring it from `git remote -v`.
- Use the numeric project ID when available; otherwise use the resolved project path consistently.
- Do not assume resolved comments are actionable unless the user asks for them.
- Companion skills should consume this skill's normalized MR context instead of redoing fetch, identity-resolution, link-handling, or classification logic.
- Artifact bootstrap is optional and must not change the existing MR context contract consumed by dependent skills.
- Keep GitLab transport selection and discussion inspection logic in this skill; let overlays add workflow-specific outputs and repository-specific conclusions.
- When a transport path or thread shape proves unusual, record it once in `Transport Notes`, `Project Resolution Fallbacks`, or `Discussion Shape Oddities` with the smallest useful explanation.

## Validation

- Before fetching, run **`scripts/check_skill_prereqs.sh gitlab`** then **`scripts/check_skill_config.sh gitlab`**. If `glab` is missing, **ask the user** to install using the **OS-appropriate** `suggest (...)` line; if auth is missing, **help the user** run `glab auth login` before falling back to GitLab MCP.
- Prefer local `glab` before GitLab MCP.
- Keep the same normalized MR context contract regardless of transport.
- Verify that `mr_iid`, `mr_link`, and project identity fields stay consistent across local tool commands.
- Exclude resolved threads only when the downstream task calls for unresolved comments only.

## Outputs / Artifacts

This skill should return normalized MR context for downstream skills, including when available:

- `mr_iid`
- `mr_link`
- project identity fields such as `project_id` or `encoded_project_path`
- thread status and comment links
- transport notes that matter for reruns

When artifact bootstrap is requested, this skill may also write under `$ARTIFACTS/<meaningful_id>/` (default `meaningful_id`: `mr-<MR>`):

- `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md`
- `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md`

**Legacy:** existing root-level `review_mr_<MR>.md` or `analysis_mr_<MR>.md` files remain valid—refresh in place instead of relocating unless the user asks to migrate.

## Safety Notes

- Stop and report when the remote host is not a GitLab instance.
- Keep GitLab transport and normalization logic here; do not duplicate it in companion skills.
- Do not let artifact bootstrap change the normalized MR context contract used by downstream skills.

## Self-Improving Behavior

When rerunning GitLab MR fetch or inspection for the same host, project, or MR family:

- preserve durable learned sections such as `## Transport Notes`, `## Project Resolution Fallbacks`, and `## Discussion Shape Oddities` when they still match the current host, project, and transport behavior
- refresh conclusions from live `glab` or GitLab MCP output before reusing them
- promote repeated confirmed observations into short transport heuristics, preferably phrased like `when glab lacks X, try Y before MCP`
- demote, mark stale, or remove heuristics contradicted by new transport behavior or updated API output

## Artifact Bootstrap

When the user explicitly asks to create a local artifact from an MR, create either:

- `$ARTIFACTS/<meaningful_id>/review_mr_<MR>.md` for normal review work
- `$ARTIFACTS/<meaningful_id>/analysis_mr_<MR>.md` for investigation-heavy work

Default `meaningful_id` is `mr-<MR>` unless a tracker key or repo `AGENTS.md` rule applies. Explicit user paths always win. Prefer `$ARTIFACTS/<meaningful_id>/` for **new** artifacts; open and extend legacy root-level files when they already exist.

Recommended flow:

1. resolve the MR IID with the normal workflow
2. choose `meaningful_id` (default `mr-<MR>`)
3. fetch MR JSON with `glab api`, using GitLab MCP only when local `glab` access is missing or insufficient
4. run `scripts/bootstrap_gitlab_artifact.py` with MR JSON (`--mr` / `--json` as today); omit `--output` to use the script default `$ARTIFACTS/mr-<MR>/review_mr_<MR>.md` or `$ARTIFACTS/mr-<MR>/analysis_mr_<MR>.md` from `--type`, or pass `--output` when the user or repo rules need a non-default location
5. let the bootstrap helper validate the generated artifact against the shared schema
6. if a local review artifact already exists (under `$ARTIFACTS/` or at repo root), preserve local sections such as `Follow-up Findings` and `Improvement Candidates` while refreshing GitLab-derived sections from live MR data
7. write the artifact using the shared section order documented in `../ARTIFACTS.md`
8. report the artifact path and next suggested action

Example requests:

- `Use gitlab to bootstrap an artifact for MR 123`
- `Use gitlab to fetch MR 123 and fill $ARTIFACTS/mr-123/review_mr_123.md`
- `Bootstrap a local review artifact from https://example.com/group/project/-/merge_requests/123`
