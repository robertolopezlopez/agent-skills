# Skills

Skills defined in this repository:

- `python-fastapi-contributor`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis`: reusable investigation-first workflow for code repositories
- `gitlab-mr-comment-analysis`: reusable GitLab merge-request comment-analysis workflow
- `private-service-contributor`: repo-specific contributor overlay for private-service
- `private-service-technical-analysis`: repo-specific technical analysis overlay for private-service
- `private-service-parallel-tests`: run private-service unit and integration tests with 10 workers
- `private-service-mr-comment-analysis`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes
- `multi-spawn-agent`: reusable template for spawning parallel worker agents with disjoint ownership

Skill locations:

- `python-fastapi-contributor/SKILL.md`
- `repository-technical-analysis/SKILL.md`
- `gitlab-mr-comment-analysis/SKILL.md`
- `private-service-contributor/SKILL.md`
- `private-service-technical-analysis/SKILL.md`
- `private-service-parallel-tests/SKILL.md`
- `private-service-mr-comment-analysis/SKILL.md`
- `multi-spawn-agent/SKILL.md`

Usage notes:

- The `private-service-*` skills are overlays intended to be used with the corresponding generic workflow skill.
- `private-service-mr-comment-analysis` specifically layers private-service analysis on top of `gitlab-mr-comment-analysis`.
- Codex discovers installed skills from `~/.codex/skills`, not directly from this repository.
- This repository installs skills via `git-hooks/post-commit`, which copies each top-level skill directory into `~/.codex/skills` after a commit.
- Restart Codex after installing or updating skills so the active session can pick them up.
