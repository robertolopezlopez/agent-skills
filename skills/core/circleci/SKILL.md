---
name: circleci
description: Fetch CircleCI pipelines, workflows, jobs, artifacts, or tests from slugs, IDs, numbers, or URLs; perform requested actions and auth diagnosis using local `circleci`/`circleci-request` before MCP.
---

# CircleCI Access

Use this transport skill for structured CircleCI state. Leave failure diagnosis and monitoring policy to companion skills.

## When to Use

Use for pipeline/workflow/job lookup, project pipeline lists, metadata pointers, explicitly requested API actions, or token diagnosis.

## When Not to Use

Use `cli-ci-monitor` for long-running CLI workflow monitoring and repository analysis skills for code-level failures.

## Inputs

- Project slug (`gh/org/repo` or documented GitHub App/GitLab form).
- Pipeline/workflow UUID, pipeline/job number, or CircleCI URL.
- Optional API root override for CircleCI Server.

Infer GitHub slugs from `GIT-ACCESS.md` identity only when unambiguous; otherwise ask.

## Workflow

1. Read repository `AGENTS.md` when working from a checkout.
2. Run `scripts/check_skill_prereqs.sh circleci` and `scripts/check_skill_config.sh circleci`; help configure `CIRCLE_TOKEN`/`CIRCLECI_TOKEN` before calls.
3. Use the local `circleci` CLI when it directly supports the operation. Otherwise resolve `scripts/circleci-request` relative to this skill.
4. Run each helper request as a standalone command so approval prefixes remain reusable. Fetch the smallest endpoint chain needed and parse responses separately.
5. Normalize project slug, pipeline ID/number, workflow IDs/statuses, job numbers/statuses, and useful URLs.
6. Use CircleCI MCP only when local tools cannot supply the required data; keep the same output contract.
7. Read [references/commands.md](references/commands.md) only when exact helper syntax, endpoint shapes, runtime config precedence, or write examples are needed.

## Validation

- Stop clearly on missing/invalid auth; never expose tokens.
- Use live API state rather than cached status.
- Keep helper calls direct and route HTTP through `circleci-request`, never raw `curl`.
- For uncertain endpoint semantics, consult the runtime API cache under `circleci-api-v2` per `AGENTS.md`.

## Outputs / Artifacts

Return normalized identifiers, states, VCS metadata, URLs, and concise auth errors. Create no artifact by default.

## Companion Skills

Use `cli-ci-monitor` for CLI workflow lineages and `repository-technical-analysis` or `diagnose` for failures.

## Safety Notes

- Read-only by default. Confirm or rely on explicit user authorization before trigger, rerun, cancel, approve, or context-secret operations.
- Do not read defaults files directly; helpers resolve the active runtime.
- Never approve holds or disclose credentials.
