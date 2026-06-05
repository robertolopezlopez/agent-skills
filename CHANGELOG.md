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

- **`$GLOBAL/`** cross-repository artifact scope under **`$AGENT_ARTIFACTS_HOME/_global/`** for org-wide knowledge (team ownership, internal tooling) accessible from any checkout; **`resolve_artifact_path.py`** flags **`--global-artifacts-root`**, **`--global-next-time-checks`**, **`--scope global`**
- **`scripts/agent-config.sh`** and **`scripts/agent_config.py`**: runtime-aware config home resolution so Cursor installs use **`~/.cursor/`** defaults only (Codex uses **`~/.codex/`**); transport skill docs no longer instruct agents to read both trees

- core **`learn-daily`** skill (`skills/core/learn-daily/`, renamed from `daily-agent-rhythm`) for a short start → work → end loop using **`$ARTIFACTS/`** (external store) and optional **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**
- core `github-pr-comment-analysis` skill (`skills/core/github-pr-comment-analysis/`) mirroring `gitlab-mr-comment-analysis` for GitHub PRs (grouped threads inside `review_pr_<number>.md` / `analysis_pr_<number>.md`)
- CLI product overlay skills under `skills/cli/` (`private-contributor`, `private-technical-analysis`, `private-parallel-tests`, `private-pr-comment-analysis`), agent- and IDE-agnostic, declared in `skills_manifest.yaml`
- shared skill schema guidance in `docs/skill-schema.md`
- release/change guidance in `docs/release-change-guidance.md`
- reusable work-plan template in `templates/work_plan.md`
- repo command shortcuts in `Makefile`
- skills manifest in `skills_manifest.yaml`
- manifest reader in `scripts/skill_manifest.py` with optional install filters (`--exclude-release-groups`, `--exclude-skill-names`, `list-excluded-skill-names`); `scripts/sync_skills.sh` reads `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` / `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` to omit manifest groups or skill names and remove them from install roots when present

### Changed

- **Artifact store:** durable agent context (follow-ups, work plans, analysis, **`NEXT_TIME_CHECKS.md`**) defaults to an **external** store **`$AGENT_ARTIFACTS_HOME/<repo-key>/`** (shorthand **`$ARTIFACTS/`** in skills), outside project git checkouts. Added **`scripts/resolve_artifact_path.py`** and **`scripts/migrate_legacy_artifacts.py`**; **`ARTIFACTS.md`**, **`learn-daily`**, bootstrap helpers, and workflow skills updated. Legacy in-repo **`_artifacts_/`** remains valid for read/extend only.
- **`learn-daily`**: bootstrap checklist for **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** (steps 1–2) plus post-bootstrap checklist; **`AGENTS.md`** documents the external playbook pointer
- **Artifact placement (prior):** shipped `ARTIFACTS.md` and updated skills prefer new local Markdown under in-repo `_artifacts_/<meaningful_id>/` — superseded by external store default above
- **`gitlab-mr-comment-analysis`** and **`github-pr-comment-analysis`** write grouped threads **inside** the main MR/PR Markdown artifact (`review_mr_*` / `review_pr_*`, or `analysis_mr_*` / `analysis_pr_*`) under `## Grouped unresolved comments`; standalone `work_plan_*`, per-issue splits, and `*_comment_report.md` outputs are legacy-only for migration
- **`private-pr-comment-analysis`** targets **GitHub** pull requests (`github` transport, **`github-pr-comment-analysis`** grouping); manifest **companion_skills** no longer lists `gitlab` / `gitlab-mr-comment-analysis`
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
