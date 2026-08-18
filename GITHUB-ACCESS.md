# GitHub access (canonical policy)

Portable GitHub issue and pull request fetch for **any repository**, **any OS**, and **any agent runtime** (Cursor, Codex, and similar). Policy syncs to **`$AGENT_CONFIG_HOME/skills/GITHUB-ACCESS.md`**. Resolve with **`scripts/agent_config.py --github-access-policy`**.

Workflow skills (`github-pr-comment-analysis`, `github-issue-triage`, …) consume normalized context produced here; they do not duplicate transport logic.

## Transport order

```text
1. **`GIT-ACCESS.md`** — repository identity / verify host (when needed)
2. gh — issue/PR overview, comments, labels
3. gh api — structured reviews, review comments, fields gh view omits
4. GitHub MCP — last resort when local tools missing or insufficient
```

Follow **Transport preference** and **Missing CLI tools — ask before fallback** in **`AGENTS.md`**.

## Prerequisites

Before fetching:

```bash
scripts/check_skill_prereqs.sh github    # gh install (OS-appropriate suggest lines)
scripts/check_skill_config.sh github       # gh auth login
```

Alias: **`check_skill_prereqs.sh github-access`** → same **`github`** group.

If **`gh`** is missing, **ask the user** to install using the OS-appropriate **`suggest (...)`** line — do not install unless asked. A failed **`gh auth status`** is ambiguous because restricted network or credential-store access can look like invalid auth. Retry with both available and probe **`gh api user`**; guide **`gh auth login`** only when that unrestricted retry confirms missing or invalid credentials.

## Path resolution

| What | Resolver |
|------|----------|
| Policy doc (this file) | `agent_config.py --github-access-policy` |
| **Helper scripts** | `agent_config.py --github-scripts-dir` |
| Skills scripts root | `agent_config.py --skills-root` |
| API doc cache | `agent_config.py --api-docs-dir github-rest` |
| Prereqs | `check_skill_prereqs.sh github` |
| Auth / config | `check_skill_config.sh github` |

## Inputs

Accept, in order of preference:

- normalized GitHub context already fetched this session
- issue or pull request URL
- object number when context makes **`issue`** vs **`pull_request`** clear
- current repository context when no explicit identifier

**Issue vs PR:** If the user gives only a number, infer from wording and context. If ambiguous, **ask** before fetching.

### URL shapes

```text
https://github.com/<owner>/<repo>/issues/<number>
https://github.com/<owner>/<repo>/pull/<number>
```

Parse: host, owner, repository name, object type, object number.

## Normalized context contract

Downstream workflow skills expect these fields (names stable across transports):

| Field | Description |
|-------|-------------|
| `repository_owner` | GitHub org or user |
| `repository_name` | Repository name |
| `object_type` | `issue` or `pull_request` |
| `object_number` | Issue or PR number |
| `pr_number` | PR number when `object_type` is `pull_request` (alias for workflows) |
| `canonical_url` | Direct issue or PR URL |
| `state` | open, closed, merged, … |
| `labels` | Label names when relevant |
| `assignees` | When relevant |
| `author` | Creator login or display |
| `created_at` / `updated_at` | ISO timestamps when available |
| `body` | Description / PR body |
| `comments` | Issue or conversation comments when requested |
| `conversation_comments` / `comment_count` | Issue timeline comments (included when owner/repo are known) |
| `reviews` / `review_comments` | PR review data when requested |
| `review_threads` | PR inline review threads with `is_resolved` when `--full` |
| `conversation_comments` | PR timeline comments (non-inline) when `--full` |
| `fetch_depth` | `overview` or `full` |
| `review_thread_count` / `unresolved_review_thread_count` | Summary counts when `--full` |

Return the same contract whether data came from **`gh`**, **`gh api`**, or GitHub MCP.

## Workflow

1. Start in the target repository root when local context is available.
2. Reuse normalized context from an earlier fetch in the same session when still valid.
3. Parse URLs into owner, repo, type, and number.
4. When repository identity is unknown, use synced **`GIT-ACCESS.md`** + **`git-repo-identity`** on remotes; stop if not hosted on GitHub.
5. Resolve issue vs PR ambiguity before fetching.
6. Run **`gh`** for common reads; escalate to **`gh api`** for structured review data.
7. Use GitHub MCP only when local tools fail after prereq/config checks.
8. Normalize output to the contract above for workflow skills.

## Local commands

Issue overview:

```bash
gh issue view <number>
gh issue view <number> --comments
```

Pull request overview:

```bash
gh pr view <number>
gh pr view <number> --comments
```

Structured REST (when **`gh view`** is insufficient):

```bash
gh api repos/<owner>/<repo>/issues/<number>
gh api repos/<owner>/<repo>/pulls/<number>
gh api repos/<owner>/<repo>/issues/<number>/comments
gh api repos/<owner>/<repo>/pulls/<number>/comments
gh api repos/<owner>/<repo>/pulls/<number>/reviews
```

GraphQL review threads (used by **`gh_context.py --full`**):

```bash
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{isResolved comments(first:100){nodes{url body author{login}}}}}}}}' -f o=<owner> -f r=<repo> -F n=<number>
```

When owner/repo are implicit from the current checkout, **`gh`** often accepts **`-R owner/repo`** or runs from repo root without full paths.

## Synced helpers (Phase B)

Resolve **`$AGENT_CONFIG_HOME/skills/scripts/github/`** with **`agent_config.py --github-scripts-dir`**.

| Script | Purpose |
|--------|---------|
| **`gh-fetch`** | Fetch normalized issue/PR JSON via **`gh`** (`gh_context.py` wrapper) |
| **`gh_context.py`** | Core fetch + normalization (`issue` / `pr`, optional `--url`, `--owner`, `--repo`, **`--full`**) |
| **`bootstrap_github_artifact.py`** | Bootstrap **`triage_issue_<n>.md`** / **`analysis_issue_<n>.md`** or **`review_pr_<n>.md`** / **`analysis_pr_<n>.md`** under **`$ARTIFACTS/`** |
| **`apply_pr_thread_groups.py`** | Mechanical first pass: upsert **`## Grouped unresolved comments`** from **`--full`** JSON |

### Fetch normalized JSON

```bash
# From repository root (uses origin remote for owner/repo)
"$GSDIR/gh-fetch" pr 336
"$GSDIR/gh-fetch" issue 42

# Explicit repository
"$GSDIR/gh-fetch" pr 336 --owner snyk --repo cli

# From URL
"$GSDIR/gh-fetch" pr --url https://github.com/snyk/cli/pull/336

# Save for bootstrap
"$GSDIR/gh-fetch" pr 336 -o /tmp/pr_336.json

# Full PR fetch for github-pr-comment-analysis (threads + conversation)
"$GSDIR/gh-fetch" pr 336 --full
"$GSDIR/gh-fetch" pr --url https://github.com/snyk/cli/pull/336 --full
```

**`--full`** (pull requests only) adds:

- **`review_threads`** — inline review threads via GraphQL (`is_resolved`, per-comment `url`, `path`, `line`)
- **`conversation_comments`** — timeline comments on the PR (REST `issues/{n}/comments`)
- **`review_thread_count`** / **`unresolved_review_thread_count`** — summary counts
- Slim normalized **`reviews`** and **`review_comments`** (overview always includes these when owner/repo are known)

Use **`--full`** before **`github-pr-comment-analysis`** grouping. Bootstrap and overview-only tasks can omit it.

Mechanical first pass (optional):

```bash
python3 "$GSDIR/bootstrap_github_artifact.py" --fetch --pr 2308 --owner django-cms --repo django-cms
ART="$ARTIFACTS/pr-2308/review_pr_2308.md"   # resolve via resolve_artifact_path.py
python3 "$GSDIR/apply_pr_thread_groups.py" --fetch --pr 2308 --owner django-cms --repo django-cms --artifact "$ART"
```

Then enrich **`### issue_*`** blocks in the artifact (technical analysis, verdict, proposed changes) per **`github-pr-comment-analysis`**.

Set `GSDIR="$(python3 ~/.cursor/skills/scripts/agent_config.py --github-scripts-dir)"` once per shell.

### Bootstrap PR artifact

```bash
# Live fetch + bootstrap (default $ARTIFACTS/pr-<PR>/review_pr_<PR>.md)
python3 "$GSDIR/bootstrap_github_artifact.py" --fetch --pr 336

# From saved JSON
"$GSDIR/gh-fetch" pr 336 -o /tmp/pr_336.json
python3 "$GSDIR/bootstrap_github_artifact.py" --json /tmp/pr_336.json --pr 336

# Investigation-heavy layout
python3 "$GSDIR/bootstrap_github_artifact.py" --fetch --pr 336 --type analysis
```

### Bootstrap issue artifact

```bash
# Live fetch + bootstrap (default $ARTIFACTS/issue-<N>/triage_issue_<N>.md)
python3 "$GSDIR/bootstrap_github_artifact.py" --fetch --issue 16 --owner org --repo repo

# From saved JSON
"$GSDIR/gh-fetch" issue 16 --owner org --repo repo -o /tmp/issue_16.json
python3 "$GSDIR/bootstrap_github_artifact.py" --json /tmp/issue_16.json --issue 16

# Investigation-heavy layout
python3 "$GSDIR/bootstrap_github_artifact.py" --fetch --issue 16 --owner org --repo repo --type analysis
```

Omit **`--output`** to use the external artifact store (**`resolve_artifact_path.py`**). Preserves **`Follow-up Findings`** and **`Improvement Candidates`** when re-bootstrapping an existing artifact.

## API reference cache

1. Read **`$AGENT_CONFIG_HOME/api-docs/github-rest/`** first (`agent_config.py --api-docs-dir github-rest`).
2. On first use or when stale, summarize [GitHub REST API](https://docs.github.com/en/rest) docs into that directory.
3. Prefer cached endpoint notes before re-downloading.

## Workflow skill pairings

| Task | Skill / doc |
|------|-------------|
| PR comment grouping | **`github-pr-comment-analysis`** |
| Issue triage | **`github-issue-triage`** |
| Repo investigation after fetch | **`repository-technical-analysis`** |
| Concrete bug repro | **`diagnose`** |
| Test-first fix | **`tdd`** |
| Repo-specific PR overlay | e.g. **`cli-pr-comment-analysis`** |

Transport stays in **this policy**; triage, grouping, and code analysis stay in workflow skills.

## Safety

- Do not mix transport with triage, planning, or implementation policy here.
- Stop when authenticated GitHub access fails — do not guess from partial data.
- Treat GitHub **writes** (comments, labels, merges) as out of scope unless a workflow skill explicitly authorizes them.
- Do not duplicate fetch logic inside **`github-pr-comment-analysis`**, **`github-issue-triage`**, or overlays — refresh live state via **`gh`** / **`gh api`** per this doc, then hand off.
