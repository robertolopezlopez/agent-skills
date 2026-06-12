---
name: git
description: >-
  DEPRECATED — use synced GIT-ACCESS.md (agent_config.py --git-access-policy) with git CLI and
  scripts/git/resolve_repo_identity.py instead. This stub remains until Phase C removes the installable skill directory.
---

# Git Repository Context (deprecated)

> **Do not use this skill for new work.** Read synced **`GIT-ACCESS.md`** instead:
>
> ```bash
> python3 ~/.cursor/skills/scripts/agent_config.py --git-access-policy
> # or: ~/.codex/skills/scripts/agent_config.py --git-access-policy
> ```
>
> Helper: **`agent_config.py --git-scripts-dir`** → **`git-repo-identity`** / **`resolve_repo_identity.py`**.

## When to Use

**Never for new sessions.** Use **`GIT-ACCESS.md`** + synced helpers.

## Workflow skills (unchanged)

- **`gitlab`** — GitLab MR transport (consumes identity from **`GIT-ACCESS.md`**)
- **`GITHUB-ACCESS.md`** — GitHub fetch after optional host verification
- **`circleci`** — project slug inference from remotes

## Migration

See **`docs/git-access-migration.md`** in the agent-skills repository.
