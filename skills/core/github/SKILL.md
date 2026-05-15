---
name: github
description: Fetch and normalize GitHub issue and pull request context, including repository identity, metadata, labels, comments, reviews, and links. Use when the user wants GitHub issue or PR data fetched, inspected, or prepared for downstream workflow skills.
---

# GitHub Issue and Pull Request Access

Use this skill from a GitHub repository root or when the user provides a GitHub issue or PR URL.

This skill is the source of truth for GitHub issue and PR identity, repository resolution, metadata fetch, comment fetch, and normalized GitHub context for companion skills.

## When to Use

Use this skill when the user wants to:

- fetch or inspect a GitHub issue
- fetch or inspect a GitHub pull request
- read issue comments
- read pull request comments, reviews, or review-comment data
- inspect labels, assignees, status, or timestamps
- prepare normalized GitHub context for a companion skill

## When Not to Use

Do not use this skill when:

- the task is only local Git repository inspection; use `git`
- the task is primarily issue-triage workflow, maintainer policy, or planning; use `github-issue-triage` or another workflow overlay instead of only this skill
- the task is primarily updating GitHub state rather than fetching or normalizing context
- the task is primarily repository-specific technical analysis or code changes; use the appropriate analysis or contributor skill after fetching GitHub context
- the repository is not hosted on GitHub

## Inputs

Accept, in order of preference:

- GitHub context that is already known from prior `github` usage
- an issue URL
- a pull request URL
- an object number when surrounding context already makes `issue` vs `pull_request` clear
- no explicit identifier, when the current repository context can be used to infer or verify the target object

Distinguish clearly between issues and pull requests.

If the user provides only a number, determine whether they mean an issue or a pull request from:

- the user's wording
- the current task context
- the current repository context

If ambiguity remains, ask before proceeding.

Extract and reuse these canonical fields consistently:

- repository owner
- repository name
- object type: `issue` or `pull_request`
- object number

For GitHub URLs, parse:

- host
- owner
- repository name
- object type
- object number

Canonical URL shapes:

```text
https://github.com/<owner>/<repo>/issues/<number>
https://github.com/<owner>/<repo>/pull/<number>
```

## First Read

- Read the repository `AGENTS.md` before running commands.
- Prefer GitHub MCP when available.
- Fall back to `gh` for common reads.
- Fall back to `gh api` when structured fields or review data are needed and `gh` output is insufficient.
- Use the `git` skill first when local repository identity or remote-host verification is needed.

## Companion Skills

Use this skill as the transport and normalization layer.

Common pairings:

- `git` for local repository identity and remote inspection
- `github-pr-comment-analysis` when the user wants PR comments grouped into actionable issues and work-plan artifacts
- `github-issue-triage` when the task is maintainer-facing issue triage
- `repository-technical-analysis` when GitHub issue or PR context leads into technical investigation
- `diagnose` when a fetched GitHub bug report leads into focused debugging
- `tdd` when a fetched GitHub issue or PR leads into test-first implementation

## Workflow

1. Start in the target repository root when local repository context is available.
2. If GitHub context is already known from prior `github` usage, reuse it.
3. If the input is a URL, parse host, owner, repository name, object type, and object number first.
4. If there is no explicit URL and repository identity is needed, use the `git` skill to inspect remotes and verify the repository is hosted on GitHub.
5. If the user gave only a number, determine whether they mean an issue or a pull request from the current wording and context.
6. If ambiguity still remains, ask before fetching.
7. If the repository is not hosted on GitHub, stop and report that instead of continuing with GitHub transport.
8. Prefer GitHub MCP for object fetch and metadata inspection when available.
9. If GitHub MCP is unavailable or insufficient, use `gh` for common reads:
   - issue overview
   - PR overview
   - comments
   - labels
   - assignees
10. If structured fallback data is still needed, use `gh api`.
11. Normalize and preserve:
    - repository owner
    - repository name
    - object type
    - object number
    - canonical URL
    - state
    - labels
    - assignees
    - author
    - created and updated timestamps
    - body
    - comments, reviews, or review-comment data when requested
12. Return normalized GitHub context for downstream skills.

## Transport Preference

Preferred order:

1. GitHub MCP for issues, pull requests, comments, reviews, and structured metadata
2. `gh` for common issue and PR reads
3. `gh api` for structured fallback when MCP or `gh` output is insufficient

Use the same normalized output contract regardless of transport so companion skills do not depend on how GitHub data was accessed.

## Fallback Command Pattern

Preferred issue fetch:

```bash
gh issue view <number>
```

Issue fetch with comments:

```bash
gh issue view <number> --comments
```

Preferred PR fetch:

```bash
gh pr view <number>
```

PR fetch with comments:

```bash
gh pr view <number> --comments
```

Structured issue fallback:

```bash
gh api repos/<owner>/<repo>/issues/<number>
```

Structured PR fallback:

```bash
gh api repos/<owner>/<repo>/pulls/<number>
```

Issue comments fallback:

```bash
gh api repos/<owner>/<repo>/issues/<number>/comments
```

PR review comments fallback:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments
```

PR reviews fallback:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/reviews
```

## Validation

- Prefer GitHub MCP first when available.
- Keep transport behavior separate from workflow logic.
- Verify `issue` vs `pull_request` before fetching when the identifier is ambiguous.
- Keep the same normalized object contract regardless of transport.
- Stop when authenticated GitHub access fails and report the missing access clearly.

## Outputs / Artifacts

This skill should return the most useful normalized GitHub result for the task, such as:

- issue summary and metadata
- PR summary and metadata
- labels and assignees
- issue comments
- PR comments, reviews, or review-comment data
- normalized GitHub context for downstream skills

This skill does not need to write a local artifact by default.

## Safety Notes

- Do not mix transport access with triage or planning policy in this skill.
- Stop when authenticated GitHub access fails instead of guessing from incomplete data.
- Do not assume a numbered object is an issue or PR without verification when the context is ambiguous.
- Treat write or update operations as out of scope for this version unless the skill is explicitly expanded later.
