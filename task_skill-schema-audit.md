# Task

## Summary
- Audit current `SKILL.md` files against the new repo skill schema and identify the highest-value normalization targets.

## Type
- Repository hardening
- Documentation
- Audit

## Repository
- `agent-skills`
- Path: `/Users/rlopezlopez/workspace/agent-skills`

## Context Links
- Repo policy: `AGENTS.md`
- Skill schema: `docs/skill-schema.md`
- Skill validator: `scripts/validate_skill.py`
- Repo validator: `scripts/validate_repo.sh`
- Hardening task: `task_repo-hardening.md`

## Selected Skills
- `repository-technical-analysis`

## Defaults Files
- `AGENTS.md`
- `ARTIFACTS.md`

## Assumptions
- Current skills are functional but not yet fully standardized.
- Central reusable skills should be normalized before repo-specific overlays.
- Recommended schema gaps should warn during migration, not fail hard by default.

## Initial Plan
1. Define the canonical skill schema document.
2. Compare current top-level skills against the recommended sections.
3. Normalize the highest-value reusable skills first.
4. Expand the validator to surface schema drift as warnings.

## Validation Plan
- Run `./scripts/validate_repo.sh`
- Run `python3 scripts/validate_artifact.py task_skill-schema-audit.md`

## Open Questions
- Should `When Not to Use` become required for all skills or only central reusable skills?
- Should warnings later become hard failures for new skills only?
- Should repo overlay skills have a lighter schema than transport skills?

## Jira Details
- None

## Description
- This audit captures the current normalization state after introducing a canonical skill schema.
- It focuses on high-value reusable skills first instead of forcing a full repo rewrite.

## Actionable Context

### Audit summary
- Strong current baseline:
  - all top-level skills already satisfy the minimum repo contract
  - repo-wide validation and sync tooling now exists
- Main schema gaps:
  - several skills do not explicitly separate `When to Use` from operational details
  - some central skills lack explicit `When Not to Use`
  - output/artifact expectations are inconsistent across skills
  - companion-skill boundaries are often implied rather than explicit

### Priority normalization targets
1. `gitlab`
   - central transport skill
   - widely reused
   - benefits from clearer companion-skill boundaries
2. `jira`
   - central transport skill
   - long workflow
   - benefits from explicit output/safety framing
3. `repository-technical-analysis`
   - foundational investigation workflow
   - benefits from clearer trigger and output sections

### Result of this batch
- `gitlab` normalized: added clearer trigger boundaries, outputs, companion skills, and safety notes.
- `jira` normalized: added explicit use boundaries, inputs, validation, outputs, companion skills, and safety notes.
- `repository-technical-analysis` normalized: added explicit trigger boundaries, outputs, companion skills, and safety notes.
- validator expanded to report recommended-section drift as warnings instead of hard failures.

### Follow-on candidates
- `gitlab-mr-comment-analysis`
- `multi-spawn-agent`
- `python-fastapi-contributor`
- `private-service-contributor`

### Migration stance
- Keep hard failures for minimum contract violations.
- Keep recommended-section gaps as warnings until more central skills are normalized.
