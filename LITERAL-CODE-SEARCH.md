# Literal code search (canonical policy)

Portable literal search for **any repository**, **any OS**, and **any agent runtime** (Cursor, Codex, and similar). Config lives under **`$AGENT_CONFIG_HOME`**; helpers sync under **`$AGENT_CONFIG_HOME/skills/scripts/literal-search/`**.

## Order (agent-portable)

```text
1. Read fast-grep.env (when set) → preferred host CLI
2. First time only: discover chain → ask install or use <tool> → write fast-grep.env
3. Host chain: rg → ugrep → ag → git grep → ack → POSIX grep
4. Last literal resort: agent Grep tool (when the runtime provides it)
```

**SemanticSearch** — behavioral / vague queries only; not a literal fallback.

## OS portability

Literal search defers to **Missing CLI tools — ask before fallback** in **`AGENTS.md`**. Summary:

1. **Detect the host OS** — helpers use **`uname -s`** and available package managers. Run **`check_skill_prereqs.sh literal-search`** for an audit (`os:` line + per-tool status).
2. **Never assume macOS/Homebrew** — offer the command that matches the user's platform (`brew`, `apt`, `dnf`, `yum`, `pacman`, `zypper`, `winget`, `scoop`, `choco`, `pkg`, or vendor docs).
3. **Ask before installing** — show **`install_cmd`** from **`fast-grep-resolve --missing`** or **`suggest (...)`** lines from **`check_skill_prereqs.sh`**. **Do not run install** unless the user explicitly asks.
4. **Universal fallbacks** — **`git grep`** (in a git repo) and POSIX **`grep`** are expected on macOS, Linux, BSD, and Windows Git Bash/WSL; prefer faster tiers when available.
5. **Helper runtime** — bash scripts require **bash** (macOS, Linux, BSD, Git Bash, WSL). Path resolution uses **`python3`** (or **`python`** when `python3` is missing on Windows).

| OS family | Typical install paths (verify with helpers) |
|-----------|---------------------------------------------|
| macOS | Homebrew (`brew install ripgrep`) |
| Debian/Ubuntu | `apt` (`sudo apt install ripgrep`) |
| Fedora/RHEL | `dnf` / `yum` |
| Arch | `pacman` |
| openSUSE | `zypper` |
| FreeBSD | `pkg` |
| Windows | `winget`, Scoop, Chocolatey; or Git Bash/WSL + Linux package manager |

When **`install_cmd`** is empty, run **`check_skill_prereqs.sh literal-search`** and use the **`suggest (...)`** line for the detected OS, or the vendor URL from **`install-cmd.sh`** stderr.

## Path resolution

Resolve runtime paths once per session (do not assume repo-relative `scripts/` exists outside **agent-skills**):

| What | Resolver |
|------|----------|
| Config home | `agent_config.py --config-home` |
| **`fast-grep.env`** | `agent_config.py --fast-grep-env` |
| **Policy doc (this file)** | `agent_config.py --literal-search-policy` |
| **Helper scripts** | `agent_config.py --literal-search-dir` |
| Skills scripts root | `agent_config.py --skills-root` |

**Portable helper discovery** (Cursor or Codex — copy/paste as one block):

```bash
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
ACFG=""
for candidate in "$HOME/.cursor/skills/scripts/agent_config.py" "$HOME/.codex/skills/scripts/agent_config.py"; do
  if [[ -f "$candidate" ]]; then ACFG=$candidate; break; fi
done
LSDIR="$($PY "$ACFG" --literal-search-dir)"
PREREQS="$(dirname "$ACFG")/check_skill_prereqs.sh"
```

Override runtime with **`AGENT_CONFIG_HOME`** or **`AGENT_SKILLS_RUNTIME`** (`cursor` | `codex`).

**Cursor only (optional):** install **`templates/cursor/rules/literal-code-search.mdc`** with **`./scripts/bootstrap_literal_search.sh --cursor-rule`** for always-on policy in every project.

## Helpers

| Script | Purpose |
|--------|---------|
| **`fast-grep-prefs.sh`** | Read/write **`fast-grep.env`** (`show`, `use`, `decline`, `accept`, `clear`) |
| **`fast-grep-resolve`** | First-time discover (`--chain`, `--missing` includes `os=` + `install_cmd`) |
| **`install-cmd.sh`** | One OS-appropriate install command (`ripgrep`, `ugrep`, `silver_searcher`, `ack`) |
| **`fast-grep`** | Host CLI runner (strict install gate; exit 5 / 4) |

## Workflow

### Later runs (prefs set)

```bash
"$LSDIR/fast-grep-prefs.sh" show
# then host rg/ag/… directly, or:
"$LSDIR/fast-grep" --literal 'PATTERN' [PATH]
```

Do **not** re-run `--chain` / `--missing` when `PREFERRED_SEARCH_TOOL` is set and the binary is on `PATH`.

### First time (empty env)

```bash
"$LSDIR/fast-grep-resolve" --missing    # includes os= and install_cmd when known
"$PREREQS" literal-search               # OS audit + suggest lines
# ask user → install OR:
"$LSDIR/fast-grep-prefs.sh" use rg      # or decline / use ag
"$LSDIR/fast-grep" --literal 'PATTERN' [PATH]
```

### In IDE agents (Cursor and similar)

Prefer **agent Grep tool** for literals when shell is unnecessary. Use host CLI + **`fast-grep.env`** for shell, CI, headless Codex, or when install gates matter.

### Exit codes (`fast-grep` runner)

| Code | Action |
|------|--------|
| **5** | Faster install-offer tool missing — ask user with **OS-appropriate** `install_cmd`; on decline `fast-grep-prefs.sh decline` |
| **4** | No host CLI — **agent Grep tool** if runtime provides it |
| **0** | Success |

## Prereqs

```bash
"$PREREQS" literal-search
# alias: fast-grep
```

## agent-skills repository checkout

When working **inside this repo**, repo-relative paths also work for development:

- `scripts/literal-search/…`
- `docs/literal-code-search.md` (pointer to this file)

Prefer synced / resolver paths above when the agent is in **another** repository.

## Migration

See **`docs/fast-grep-migration.md`** for the completed move from the removed **`fast-grep`** installable skill.
