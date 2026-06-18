# Skill Schema

This document defines the recommended structure for `SKILL.md` files in this repository.

The goals are:
- keep skills easy to scan
- keep auto-use behavior predictable
- separate required minimum contract from recommended structure
- make future validation stricter without breaking useful legacy skills abruptly

## Minimum required contract

Every top-level skill directory must include:
- `SKILL.md`
- YAML frontmatter
- `name`
- `description`
- one primary heading beginning with `# `
- enough operational content to use the skill correctly

Every skill should include at least one operational section:
- `## Workflow`
- `## First Read`
- `## Inputs`
- or `## Input`

## Recommended section order

Use this order when practical:

1. YAML frontmatter
2. `# <Skill Name>`
3. short purpose statement
4. `## When to Use`
5. `## When Not to Use`
6. `## Inputs`
7. `## First Read` when needed
8. `## Workflow`
9. `## Validation`
10. `## Outputs` or `## Outputs / Artifacts`
11. `## Companion Skills`
12. `## Safety Notes` or `## Constraints`
13. optional deeper sections such as transport details, examples, or self-improving behavior

Not every skill needs every section, but central reusable skills should aim for this structure.

## Section intent

### `## When to Use`
Say what request shapes should trigger the skill.

### `## When Not to Use`
Prevent overlap with nearby skills.

### `## Inputs`
State accepted input forms and defaults.

### `## First Read`
List required local docs, upstream skills, or preconditions to inspect before acting.

### `## Workflow`
State the default operating sequence.

### `## Validation`
List commands, checks, or evidence expectations.

### `## Outputs`
State what the skill returns, writes, or preserves.

### `## Companion Skills`
Describe layering such as:
- transport skill
- workflow skill
- repo overlay skill

### `## Safety Notes`
Record important limits, non-goals, or stop conditions.

## Preferred architecture patterns

### Transport skill
Responsible for:
- fetching remote data
- resolving identity
- normalizing links and transport-specific fields

Examples:
- `gitlab`
- **`JIRA-ACCESS.md`** (Jira; installable **`jira`** skill removed in Phase C)
- `confluence`

### Workflow skill
Responsible for:
- grouping
- planning
- reporting
- follow-on decisions

Examples:
- `gitlab-mr-comment-analysis`

### Repo overlay skill
Responsible for:
- repo-local commands
- repo-local constraints
- project-specific defaults

Examples:
- `private-service-*`

### GitHub access (`GITHUB-ACCESS.md`)

GitHub issue and PR fetch is portable policy in synced **`GITHUB-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --github-access-policy`**). Transport: **`GIT-ACCESS.md`** (identity when needed) → **`gh`** → **`gh api`** → GitHub MCP (last). Prereqs: **`check_skill_prereqs.sh github`** (alias **`github-access`**); auth: **`check_skill_config.sh github`**. The installable **`github`** skill was removed in Phase C; transport is policy + helpers only.

| Skill type | Wire GitHub transport? | How |
|------------|------------------------|-----|
| **Transport** (`jira`, `confluence`, `gitlab`, `circleci`) | No | Use **`GITHUB-ACCESS.md`** for GitHub fetch; **`JIRA-ACCESS.md`** for Jira; identity via **`GIT-ACCESS.md`**; do not duplicate **`gh`** / **`acli`** logic. |
| **GitHub workflow** (`github-pr-comment-analysis`, `github-issue-triage`, `private-pr-comment-analysis`) | Yes — consumer | Read **`GITHUB-ACCESS.md`**; refresh via **`gh`**. |
| **Investigation / contributor / planning** | Pointer only | One line to **`GITHUB-ACCESS.md`** when task starts from a GitHub URL or issue. |

**Manifest rule:** do **not** add **`github`** under `companion_skills` for new or updated skills. Policy lives in synced **`GITHUB-ACCESS.md`**; helpers in **`agent_config.py --github-scripts-dir`**.

### Jira access (`JIRA-ACCESS.md`)

Jira Cloud issue fetch and update is portable policy in synced **`JIRA-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --jira-access-policy`**). Transport: **`acli jira workitem …`** → **`jira-request`** → **`jira-api`** → Jira MCP (last). Prereqs: **`check_skill_prereqs.sh jira`** (alias **`jira-access`**); auth: **`check_skill_config.sh jira`** → **`acli jira auth status`**. The installable **`jira`** skill was removed in Phase C; transport is policy + **`acli`** + synced helpers only.

| Skill type | Wire Jira transport? | How |
|------------|---------------------|-----|
| **Transport** (`confluence`, `gitlab`, `circleci`) | No | Use **`JIRA-ACCESS.md`** for Jira fetch; do not duplicate **`acli`** logic. |
| **Planning / investigation** | Pointer only | One line to **`JIRA-ACCESS.md`** when task starts from a Jira URL or issue key. |

**Manifest rule:** do **not** add **`jira`** under `companion_skills` for new or updated skills. Policy lives in synced **`JIRA-ACCESS.md`**; helpers in **`agent_config.py --jira-scripts-dir`** (Phase B).

### Git repository identity (`GIT-ACCESS.md`)

Local remote identity resolution is portable policy in synced **`GIT-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --git-access-policy`**). Helpers sync to **`agent_config.py --git-scripts-dir`**. Prereqs: **`check_skill_prereqs.sh git-access`** (git binary); GitLab numeric ID: **`check_skill_prereqs.sh gitlab`**. The installable **`git`** skill was removed in Phase C.

| Skill type | Wire git identity? | How |
|------------|-------------------|-----|
| **Transport** (`jira`, `confluence`, `gitlab`, `circleci`) | Consumer when needed | Read **`GIT-ACCESS.md`**; run **`git-repo-identity`**. |
| **GitHub workflow** | Pointer only | Host check via **`GIT-ACCESS.md`**; fetch via **`GITHUB-ACCESS.md`**. |
| **Investigation / contributor** | No | Raw **`git`** CLI for branch/diff only. |

**Manifest rule:** do **not** add **`git`** under `companion_skills` for new or updated skills. Policy lives in synced **`GIT-ACCESS.md`**; helpers in **`agent_config.py --git-scripts-dir`**.

### Literal code search (`LITERAL-CODE-SEARCH.md`)

Literal search for the **current directory tree** is portable policy in synced **`LITERAL-CODE-SEARCH.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --literal-search-policy`**). Helpers sync to **`agent_config.py --literal-search-dir`**. Read **`fast-grep.env`** after first discover; speed-ordered host CLIs; **OS-appropriate** install offers via **`install-cmd.sh`** / **`check_skill_prereqs.sh literal-search`** (never Homebrew-only); ask-before-install; **agent Grep tool** as last literal resort. **SemanticSearch** is separate (behavioral queries only). Cursor may install an optional always-on rule via **`bootstrap_literal_search.sh --cursor-rule`**; Codex and other agents use the synced doc + skills.

| Skill type | Wire literal search? | How |
|------------|----------------------|-----|
| **Transport** (`jira`, `confluence`, `gitlab`, `circleci`) | No | Remote fetch only; GitHub via **`GITHUB-ACCESS.md`**; identity via **`GIT-ACCESS.md`**; code search via investigation companions. |
| **Investigation hub** (`repository-technical-analysis`) | Yes — owner | Workflow step 3 holds the full procedure. No manifest `companion_skills` entry for search. |
| **Investigation overlay** (`private-technical-analysis`, `private-service-technical-analysis`, …) | Inherit | Load `repository-technical-analysis`; one line in **First Read** pointing to RTA step 3 / **`LITERAL-CODE-SEARCH.md`**. Do not duplicate the full search workflow. |
| **Debugging** (`diagnose`) | Inherit + pointer | **First Read** one-liner to **`LITERAL-CODE-SEARCH.md`**; manifest pairs **`repository-technical-analysis`**. |
| **Implementation / contributor** (`python-fastapi-contributor`, `private-contributor`, …) | Pointer only | **First Read** one-liner to **`LITERAL-CODE-SEARCH.md`**. Repo overlays inherit via parent contributor or RTA — no extra search prose. |
| **TDD** (`tdd`) | Pointer only | **First Read** one-liner; manifest chains through `python-fastapi-contributor` or `repository-technical-analysis`. |
| **Branch review / rebase** (`branch-change-reviewer`, `git-rebase-conflict-resolver`) | Pointer only | When diff alone is insufficient (call sites, rename fallout, conflict intent). |
| **Comment-analysis workflow** (`github-pr-comment-analysis`, `gitlab-mr-comment-analysis`, `private-pr-comment-analysis`, …) | Inherit | Transport + grouping here; fixes use contributor / RTA chains that already carry literal search policy. |
| **Planning / meta** (`plan-issues`, `learn-daily`, `multi-spawn-agent`) | No | No routine codebase literal search. |

**Manifest rule:** do **not** add a literal-search skill under `companion_skills`. Policy lives in synced **`LITERAL-CODE-SEARCH.md`** + **`agent_config.py --literal-search-dir`** helpers.

**SKILL.md rule:** at most **one** short **First Read** bullet *or* **Companion Skills** line per skill — never both. Link to synced **`LITERAL-CODE-SEARCH.md`** or RTA step 3; do not copy install order, tool chain, or helper flags.

**Single owner:** `repository-technical-analysis` workflow step 3 and **`LITERAL-CODE-SEARCH.md`** hold the full search procedure. Overlays and contributors inherit via `repository-technical-analysis` or a one-line pointer; do not restate step 3 in overlay **First Read** lines.

**Prereqs:** `scripts/check_skill_prereqs.sh literal-search` (alias: `fast-grep`) is the search-tool audit; `investigate` / `repository-technical-analysis` / `diagnose` defer to it. OS install commands: **`scripts/literal-search/install-cmd.sh`** (not duplicated in consumer skills).

## Validation guidance

- Hard-fail only on breakage or missing minimum contract.
- Prefer warnings for missing recommended sections during migration.
- Expand strictness gradually after core skills are normalized.

## Migration guidance

- Do not rewrite every skill at once.
- Normalize highest-value reusable skills first.
- Preserve working behavior while improving section clarity.
- Move repeated repo-wide policy into `AGENTS.md` instead of duplicating it across many skills.
