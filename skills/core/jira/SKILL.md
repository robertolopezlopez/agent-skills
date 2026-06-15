---
name: jira
description: Deprecated transport stub — use synced JIRA-ACCESS.md and acli for Jira Cloud issue access. This installable skill remains until Phase C removes it; bootstrap helpers live under this skill's scripts/ directory until Phase B moves them to the synced scripts tree.
---

# jira (deprecated — use JIRA-ACCESS.md)

The installable **`jira`** skill is being replaced by synced **`JIRA-ACCESS.md`** + **`acli`** (mirrors the **`github`** → **`GITHUB-ACCESS.md`** migration).

## When to Use

Do **not** load this skill for new work. Use **`JIRA-ACCESS.md`** instead.

## When Not to Use

Always prefer **`JIRA-ACCESS.md`** + **`acli`** for Jira transport.

## Workflow

1. Read synced **`JIRA-ACCESS.md`** — **`scripts/agent_config.py --jira-access-policy`**
2. Run **`scripts/check_skill_prereqs.sh jira`** and **`scripts/check_skill_config.sh jira`**
3. Fetch and update issues with **`acli jira workitem …`** per the policy
4. Use **`jira-request`** / **`jira-api`** under this skill's **`scripts/`** only as REST escape hatches per **`JIRA-ACCESS.md`**

## Helpers (until Phase B sync)

| Script | Path |
|--------|------|
| `bootstrap_jira_artifact.py` | `scripts/bootstrap_jira_artifact.py` |
| `jira-api` | `scripts/jira-api` |
| `jira-request` | `scripts/jira-request` |

See **`docs/jira-access-migration.md`** for the full checklist.

## Safety Notes

Do not duplicate transport policy here — **`JIRA-ACCESS.md`** is the source of truth.
