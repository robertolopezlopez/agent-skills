---
name: cli-ci-monitor
description: Monitor a CLI CircleCI workflow or PR for up to two hours; retry transient failures, diagnose non-transient failures, update conflicted or out-of-date PRs, and follow replacement workflows.
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
- Retry proven transient/environment failures by default. Only explicit monitor-only or do-not-retry requests add `--no-retry-infra` and remain read-only.

## First Read

- Read CLI repository `AGENTS.md`.
- Load `circleci`; follow its prerequisites, CLI-first transport, and secret rules.
- For PR monitoring, load `gh-pr-rebase`.

## Workflow

1. Resolve `scripts/monitor_workflow.py` relative to this skill.
2. Run, adding `--pr-branch` when known:

   ```bash
   scripts/monitor_workflow.py '<workflow-id-or-url>' --pr-branch '<branch>'
   ```

3. With `--pr-branch`, call `gh-pr-rebase` immediately and every 300 seconds alongside CI. On conflict or `BEHIND`, let it rebase onto the PR target; return `pr_conflict` or `pr_out_of_date` plus `remaining_seconds` so replacement CI can resume within the deadline.
4. The runner retries by default. Add `--no-retry-infra` only when the user explicitly requests monitor-only or no retries. It uses the CircleCI CLI for workflow, job, output, cancel, and rerun operations; keeps one two-hour deadline; polls every 60 seconds; sounds the terminal alert when a failure needs attention; follows rerun workflow IDs; and retries only structured `timedout`/`infrastructure_fail` results or narrow transient signatures in failed output (such as a Jest test timeout or temporary network reset), with no code or ambiguous failures. Use `--request-helper <path>` only when CLI output or CircleCI Server compatibility is insufficient.
5. As soon as any job fails, inspect its output without waiting for unrelated running jobs. Unless retries were explicitly disabled, immediately cancel and rerun from failed when the runner or `cli-technical-analysis` proves a transient/environment cause, then resume within the original deadline. Otherwise return `failing` with classification, current workflow, and remaining deadline; never retry code or ambiguous failures.
6. After `gh-pr-rebase` updates the branch, stop the obsolete workflow, run `cli-contributor`, resolve replacement CI, and resume with its `remaining_seconds` and the same branch; never guess ambiguous matches.
7. On a final non-transient failure, present the diagnosis, then stop.
8. If a failed job remains ambiguous but CircleCI output explicitly proves timeout, missing heartbeat, executor startup failure, or runner loss, inspect via `circleci` and apply the same retry boundary manually. Never infer a transient failure from an ordinary nonzero exit.

## Validation

- Run `python3 -m unittest tests/test_cli_ci_monitor.py` after changing the runner.
- Verify final JSON includes status, attempts, and workflow lineage.

## Outputs / Artifacts

Return final status, attempt count, workflow IDs, classification when failed, and current workflow when unfinished. Create no artifact unless diagnosing a final failure.

## Companion Skills

- `circleci` for transport
- `gh-pr-rebase` for PR conflicts and rebases
- `cli-technical-analysis` for code failures

## Safety Notes

- Never expose tokens or read defaults files.
- Never use raw `curl`.
- Never retry code/ambiguous failures, approve holds, change parameters, or trigger a fresh pipeline. A transient log signature must be explicit.
- Limit mutations to supplied workflow lineage.
