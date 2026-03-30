# Agent Skills

Custom Codex skills tracked in git.

## Layout

- `python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `private-service-contributor/`: repo workflow skill for private-service
- `private-service-technical-analysis/`: investigation and analysis skill for private-service
- `splunk-jira-ticket/`: fetch and summarize Splunk Jira or Atlassian tickets through the Jira REST API
  See `splunk-jira-ticket/README.md` for shell setup and the `jira-api` helper command.
- `git-hooks/post-commit`: copies committed skills into `~/.codex/skills`

The private-service skills are overlays. Use them with the generic skills when working in that repository.

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

- `splunk-jira-ticket/README.md`: fish, bash, and zsh shell setup plus `jira-api` helper setup and Codex approval guidance
