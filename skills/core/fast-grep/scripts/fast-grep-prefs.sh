#!/usr/bin/env bash
set -euo pipefail

# Read/write fast-grep runtime preferences in fast-grep.env (agent config home).
#
# Usage:
#   fast-grep-prefs.sh path | show
#   fast-grep-prefs.sh use <tool>       # user choice — writes fast-grep.env directly
#   fast-grep-prefs.sh decline <tool_id>
#   fast-grep-prefs.sh accept <tool_id>
#   fast-grep-prefs.sh clear

FAST_GREP_ENV_BASENAME=fast-grep.env
INSTALL_OFFER_IDS=(ripgrep ugrep silver_searcher)
VALID_TOOL_IDS=(ripgrep ugrep silver_searcher git ack grep)

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

resolve_agent_config_sh() {
  local candidate
  for candidate in \
    "$SCRIPT_DIR/../../scripts/agent-config.sh" \
    "$SCRIPT_DIR/../../../../scripts/agent-config.sh"; do
    if [[ -f "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

init_config_home() {
  local agent_config
  agent_config=$(resolve_agent_config_sh) || {
    echo "fast-grep-prefs: agent-config.sh not found" >&2
    exit 2
  }
  # shellcheck source=/dev/null
  . "$agent_config"
  agent_config_init "$SCRIPT_DIR"
}

env_file_path() {
  init_config_home
  agent_config_env_path "$FAST_GREP_ENV_BASENAME"
}

ensure_env_file() {
  local file
  file=$(env_file_path)
  if [[ ! -f "$file" ]]; then
    mkdir -p "$(dirname "$file")"
    cat >"$file" <<'EOF'
# fast-grep preferences — see templates/fast-grep.env.example in agent-skills
DECLINED_INSTALL_OFFERS=
PREFERRED_SEARCH_TOOL=
EOF
  fi
  printf '%s' "$file"
}

read_env_var() {
  local name=$1
  local file line
  file=$(ensure_env_file)
  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
      \#*|"") continue ;;
      "${name}"=*)
        printf '%s' "${line#${name}=}"
        return 0
        ;;
    esac
  done <"$file"
  return 0
}

write_env_var() {
  local name=$1
  local value=$2
  local file tmp
  file=$(ensure_env_file)
  tmp=$(mktemp)
  grep -v "^${name}=" "$file" >"$tmp" || true
  printf '%s=%s\n' "$name" "$value" >>"$tmp"
  mv "$tmp" "$file"
}

normalize_tool() {
  local raw
  raw=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  case "$raw" in
    rg|ripgrep) printf '%s' ripgrep ;;
    ugrep) printf '%s' ugrep ;;
    ag|silver-searcher|silver_searcher|the_silver_searcher) printf '%s' silver_searcher ;;
    git|git-grep|git_grep) printf '%s' git ;;
    ack|ack3) printf '%s' ack ;;
    grep|posix_grep) printf '%s' grep ;;
    *)
      echo "fast-grep-prefs: unknown tool: $1 (try: rg, ugrep, ag, git, ack, grep)" >&2
      return 1
      ;;
  esac
}

valid_tool_id() {
  local id=$1
  local v
  for v in "${VALID_TOOL_IDS[@]}"; do
    [[ "$v" == "$id" ]] && return 0
  done
  return 1
}

is_install_offer() {
  local id=$1
  local v
  for v in "${INSTALL_OFFER_IDS[@]}"; do
    [[ "$v" == "$id" ]] && return 0
  done
  return 1
}

read_declined_csv() {
  read_env_var DECLINED_INSTALL_OFFERS
}

write_declined_csv() {
  write_env_var DECLINED_INSTALL_OFFERS "$1"
}

csv_add() {
  local csv=$1
  local item=$2
  local part parts
  [[ -z "$item" ]] && return 0
  if [[ -z "$csv" ]]; then
    printf '%s' "$item"
    return 0
  fi
  IFS=',' read -ra parts <<<"$csv"
  for part in "${parts[@]}"; do
    [[ -n "$part" && "$part" == "$item" ]] && {
      printf '%s' "$csv"
      return 0
    }
  done
  printf '%s,%s' "$csv" "$item"
}

csv_remove() {
  local csv=$1
  local item=$2
  local part out=""
  [[ -z "$csv" ]] && return 0
  IFS=',' read -ra parts <<<"$csv"
  for part in "${parts[@]}"; do
    [[ -z "$part" || "$part" == "$item" ]] && continue
    if [[ -z "$out" ]]; then
      out=$part
    else
      out="$out,$part"
    fi
  done
  printf '%s' "$out"
}

is_declined() {
  local tool_id=$1
  local csv part parts
  csv=$(read_declined_csv)
  [[ -z "$csv" ]] && return 1
  IFS=',' read -ra parts <<<"$csv"
  for part in "${parts[@]}"; do
    [[ -n "$part" && "$part" == "$tool_id" ]] && return 0
  done
  return 1
}

faster_install_offers_than() {
  local target=$1
  local id
  for id in "${INSTALL_OFFER_IDS[@]}"; do
    [[ "$id" == "$target" ]] && break
    printf '%s\n' "$id"
  done
}

decline_tool() {
  local tool_id=$1
  is_install_offer "$tool_id" || {
    echo "fast-grep-prefs: decline applies only to: ripgrep, ugrep, silver_searcher" >&2
    exit 2
  }
  write_declined_csv "$(csv_add "$(read_declined_csv)" "$tool_id")"
  printf 'declined %s → %s\n' "$tool_id" "$(env_file_path)"
}

accept_tool() {
  local tool_id=$1
  is_install_offer "$tool_id" || {
    echo "fast-grep-prefs: accept applies only to: ripgrep, ugrep, silver_searcher" >&2
    exit 2
  }
  write_declined_csv "$(csv_remove "$(read_declined_csv)" "$tool_id")"
  local preferred
  preferred=$(read_env_var PREFERRED_SEARCH_TOOL)
  if [[ "$preferred" == "$tool_id" ]]; then
    write_env_var PREFERRED_SEARCH_TOOL ""
  fi
  printf 'accepted %s (removed from declined) → %s\n' "$tool_id" "$(env_file_path)"
}

use_tool() {
  local tool_id
  tool_id=$(normalize_tool "$1") || exit 2
  valid_tool_id "$tool_id" || exit 2

  local csv="" id preferred
  if is_install_offer "$tool_id"; then
    while IFS= read -r id; do
      [[ -n "$id" ]] && csv=$(csv_add "$csv" "$id")
    done < <(faster_install_offers_than "$tool_id")
    csv=$(csv_remove "$csv" "$tool_id")
    preferred=$tool_id
  else
    for id in "${INSTALL_OFFER_IDS[@]}"; do
      csv=$(csv_add "$csv" "$id")
    done
    preferred=$tool_id
  fi

  write_declined_csv "$csv"
  write_env_var PREFERRED_SEARCH_TOOL "$preferred"
  printf 'use %s (preferred=%s) → %s\n' "$1" "$preferred" "$(env_file_path)"
}

clear_prefs() {
  local file
  file=$(env_file_path)
  if [[ -f "$file" ]]; then
    write_declined_csv ""
    write_env_var PREFERRED_SEARCH_TOOL ""
    printf 'cleared fast-grep preferences in %s\n' "$file"
  fi
}

show_prefs() {
  local file
  file=$(ensure_env_file)
  printf 'file=%s\n' "$file"
  printf 'preferred=%s\n' "$(read_env_var PREFERRED_SEARCH_TOOL)"
  printf 'declined=%s\n' "$(read_declined_csv)"
}

usage() {
  cat <<'EOF'
Usage: fast-grep-prefs.sh <command> [args]

Commands:
  path                    Print resolved fast-grep.env path
  show                    Print preferred tool and declined install offers
  use TOOL                User choice — set preferred tool in fast-grep.env
                          (aliases: rg, ugrep, ag, git, ack, grep)
  decline TOOL_ID         Record declined install (ripgrep, ugrep, silver_searcher)
  accept TOOL_ID          Remove declined install; clear preferred if it matches
  clear                   Reset preferred and declined entries
  is-declined ID          Exit 0 when tool_id is declined; else exit 1
  preferred               Print PREFERRED_SEARCH_TOOL (empty if unset)
EOF
}

cmd=${1:-}
case "$cmd" in
  path)
    env_file_path
    ;;
  show)
    show_prefs
    ;;
  preferred)
    read_env_var PREFERRED_SEARCH_TOOL
    printf '\n'
    ;;
  declined-list)
    read_declined_csv
    printf '\n'
    ;;
  use)
    [[ $# -eq 2 ]] || {
      usage >&2
      exit 2
    }
    use_tool "$2"
    ;;
  decline)
    [[ $# -eq 2 ]] || {
      usage >&2
      exit 2
    }
    decline_tool "$(normalize_tool "$2" 2>/dev/null || printf '%s' "$2")"
    ;;
  accept)
    [[ $# -eq 2 ]] || {
      usage >&2
      exit 2
    }
    accept_tool "$(normalize_tool "$2" 2>/dev/null || printf '%s' "$2")"
    ;;
  clear)
    clear_prefs
    ;;
  is-declined)
    [[ $# -eq 2 ]] || {
      usage >&2
      exit 2
    }
    if is_declined "$2"; then
      exit 0
    fi
    exit 1
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
