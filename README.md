# Agent Skills

Custom Codex skills tracked in git.

## Layout

- `python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `gitlab-mr-comment-analysis/`: reusable GitLab merge request comment-analysis workflow for any GitLab repository
- `jira/`: generic Jira and Atlassian issue access and update workflow through the Jira REST API
  See `jira/README.md` for setup, auth expectations, and `jira-api` usage.
- `private-service-contributor/`: repo workflow skill for private-service
- `private-service-technical-analysis/`: investigation and analysis skill for private-service
- `private-service-parallel-tests/`: run private-service unit and integration tests with 10 workers
- `private-service-mr-comment-analysis/`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes
- `multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
- `splunk-jira/`: Splunk-specific overlay on top of `jira` for reading, creating, and updating Splunk Jira tickets
  See `splunk-jira/README.md` for Splunk-specific defaults and create/read/update workflows.
- `git-hooks/post-commit`: copies committed skills into `~/.codex/skills`

The private-service skills are overlays. Use them with the matching generic skills when working in that repository.
Likewise, `splunk-jira` is an overlay on `jira`: use `jira` for generic Atlassian/Jira access and `splunk-jira` when Splunk defaults should apply.

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
- `splunk-jira/README.md`: fish, bash, and zsh shell setup plus auto-bootstrap details for `jira-api` and Codex approval guidance
