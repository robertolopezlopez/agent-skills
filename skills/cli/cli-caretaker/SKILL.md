---
name: cli-caretaker
description: >-
  Research a CLI Ask Caretaker shift and write an evidence-backed, read-only report covering Asks,
  `@ask-cli-caretaker` (`S075HU4SREC`) questions, support triage, alerts, Datadog, main CircleCI
  failures, redirected requests, and PR asks. Use for caretaker triage or handoffs, not On Caller or
  incident work. Advise actions; mutate external systems only when explicitly asked.
---

# CLI Ask Caretaker

Protect sprint focus by researching the queue and advising actions.

## When to Use

Use for CLI caretaker shifts, Ask/support triage, or handoffs. Exclude On Caller, paging, incident command, and deep investigation after initial triage.

## When Not to Use

Do not use outside CLI Ask Caretaker scope or for On Caller/incident ownership.

## Sources

- Refresh the [CLI Support page](https://snyksec.atlassian.net/wiki/spaces/CLI/pages/2120417317/Support) with `confluence`; use only `CLI Ask Caretaker` guidance. Live policy wins.
- Use the [decision diagram](https://miro.com/app/board/uXjVKD3VYxU=/) secondarily, plus [Support Board](https://snyksec.atlassian.net/jira/software/c/projects/CLI/boards/715) and [Support Dashboard](https://snyksec.atlassian.net/jira/dashboards/10913) `Triage Status`.
- Use `JIRA-ACCESS.md`; any connected Slack capability for group `S075HU4SREC` and `#ask-cli`, `#cli-alerts`, `#hammerhead-alerts`; `circleci`; and connected Datadog skills when relevant. Never assume runtime-specific Slack tool names.

## Inputs

Accept a shift window, queue snapshot, issue list, or handoff. Research/triage/report requests authorize reads only. Require an explicit request for each comment, transition, close, assignment, message, reply, or PR review; confirm destructive, ambiguous, or bulk writes.

## Workflow

1. Read and deduplicate:
   - every non-`Done` Ask
   - every visible shift-window `@ask-cli-caretaker`/`S075HU4SREC` question, including parent and thread
   - new support `Triage Status` items
   - CLI/Hammerhead alerts, `main` failures in [snyk/cli CircleCI](https://app.circleci.com/pipelines/gh/snyk/cli), redirected requests, and PR asks
   - acceptance failures where documented `TEST_SNYK_IGNORE_LIST` may unblock an out-of-scope spec, never a CLI regression
2. For observable alerts, CI errors, or performance symptoms, discover and load the matching Datadog guide; query the narrowest useful identifier/service/error/time window. Record query, range, link, and whether evidence confirms or suggests. Skip Datadog when no signal exists or other evidence answers the item.
3. Classify each Ask:
   - simple question/update: draft answer; advise close, or `#ask-cli` follow-up if unclear
   - feature: advise Aha! entry, then close after capture
   - customer bug: advise Zendesk ticket/link with logs, screenshots, repro; then close Ask and follow support flow
   - non-customer bug: advise CLI/IDE Jira bug, Ask link, and KLO/Cooldown prioritization
   - documentation debt: advise tech-debt ticket; if urgent, `Cycle <X> Cooldown candidate`
   - PR ask: inspect read-only; advise review/closure, never submit or close
4. Apply 30-minute Ask gate: route longer work into tracked flow instead of continuing channel investigation.
5. Perform initial SUP triage in 5–10 minutes and within 1–3 days by priority:
   - decide CLI ownership; otherwise advise owner assignment and project move
   - confirmed CLI bug: advise `Backlog`; for `Highest (Critical)`, also current sprint and fix
   - surface red breached due dates and yellow breached triage dates
   - feature: advise `Customer Need` with reason; sanity-check priority/missing data
   - declined bug: advise `Won't Fix` with reason
   - do not design solutions, deeply investigate, or promise exact ETA
6. During planning, flag whether about 30% capacity remains for support and whether SLOs are at risk.
7. Write report with reminder to update Slack group when appropriate; do not update it.
8. Perform only separately requested external actions and record resulting URLs.

## Validation

- Cover all visible non-Done Asks, new triage items, and shift-window group mentions, or state gaps.
- Record source type, ownership, classification, customer origin, priority, and decision branch where applicable.
- Keep over-30-minute work out of Ask; cite evidence; exclude On Caller.
- Verify Jira, Slack, GitHub, CircleCI, and Datadog remained unchanged unless explicitly requested.

## Outputs

Write non-trivial work to the user path or `$ARTIFACTS/cli-caretaker-YYYY-MM-DD/analysis_cli_caretaker.md`. Resolve via `ARTIFACTS.md`; extend same-day report.

For each item record identifier/source, classification, advised action/rationale, owner/blocker/follow-up, and links. End with counts, evidence gaps, prioritized advice, and share-ready handoff; separate observation from advice.

## Companion Skills

Use connected Slack capability read-only when available, `confluence`, `circleci` read-only, `cli-branch-change-reviewer` read-only for PR asks, `cli-technical-analysis` only after explicit deep-investigation request, and discovered Datadog guides. External writes require their write workflow and explicit request.

## Safety Notes

Never expose customer data, credentials, private logs, or Salesforce content. Draft messages in report; never infer write authority from research, triage, review, prepare, run, or report.
