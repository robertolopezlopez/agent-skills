---
name: cli-ci-monitor
description: Monitor or babysit a CLI CircleCI workflow for up to two hours, automatically canceling and rerunning confirmed infrastructure failures or high-confidence transient errors.
---

# CLI CI Monitor

Monitor one workflow lineage through the bundled deterministic runner.

## When to Use

- Watch a CLI CircleCI workflow until success or timeout.
- Automatically retry confirmed environment failures and high-confidence transient errors.

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

1. Resolve `scripts/monitor_workflow.py` relative to this skill.
2. For monitor-only requests run:

   ```bash
   scripts/monitor_workflow.py '<workflow-id-or-url>'
   ```

3. Only when the user authorized monitor-and-retry, add `--retry-infra`. The runner uses one two-hour deadline, polls every 60 seconds, paginates jobs, follows rerun workflow IDs, and retries only structured `timedout`/`infrastructure_fail` results or narrow transient signatures in failed action output (such as a Jest test timeout or temporary network reset), with no code or ambiguous failures.
4. Report transition lines and the final JSON. For code failures, suggest `cli-technical-analysis`.
5. If a failed job remains ambiguous but CircleCI output explicitly proves timeout, missing heartbeat, executor startup failure, or runner loss, inspect via `circleci` and apply the same retry boundary manually. Never infer a transient failure from an ordinary nonzero exit.

## Validation

- Run `python3 -m unittest tests/test_cli_ci_monitor.py` after changing the runner.
- Verify final JSON includes status, attempts, and workflow lineage.

## Outputs / Artifacts

Return final status, attempt count, workflow IDs, classification when failed, and current workflow when unfinished. Create no artifact by default.

## Companion Skills

- `circleci` for transport
- `cli-technical-analysis` for code failures

## Safety Notes

- Never expose tokens or read defaults files.
- Never use raw `curl`.
- Never retry code/ambiguous failures, approve holds, change parameters, or trigger a fresh pipeline. A transient log signature must be explicit.
- Limit mutations to supplied workflow lineage.
