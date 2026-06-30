---
name: git-rebase-conflict-resolver
description: Rebase a Git branch onto a user-provided target branch, defaulting to origin/main, resolve merge or rebase conflicts by preserving compatible intent from both remote and local changes, complete interrupted rebases, and verify the rebased branch with the repository's real lint, format, and test commands. Use when Codex is asked to rebase onto origin/main or another specified branch, fix conflicts, keep both sides' changes where possible, or ensure the final branch still works after history rewrite.
---

# Git Rebase Conflict Resolver

Take an optional target branch input. Default to `origin/main`. Rebase carefully. Merge intent, not markers.

## When to Use

Use this skill when the user wants to:

- rebase a branch onto `origin/main` or another target branch
- resolve rebase or merge conflicts carefully
- preserve compatible intent from both sides of a conflict
- validate the rebased branch before finishing

## When Not to Use

Do not use this skill when:

- the task is a non-rebase branch review with no history rewrite
- the user wants destructive reset behavior not tied to conflict-preserving rebase work
- the task is general Git repository context lookup rather than rebase execution

## Input

- Accept an optional target branch.
- If the user provides a target branch, use it.
- If the user does not provide one, use `origin/main`.

## First read

- Read repo guidance from `AGENTS.md`, `Makefile`, `pyproject.toml`, `package.json`, or CI config when choosing validation commands.
- Literal codebase search: follow synced **`LITERAL-CODE-SEARCH.md`** (`agent_config.py --literal-search-policy`) when conflict hunks need surrounding context.

## Inspect state first

- Run `git status --short --branch`.
- Detect whether a rebase is already in progress before starting a new one.
- If the worktree is dirty, separate unrelated user changes from rebase work.
- Do not overwrite or discard unrelated local changes.
- Refresh the chosen target branch with `git fetch` before rebasing.
- When rerunning similar rebases, preserve durable learned sections such as `Conflict Pattern Notes`, `Files With Recurring Conflicts`, and `Post-Rebase Validation Lessons` when they still match the current branch and conflict set.

## Literal codebase search (conflict context)

When a conflicted hunk is not self-explanatory — renamed symbols, moved imports, duplicate helpers, signature changes, or both sides touching the same call path — use **host literal search through Shell**, not the agent Grep tool, unless **`fast-grep`** exits **4** or Shell is unavailable.

1. Read **`fast-grep.env`** when set (`agent_config.py --fast-grep-env`); else run **`fast-grep-prefs.sh show`** once.
2. Search with **`fast-grep --literal 'PATTERN' [PATH]`** from **`agent_config.py --literal-search-dir`**, or run **`rg`** directly when it is the preferred/on-PATH tool.
3. Tighten scope: search the conflicted file's directory or package first; widen only when hits are insufficient.
4. Typical conflict probes:
   - symbols, types, or functions appearing in one side of the hunk but not the other
   - import paths changed on the target branch
   - callers of a merged API or shared config key
   - test files referencing the conflicted module
5. On **`fast-grep`** exit **5**, show **OS-appropriate** **`install_cmd`** from **`fast-grep-resolve --missing`** or **`check_skill_prereqs.sh literal-search`** — ask before installing; do not install unless the user asks.
6. On exit **4** only, fall back to the agent Grep tool if the runtime provides it.

Do not walk the tree manually when a host search tier is available. Prefer **`git grep`** inside the repo when faster tools are missing.

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
- When either side renames, moves, or reshapes a symbol, run **literal codebase search** (above) before merging so callers, imports, and tests stay consistent.
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
- When a validation step proves noisy or low-signal after conflict resolution, record it once in `Post-Rebase Validation Lessons` with the better follow-up command.

## Validation

- Refresh the chosen target branch before rebasing.
- Verify merged conflict resolution behavior from live files and Git stages, not just conflict markers.
- When resolution depended on call-site or import context, confirm findings with **host literal search** (`rg`, `fast-grep`, or documented fallback) rather than guesswork.
- Run relevant lint, format, and test commands before treating the rebase as complete.
- Keep unrelated local changes intact throughout the workflow.

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

## Outputs / Artifacts

This skill should produce:

- a rebased branch state
- a concise outcome report covering conflict resolution and validation

The report should include:

- target branch used
- files with manual conflicts
- important merge decisions
- validation commands run and results
- final worktree state

## Safety rules

- Never use destructive resets unless explicitly requested.
- Never discard unrelated local changes.
- Never claim both sides were preserved without verifying the merged code path.
- Never stop after resolving conflicts without running relevant validation.

## Self-Improving Behavior

When rerunning rebases for the same branch family or recurring conflict area:

- preserve durable learned sections such as `## Conflict Pattern Notes`, `## Files With Recurring Conflicts`, and `## Post-Rebase Validation Lessons` when they still match the current conflict set
- refresh conclusions against the live conflict markers, Git stages, and current validation output before reusing them
- promote repeated confirmed observations into short heuristics, preferably phrased like `when conflict touches X and Y, validate Z first`
- demote, mark stale, or remove heuristics contradicted by newer branch state or validation evidence

## Companion Skills

Common pairings:

- **`LITERAL-CODE-SEARCH.md`** + **`check_skill_prereqs.sh literal-search`** for host `rg` / `fast-grep` readiness
- **`GIT-ACCESS.md`** for repository identity and safe git operations
- repository-specific contributor skills for repo-local validation commands
- **`repository-technical-analysis`** when conflict resolution needs deeper investigation before merging intent

## Safety Notes

- Never use destructive resets unless explicitly requested.
- Never discard unrelated local changes.
- Never claim both sides were preserved without verifying the merged code path.
- Never stop after resolving conflicts without running relevant validation.
