# Agent Skills

Custom Codex skills tracked in git.

## Layout

- `python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `gitlab/`: generic GitLab merge request fetch and discussion-inspection workflow
- `gitlab-mr-comment-analysis/`: reusable GitLab merge request comment-analysis workflow for any GitLab repository
- `jira/`: generic Jira and Atlassian issue access and update workflow through the Jira REST API
  See `jira/README.md` for setup, auth expectations, and `jira-api` usage.
- `private-service-contributor/`: repo workflow skill for private-service
- `private-service-technical-analysis/`: investigation and analysis skill for private-service
- `private-service-parallel-tests/`: run private-service unit and integration tests with 10 workers
- `private-service-mr-comment-analysis/`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes
- `multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
- `git-hooks/post-commit`: copies committed skills into `~/.codex/skills`

The private-service skills are overlays. Use them with the matching generic skills when working in that repository.
Use `jira` for generic Atlassian/Jira access, including site-specific Jira usage when `~/.codex/jira.env` sets `ATLASSIAN_API_BASE_URL=https://example.atlassian.net`.
Likewise, `gitlab-mr-comment-analysis` is an overlay on `gitlab`: use `gitlab` for generic MR fetch/discussion inspection and `gitlab-mr-comment-analysis` for grouped unresolved-comment analysis and reporting.

## Install

Copy the tracked hook into the local git hooks directory:

```bash
cp git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Behavior

After each commit in this repository, the `post-commit` hook:

- finds each top-level directory that contains `SKILL.md`
- removes the matching directory in `~/.codex/skills`
- copies the committed skill directory into `~/.codex/skills`

This keeps this repository as the source of truth while installing real copied directories for Codex discovery.

## Skill Docs

- `jira/README.md`: generic Jira setup, auth expectations, base URL behavior, and `jira-api` examples

## Local Defaults Files

Use home-local env files for non-secret skill defaults when a skill documents that behavior.

See the relevant skill `README.md` for the supported variables and precedence rules:

- `jira/README.md`
- `private-service-contributor/README.md`
- `private-service-technical-analysis/README.md`
- `private-service-parallel-tests/README.md`
- `private-service-mr-comment-analysis/README.md`

Do not store secrets such as `ATLASSIAN_API_TOKEN` or `IAC_TOKEN` in these files.
