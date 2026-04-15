---
name: git
description: Inspect local Git repository state and derive metadata from configured remotes. Use when Codex needs information from `git remote -v`, must resolve a remote host or `<namespace>/<project>` path, or needs a helper operation such as resolving a GitLab numeric project ID before another skill calls an API.
---

# Git Repository Context

Use this skill for local Git-derived context that other skills can build on.

## Current capability

Resolve remote-derived project identity, including:

- remote URL
- remote host
- `<namespace>/<project>` path
- URL-encoded project path
- optional GitLab numeric project ID through `glab api`

This skill is intended to be reused by companion skills such as `gitlab`.

## Workflow

1. Start in the target repository root when possible.
2. Read `origin` first unless the user names another remote.
3. Prefer the helper script for repeatable parsing and machine-readable output.
4. If another skill needs a numeric GitLab project ID, call the helper with `--fetch-id`.
5. When rerunning similar repository-identity work, preserve durable learned sections such as `Resolved Repo Identity Notes`, `Remote URL Oddities`, and `Project ID Resolution Notes` when they still match the current remote configuration.

## Commands

Inspect remotes:

```bash
git remote -v
git config --get remote.origin.url
```

Resolve from the current repository:

```bash
python3 git/scripts/resolve_project_id.py
```

Resolve from an explicit remote URL:

```bash
python3 git/scripts/resolve_project_id.py --remote-url git@gitlab.example.com:group/project.git --json
```

Resolve and fetch a numeric GitLab project ID:

```bash
python3 git/scripts/resolve_project_id.py --fetch-id --json
```

## Output contract

When another skill needs repository identity, return these fields:

- `remote`
- `remote_url`
- `host`
- `project_path`
- `encoded_project_path`
- `project_id`

Expected behavior:

- set `project_id` when it can be resolved from GitLab
- otherwise leave `project_id` empty or `null`
- preserve nested groups in `project_path`
- URL-encode `/` as `%2F` in `encoded_project_path`

Companion-skill guidance:

- `gitlab` should prefer `project_id` for `/projects/<project_id>/...`
- if `project_id` is unavailable, fall back to `/projects/<encoded_project_path>/...`
- companion skills must decide whether the resolved `host` is compatible with their own platform-specific APIs

## Self-Improving Behavior

When rerunning repository identity resolution for the same checkout:

- preserve durable learned sections such as `## Resolved Repo Identity Notes`, `## Remote URL Oddities`, and `## Project ID Resolution Notes` when they still match the current remotes
- refresh conclusions from the live local Git configuration before reusing them
- record unusual remote formats, SSH aliases, or project ID lookup failures once with the shortest useful explanation
- demote, mark stale, or remove notes contradicted by changed remotes or updated lookup results

## Notes

- Prefer `origin` unless repository conventions say otherwise.
- Preserve nested groups exactly.
- Strip a trailing `.git` suffix before building a project path.
- Use this skill for Git transport and repository-context discovery; let companion skills handle GitLab merge requests, issues, and deeper workflows.
