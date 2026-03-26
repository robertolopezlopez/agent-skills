# Agent Skills

Custom Codex skills tracked in git.

## Layout

- `private-service-contributor/`: repo workflow skill for private-service
- `private-service-technical-analysis/`: investigation and analysis skill for private-service
- `git-hooks/post-commit`: copies committed skills into `~/.codex/skills`

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

This keeps `/Users/rlopezlopez/workspace/agent-skills` as the source of truth while installing real copied directories for Codex discovery.
