---
name: fast-grep
description: >-
  Find occurrences of a text slice in the current directory tree using a
  speed-ordered search fallback chain (rg, ugrep, ag, git grep, ack, POSIX
  grep, then agent Grep or SemanticSearch). Asks the user before installing
  missing fast host tools with OS-appropriate commands. Use when the user or a
  companion skill needs to locate strings, symbols, imports, config keys, or
  other literal text under the active workspace without opening every file
  manually.
---

# Fast Grep

Search the **current directory tree** for a literal or regex **text slice** (pattern). **Default: always use the fastest install-offer tool** (`rg`, then `ugrep`, then `ag`). The helper **refuses slower fallbacks** (for example `ag` when `rg` is missing) until the user installs the faster tool or explicitly declines and you re-run with **`--allow-slower`**.

## When to Use

Use this skill when the task needs to:

- find where a string, symbol, function name, import, or config key appears
- count or list matches across the active repository or a subdirectory
- narrow investigation before reading files or running deeper analysis
- replace ad-hoc `grep -R` with a consistent, ignore-aware search order

## When Not to Use

Do not use this skill when:

- the goal is semantic or meaning-based discovery ("how does auth work?") — use **SemanticSearch** instead of literal grep
- the task is remote transport (GitHub, GitLab, Jira) — use the matching transport skill
- the user already named a single file and line — read that file directly

## Inputs

Accept any of:

- **pattern** — literal text or regex to find (required)
- **path** — directory or file under the workspace (default: `.`, the current directory tree root)
- **glob** — optional file filter (for example `*.py`, `*.{ts,tsx}`)
- **case** — `sensitive` (default) or `insensitive`

Treat `{current-directory-tree}` as the workspace root or the user's stated subdirectory, resolved from the active shell cwd when possible.

## Workflow

1. Confirm **pattern** and **path** (default `.`). Note whether the match should be literal or regex.
2. **Resolve the host tool** before searching:
   - Run **`fast-grep/scripts/fast-grep-resolve --chain`** to see which tiers are `ok` or `missing`.
   - Run **`fast-grep/scripts/fast-grep-resolve --missing`** to get the first missing **install-offer** tier (`rg`, `ugrep`, or `ag`) plus an OS-specific **`install_cmd`** when available.
3. **Install permission loop** (repeat until search succeeds or exit **4**):
   - On exit **5**, **ask the user** whether to install the printed **`install_cmd`**.
   - **Do not install** unless the user explicitly agrees (see **AGENTS.md**).
   - **User accepts** → run **`install_cmd`**, verify with `command -v <binary>`, re-run step 4.
   - **User declines** → write **`fast-grep.env`** immediately, then re-run step 4:

```bash
fast-grep/scripts/fast-grep-prefs.sh decline <tool>
```

   - **User asks to change search tool** (for example *"use ag"*, *"switch to rg"*, *"don't ask for ripgrep"*) → **update `fast-grep.env` directly before searching** — do not only answer in chat:

```bash
fast-grep/scripts/fast-grep-prefs.sh use <tool>
# aliases: rg, ugrep, ag, git, ack, grep
# or: fast-grep/scripts/fast-grep use <tool>
```

   - **`use`** sets **`PREFERRED_SEARCH_TOOL`** and declines faster install-offer tiers so install prompts match the user's choice.
   - **`accept ripgrep`** (or **`fast-grep-prefs.sh accept rg`**) removes a decline when the user wants the fastest tool again.
   - Config file: **`fast-grep.env`** under the agent config home (**`scripts/agent_config.py --fast-grep-env`**). Cursor: `~/.cursor/fast-grep.env`; Codex: `~/.codex/fast-grep.env`; override with **`AGENT_CONFIG_HOME`**. Inspect with **`fast-grep-prefs.sh show`**.
   - After each decline, step 4 offers the **next** missing install-offer tier. When all three are declined or a **`use`** preference is set, the helper searches with the chosen or fastest remaining binary automatically.
   - Offer installs only for **`rg`**, **`ugrep`**, and **`ag`**. Do not prompt to install `git`, `ack`, or POSIX `grep`.
4. Run the bundled helper (strict by default — does **not** silently use `ag` when `rg` is missing):

```bash
fast-grep/scripts/fast-grep 'PATTERN' [PATH]
fast-grep/scripts/fast-grep --literal 'exact slice' src/
fast-grep/scripts/fast-grep -i 'pattern' --glob '*.go' .
```

5. If the helper exits with code **5**, follow step 3 (install or **`fast-grep-prefs.sh decline`**, then re-run step 4).
6. If the helper exits with code **4** (no host search CLI available), use the **agent search fallback** in step 7.
7. **Agent search fallback** (last resort — Cursor built-in tools):
   - **Grep** tool — ripgrep-backed search; pass `pattern`, optional `path`, `glob`, `-i`, context flags.
   - **SemanticSearch** — when the slice is uncertain, misspelled, or the user cares about behavior rather than exact text; query by meaning, then confirm hits with **Grep** or file reads.
8. Present results as **path:line:content** (or grouped by file). Cap very large result sets; offer to refine pattern, path, or glob.
9. Open only the most relevant files for the next step (definition, call sites, tests).

### Install permission example

When `rg` is missing but `ag` is present:

1. `fast-grep/scripts/fast-grep 'PATTERN'` exits **5** and prints `tool_id=ripgrep`, `install_cmd=brew install ripgrep` (on macOS with Homebrew). It does **not** search with `ag`.
2. Ask: *"ripgrep (`rg`) is the fastest search tool and is not installed. Install with `brew install ripgrep`?"*
3. **Yes** → run install, re-check `command -v rg`, re-run `fast-grep` (now uses `rg`).
4. **No** → `fast-grep/scripts/fast-grep-prefs.sh decline ripgrep` (writes `~/.cursor/fast-grep.env` or Codex equivalent), then re-run `fast-grep 'PATTERN'`.
5. Next run exits **5** for `ugrep` if still missing (ask again), or searches with **`ag`** when `ugrep` is also declined/missing. No **`--allow-slower`** flag needed for the normal decline path.

## Search tool order (fastest → slowest)

The helper and manual invocations try tools **in this order**; stop at the first one on `PATH`:

| Priority | Tool | Binary | Speed tier | Install offer | Notes |
|----------|------|--------|------------|---------------|-------|
| 1 | [ripgrep](https://github.com/BurntSushi/ripgrep) | `rg` | Fastest | Yes | Parallel, SIMD; respects ignore files |
| 2 | [ugrep](https://github.com/Genivia/ugrep) | `ugrep` | Very fast | Yes | Competitive with `rg` on many trees |
| 3 | [The Silver Searcher](https://github.com/ggreer/the_silver_searcher) | `ag` | Very fast | Yes | C-based; respects `.gitignore` |
| 4 | git grep | `git` | Fast (scoped) | No | Inside a Git work tree; tracked files only |
| 5 | [ack 3](https://github.com/beyondgrep/ack3) | `ack` | Moderate | No | Perl-based; portable |
| 6 | POSIX grep | `grep` | Slowest host | No | `grep -R`; manual `--exclude-dir` for vendor trees |
| 7 | Agent tools | Grep, SemanticSearch | Last | No | When no suitable host CLI is available |

Do not skip earlier tiers when their binary is available.

### OS-transparent install commands

Resolve installs with **`fast-grep/scripts/install-cmd.sh <tool_id>`** (`tool_id`: `ripgrep`, `ugrep`, `silver_searcher`, `ack`). It picks one command for the detected OS:

| OS / package manager | Examples |
|----------------------|----------|
| macOS + Homebrew | `brew install ripgrep` |
| Debian/Ubuntu + apt | `sudo apt update && sudo apt install -y ripgrep` |
| Arch + pacman | `sudo pacman -S --noconfirm ripgrep` |
| Fedora/RHEL + dnf | `sudo dnf install -y ripgrep` |
| Windows + winget | `winget install --id BurntSushi.ripgrep.MSVC -e` |
| Windows + Scoop | `scoop install ripgrep` |
| Windows + Chocolatey | `choco install ripgrep -y` |

When no package manager matches, print the vendor URL from the helper stderr and ask the user to install manually.

### Manual equivalents

When not using the helper, mirror the same order:

```bash
# 1 — rg
rg --no-heading --line-number 'PATTERN' PATH

# 2 — ugrep
ugrep -n --color=never 'PATTERN' PATH

# 3 — ag
ag --nogroup --nocolor --numbers 'PATTERN' PATH

# 4 — git grep (from repo root)
git grep -n 'PATTERN' -- PATH

# 5 — ack
ack --noheading --with-filename --line 'PATTERN' PATH

# 6 — POSIX grep
grep -R -n -H --exclude-dir=.git --exclude-dir=node_modules 'PATTERN' PATH
```

## Validation

- Run **`scripts/check_skill_prereqs.sh fast-grep`** or **`fast-grep-resolve --chain`** before advising installs.
- **Ask the user** before running any install command; **only install when they explicitly agree** (see **AGENTS.md**).
- After install, verify with `command -v <binary>` before searching.
- After a host search, spot-check at least one hit by reading the file slice.
- If zero matches, say so explicitly and try: case-insensitive search, parent directory, renamed symbol, or **SemanticSearch**.

## Outputs

Return:

- match list as **file:line:content** (sorted by path then line)
- which tool ran (`rg`, `ugrep`, `ag`, `git-grep`, `ack`, `grep`, or `agent-grep`)
- whether a host tool was installed during the session (and which command ran)
- total match count or a capped summary (for example "showing 50 of 312")
- optional next files to read (definition, tests, config)

No artifact is required unless a companion skill asks for one.

## Companion Skills

- `repository-technical-analysis` — **workflow owner** for investigation search (step 3); do not duplicate this skill's workflow in RTA **First Read** or **Companion Skills**
- Other direct vs inherited pairings: see **`docs/skill-schema.md`** (Fast-grep integration)

## Safety Notes

- Prefer ignore-aware tools (`rg`, `ugrep`, `ag`) over bare `grep -R` in large trees.
- Do not search outside the user-requested tree without saying so.
- Redact secrets if match lines contain tokens, passwords, or private keys in output.
- Very broad patterns (for example `error`, `import`) need a tight `path` or `glob`.
- Never run `curl | bash` or other non-standard installers without explicit user approval.
