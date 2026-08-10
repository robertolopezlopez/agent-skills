# Changelog

- Added **`scripts/sync_codex_rules.sh`** and `templates/codex/rules/*.md` to maintain always-on Codex guidance as managed blocks in the global `AGENTS.md`, with selective sync, dry-run, personal-content preservation, bootstrap integration, tests, and post-commit refresh parity with Cursor rules.

This repository uses a lightweight changelog.

It is intended for:

- notable breaking changes
- workflow-affecting behavior changes
- durable repository-level guidance changes

It is not intended to mirror every commit.
Use commit history for routine wording, cleanup, and implementation-only changes.

## Unreleased

### Changed

- **Cross-agent skill portability** — remove a Cursor-only GitLab artifact path,
  make `multi-spawn-agent` runtime-neutral, and route optional CLI Slack
  enrichment through whichever connected Slack capability is available.
- **`cli-caretaker`** — include read-only questions mentioning Slack user group
  `@ask-cli-caretaker` (`S075HU4SREC`) in caretaker research and reports.
- **`branch-change-reviewer`** — require output under the resolved external
  `$ARTIFACTS` store by default.
- **`cli-branch-change-reviewer`** — add a separate `ponytail-review` pass for
  unnecessary complexity.
- **Artifact store default** — use **`~/Documents/agent-artifacts`** for both
  Codex and Cursor unless `AGENT_ARTIFACTS_HOME` overrides it.
- **Jira access migration (Phase C)** — removed installable **`skills/core/jira/`** skill directory and manifest entry. Jira transport is **`JIRA-ACCESS.md`** + synced **`scripts/jira/`** helpers only.
- **Jira access migration (Phase B)** — synced helpers under **`scripts/jira/`**: **`jira-fetch`**, **`jira_context.py`**, **`jira-api`**, **`jira-request`**, **`bootstrap_jira_artifact.py --fetch`**; **`ATLASSIAN_AUTH_EMAIL`** in **`atlassian.env`** for REST fallback.
- **Jira access migration (Phase A)** — portable Jira Cloud policy in **`JIRA-ACCESS.md`**; primary transport **`acli jira workitem …`**; installable **`jira`** skill stubbed until Phase C; **`jira`** removed from **`plan-issues`** **`companion_skills`**; **`check_skill_prereqs.sh jira`** checks **`acli`**; **`check_skill_config.sh jira`** checks **`acli jira auth status`**. See **`docs/jira-access-migration.md`**.
- **Git access migration (Phase D)** — shared **`scripts/parse_remote_url.py`** for remote URL parsing; consumed by **`resolve_repo_identity.py`**, **`gh_context.py`**, and **`resolve_artifact_path.py`**. Self-test via **`parse_remote_url.py --self-test`**.
- **Git access migration (Phase C)** — removed installable **`skills/core/git/`** skill directory and manifest entry. Repository identity is **`GIT-ACCESS.md`** + synced **`scripts/git/`** helpers only.
- **Git access migration (Phase B)** — synced helpers under **`scripts/git/`**; resolve with **`agent_config.py --git-access-policy`** / **`--git-scripts-dir`**; **`check_skill_prereqs.sh git-access`** for the git binary.
- **Git access migration (Phase A)** — portable repository identity policy in **`GIT-ACCESS.md`**; downstream skills (**`gitlab`**, **`circleci`**, GitHub workflows) reference the policy instead of the installable **`git`** skill; **`git`** removed from manifest **`companion_skills`**; installable skill stubbed until Phase C. See **`docs/git-access-migration.md`**.
- **GitHub access migration (Phase C)** — removed installable **`skills/core/github/`** skill directory and manifest entry. GitHub transport is **`GITHUB-ACCESS.md`** + synced **`scripts/github/`** helpers only.
- **GitHub issue bootstrap** — **`bootstrap_github_artifact.py --fetch --issue <N>`** → **`$ARTIFACTS/issue-<N>/triage_issue_<N>.md`** (or **`analysis_issue_<N>.md`** with **`--type analysis`**). Issue fetch includes conversation comments when owner/repo are known.
- **`gh_context.py --full`** — PR fetch adds normalized **`review_threads`** (GraphQL, includes **`is_resolved`**), **`conversation_comments`**, thread summary counts, and slim **`reviews`** / **`review_comments`** for **`github-pr-comment-analysis`**.
- **`apply_pr_thread_groups.py`** — mechanical upsert of **`## Grouped unresolved comments`** from **`--full`** JSON into **`review_pr_<n>.md`** / **`analysis_pr_<n>.md`**.
- **GitHub access migration (Phase B)** — synced helpers under **`scripts/github/`**: **`gh-fetch`**, **`gh_context.py`**, **`bootstrap_github_artifact.py`**. Resolve with **`agent_config.py --github-scripts-dir`**. Documented in **`GITHUB-ACCESS.md`**.
- **GitHub access migration (Phase A)** — routine GitHub issue/PR fetch no longer uses an installable **`github`** skill. Policy lives in synced **`GITHUB-ACCESS.md`** (`agent_config.py --github-access-policy`). Workflow skills refresh via **`gh`** / **`gh api`** per policy. See **`docs/github-access-migration.md`**.
- **Literal code search migration** — routine literal search no longer uses an installable **`fast-grep`** skill. Policy lives in synced **`LITERAL-CODE-SEARCH.md`** (`agent_config.py --literal-search-policy`); helpers sync under **`agent_config.py --literal-search-dir`**. Optional Cursor rule: **`templates/cursor/rules/literal-code-search.mdc`** via **`bootstrap_literal_search.sh --cursor-rule`**. Codex and other agents use the synced doc + skills (no `.mdc`). **`skills/core/fast-grep/`** removed.
- **Literal search OS portability** — **`LITERAL-CODE-SEARCH.md`**, Cursor rule, RTA step 3, **`install-cmd.sh`**, and **`check_skill_prereqs.sh literal-search`** enforce OS-detected installs (`brew`/`apt`/`dnf`/`yum`/`zypper`/`pacman`/`winget`/`scoop`/`choco`/`pkg`); **`fast-grep-resolve --missing`** includes **`os=`**; ask-before-install, never Homebrew-only.
- **Transport preference inverted** across transport skills and **AGENTS.md**: local CLI tools and bundled shell helpers (`gh`, `glab`, `jira-api`, `circleci-request`, …) are preferred before MCP. MCP is the last resort when local tools are missing or insufficient.
- **REST API reference cache** in **AGENTS.md**: on first REST API need, fetch or summarize official docs into **`$AGENT_CONFIG_HOME/api-docs/<service-slug>/`** (`~/.cursor/api-docs/` or `~/.codex/api-docs/`); read the cache on later uses. Path resolution via **`agent_config.py --api-docs-root`** / **`--api-docs-dir`**.
- **Missing CLI tools — ask before fallback** in **AGENTS.md**: when a skill needs a host CLI, check availability; if a safe install exists, ask the user with an **OS-appropriate** command (Homebrew, `apt`, `dnf`, `pacman`, or vendor docs — not Homebrew-only). Shared helper **`scripts/check_skill_prereqs.sh`** detects OS and package managers; transport and investigation skills updated.
- **Runtime tool and helper configuration** in **AGENTS.md**: **`scripts/check_skill_config.sh`** reports missing `atlassian.env`, `circleci.env`, CLI auth, and synced helpers; agents help users finish setup. Added **`templates/circleci.env.example`**, **`agent_config.py --circleci-env`**.

### Added

- **`cli-ci-monitor`**: monitor CLI CircleCI workflow lineages for up to two
  hours, conservatively classify environment failures, cancel active workflows,
  and rerun from failed jobs until success.
- **`latex-to-pdf`**: local LaTeX compilation using project commands or
  XeLaTeX/`latexmk`.
- **`cli-caretaker`**: CLI Ask Caretaker workflow for asks, initial support triage, alerts, `main` CI failures, PR asks, and shift handoff.
- **`JIRA-ACCESS.md`**: synced portable Jira Cloud access policy (`shared_files`; resolve with **`agent_config.py --jira-access-policy`**)
- **`docs/jira-access-migration.md`**: Jira transport migration checklist
- **`scripts/git/`**: **`git-repo-identity`**, **`resolve_repo_identity.py`** (synced; **`agent_config.py --git-scripts-dir`**)
- **`scripts/parse_remote_url.py`**: shared Git remote URL parser (synced; **`--self-test`**)
- **`scripts/jira/`**: **`jira-fetch`**, **`jira_context.py`**, **`jira-api`**, **`jira-request`**, **`bootstrap_jira_artifact.py`** (synced; **`agent_config.py --jira-scripts-dir`**)
- **`docs/git-access-migration.md`**: Phase A–C checklist (mirrors GitHub/literal-search migrations)
- **`GITHUB-ACCESS.md`**: synced portable GitHub fetch policy (`shared_files`; resolve with **`agent_config.py --github-access-policy`**)
- **`scripts/github/`**: **`gh-fetch`**, **`gh_context.py`**, **`bootstrap_github_artifact.py`** (synced; **`agent_config.py --github-scripts-dir`**)
- **`docs/github-access-migration.md`**: Phase A–C checklist (mirrors literal-search migration)
- **`LITERAL-CODE-SEARCH.md`**: synced portable literal-search policy (`shared_files`; resolve with **`agent_config.py --literal-search-policy`**)
- **`scripts/sync_cursor_rules.sh`**: sync **`templates/cursor/rules/*.mdc`** to **`~/.cursor/rules/`** (post-commit uses **`--overwrite`**)
- **`templates/cursor/rules/literal-code-search.mdc`** and **`scripts/bootstrap_literal_search.sh`**: optional Cursor always-on rule; Codex uses synced doc + skills
- **`agent_config.py` / `agent-config.sh`**: **`--skills-root`**, **`--literal-search-dir`**, **`--literal-search-policy`**, **`--github-access-policy`**, **`--github-scripts-dir`**, **`--git-access-policy`**, **`--git-scripts-dir`**

- **`templates/agent-artifacts/`** and **`templates/cursor/rules/agent-artifacts-directory.mdc`**: portable store index and Cursor phrase rule for "the artifacts directory"
- **`scripts/bootstrap_agent_artifacts.sh`**: one-time bootstrap for **`$AGENT_ARTIFACTS_HOME/README.md`**, **`$GLOBAL/NEXT_TIME_CHECKS.md`**, and optional Cursor rule (Codex uses **`AGENTS.md`** + **`ARTIFACTS.md`** for the same contract)

- **`$GLOBAL/`** cross-repository artifact scope under **`$AGENT_ARTIFACTS_HOME/_global/`** for org-wide knowledge (team ownership, internal tooling) accessible from any checkout; **`resolve_artifact_path.py`** flags **`--global-artifacts-root`**, **`--global-next-time-checks`**, **`--scope global`**
- **`scripts/agent-config.sh`** and **`scripts/agent_config.py`**: runtime-aware config home resolution so Cursor installs use **`~/.cursor/`** defaults only (Codex uses **`~/.codex/`**); **`agent_config.py --atlassian-env`** resolves the active defaults file (mirrors **`resolve_artifact_path.py`**); transport skill docs no longer instruct agents to read both trees
- **`templates/atlassian.env.example`**: documents optional **`ATLASSIAN_API_TOKEN`** in runtime **`atlassian.env`**

- core **`learn-daily`** skill (`skills/core/learn-daily/`, renamed from `daily-agent-rhythm`) for a short start → work → end loop using **`$ARTIFACTS/`** (external store) and optional **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**
- core `github-pr-comment-analysis` skill (`skills/core/github-pr-comment-analysis/`) mirroring `gitlab-mr-comment-analysis` for GitHub PRs (grouped threads inside `review_pr_<number>.md` / `analysis_pr_<number>.md`)
- CLI product overlay skills under `skills/cli/` (`cli-contributor`, `cli-technical-analysis`, `cli-parallel-tests`, `cli-pr-comment-analysis`), agent- and IDE-agnostic, declared in `skills_manifest.yaml`
- shared skill schema guidance in `docs/skill-schema.md`
- release/change guidance in `docs/release-change-guidance.md`
- reusable work-plan template in `templates/work_plan.md`
- repo command shortcuts in `Makefile`
- skills manifest in `skills_manifest.yaml`
- manifest reader in `scripts/skill_manifest.py` with optional install filters (`--exclude-release-groups`, `--exclude-skill-names`, `list-excluded-skill-names`); `scripts/sync_skills.sh` reads `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` / `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` to omit manifest groups or skill names and remove them from install roots when present

### Changed

- **`atlassian-auth.sh`**: load **`ATLASSIAN_API_TOKEN`** from runtime **`atlassian.env`** when not exported and not in the credentials file; **`jira`** and **`confluence`** skills/docs updated
- **`learn-daily`**: bootstrap checklist for **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** (steps 1–2) plus post-bootstrap checklist; **`AGENTS.md`** documents the external playbook pointer
- **Artifact placement (prior):** shipped `ARTIFACTS.md` and updated skills prefer new local Markdown under in-repo `_artifacts_/<meaningful_id>/` — superseded by external store default above
- **`gitlab-mr-comment-analysis`** and **`github-pr-comment-analysis`** write grouped threads **inside** the main MR/PR Markdown artifact (`review_mr_*` / `review_pr_*`, or `analysis_mr_*` / `analysis_pr_*`) under `## Grouped unresolved comments`; standalone `work_plan_*`, per-issue splits, and `*_comment_report.md` outputs are legacy-only for migration
- **`cli-pr-comment-analysis`** targets **GitHub** pull requests (`github` transport, **`github-pr-comment-analysis`** grouping); manifest **companion_skills** no longer lists `gitlab` / `gitlab-mr-comment-analysis`
- Renamed **`cli-mr-comment-analysis`** → **`cli-pr-comment-analysis`** (directory `skills/cli/mr-comment-analysis/` → `skills/cli/pr-comment-analysis/`). Remove stale installs with `./scripts/sync_skills.sh --all --verify --delete-missing`.
- Atlassian auth is a single manifest **shared_files** script (`scripts/atlassian-auth.sh`); `jira` and `confluence` helpers source it from the skills install root `scripts/` directory next to `validate_artifact.py` instead of copying to `$HOME/.local/share/jira/`
- `scripts/sync_skills.sh --delete-missing` skips the non-skill `scripts/` directory under each install root (it carries shared helpers such as `validate_artifact.py`)
- CLI overlay skills: `cursor-cli-*` → `cli-*`, directory `skills/cursor-cli/` → `skills/cli/`, manifest `repo_scope` / `release_group` → `cli`; prose is agent- and IDE-agnostic
- `git-hooks/post-commit` forces `AGENT_SKILLS_SYNC_TARGETS=codex,cursor`, runs **`scripts/sync_cursor_rules.sh --overwrite`** after skill sync, and resolves the repo with `git rev-parse`; `git-hooks/pre-commit` uses the same repo resolution for symlink-safe paths
- **`jira`** / **`confluence`** helpers and Jira artifact bootstrap read `ATLASSIAN_API_BASE_URL` from **`~/.cursor/atlassian.env`** before **`~/.codex/atlassian.env`**; **`~/.cursor/jira.env`** / **`~/.codex/jira.env`** are no longer read (rename existing files if needed).
- top-level skills normalized to the shared schema
- `scripts/validate_skill.py` now distinguishes hard failures from schema-drift warnings and checks manifest consistency
- `scripts/validate_repo.sh` now supports `--summary`
- `codex-multi-agent-template/AGENTS.md` now has clearer role output, ownership, and handoff rules

### Notes

- For change-recording guidance, see `docs/release-change-guidance.md`.
