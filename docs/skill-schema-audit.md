# Skill Schema Audit

This document records the first normalization pass after introducing the shared skill schema in `docs/skill-schema.md`.

It is an audit and migration snapshot, not a local work log.

## Purpose

- explain which skills were normalized first
- record the main schema gaps still present in the repository
- document the current migration stance for validator behavior
- identify the next highest-value normalization targets

## Context

Relevant files:

- `AGENTS.md`
- `docs/skill-schema.md`
- `scripts/validate_skill.py`
- `scripts/validate_repo.sh`

## Audit summary

Strong current baseline:

- all top-level skills satisfy the minimum repo contract
- repo-wide validation and sync tooling exists
- schema guidance now exists in checked-in docs

Main schema gaps still visible across the repo:

- several skills do not explicitly separate `When to Use` from operational details
- some central skills still lack explicit `When Not to Use`
- output and artifact expectations remain inconsistent
- companion-skill boundaries are sometimes implied instead of stated

## Priority normalization targets for the first batch

### `gitlab`

Why it was selected first:

- central transport skill
- widely reused by follow-on MR workflows
- benefits from clearer companion-skill boundaries

### `jira`

Why it was selected first:

- central transport skill
- long workflow with multiple helper paths and fallback modes
- benefits from explicit output and safety framing

### `repository-technical-analysis`

Why it was selected first:

- foundational investigation workflow
- reused across repositories
- benefits from clearer trigger and output sections

## Result of the first normalization batch

Normalized in this batch:

- `gitlab`
- `jira`
- `repository-technical-analysis`

Changes made in that batch:

- added clearer trigger boundaries
- added or clarified output and artifact expectations
- made companion-skill layering more explicit
- added safety-oriented framing where missing
- expanded the validator to report recommended-section drift as warnings instead of hard failures

## Follow-on candidates

Next strong candidates for normalization:

- `gitlab-mr-comment-analysis`
- `multi-spawn-agent`
- `python-fastapi-contributor`
- `private-service-contributor`

## Migration stance

- keep hard failures for minimum contract violations
- keep recommended-section gaps as warnings during migration
- normalize central reusable skills before pushing schema expectations into repo overlays
- avoid rewriting every skill at once when a targeted pass gives better value with lower churn

## Open questions

- Should `When Not to Use` become required for all skills or only central reusable skills?
- Should warnings later become hard failures for new skills only?
- Should repo overlay skills use a lighter recommended structure than transport skills?
