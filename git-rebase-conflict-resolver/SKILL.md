---
name: git-rebase-conflict-resolver
description: Rebase a Git branch onto a user-provided target branch, defaulting to origin/main, resolve merge or rebase conflicts by preserving compatible intent from both remote and local changes, complete interrupted rebases, and verify the rebased branch with the repository's real lint, format, and test commands. Use when Codex is asked to rebase onto origin/main or another specified branch, fix conflicts, keep both sides' changes where possible, or ensure the final branch still works after history rewrite.
---

# Git Rebase Conflict Resolver

Take an optional target branch input. Default to `origin/main`. Rebase carefully. Merge intent, not markers.

## Input

- Accept an optional target branch.
- If the user provides a target branch, use it.
- If the user does not provide one, use `origin/main`.

## Inspect state first

- Run `git status --short --branch`.
- Detect whether a rebase is already in progress before starting a new one.
- If the worktree is dirty, separate unrelated user changes from rebase work.
- Do not overwrite or discard unrelated local changes.
- Refresh the chosen target branch with `git fetch` before rebasing.

## Start or resume

- If no rebase is in progress, run `git rebase <target-branch>`.
- If a rebase is already in progress, inspect the current conflict set and continue from there.
- Do not push unless the user explicitly asks.

## Resolve conflicts by behavior

For each conflicted file:

- Read the conflicted file with markers.
- Inspect Git stages when useful:
  - `:1:path` for merge base
  - `:2:path` for the rebased-onto branch
  - `:3:path` for the local commit being replayed
- During rebase, remember that `ours` is the target branch side and `theirs` is the replayed local commit side.
- Do not take `ours` or `theirs` wholesale unless the conflict is trivial and verified.
- Identify what changed on the target branch.
- Identify what the local commit intended to add or fix.
- Keep both changes when compatible.
- If both sides changed the same logic, produce a merged version that preserves the newer architecture and the useful behavior from the local branch.
- Use `git show ORIG_HEAD:path` when helpful to understand the branch state before the rebase began.
- Update tests together with code when the conflict changes behavior, call shape, or architecture.

## Continue cleanly

- Stage resolved files and run `git rebase --continue`.
- If Git opens an editor, continue non-interactively when appropriate, for example with `GIT_EDITOR=true git rebase --continue`.
- Repeat until the rebase completes.
- Skip a commit only after verifying its intended effect already exists on the target branch.

## Validate the result

Use the repository's real validation flow.

- Read repo guidance from files such as `AGENTS.md`, `Makefile`, `pyproject.toml`, `package.json`, or CI config.
- Run lint first when fast.
- Run the formatter if required, then rerun lint.
- Run targeted tests for the modules touched by the conflict.
- Run broader tests if the conflict affected shared infrastructure, schemas, core models, or cross-cutting utilities.
- If validation fails, fix the branch before considering the rebase complete.

## Report the outcome

State:

- which branch was rebased onto which target branch
- whether the target branch was user-provided or defaulted to `origin/main`
- which files required manual conflict resolution
- how the important conflicts were merged
- which validation commands were run
- whether they passed
- whether the worktree is clean
- whether the branch now diverges from its remote because history was rewritten

## Safety rules

- Never use destructive resets unless explicitly requested.
- Never discard unrelated local changes.
- Never claim both sides were preserved without verifying the merged code path.
- Never stop after resolving conflicts without running relevant validation.
