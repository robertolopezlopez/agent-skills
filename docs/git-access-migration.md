# git skill → GIT-ACCESS.md + git CLI migration

## Goal

Remove the installable **`git`** skill; keep **`GIT-ACCESS.md`** + **`git` CLI** + **`scripts/git/`** as the portable layer (mirrors **`GITHUB-ACCESS.md`** + **`gh`**).

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| 1. Canonical policy in **`GIT-ACCESS.md`** + **`AGENTS.md`** | done | Synced via `shared_files` |
| 2. **`agent_config.py --git-access-policy`** | done | Shell: **`agent-config.sh --git-access-policy`** |
| 3. Workflow skills point to policy + helper, not skill | done | `gitlab`, `circleci`, `github-*`, … |
| 4. **`git/SKILL.md`** → deprecation stub | done | Skill still installed until Phase C |
| 5. Helpers in **`scripts/git/`** | done | **`git-repo-identity`**, **`resolve_repo_identity.py`**; **`--git-scripts-dir`** |
| 6. Remove **`git`** from downstream **`companion_skills`** | done | Phase A |
| 7. **`check_skill_prereqs.sh git-access`** alias | done | **`git`** group legacy alias → **`gitlab`** (**`glab`**) |
| 8. Update **`docs/skill-schema.md`**, README, ARTIFACTS | done | Phase A |
| 9. Delete **`skills/core/git/`** + manifest entry | done | Phase C |

## Safe to delete `skills/core/git/` when

- [x] No manifest `companion_skills` entry references `git`
- [x] No `SKILL.md` tells agents to load the `git` skill for identity (stub points to policy)
- [x] **`gitlab`** refreshes via **`GIT-ACCESS.md`** + helper only
- [x] `validate_skill.py` passes without `git` manifest entry
- [x] **`scripts/git/`** helpers shipped

## User-facing names (unchanged where noted)

- Git binary prereqs: **`check_skill_prereqs.sh git-access`**
- GitLab ID fetch prereqs: **`check_skill_prereqs.sh gitlab`** (legacy: **`check_skill_prereqs.sh git`** → **`glab`**)
- Auth: **`glab auth login`** for **`--fetch-id`**

## Phase D (optional polish)

| Step | Status | Notes |
|------|--------|-------|
| 10. Shared **`scripts/parse_remote_url.py`** | done | Used by **`resolve_repo_identity.py`**, **`gh_context.py`**, **`resolve_artifact_path.py`** |
| 11. Self-test / smoke | done | **`parse_remote_url.py --self-test`**; **`git-repo-identity --json`** on checkout remotes |

### Smoke commands

```bash
python3 scripts/parse_remote_url.py --self-test

GSDIR="$(python3 scripts/agent_config.py --git-scripts-dir)"
"$GSDIR/git-repo-identity" --json

# CircleCI slug candidate from identity (GitHub OAuth projects):
# gh/<org>/<repo> from project_path tail
python3 -c "
from parse_remote_url import parse_remote_url, tail_path_segments
import subprocess, sys
sys.path.insert(0, 'scripts')
url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], text=True).strip()
_, path = parse_remote_url(url)
tail = tail_path_segments(path, 2)
print('gh/' + '/'.join(tail) if tail else 'no slug')
"

# GitLab numeric ID (needs glab auth + GitLab remote):
# "$GSDIR/git-repo-identity" --fetch-id --json
```
