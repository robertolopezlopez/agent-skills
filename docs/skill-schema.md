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
- `jira`
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

### Literal code search (`LITERAL-CODE-SEARCH.md`)

Literal search for the **current directory tree** is portable policy in synced **`LITERAL-CODE-SEARCH.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --literal-search-policy`**). Helpers sync to **`agent_config.py --literal-search-dir`**. Read **`fast-grep.env`** after first discover; speed-ordered host CLIs; **OS-appropriate** install offers via **`install-cmd.sh`** / **`check_skill_prereqs.sh literal-search`** (never Homebrew-only); ask-before-install; **agent Grep tool** as last literal resort. **SemanticSearch** is separate (behavioral queries only). Cursor may install an optional always-on rule via **`bootstrap_literal_search.sh --cursor-rule`**; Codex and other agents use the synced doc + skills.

| Skill type | Wire literal search? | How |
|------------|----------------------|-----|
| **Transport** (`jira`, `confluence`, `gitlab`, `github`, `git`, `circleci`) | No | Remote fetch only; when code search is needed, hand off to investigation or contributor companions. |
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
