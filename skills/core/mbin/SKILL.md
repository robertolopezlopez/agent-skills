---
name: mbin
description: Read, moderate, or act on an Mbin (joinmbin.org) instance through its OAuth2 REST API using the bundled `mbin-api` helper; handle client creation, token setup, user/magazine lookup, trash/restore, and bans.
---

# Mbin Access

Transport skill for Mbin instances. All HTTP goes through `scripts/mbin-api` (Python 3 stdlib, no deps); never raw `curl`.

## When to Use

- OAuth2 client/token setup for an Mbin instance
- lookups: current user, users, magazines, a user's entries/posts/comments
- moderator actions: trash/restore content, ban/unban in a moderated magazine, bulk-trash one user's content in a magazine
- arbitrary authenticated API calls when a convenience command is missing

## When Not to Use

- instance admin tasks (purge, defederation) unless the user is admin and asks explicitly
- content analysis or policy decisions — this skill only moves data

## Inputs

- instance URL (`MBIN_INSTANCE_URL`), usernames, magazine names, content type (`entry|post|comment|post-comment`) and numeric ids
- optional scopes for `client create` / `auth url` (default `read moderate user:profile:read`)

## First Read

- Resolve `scripts/mbin-api` relative to this skill. Run `mbin-api auth status` first; it prints the resolved `mbin.env` path and which keys are set without revealing values.
- Endpoint shapes: `https://<instance>/api/docs` (Swagger) or the runtime API cache slug `mbin-api` per `AGENTS.md`.

## Workflow

1. `mbin-api auth status`. If `MBIN_INSTANCE_URL` is missing, offer to copy `templates/mbin.env.example` to the printed path and let the user set the URL.
2. First-time auth (acts as the user, required for moderation; `client_credentials` creates a bot and cannot moderate):
   - `mbin-api client create --name <app> --email <contact>` — saves client id/secret
   - `mbin-api auth url` — user opens it, approves, copies the `code` from the redirect URL (nothing needs to listen on localhost)
   - `mbin-api auth code '<code-or-redirect-url>'` — saves access/refresh tokens; later calls auto-refresh
3. Lookups: `mbin-api me`, `mbin-api user <name>`, `mbin-api magazine <name>`, `mbin-api user-content <name> [--magazine M] [--types entry,post]` (JSON lines).
4. Moderation: `mbin-api trash <type> <id>`, `mbin-api restore <type> <id>`, `mbin-api ban <magazine> <user> [--reason R] [--expires ISO]`, `mbin-api unban <magazine> <user>`.
5. Bulk: `mbin-api trash-user <name> --magazine M` is a dry run; show the list, get explicit confirmation, then rerun with `--apply`.
6. Anything else: `mbin-api request METHOD /api/... [--param k=v] [--data '{json}']`.

## Validation

- Helper exits non-zero with `METHOD PATH -> status: body` on API errors; report that line, do not retry blindly.
- `403` on moderate endpoints means the token's user does not moderate that magazine or the client lacks `moderate` scope.
- Trash is reversible (`restore`); ban is reversible (`unban`). Purge is admin-only and not exposed.

## Outputs / Artifacts

JSON from the API, JSON lines for listings, and a count summary for bulk operations. No artifact by default.

## Companion Skills

None required. `repository-technical-analysis` only if the instance misbehaves.

## Safety Notes

- Mutations (`trash`, `restore`, `ban`, `unban`, `trash-user --apply`, non-GET `request`) require explicit user authorization in the current conversation.
- `mbin.env` holds secrets; the helper writes it `0600`. Never read it with the Read tool or print its values.
- Mods can only act in magazines they moderate; confirm the magazine name before bulk actions.
