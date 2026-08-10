---
name: gitlab
description: Fetch and normalize GitLab merge requests and discussions from an IID or URL. Use for MR metadata, comments, unresolved thread state, project identity, or local MR artifact bootstrap. Prefer the bundled `gl-fetch` wrapper over manual `glab api`; use GitLab MCP only when local transport is unavailable or insufficient.
---

# GitLab Merge Request Access

Use local `glab` through the normalized helper; keep review grouping and code analysis in companion skills.

## When to Use

Use for GitLab MR identity, metadata, discussions, unresolved state, or requested artifact bootstrap.

## When Not to Use

For local Git identity only, use `GIT-ACCESS.md`; for grouped review analysis, add `gitlab-mr-comment-analysis`.

## Inputs

- MR IID, MR URL, or previously normalized context.
- For a bare IID, run from the target repository so `git-repo-identity` can resolve the project.
- Optional artifact type: `review` (default) or `analysis`.

## Workflow

1. Read repository `AGENTS.md`, then run `scripts/check_skill_prereqs.sh gitlab` and `scripts/check_skill_config.sh gitlab`. Help with OS-appropriate installation or `glab auth login` before fallback.
2. Resolve the helper directory with `agent_config.py --gitlab-scripts-dir`.
3. Fetch metadata only:

   ```bash
   <resolved-gitlab-scripts-dir>/gl-fetch mr '<iid-or-url>'
   ```

4. Add `--full` when discussions or unresolved state matter. The helper:
   - parses nested-group MR URLs
   - resolves bare-IID project identity through `git-repo-identity`
   - calls `glab api` and paginates discussions
   - removes system notes and normalizes direct note links and thread resolution
5. Reuse returned `mr_iid`, `mr_link`, project identity, and discussions. Do not re-parse remotes, URLs, or raw discussion shapes downstream.
6. Use GitLab MCP only if authenticated local transport cannot provide required data; preserve the output contract below.
7. For comment grouping, pass normalized context to `gitlab-mr-comment-analysis`. For repository conclusions or changes, add the appropriate analysis/contributor overlay.

## Artifact Bootstrap

Only when requested:

1. Save `<resolved-gitlab-scripts-dir>/gl-fetch mr '<iid-or-url>' --full` JSON to a temporary file.
2. Run `scripts/bootstrap_gitlab_artifact.py --json <file> [--type review|analysis]` relative to this skill.
3. Default to `$ARTIFACTS/mr-<IID>/{review,analysis}_mr_<IID>.md`; explicit paths win. Extend an existing artifact instead of creating a duplicate.
4. Report the path. Bootstrap is local and must not mutate GitLab.

## Validation

- Normalized context keeps `mr_iid`, `mr_link`, host, and project identity consistent.
- `--full` includes paginated non-system discussions and `unresolved_count`.
- Resolved threads remain available for explicit requests; downstream workflows filter them by default.
- Run `python3 -m unittest tests/test_gl_context.py` after changing the helper.

## Outputs / Artifacts

Return JSON fields:

- `transport`, `host`, `project_path`, `encoded_project_path`, `project_id`
- `mr_iid`, `mr_link`, slim `merge_request` metadata
- `discussions` and `unresolved_count` with `--full`

Each normalized note includes author, body, timestamps, position, resolution flags, and direct URL when available.

## Companion Skills

Use `gitlab-mr-comment-analysis` for grouped feedback and repository-specific analysis/contributor skills for code conclusions or changes.

## Safety Notes

- Read-only unless the user explicitly requests a GitLab write.
- Never expose credentials or guess project identity.
- Stop when the remote is not GitLab.
- Do not duplicate transport logic in companion skills.
