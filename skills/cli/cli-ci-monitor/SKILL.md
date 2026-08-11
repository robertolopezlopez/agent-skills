---
name: cli-ci-monitor
description: Monitor a CLI CircleCI workflow or PR for up to two hours; retry transient failures, resolve PR conflicts with rebase/contributor skills, and follow replacement workflows.
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
- Optional PR URL, number, or branch; resolve its branch with local `gh`, or use the workflow revision only for one matching open PR.
- Defaults: 2-hour shared deadline and 60-second polling. Never reset deadline after reruns.
- Monitor-and-retry requests authorize cancel/rerun below; monitor-only requests remain read-only.

## First Read

- Read CLI repository `AGENTS.md`.
- Load `circleci`; follow its prerequisites, CLI-first transport, and secret rules.
- For PR monitoring, follow synced `GITHUB-ACCESS.md` and use local `gh` first.

## Workflow

1. Resolve `scripts/monitor_workflow.py` relative to this skill.
2. Run, adding `--pr-branch` when known:

   ```bash
   scripts/monitor_workflow.py '<workflow-id-or-url>' --pr-branch '<branch>'
   ```

3. With `--pr-branch`, the runner resolves the PR via local `gh pr view`, checks immediately and every 300 seconds alongside CI, and returns `pr_conflict` plus `remaining_seconds` on conflict.
4. Only when the user authorized monitor-and-retry, add `--retry-infra`. The runner uses the CircleCI CLI for workflow, job, output, cancel, and rerun operations; keeps one two-hour deadline; polls every 60 seconds; follows rerun workflow IDs; and retries only structured `timedout`/`infrastructure_fail` results or narrow transient signatures in failed output (such as a Jest test timeout or temporary network reset), with no code or ambiguous failures. Use `--request-helper <path>` only when CLI output or CircleCI Server compatibility is insufficient.
5. On `pr_conflict`, stop monitoring the obsolete workflow; run `git-rebase-conflict-resolver`, then `cli-contributor`. Push only with user authorization. Resolve the replacement workflow and resume with `--timeout-seconds <remaining_seconds>` and the same branch; never guess ambiguous PR/workflow matches.
6. Report transition lines and the final JSON. For code failures, suggest `cli-technical-analysis`.
7. If a failed job remains ambiguous but CircleCI output explicitly proves timeout, missing heartbeat, executor startup failure, or runner loss, inspect via `circleci` and apply the same retry boundary manually. Never infer a transient failure from an ordinary nonzero exit.

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
