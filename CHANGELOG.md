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

- core `confluence` skill (`skills/core/confluence/`) for Confluence Cloud REST access via helpers; reads non-secret defaults from **`~/.cursor/atlassian.env`** then **`~/.codex/atlassian.env`**
- CLI product overlay skills under `skills/cli/` (`private-contributor`, `private-technical-analysis`, `private-parallel-tests`, `private-pr-comment-analysis`), agent- and IDE-agnostic, declared in `skills_manifest.yaml`
- shared skill schema guidance in `docs/skill-schema.md`
- release/change guidance in `docs/release-change-guidance.md`
- reusable work-plan template in `templates/work_plan.md`
- repo command shortcuts in `Makefile`
- skills manifest in `skills_manifest.yaml`
- manifest reader in `scripts/skill_manifest.py` with optional install filters (`--exclude-release-groups`, `--exclude-skill-names`, `list-excluded-skill-names`); `scripts/sync_skills.sh` reads `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` / `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` to omit manifest groups or skill names and remove them from install roots when present

### Changed

- Renamed **`cli-mr-comment-analysis`** → **`private-pr-comment-analysis`** (directory `skills/cli/mr-comment-analysis/` → `skills/cli/pr-comment-analysis/`). Remove stale installs with `./scripts/sync_skills.sh --all --verify --delete-missing`.
- Atlassian auth is a single manifest **shared_files** script (`scripts/atlassian-auth.sh`); `jira` and `confluence` helpers source it from the skills install root `scripts/` directory next to `validate_artifact.py` instead of copying to `$HOME/.local/share/jira/`
- `scripts/sync_skills.sh --delete-missing` skips the non-skill `scripts/` directory under each install root (it carries shared helpers such as `validate_artifact.py`)
- CLI overlay skills: `private-prefix-*` → `cli-*`, directory `skills/private-prefix/` → `skills/cli/`, manifest `repo_scope` / `release_group` → `cli`; prose is agent- and IDE-agnostic
- `git-hooks/post-commit` forces `AGENT_SKILLS_SYNC_TARGETS=codex,cursor` and resolves the repo with `git rev-parse`; `git-hooks/pre-commit` uses the same repo resolution for symlink-safe paths
- **`jira`** / **`confluence`** helpers and Jira artifact bootstrap read `ATLASSIAN_API_BASE_URL` from **`~/.cursor/atlassian.env`** before **`~/.codex/atlassian.env`**; **`~/.cursor/jira.env`** / **`~/.codex/jira.env`** are no longer read (rename existing files if needed).
- top-level skills normalized to the shared schema
- `scripts/validate_skill.py` now distinguishes hard failures from schema-drift warnings and checks manifest consistency
- `scripts/validate_repo.sh` now supports `--summary`
- `codex-multi-agent-template/AGENTS.md` now has clearer role output, ownership, and handoff rules

### Notes

- For change-recording guidance, see `docs/release-change-guidance.md`.
