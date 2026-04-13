---
name: gitlab
description: Fetch and inspect GitLab merge requests and their discussions. Use when given an MR IID or URL and asked to fetch merge request details with `glab`, read comments or discussion threads, inspect structured discussion data with `glab api`, extract the MR IID from a URL, or prepare GitLab MR context for another companion skill.
---

# GitLab Merge Request Access

Use this skill from a GitLab repository root when the user wants merge request data fetched or inspected.

## First Read

- Read the repository `AGENTS.md` before running commands.
- Use `glab` to fetch the merge request overview and its comment threads.
- Use `glab api` when structured discussion data is needed.
- Pair this skill with a repository-specific or workflow-specific companion skill when the user wants deeper technical analysis, implementation planning, or code changes.

## Inputs

Require a merge request parameter:

- MR IID like `123`
- or an MR URL that contains the IID

Extract the IID first and use that single value consistently in commands, filenames, and reporting.

## Workflow

1. Start in the target repository root.
2. Read the MR overview and comments with `glab mr view <MR> --comments`.
3. If needed, inspect structured discussion data for the same MR with `glab api`.
4. Distinguish:
   - unresolved vs resolved review threads
   - human comments vs system notes
   - actionable review comments vs non-actionable chatter
5. Preserve direct MR links and direct comment links when available.
6. When the follow-on task needs unresolved comments only, exclude resolved threads.
7. When the follow-on task needs comment status, note whether:
   - the author is still waiting on a reply
   - you have already replied and are waiting for author feedback
8. Keep GitLab-specific fetch, discussion, and link-handling logic here. Leave repository-specific technical analysis to companion skills.

## Command Pattern

Preferred MR overview and comments fetch:

```bash
glab mr view <MR> --comments
```

Structured discussion fetch when needed:

```bash
glab api /projects/:id/merge_requests/<MR>/discussions
```

## Notes

- Prefer `glab mr view` first, then use `glab api` only when structured discussion data is needed.
- Extract the MR IID once and reuse it consistently.
- Do not assume resolved comments are actionable unless the user asks for them.
- Keep GitLab transport and discussion inspection logic in this skill; let overlays add workflow-specific outputs and repository-specific conclusions.
