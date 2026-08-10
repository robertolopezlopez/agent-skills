---
name: cli-ci-monitor
description: >-
  Monitor a CLI CircleCI workflow for up to two hours. Use when asked to watch or babysit a
  workflow and automatically cancel and rerun from failed jobs only for confirmed CircleCI
  timeouts or infrastructure failures.
---

# CLI CI Monitor

Monitor one workflow lineage. Use `circleci` for transport; keep retry judgment here.

## When to Use

- Watch a CLI CircleCI workflow until success or timeout.
- Automatically retry confirmed environment failures.

## When Not to Use

- For one status lookup, use `circleci`.
- For local tests, use `cli-parallel-tests`.
- Never retry code or ambiguous failures.

## Inputs

- Workflow ID or any CircleCI URL containing `workflowId`.
- Defaults: 2-hour shared deadline and 60-second polling. Never reset deadline after reruns.
- Monitor-and-retry requests authorize cancel/rerun below; monitor-only requests remain read-only.

## First Read

- Read CLI repository `AGENTS.md`.
- Load `circleci`; follow its prerequisites, helper transport, and secret rules.

## Workflow

1. Record start, deadline, workflow ID, and attempt `1`. Resolve `workflowId` directly from URLs.
2. Check CircleCI authentication. Stop on auth failure. Fetch `GET /workflow/{id}` and paginated `GET /workflow/{id}/job`.
3. Poll with the runtime wait mechanism, never blocking over 60 seconds. Report transitions, retry decisions, and remaining time.
4. Handle status:
   - `success`: finish.
   - `running`, `queued`: poll.
   - `on_hold`: poll; never approve.
   - `failing`: classify completed failed jobs.
   - `failed`, `error`: classify all failed jobs.
   - `unauthorized`: stop.
   - `canceled`: continue only when this monitor canceled it for retry; otherwise stop.
5. Classify conservatively from full job details. For `gh/org/repo`, use v1.1 `/project/gh/org/repo/{job-number}` when needed for structured fields. Environment evidence is any of:
   - `status` or `outcome` is `timedout` or `infrastructure_fail`
   - `timedout: true` or `infrastructure_fail: true`
   - explicit CircleCI platform output for runtime/no-output timeout, missing heartbeat, executor startup failure, or runner loss
6. Classify ordinary nonzero exits, tests, lint, compile, dependency, or project configuration errors as code failures. Missing or conflicting evidence is ambiguous. Ignore downstream `canceled` or `not_run` jobs.
7. Retry only with at least one environment failure and no code or ambiguous failure. Otherwise stop with evidence; suggest `cli-technical-analysis` for code failures.
8. Recheck deadline. If workflow is non-terminal, `POST /workflow/{id}/cancel` and wait for `canceled`. Then `POST /workflow/{id}/rerun` using resolved `assets/rerun-from-failed.json`; require returned `workflow_id`, increment attempt, and resume step 2 without resetting deadline.
9. At deadline, stop without canceling a running workflow unless separately requested.

## Validation

- Never rerun before terminal state or after deadline.
- Follow returned `workflow_id`, not completed source workflow.
- Keep an in-memory timeline of IDs, statuses, evidence, and mutations.

## Outputs / Artifacts

Return final status, elapsed time, attempt count, workflow IDs, retry evidence/actions, and current workflow when unfinished. Create no artifact by default.

## Companion Skills

- `circleci` for transport
- `cli-technical-analysis` for code failures

## Safety Notes

- Never expose tokens or read defaults files.
- Never use raw `curl`.
- Never retry code/ambiguous failures, approve holds, change parameters, or trigger a fresh pipeline.
- Limit mutations to supplied workflow lineage.
