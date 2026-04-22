# Release and Change Guidance

This document describes how to record notable repository changes for skills, shared tooling, and artifact schemas.

The goal is lightweight release hygiene, not heavyweight release process.

## Record changes when they are likely to affect downstream users

Write down changes when they affect:

- installed skill names or paths
- expected `SKILL.md` structure
- shared helper locations
- artifact schemas or naming
- sync or validation behavior
- default workflow assumptions used across multiple skills

## Types of changes to note

### Breaking changes

Record changes that may break existing usage, including:

- renamed skill directories
- removed skills
- renamed shared helper scripts
- changed artifact filename patterns
- changed required `SKILL.md` contract fields
- changed output contracts consumed by companion skills

For breaking changes, include:

- what changed
- who is affected
- what must be updated
- whether a migration path exists

### Behavior changes

Record changes that alter default behavior without fully breaking usage, including:

- new validation rules
- changed sync defaults
- changed workflow ordering
- new required prerequisites
- more restrictive safety behavior

### Documentation or guidance changes

Record major doc-level changes when they change how contributors are expected to work, such as:

- new schema guidance
- new workflow templates
- new repo-wide policy

## Where to record changes

Use lightweight location choices:

- commit messages for small isolated changes
- `docs/` reference docs for durable workflow guidance
- task or analysis artifacts only for local working context, not long-term repo guidance

If a change is durable and repository-wide, prefer a checked-in doc in `docs/`.

## Changelog policy

Use `CHANGELOG.md` for:

- breaking changes
- workflow-level repository changes
- notable tooling or manifest behavior changes that contributors should know about

Do not use `CHANGELOG.md` for:

- every small skill wording tweak
- routine cleanup or refactors
- minor doc phrasing changes
- implementation details already covered well by commit history

## Suggested changelog entry shape

Use a short format like:

```text
Change: <short title>
Type: breaking | behavior | docs
Affected: <skills, scripts, or artifacts>
Action: <what contributors or downstream users should do>
```

## Skill rename guidance

When renaming a skill:

1. rename the top-level directory
2. update `SKILL.md` frontmatter `name`
3. update `skills_manifest.yaml`
4. update references in companion skills and docs
5. note the rename as a breaking change
6. sync installed skills and remove the old installed copy if needed

## Artifact schema change guidance

When changing artifact schema or naming:

1. update `ARTIFACTS.md`
2. update `scripts/validate_artifact.py`
3. update any affected skills that bootstrap or enrich those artifacts
4. note whether existing artifacts need migration or only future artifacts use the new rules

## Shared tooling change guidance

When changing shared tooling such as sync, validation, hooks, or manifest behavior:

1. update the relevant script or template
2. update docs when contributor expectations change
3. note behavior changes when users may rely on old defaults
4. resync installed copies when skill-distributed helpers changed

## Current release hygiene stance

- prefer lightweight notes over heavy release ceremony
- be explicit about breaking changes
- keep local work logs untracked unless they become durable repo docs
- prefer stable docs in `docs/` for repository-wide guidance
