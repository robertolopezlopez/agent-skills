# git skill → GIT-ACCESS.md + git CLI migration

## Goal

Remove the installable **`git`** skill; keep **`GIT-ACCESS.md`** + **`git` CLI** + **`scripts/git/`** as the portable layer (mirrors **`GITHUB-ACCESS.md`** + **`gh`**).

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| 1. Canonical policy in **`GIT-ACCESS.md`** + **`AGENTS.md`** | done | Sync via `shared_files` in Phase B |
| 2. **`agent_config.py --git-access-policy`** | todo | Phase B; shell: **`agent-config.sh --git-access-policy`** |
| 3. Workflow skills point to policy + helper, not skill | done | `gitlab`, `circleci`, `github-*`, … |
| 4. **`git/SKILL.md`** → deprecation stub | done | Skill still installed until Phase C |
| 5. Helpers in **`scripts/git/`** | todo | Phase B |
| 6. Remove **`git`** from downstream **`companion_skills`** | done | Phase A |
| 7. **`check_skill_prereqs.sh git-access`** alias | todo | Phase B; **`git`** group legacy alias → **`gitlab`** (**`glab`**) |
| 8. Update **`docs/skill-schema.md`**, README, ARTIFACTS | done | Phase A |
| 9. Delete **`skills/core/git/`** + manifest entry | todo | Phase C |

## Safe to delete `skills/core/git/` when

- [x] No manifest `companion_skills` entry references `git`
- [x] No `SKILL.md` tells agents to load the `git` skill for identity (stub points to policy)
- [x] **`gitlab`** refreshes via **`GIT-ACCESS.md`** + helper only
- [ ] `validate_skill.py` passes without `git` manifest entry
- [ ] **`scripts/git/`** helpers shipped

## User-facing names (unchanged where noted)

- Git binary prereqs: **`check_skill_prereqs.sh git-access`**
- GitLab ID fetch prereqs: **`check_skill_prereqs.sh gitlab`** (legacy: **`check_skill_prereqs.sh git`** → **`glab`**)
- Auth: **`glab auth login`** for **`--fetch-id`**
