---
name: gh-pr-rebase
description: Check a GitHub pull request for conflicts with local gh, resolve confirmed conflicts by rebasing onto the PR target branch, then force-push the rebased head branch.
---

# GitHub PR Rebase

Check one PR and rebase only when GitHub confirms a conflict.

## When to Use

Use for periodic PR conflict checks or conflict-triggered rebases.

## When Not to Use

For one metadata lookup, use `gh pr view` directly.

## Inputs

PR URL, number, or branch accepted by `gh pr view`.

## Workflow

1. Follow synced `GITHUB-ACCESS.md`; check `gh` availability and auth.
2. Resolve `scripts/check_pr.py` relative to this skill and run `scripts/check_pr.py '<pr>'`.
3. On `status=clean`, return without changing Git state. On `status=unknown`, stop and retry later.
4. On `status=conflict`, verify the checkout and remote match `headRefName` and the PR repository; stop if ambiguous.
5. Run `git-rebase-conflict-resolver` with `origin/<baseRefName>` and follow its conflict resolution, validation, push-safety, and reporting rules completely.
6. After successful validation, run `git push -f origin HEAD:<headRefName>`.

## Validation

Run `python3 -m unittest tests/test_gh_pr_rebase.py` after changing the command.

## Outputs / Artifacts

Return normalized PR JSON and, when rebased, the resolver and force-push results. Create no artifact.

## Companion Skills

- `git-rebase-conflict-resolver` for confirmed conflicts

## Safety Notes

- Never invoke the resolver for an ambiguous PR or unknown merge state.
- Force-push only the verified PR head branch and only after successful rebase validation.
