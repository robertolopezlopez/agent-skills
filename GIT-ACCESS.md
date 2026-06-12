# Git repository identity (canonical policy)

Portable **local Git remote identity** resolution for **any repository**, **any OS**, and **any agent runtime** (Cursor, Codex, and similar). Policy syncs to **`$AGENT_CONFIG_HOME/skills/GIT-ACCESS.md`**. Resolve with **`scripts/agent_config.py --git-access-policy`**.

Use this for **repository identity** (host, project path, GitLab numeric ID). Do **not** use it for GitHub issue/PR fetch — that is **`GITHUB-ACCESS.md`** + **`gh`**. Do **not** use it for GitLab MR transport — that is the **`gitlab`** skill + **`glab`**.

## When to use

- resolve `origin` (or another remote) into host + `namespace/project` path
- produce URL-encoded project path for GitLab REST (`%2F` for `/`)
- optional GitLab numeric **`project_id`** via **`glab api`** (`--fetch-id`)
- verify a checkout is on the expected host before **`GITHUB-ACCESS.md`** fetch (e.g. `github.com`)

## When not to use

- full GitLab MR workflow → **`gitlab`** skill
- GitHub issue/PR fetch → **`GITHUB-ACCESS.md`**
- rebase/conflict resolution → **`git-rebase-conflict-resolver`** or raw **`git`**
- Jira/Confluence/CircleCI transport beyond slug inference pointers

## Prerequisites

Identity from local remotes ( **`git`** must be on PATH):

```bash
scripts/check_skill_prereqs.sh git-access
```

GitLab numeric project ID (`--fetch-id`) also needs **`glab`**:

```bash
scripts/check_skill_prereqs.sh gitlab    # alias: check_skill_prereqs.sh git (legacy group name)
scripts/check_skill_config.sh gitlab    # glab auth login
```

Alias: **`check_skill_prereqs.sh git`** → same **`gitlab`** group (**`glab`** install/auth), not the **`git`** binary.

## Path resolution

| What | Resolver |
|------|----------|
| Policy doc (this file) | `agent_config.py --git-access-policy` |
| **Helper scripts** | `agent_config.py --git-scripts-dir` |
| Skills scripts root | `agent_config.py --skills-root` |
| Git binary / remotes | `check_skill_prereqs.sh git-access` |
| GitLab ID fetch | `check_skill_prereqs.sh gitlab` + `check_skill_config.sh gitlab` |

## Normalized output contract

Downstream skills (especially **`gitlab`**, **`circleci`**) expect:

| Field | Description |
|-------|-------------|
| `remote` | Remote name (e.g. `origin`) or null when `--remote-url` |
| `remote_url` | Configured URL |
| `host` | Hostname |
| `project_path` | `namespace/project` (nested groups preserved) |
| `encoded_project_path` | URL-encoded path for GitLab API |
| `project_id` | GitLab numeric ID when `--fetch-id` succeeds; else null |

Return the same contract whether data came from the synced helper or explicit **`git config`** + manual parsing (prefer the helper).

## Workflow

1. Start in the target repository root when possible.
2. Read **`origin`** first unless the user names another remote.
3. Run the synced helper for machine-readable JSON (do not re-parse ad hoc in workflow skills).
4. For GitLab API calls, prefer **`project_id`** when available; else **`encoded_project_path`**.
5. For GitHub fetch, confirm **`host`** matches expectations, then hand off to **`GITHUB-ACCESS.md`**.

## Local commands

Inspect remotes (debug only — prefer helper output):

```bash
git remote -v
git config --get remote.origin.url
```

Resolve identity (synced helper):

```bash
GSDIR="$(python3 ~/.cursor/skills/scripts/agent_config.py --git-scripts-dir)"

"$GSDIR/git-repo-identity" --json
"$GSDIR/git-repo-identity" --remote-url 'git@gitlab.example.com:group/project.git' --json
"$GSDIR/git-repo-identity" --fetch-id --json
```

## Synced helpers

Resolve **`$AGENT_CONFIG_HOME/skills/scripts/git/`** with **`agent_config.py --git-scripts-dir`**.

| Script | Purpose |
|--------|---------|
| **`git-repo-identity`** | Wrapper for **`resolve_repo_identity.py`** |
| **`resolve_repo_identity.py`** | Parse remotes; optional GitLab **`project_id`** via **`glab api`** |

## Companion skill pairings

| Task | Skill / doc |
|------|-------------|
| GitLab MR fetch | **`gitlab`** (consumes identity from this policy) |
| GitHub issue/PR fetch | **`GITHUB-ACCESS.md`** (host check only; fetch via **`gh`**) |
| CircleCI slug inference | **`circleci`** (may derive `gh/<org>/<repo>` from identity) |
| Rebase / conflicts | **`git-rebase-conflict-resolver`** |

Transport stays in **this policy** + helper; platform workflows stay in companion skills.

## Safety

- Prefer **`origin`** unless repo conventions say otherwise.
- Preserve nested groups exactly; strip trailing **`.git`** before building paths.
- Do not duplicate identity parsing inside **`gitlab`**, **`circleci`**, or GitHub workflow skills.
- When **`glab`** auth fails for **`--fetch-id`**, stop and help the user finish setup — do not guess **`project_id`**.
