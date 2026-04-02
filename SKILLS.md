# Skills

Skills defined in this repository:

- `python-fastapi-contributor`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis`: reusable investigation-first workflow for code repositories
- `private-service-contributor`: repo-specific contributor overlay for private-service
- `private-service-technical-analysis`: repo-specific technical analysis overlay for private-service
- `multi-spawn-agent`: reusable template for spawning parallel worker agents with disjoint ownership

Skill locations:

- `python-fastapi-contributor/SKILL.md`
- `repository-technical-analysis/SKILL.md`
- `private-service-contributor/SKILL.md`
- `private-service-technical-analysis/SKILL.md`
- `multi-spawn-agent/SKILL.md`

Usage notes:

- The `private-service-*` skills are overlays intended to be used with the corresponding generic workflow skill.
- Codex discovers installed skills from `~/.codex/skills`, not directly from this repository.
- This repository installs skills via `git-hooks/post-commit`, which copies each top-level skill directory into `~/.codex/skills` after a commit.
- Restart Codex after installing or updating skills so the active session can pick them up.
