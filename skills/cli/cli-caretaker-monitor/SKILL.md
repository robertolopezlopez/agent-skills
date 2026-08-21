---
name: cli-caretaker-monitor
description: Monitor new CLI support Asks until explicitly stopped, run two-hour caretaker sweeps, and parallel-review PR requests with conditional automatic approval.
---

# CLI Caretaker Monitor

## When to Use

Run only in an explicitly started active session; poll every five minutes and run a full `cli-caretaker` sweep every two hours until the user stops it.

## When Not to Use

Exclude read-only reports, backlog cleanup, On Caller work, and unattended scheduling.

## Setup

Refresh live CLI Support guidance and resolve the authenticated Jira user, Support Board, and its `In Review` status. Retry unresolved setup on later polls, but never write while it is missing or ambiguous.

## Companion Skills

Read `cli-caretaker` and synced `JIRA-ACCESS.md` at startup; for PR Asks, read `multi-spawn-agent`, `cli-branch-change-reviewer`, and synced `GITHUB-ACCESS.md`. Use `prepare-daily-status` for status handoff.

## Workflow

1. Run `cli-caretaker` read-only and save visible support-Ask keys as the baseline; never claim them.
2. Every two hours from startup, run a full read-only `cli-caretaker` sweep and append it to the same artifact without resetting the baseline or replacing five-minute polls.
3. On each poll, analyze keys first seen after baseline. Reread each key: if another person owns it, mark it seen and skip silently without recording or naming the owner.
4. Otherwise assign it to the authenticated user, apply the live `In Review` transition, and skip already-satisfied mutations. Verify both fields with a native Jira read.
5. Append its analysis, links, assignee, and status to the same-day caretaker artifact; never reprocess a verified key. For non-PR reviews, hand it once to `prepare-daily-status` as `In progress`.
6. Retry a transient item failure on the next poll once. After two matching auth, ACL, configuration, identity, or board-contract failures, report and pause that action without stopping the monitor.
7. After every successful write, immediately run `printf '\a'`; never ring for reads, idle polls, skips, or failures.

## PR-review Asks

After claiming a PR-review Ask:

1. Start one separate read-only review worker from a temporary work definition containing the PR URL, target, head SHA, artifact path, and result contract; keep polling without waiting.
2. Require full changed-file coverage, relevant callers/tests, unresolved review context, CI evidence, and task-relevant verification. Missing, failed, or inconclusive evidence is an open question. For any `CODEOWNERS` change, also validate syntax and precedence, then compare effective owners before and after for affected paths; ambiguity or unintended coverage loss blocks approval.
3. Compare the artifact with the live PR. If the head changed, launch one fresh review; never approve stale evidence.
4. Approve through `gh` only when the reviewed head is current, the PR is open and not draft, the reviewer is not the author and has not already approved, and the artifact has no findings or open questions.
5. Record the reviewed SHA and review/approval outcome in both review and caretaker artifacts. Refresh PR state and hand it to `prepare-daily-status` as `Done since last log` if merged, otherwise `In progress`; then run one final `printf '\a'`.

## Validation

- Baseline and other-owned Asks remain unchanged; no other owner identity is reported or stored.
- Two-hour sweeps are recorded without disrupting new-Ask tracking.
- Claimed Asks have verified assignment/status, caretaker analysis, and exactly one matching daily-status entry.
- PR work never blocks polling; automatic approval satisfies every review gate above.
- No comments, messages, priority changes, closures, or unrelated transitions occur.

## Outputs

Report only changes and failures during polling, then claimed/skipped/failed counts after explicit stop. Extend `$ARTIFACTS/cli-caretaker-YYYY-MM-DD/analysis_cli_caretaker.md`; create no separate monitor artifact.

## Safety Notes

Starting the monitor authorizes recurring assignment, `In Review` transition, artifact/status logging, and gated clean-PR approval only for newly detected Asks. It does not authorize other external writes or reassignment from another owner.
