# github skill → GITHUB-ACCESS.md + gh migration

## Goal

Remove the **`github`** installable skill; keep **`GITHUB-ACCESS.md`** + **`gh` / `gh api`** + **`scripts/github/`** as the portable layer (mirrors **`fast-grep`** → **`LITERAL-CODE-SEARCH.md`** + **`rg`**).

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| 1. Canonical policy in **`GITHUB-ACCESS.md`** + **`AGENTS.md`** | done | Synced via `shared_files` |
| 2. **`agent_config.py --github-access-policy`** | done | Shell: **`agent-config.sh --github-access-policy`** |
| 3. Workflow skills point to policy + `gh`, not skill | done | `github-pr-comment-analysis`, `github-issue-triage`, `private-pr-comment-analysis`, … |
| 4. **`github/SKILL.md`** → deprecation stub | done | Removed in Phase C |
| 5. Helpers in **`scripts/github/`** | done | **`gh-fetch`**, **`gh_context.py`**, **`bootstrap_github_artifact.py`**; **`--github-scripts-dir`** |
| 6. **`bootstrap_github_artifact.py`** | done | **`--fetch`**, **`--json`**, external **`$ARTIFACTS/pr-<n>/`** defaults |
| 7. Remove **`github`** from downstream **`companion_skills`** | done | Phase A |
| 8. **`check_skill_prereqs.sh github-access`** alias | done | Maps to **`github`** group |
| 9. Update **`docs/skill-schema.md`**, README, ARTIFACTS | done | Phase A |
| 10. Delete **`skills/core/github/`** + manifest entry | done | Phase C |

## Safe to delete `skills/core/github/` when

- [x] No manifest `companion_skills` entry references `github`
- [x] No `SKILL.md` tells agents to load the `github` skill for transport
- [x] Workflow skills refresh via **`GITHUB-ACCESS.md`** + `gh` only
- [x] `validate_skill.py` passes without `github` manifest entry
- [x] **`scripts/github/`** helpers shipped

## User-facing names (unchanged)

- Prereqs group: **`check_skill_prereqs.sh github`** (alias **`github-access`**)
- Auth: **`gh auth login`**
- API cache slug: **`github-rest`**
