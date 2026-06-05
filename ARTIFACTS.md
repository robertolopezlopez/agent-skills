# Artifact Schema

This repository uses a shared Markdown schema for locally bootstrapped workflow artifacts.

## Goals

- keep Jira, GitLab, GitHub, and follow-on analysis artifacts easy to read
- make downstream skills reuse existing context instead of rebuilding it
- standardize headings, ordering, and file naming without changing skill-specific behavior
- keep durable agent context **outside** project git checkouts so `git clean` and accidental commits do not destroy or ship working notes

## Artifact store location

The external store has **two scopes**:

1. **`$GLOBAL/`** — cross-repository knowledge (org maps, team ownership, company-wide tooling). Same on every machine regardless of which checkout is active.
2. **`$ARTIFACTS/`** — repository-scoped work (tickets, MR/PR analysis, repo-specific CI quirks).

**Default layout:**

```text
$AGENT_ARTIFACTS_HOME/_global/NEXT_TIME_CHECKS.md
$AGENT_ARTIFACTS_HOME/_global/<meaningful_id>/<basename>.md
$AGENT_ARTIFACTS_HOME/<repo-key>/NEXT_TIME_CHECKS.md
$AGENT_ARTIFACTS_HOME/<repo-key>/<meaningful_id>/<basename>.md
```

Shorthand used in skills:

- **`$GLOBAL/`** means **`$AGENT_ARTIFACTS_HOME/_global/`**
- **`$ARTIFACTS/`** means **`$AGENT_ARTIFACTS_HOME/<repo-key>/`** for the active repository

### Scope decision (writes)

| Content | Scope | Example |
| --- | --- | --- |
| Ticket / PR / MR session work | `$ARTIFACTS/` | `mr-1447/review_mr_1447.md` |
| Repo-specific CI, layout, validation quirks | `$ARTIFACTS/NEXT_TIME_CHECKS.md` | “run `make test` before push in this repo” |
| Org structure, team ownership, internal URLs | `$GLOBAL/<topic>/` | Snyk repo → team mapping |
| Lessons that apply in **any** checkout | `$GLOBAL/NEXT_TIME_CHECKS.md` | “refresh expired `ATLASSIAN_API_TOKEN`” |

When unsure: if the fact would still be true after `cd` into a different repository, use **`$GLOBAL/`**.

### User phrase: "the artifacts directory"

When the user says **"the artifacts directory"** (or similar: "artifact path", "save to artifacts", "write the analysis md"):

1. Resolve **`$ARTIFACTS/<meaningful_id>/`** for the active ticket, PR, MR, or branch — not in-repo **`_artifacts_/`** unless they explicitly ask for that.
2. Use **`$GLOBAL/<topic>/`** for cross-repo reference material.
3. When the repo or **`meaningful_id`** is unclear, resolve paths with **`scripts/resolve_artifact_path.py`** (installed under each skills root after sync).
4. Read existing files in the target folder before creating duplicates; extend in place when an analysis or review artifact already exists.

**Cursor:** optional always-on rule from **`templates/cursor/rules/agent-artifacts-directory.mdc`**, installed with **`scripts/bootstrap_agent_artifacts.sh --cursor-rule`**.

**Codex:** same semantics live in repo and project **`AGENTS.md`** (no `.mdc` format).

Store index at **`$AGENT_ARTIFACTS_HOME/README.md`**, bootstrapped from **`templates/agent-artifacts/README.md`**.

### Defaults and overrides

Resolve **`AGENT_ARTIFACTS_HOME`** in this order:

1. exported environment variable **`AGENT_ARTIFACTS_HOME`**
2. **`~/.cursor/agent-artifacts`** when **`~/.cursor`** exists
3. **`~/.codex/agent-artifacts`**

Resolve **`<repo-key>`** in this order:

1. **`git remote get-url origin`** → sanitized host/org/repo (e.g. `github.com-snyk-cli`)
2. else sanitized basename of the repository root directory

Helper (installed next to other shared scripts under each skills root). Examples use the Cursor path; on Codex replace with **`~/.codex/skills/scripts/`**:

```bash
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --global-artifacts-root
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --global-next-time-checks
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --scope global --meaningful-id snyk-repo-ownership --basename repo-snyk-docker-registry-v2-client.md
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --repo-artifacts-root
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --next-time-checks
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --meaningful-id mr-1447 --basename review_mr_1447.md
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --find-existing --meaningful-id mr-1447 --basename review_mr_1447.md
```

Pass **`--repo-root`** when the working directory is not the target repository.

### Migrating legacy in-repo `_artifacts_/`

Copy existing in-repo trees into the external store with the shared helper (synced to each skills install root):

```bash
python3 ~/.cursor/skills/scripts/migrate_legacy_artifacts.py --search-root ~/go --search-root ~/workspace --dry-run
python3 ~/.cursor/skills/scripts/migrate_legacy_artifacts.py --search-root ~/go --search-root ~/workspace --remove-source
```

The script resolves **`$ARTIFACTS/`** per repository, skips files that already exist in the external store, and optionally deletes the legacy **`_artifacts_/`** tree after copy.

### Path precedence (writes)

1. **Explicit user instruction** — absolute or relative paths always win for that run.
2. **Repo `AGENTS.md` or project rules** — may pin a canonical pattern.
3. **External store** — **`$ARTIFACTS/<meaningful_id>/`** (preferred for **new** files).
4. **Legacy in-repo** — **`_artifacts_/<meaningful_id>/`** at the repository root only when the user or repo rules opt in, or when extending files that already live there.

### Path precedence (reads)

When opening existing context, check in this order:

1. explicit user path
2. **`$GLOBAL/<meaningful_id>/`** when the topic is cross-repo
3. **`$ARTIFACTS/<meaningful_id>/`**
4. legacy **`_artifacts_/<meaningful_id>/`** under the repository root
5. legacy repo-root filenames (e.g. `review_mr_<iid>.md`) when already in use

Prefer **non-destructive migration**: read legacy paths, write new material to **`$ARTIFACTS/`** unless the user keeps using the old location.

### Why external storage

- survives **`git clean -fdx`** and similar cleanup in the project checkout
- avoids accidental **`git add`** / push of follow-ups, work plans, and acquired knowledge
- keeps ticket-scoped notes portable across clones of the same repository

## Canonical Core Sections

Bootstrapped task or review artifacts should keep this core order when present:

1. `# Task`
2. `## Summary`
3. `## Type`
4. `## Repository`
5. `## Context Links`
6. `## Selected Skills`
7. `## Defaults Files`
8. `## Assumptions`
9. `## Initial Plan`
10. `## Validation Plan`
11. `## Open Questions`
12. domain-specific details section, such as:
    - `## Jira Details`
    - `## GitLab Details`
    - `## GitHub Details`
13. `## Description`
14. `## Actionable Context`

Downstream workflow files may add extra sections after these, but they should preserve the core sections above when they bootstrap or enrich the same artifact.

## Artifact directories

Prefer writing **new** artifacts under **`$ARTIFACTS/`**:

```text
$ARTIFACTS/<meaningful_id>/<basename>.md
```

Portable cross-ticket lessons belong in:

- **`$GLOBAL/NEXT_TIME_CHECKS.md`** when they apply in any repository (see **`learn-daily`**)
- **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** when they apply only to the active repository

### `meaningful_id`

Pick a compact, filesystem-safe label so parallel work separates cleanly:

1. **Tracker key first** — e.g. `CLI-123`, `GOV-456`.
2. **Else PR / MR shorthand** — e.g. `pr-336`, `mr-1447`.
3. **Else** a sanitized slug from the git branch (`feature/foo-bar` → `feature-foo-bar`) or a topic slug the user provides.

Use the **same `meaningful_id` for every file** belonging to one ticket/session when possible.

### Precedence

Resolution order for **new writes**:

1. **Explicit user instruction** — absolute or relative paths always win for that run.
2. **Repo `AGENTS.md` or project rules** — may pin a canonical pattern (always use Jira keys, hyphen rules, prefix per team).
3. **External `$ARTIFACTS/`** — default for new bootstrap and analysis sessions.
4. **Heuristic** — tracker key → PR/MR id → branch/topic slug as above.

### Backward compatibility

- Existing artifacts **at repo root**, under in-repo **`_artifacts_/`**, or elsewhere remain valid. Open and extend them instead of relocating unless the user asks to migrate.
- **New bootstrap or analysis sessions** prefer **`$ARTIFACTS/<meaningful_id>/`** so generated files cluster outside the git checkout.

### Git hygiene

- Do **not** rely on in-repo **`_artifacts_/`** for durable agent context; it is **legacy** and vulnerable to **`git clean`** even when gitignored.
- Teams that still use in-repo **`_artifacts_/`** should gitignore it and treat accidental tracking as a process bug—not the default contract.

## Naming

**Basenames** (under **`$ARTIFACTS/<meaningful_id>/`**):

- Jira issue bootstrap: `task_<issue>.md`
- GitLab MR review bootstrap: `review_mr_<iid>.md`
- GitLab MR investigation bootstrap: `analysis_mr_<iid>.md`
- GitHub PR review bootstrap: `review_pr_<number>.md`
- GitHub PR investigation bootstrap: `analysis_pr_<number>.md`
- Repository / branch investigations: existing patterns such as `analysis_<relevant_name>.md` or `review_<sanitized-branch>.md` — place them under **`$ARTIFACTS/<meaningful_id>/`** unless the artifact already exists elsewhere
- Informal working drafts: `fix_draft_<topic>.md` (same folder; not validated by default)

Equivalent paths at repo root or under in-repo **`_artifacts_/`** are still tolerated for legacy workflows; **`$ARTIFACTS/...`** remains the preference for newly created files.

Full examples (external store; home and repo-key vary by machine):

- `$AGENT_ARTIFACTS_HOME/README.md` (store index; see **`scripts/bootstrap_agent_artifacts.sh`**)
- `$GLOBAL/snyk-repo-ownership/repo-snyk-docker-registry-v2-client.md`
- `$GLOBAL/NEXT_TIME_CHECKS.md`
- `$ARTIFACTS/github.com-snyk-cli/CLI-123/task_CLI-123.md`
- `$ARTIFACTS/mr-1447/review_mr_1447.md`
- `$ARTIFACTS/pr-336/review_pr_336.md`
- `$ARTIFACTS/feature-auth-guard/review_feature-auth-guard.md` (branch-based branch review layouts)
- `$ARTIFACTS/NEXT_TIME_CHECKS.md`

**Grouped MR/PR comment analysis** lives **inside** the corresponding review or analysis artifact under:

- `## Grouped unresolved comments`
- stable subsections `### issue_01`, `### issue_02`, …

Legacy split filenames (older workflows) may still appear in checkouts and validators:

- `work_plan_mr_<iid>.md`, `analysis_mr_<iid>_issue_<nn>.md`, `mr_<iid>_comment_report.md`
- `work_plan_pr_<number>.md`, `analysis_pr_<number>_issue_<nn>.md`, `pr_<number>_comment_report.md`

Prefer merging durable content from legacy files into the main artifact, then deleting the splits once merged.

## Content Rules

- Keep artifacts local-only unless the user explicitly asks to publish or copy them elsewhere.
- Prefer concise bullets over long prose.
- Keep links canonical and direct when possible.
- Use live Jira/GitLab/GitHub data as source of truth when refreshing artifact contents.
- Treat the artifact as durable working context, not as authority over remote state.
- Never store secrets in artifacts; reference **where** to load credentials.

## Skill Responsibilities

- `learn-daily` reads **`$GLOBAL/NEXT_TIME_CHECKS.md`** and **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**, writes cross-repo reference material under **`$GLOBAL/<meaningful_id>/`**, and ticket folders under **`$ARTIFACTS/<meaningful_id>/`**
- `jira` bootstraps `task_<issue>.md` under **`$ARTIFACTS/<meaningful_id>/`** (`meaningful_id` defaults to issue key unless overridden)
- `gitlab` bootstraps `review_mr_<iid>.md` or `analysis_mr_<iid>.md` under **`$ARTIFACTS/<meaningful_id>/`** (`meaningful_id` defaults sensibly — e.g. `mr-<iid>` unless the repo dictates otherwise)
- `gitlab-mr-comment-analysis` refreshes live MR state and writes grouped unresolved threads **into** the main MR Markdown file (typically **`$ARTIFACTS/…/review_mr_<iid>.md`** or **`$ARTIFACTS/…/analysis_mr_<iid>.md`**) inside `## Grouped unresolved comments`
- `github` prepares normalized PR context; bootstrap filenames such as `review_pr_<number>.md` follow this schema when written locally, defaulting beneath **`$ARTIFACTS/<meaningful_id>/`** for new artifacts
- `github-pr-comment-analysis` refreshes live PR state and writes grouped unresolved threads **into** the canonical PR Markdown file (typically **`$ARTIFACTS/…/review_pr_<number>.md`** or **`$ARTIFACTS/…/analysis_pr_<number>.md`**) under the same subsection contract
- repository-specific overlay skills should reuse these artifacts when possible instead of recreating context
