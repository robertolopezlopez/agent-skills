---
name: cli-gaf-propagate
description: After pushing a go-application-framework (GAF) PR, rebase GAF PRs stacked on it, bump the GAF pin in the associated snyk/cli PR, fix affected CLI tests, then commit and force-push.
---

# CLI GAF Propagate

Propagate a pushed GAF PR head into its dependent GAF stack and its paired CLI PR.

## When to Use

Use right after pushing commits to a GAF PR that has a companion `snyk/cli` PR pinning it.

## When Not to Use

- Bumping GAF to `main` — run the CLI's documented `go run ./scripts/upgrade-snyk-go-dependencies.go -name=go-application-framework && make tidy` instead.
- Plain rebase of one PR — use `gh-pr-rebase`.

## Inputs

- GAF PR: URL, number, or branch; default is the checked-out branch's PR (`gh pr view --json number,url,headRefName,headRefOid,baseRefName`).
- CLI PR: URL or number; default is discovered from a `snyk/cli` PR link in the GAF PR body (`gh pr view --json body`), then by searching `snyk/cli` open PRs whose body links the GAF PR URL. Stop and ask when zero or several match.
- CLI checkout path; default is a sibling `../cli` of the GAF checkout.

## First Read

Synced `GITHUB-ACCESS.md`, `gh-stack`, `gh-pr-rebase`, and the CLI `AGENTS.md` (Commit Message Format, Pull Request Checks, Updating Go Dependencies).

## Workflow

1. **Confirm the GAF head is pushed.** In the GAF checkout, `git fetch origin` and compare `HEAD` with the PR `headRefOid`. If local is ahead, push it first; if they diverge, stop and ask. Record the pushed SHA as `GAF_SHA`.
2. **Rebase stacked GAF PRs.**
   - When `gh stack view --json` lists the PR branch: `gh stack rebase --upstack --remote origin` then `gh stack push --remote origin`. On exit 3, resolve with `git-rebase-conflict-resolver`, then `gh stack rebase --continue`.
   - Otherwise, for each open PR with `--base <headRefName>` (`gh pr list --base <headRefName> --json number,headRefName`), bottom-up: run `gh-pr-rebase` onto `origin/<headRefName>` and let it verify and force-push. Recurse for PRs based on those branches.
3. **Bump the CLI pin.** In the CLI checkout: `gh pr checkout <cli-pr>`, then

   ```bash
   cd cliv2 && go get github.com/snyk/go-application-framework@"$GAF_SHA" && cd .. && make tidy
   ```

   Never edit `go.sum` by hand. Verify `cliv2/go.mod` shows a pseudo-version ending in the 12-char `GAF_SHA` prefix.
4. **Fix affected CLI tests.** Build and run the narrowest relevant suites (`cd cliv2 && go build ./... && go test ./...`; TS suites via documented `npm run test:*` scripts only when the GAF change reaches them). Update tests whose expectations legitimately changed with the GAF diff; follow `cli-contributor` and `tdd`. A failure not explained by the GAF diff is a regression — stop and report, do not adapt the test.
5. **Commit and force-push.** Stage `cliv2/go.mod`, `cliv2/go.sum`, and test changes. If the CLI PR has one commit, `git commit --amend --no-edit`; otherwise `git commit -m "chore: bump go-application-framework to <short-sha>"` (Conventional Commits, no `!`, no attribution trailers). Then `git push --force-with-lease origin HEAD:<cli-headRefName>`.

## Validation

- `git range-diff` output from `gh-pr-rebase` shows no lost changes in every rebased GAF PR.
- `cliv2/go.mod` pin equals `GAF_SHA`; `go build ./...` and chosen tests pass; CLI PR head on GitHub equals the pushed commit.

## Outputs / Artifacts

Report: `GAF_SHA`, rebased GAF PR numbers, CLI PR URL, commit SHA, tests changed and commands run. No artifact.

## Companion Skills

`gh-stack`, `gh-pr-rebase`, `git-rebase-conflict-resolver`, `cli-contributor`, `tdd`, `cli-parallel-tests` for broad test runs, `cli-ci-monitor` to watch the resulting CI.

## Safety Notes

- Force-push only branches this workflow rebased or amended, always with `--force-with-lease`.
- Stop when CLI PR discovery is ambiguous, the GAF head diverges from the PR, or a test failure is not explained by the GAF diff.
