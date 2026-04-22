# Changelog

This repository uses a lightweight changelog.

It is intended for:

- notable breaking changes
- workflow-affecting behavior changes
- durable repository-level guidance changes

It is not intended to mirror every commit.

## Unreleased

### Added

- shared skill schema guidance in `docs/skill-schema.md`
- skill schema audit in `docs/skill-schema-audit.md`
- release/change guidance in `docs/release-change-guidance.md`
- reusable work-plan template in `templates/work_plan.md`
- repo command shortcuts in `Makefile`
- skills manifest in `skills_manifest.yaml`
- manifest reader in `scripts/skill_manifest.py`

### Changed

- top-level skills normalized to the shared schema
- `scripts/validate_skill.py` now distinguishes hard failures from schema-drift warnings and checks manifest consistency
- `scripts/validate_repo.sh` now supports `--summary`
- `scripts/sync_skills.sh` now supports `--changed`, `--dry-run`, and `--verify`
- `codex-multi-agent-template/AGENTS.md` now has clearer role output, ownership, and handoff rules

### Notes

- For change-recording guidance, see `docs/release-change-guidance.md`.
