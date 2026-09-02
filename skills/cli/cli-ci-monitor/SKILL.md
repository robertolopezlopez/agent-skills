---
name: cli-ci-monitor
description: Run the local CLI CircleCI monitor for one workflow lineage, including conservative retries, PR checks, and post-rebase replacement discovery.
---

# CLI CI Monitor

## When to Use

Monitor one CLI CircleCI workflow or PR until success or the shared two-hour deadline.

## When Not to Use

Use `circleci` for one lookup and `cli-parallel-tests` for local tests.

## Inputs

- Workflow UUID or CircleCI URL containing `workflowId`.
- Optional PR URL, number, or branch.
- Defaults: 60-second polling, two-hour deadline, and retries for proven transient/environment failures. Add `--no-retry-infra` only when explicitly requested.

## First Read

Read repository `AGENTS.md` and `circleci`; for PR monitoring, also read `gh-pr-rebase`.

## Workflow

1. Run the bundled local runner; it owns CircleCI transport, polling, failure-output classification, conservative cancel/rerun, alerts, workflow lineage, PR resolution/checks, and deadline accounting:

   ```bash
   scripts/monitor_workflow.py '<workflow>' [--pr '<pr>']
   ```

   Use `--request-helper <path>` only when the CircleCI CLI is insufficient.
2. On `success`, stop. On a code or ambiguous failure, use `cli-technical-analysis`, report the diagnosis, and stop; never retry it.
3. On `pr_conflict` or `pr_out_of_date`, run `gh-pr-rebase`. After its verified push, let the runner cancel obsolete CI, find the workflow matching both the new PR head and prior workflow name, and resume against the original absolute deadline:

   ```bash
   scripts/monitor_workflow.py '<obsolete-workflow>' --pr '<pr>' --resume-after-rebase --deadline-epoch '<deadline_epoch>'
   ```

   Stop if replacement matching is ambiguous or the deadline expires.

## Validation

Run `python3 -m unittest tests/test_cli_ci_monitor.py tests/test_gh_pr_rebase.py`. Final JSON includes status, attempts, lineage, and `deadline_epoch`.

## Outputs / Artifacts

Return runner JSON plus final diagnosis when needed. Create an artifact only for a final failure.

## Companion Skills

`circleci` owns transport, `gh-pr-rebase` owns risky Git changes, and `cli-technical-analysis` owns code/ambiguous diagnosis.

## Safety Notes

Never expose tokens, read defaults files, use raw `curl`, retry code/ambiguous failures, approve holds, change parameters, trigger a fresh pipeline, or mutate outside the supplied workflow lineage.
