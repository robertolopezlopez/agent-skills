# fast-grep → literal-code-search migration

## Goal

Remove the **`fast-grep`** installable skill; keep **`fast-grep.env`** + **`scripts/literal-search/`** as the portable layer.

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| 1. Helpers in `scripts/literal-search/` | done | Synced via `shared_files` |
| 2. Canonical policy in `LITERAL-CODE-SEARCH.md` + `AGENTS.md` | done | Synced via `shared_files` |
| 3. RTA step 3 points to policy, not skill | done | |
| 4. Contributor one-liners updated | done | RTA, diagnose, tdd, contributors, branch/rebase |
| 5. `fast-grep` skill scripts → wrappers to `scripts/literal-search/` | done | Wrappers removed with skill |
| 6. `fast-grep` SKILL.md → deprecation stub | done | Skill removed in step 10 |
| 7. Remove `fast-grep` from `companion_skills` | done | |
| 8. `check_skill_prereqs.sh literal-search` | done | `fast-grep` alias kept |
| 9. Benchmarks updated to `scripts/literal-search/` | done | pilot-tasks.json, prompts, run-pilot.sh |
| 10. Delete `skills/core/fast-grep/` + manifest entry | done | |

## Safe to delete `skills/core/fast-grep/` when

- [x] No manifest `companion_skills` entry references `fast-grep`
- [x] No `SKILL.md` tells agents to load `/fast-grep`
- [x] Synced installs use `scripts/literal-search/` only
- [x] `validate_skill.py` passes without `fast-grep` manifest entry

## User-facing renames (unchanged)

- Config file: **`fast-grep.env`** (name kept)
- Prefs script: **`fast-grep-prefs.sh`** (name kept)
- Runner script: **`fast-grep`** under **`scripts/literal-search/`** (name kept)
