---
name: cli-caretaker
description: Research CLI Ask Caretaker shifts and handoffs read-only across Asks, `S075HU4SREC` questions, support, alerts, Datadog, main CircleCI, redirects, and PR asks; exclude On Caller/incident work.
---

# CLI Ask Caretaker

Protect sprint focus by researching the queue and advising actions.

## When to Use

Use for CLI caretaker shifts, Ask/support triage, or handoffs. Exclude On Caller, paging, incident command, and deep investigation after initial triage.

## When Not to Use

Do not use outside CLI Ask Caretaker scope or for On Caller/incident ownership.

## Sources

- Before the caretaker workflow, run the **policy freshness gate** below. Use only the `CLI Ask Caretaker` section of the [CLI Support page](https://snyksec.atlassian.net/wiki/spaces/CLI/pages/2120417317/Support); live policy wins for the current run.
- Use the [decision diagram](https://miro.com/app/board/uXjVKD3VYxU=/) secondarily, plus [Support Board](https://snyksec.atlassian.net/jira/software/c/projects/CLI/boards/715) and [Support Dashboard](https://snyksec.atlassian.net/jira/dashboards/10913) `Triage Status`.
- Use `JIRA-ACCESS.md`; any connected Slack capability for group `S075HU4SREC` and `#ask-cli`, `#cli-alerts`, `#hammerhead-alerts`; `circleci`; and connected Datadog skills when relevant. Never assume runtime-specific Slack tool names.

## Policy Freshness Gate

- Baseline: Support page `v:10`, checked `2026-09-25`. Update this line when the skill incorporates a newer policy.
- State: resolve `$GLOBAL/cli-caretaker-policy/state.md` with `resolve_artifact_path.py`; read it before external work.
- Check at most once per local calendar day. If `last_checked_date` is today, use the stored state and do not fetch Confluence again.
- Otherwise fetch the page with `twg confluence content get <URL> --detail full --format markdown --include-metadata`, compare the page version and `CLI Ask Caretaker` section with the baseline, and record the date/version/delta in the state file.
- If the page changed, learn the delta for the current run, then warn at the start and end: `CLI caretaker skill stale: Support policy changed from <baseline> to <version>; update cli-caretaker/SKILL.md.` Keep warning on later triggers until this skill's baseline and instructions are updated.
- Do not silently edit this skill or clear the stale state. After updating the skill, set its baseline to the incorporated page version and mark the state current.

## Inputs

Accept a shift window, queue snapshot, issue list, or handoff. Research/triage/report requests authorize reads only. Require an explicit request for each comment, transition, close, assignment, message, reply, or PR review; confirm destructive, ambiguous, or bulk writes.

## Workflow

1. Read and deduplicate:
   - every non-`Done` Ask
   - every visible shift-window `@ask-cli-caretaker`/`S075HU4SREC` question, including parent and thread
   - new support `Triage Status` items
   - CLI/Hammerhead alerts, `main` failures in [snyk/cli CircleCI](https://app.circleci.com/pipelines/gh/snyk/cli), redirected requests, and PR asks
   - acceptance failures where documented `TEST_SNYK_IGNORE_LIST` may unblock an out-of-scope spec, never a CLI regression
   - batch authoritative local reads first (`acli`/`JIRA-ACCESS.md`, `circleci`, `gh`); after deduplication, use one bounded `twg context` or `twg responsibility` lookup only when ownership or related work is unclear; never enrich every item or use TWG search as coverage proof
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
- Follow the report order below. Put full details in one section only; use internal Markdown links elsewhere.
- Give every deferred item a next trigger and every closed item closure evidence.
- Verify Jira, Slack, GitHub, CircleCI, and Datadog remained unchanged unless explicitly requested.

## Outputs

Write non-trivial work to the user path or `$ARTIFACTS/cli-caretaker-YYYY-MM-DD/analysis_cli_caretaker.md`. Resolve via `ARTIFACTS.md`; extend same-day report.

Keep the report tight: one line per item with linked ID, advised action, and
only a material blocker or follow-up. Omit recap, classification, owner, and
rationale when the action is clear.

Use this report order:

```markdown
# CLI Ask Caretaker — YYYY-MM-DD
Analysis window: ...

## Summary
## Urgent Alerts / CircleCI Failures
## Prioritized Advice
## Share-ready Handoff
## Evidence Gaps and Safety
## External Actions / Side Effects
## Ask Queue
## Shift-window Slack Coverage and Rotation
## Support Triage and SLOs
## Routine Alerts / Main CircleCI
## Live Policy
## Deferred Items
## Closed Items
```

- In `Summary`, mention urgent items and external actions only by name with an
  internal link to their detail section.
- Put actionable urgent alert or CircleCI details immediately below `Summary`.
- Put PR asks and redirects in `Ask Queue`.
- In `Ask Queue`, put **Close** immediately after the linked ID when closure is advised: `[ASK-ID](https://…) — **Close** — …`.
- Omit already-closed Asks unless they still require action.
- Keep routine or healthy alert and CircleCI status in its later section.
- Omit empty urgent, external-action, deferred, and closed sections.
- Never duplicate detailed items; link to their single detailed location.

## Companion Skills

Use connected Slack capability read-only when available, `confluence`, `circleci` read-only, `cli-branch-change-reviewer` read-only for PR asks, `cli-technical-analysis` only after explicit deep-investigation request, and discovered Datadog guides. External writes require their write workflow and explicit request.

## Safety Notes

Never expose customer data, credentials, private logs, or Salesforce content. Draft messages in report; never infer write authority from research, triage, review, prepare, run, or report.
