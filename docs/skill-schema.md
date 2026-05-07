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

## Validation guidance

- Hard-fail only on breakage or missing minimum contract.
- Prefer warnings for missing recommended sections during migration.
- Expand strictness gradually after core skills are normalized.

## Migration guidance

- Do not rewrite every skill at once.
- Normalize highest-value reusable skills first.
- Preserve working behavior while improving section clarity.
- Move repeated repo-wide policy into `AGENTS.md` instead of duplicating it across many skills.
