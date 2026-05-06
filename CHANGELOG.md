# Changelog

This repository uses a lightweight changelog.

It is intended for:

- notable breaking changes
- workflow-affecting behavior changes
- durable repository-level guidance changes

It is not intended to mirror every commit.
Use commit history for routine wording, cleanup, and implementation-only changes.

## Unreleased

### Added

- CLI product overlay skills under `skills/cli/` (`private-contributor`, `private-technical-analysis`, `private-parallel-tests`, `cli-mr-comment-analysis`), agent- and IDE-agnostic, declared in `skills_manifest.yaml`
- shared skill schema guidance in `docs/skill-schema.md`
- release/change guidance in `docs/release-change-guidance.md`
- reusable work-plan template in `templates/work_plan.md`
- repo command shortcuts in `Makefile`
- skills manifest in `skills_manifest.yaml`
- manifest reader in `scripts/skill_manifest.py`

### Changed

- `scripts/sync_skills.sh --delete-missing` skips the non-skill `scripts/` directory under each install root (it carries shared helpers such as `validate_artifact.py`)
- CLI overlay skills: `private-prefix-*` → `cli-*`, directory `skills/private-prefix/` → `skills/cli/`, manifest `repo_scope` / `release_group` → `cli`; prose is agent- and IDE-agnostic
- `git-hooks/post-commit` forces `AGENT_SKILLS_SYNC_TARGETS=codex,cursor` and resolves the repo with `git rev-parse`; `git-hooks/pre-commit` uses the same repo resolution for symlink-safe paths
- `jira` skill helpers read `ATLASSIAN_API_BASE_URL` from **`~/.cursor/jira.env`** before **`~/.codex/jira.env`**; bootstrap artifact metadata and validator lookup prefer Cursor install paths when present
- top-level skills normalized to the shared schema
- `scripts/validate_skill.py` now distinguishes hard failures from schema-drift warnings and checks manifest consistency
- `scripts/validate_repo.sh` now supports `--summary`
- `codex-multi-agent-template/AGENTS.md` now has clearer role output, ownership, and handoff rules

### Notes

- For change-recording guidance, see `docs/release-change-guidance.md`.
