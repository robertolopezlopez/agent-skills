---
name: mbin-purge-user
description: Purge one user's visible Mbin content with the bundled mbin transport, then ban that user from affected magazines for five years. Use when a moderator asks to delete a user's posts, threads, or comments and apply a time-limited magazine ban.
---

# Mbin Purge User

Workflow skill for one-user Mbin moderation. Reuse `mbin`; do not create ad hoc API clients or raw `curl`.

## When to Use

- Delete or trash all visible content by one Mbin user.
- Ban that user from every magazine where deleted content was found.
- Produce an auditable before/after moderation summary.

## When Not to Use

- Site-wide user bans, instance blocks, magazine deletion, or purge operations.
- Multi-user campaigns unless the user explicitly provides a list; handle users one at a time.

## Inputs

- Mbin username or profile URL, for example `@name@example.org` or `https://instance/u/name`.
- Optional ban duration; default **5 years** from today.
- Optional content scope; default `entry,post,comment,post-comment`.

## First Read

- Load `mbin` and run `mbin-api auth status`.
- Load `multi-spawn-agent` only when the user explicitly asks for parallel read-only inventory or validation and a work definition exists.

## Workflow

1. Resolve the user with `mbin-api user <username>`. Stop if the API cannot resolve the exact user.
2. Inventory before writing:
   - `mbin-api user-content <username> --types entry,post,comment,post-comment`
   - group by content type and magazine
   - show counts, magazines, and representative ids
3. Ask for confirmation unless the user already gave explicit current-turn authorization after seeing the inventory.
4. Apply in the main thread, not in workers:
   - `mbin-api trash <type> <id>` for each inventoried item
   - `mbin-api ban <magazine> <username> --expires <today+5y>`
5. If a ban returns 500, check whether the user moderates that magazine. Do not remove moderator roles unless explicitly requested.
6. Post-check:
   - rerun `mbin-api user-content` for the same types
   - report remaining visible items, trash failures, ban failures, and expiry date

## Multi-Spawn Rule

Use `multi-spawn-agent` only for read-only inventory or audit on large scopes. Never delegate mutation calls (`trash`, `ban`, moderator removal, magazine delete) to workers; keep writes sequential and locally summarized.

## Validation

- Treat `429` as incomplete inventory; wait and retry before writing.
- Treat empty text plus raw content `404` as likely removed, but report it.
- Store temporary JSON under `/tmp/mbin_<user>_*` when useful; do not store tokens.

## Outputs

- User id and username resolved.
- Counts by content type and magazine before writing.
- Number of items trashed and bans applied.
- Ban expiry and any failed operations.

## Companion Skills

Use `mbin` for all API transport and `multi-spawn-agent` only for optional read-only inventory or audit splits.

## Safety Notes

- Default action is soft-trash, not purge.
- Magazine bans are magazine-scoped; the skill cannot apply an admin site-wide ban.
- Confirm before broadening from one user to all authors, all magazines, or magazine deletion.
