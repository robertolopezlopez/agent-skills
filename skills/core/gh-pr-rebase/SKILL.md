---
name: gh-pr-rebase
description: Check whether a GitHub pull request conflicts with or is behind its target, rebase while preserving source changes, then force-push the verified head branch.
---

# GitHub PR Rebase

Check one PR and rebase when GitHub reports a conflict or out-of-date branch.

## When to Use

Use for periodic PR checks or conflict/out-of-date-triggered rebases.

## When Not to Use

For one metadata lookup, use `gh pr view` directly.

## Inputs

PR URL, number, or branch accepted by `gh pr view`.

## Workflow

1. Follow synced `GITHUB-ACCESS.md`; check `gh` availability and auth.
2. Resolve `scripts/check_pr.py` relative to this skill and run `scripts/check_pr.py '<pr>'`.
3. On `status=clean`, return without changing Git state. On `status=unknown`, stop and retry later.
4. On `status=conflict` or `status=out_of_date`, verify the checkout and remote match `headRefName` and the PR repository; stop if ambiguous. Record the original head and its merge-base with `origin/<baseRefName>`.
5. Run `git-rebase-conflict-resolver` with `origin/<baseRefName>` and follow its conflict resolution, validation, push-safety, and reporting rules completely.
6. Run `git range-diff <original-base>..<original-head> origin/<baseRefName>..HEAD`. Confirm every original source change remains, either unchanged or intentionally adapted to the target; stop on unexplained loss.
7. After successful validation and range comparison, run `git push -f origin HEAD:<headRefName>`.

## Validation

Run `python3 -m unittest tests/test_gh_pr_rebase.py` after changing the command.

## Outputs / Artifacts

Return normalized PR JSON and, when rebased, the resolver and force-push results. Create no artifact.

## Companion Skills

- `git-rebase-conflict-resolver` for confirmed conflicts

## Safety Notes

- Never invoke the resolver for an ambiguous PR or unknown merge state.
- Force-push only the verified PR head branch after validation proves the original source changes remain.
