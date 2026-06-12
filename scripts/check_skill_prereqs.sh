#!/usr/bin/env bash
set -euo pipefail

# Report host CLI availability for agent skills. Suggests OS-appropriate installs; never installs.
#
# Usage:
#   check_skill_prereqs.sh [SKILL ...]
#   check_skill_prereqs.sh github gitlab
#   check_skill_prereqs.sh --all

usage() {
  cat <<'EOH'
Usage: check_skill_prereqs.sh [--all | SKILL ...]

Check whether host CLIs referenced by skills are on PATH. When a tool is
missing, print install suggestions for the detected OS and package managers.

Does not install anything.

Examples:
  check_skill_prereqs.sh github gitlab
  check_skill_prereqs.sh --all
EOH
}

OS_FAMILY=""
OS_NAME=""

detect_os() {
  OS_NAME=$(uname -s 2>/dev/null || echo unknown)
  case "$OS_NAME" in
    Darwin) OS_FAMILY=darwin ;;
    Linux) OS_FAMILY=linux ;;
    FreeBSD) OS_FAMILY=freebsd ;;
    MINGW*|MSYS*|CYGWIN*|Windows_NT) OS_FAMILY=windows ;;
    *)
      if [[ -n "${WINDIR:-}" || -n "${windir:-}" ]]; then
        OS_FAMILY=windows
        OS_NAME=Windows
      else
        OS_FAMILY=other
      fi
      ;;
  esac
}

has_brew() { command -v brew >/dev/null 2>&1; }
has_apt() { command -v apt-get >/dev/null 2>&1; }
has_dnf() { command -v dnf >/dev/null 2>&1; }
has_yum() { command -v yum >/dev/null 2>&1; }
has_pacman() { command -v pacman >/dev/null 2>&1; }
has_zypper() { command -v zypper >/dev/null 2>&1; }
has_winget() { command -v winget >/dev/null 2>&1; }
has_scoop() { command -v scoop >/dev/null 2>&1; }
has_choco() { command -v choco >/dev/null 2>&1; }
has_pkg() { command -v pkg >/dev/null 2>&1; }

# Resolve fast-grep install-cmd.sh (synced install or repo checkout).
fast_grep_install_cmd_sh() {
  local script_dir
  script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  if [[ -x "$script_dir/literal-search/install-cmd.sh" ]]; then
    printf '%s\n' "$script_dir/literal-search/install-cmd.sh"
    return 0
  fi
  return 1
}

# print_fast_grep_install TOOL_ID — one OS-specific command when install-cmd.sh exists.
print_fast_grep_install() {
  local tool_id=$1
  local installer cmd
  installer=$(fast_grep_install_cmd_sh) || return 1
  cmd=$("$installer" "$tool_id" 2>/dev/null) || return 1
  printf '       install_cmd: %s\n' "$cmd"
}

# suggest_install TOOL_ID LABEL VENDOR_URL
# Prints one or more "suggest:" lines based on OS and available package managers.
suggest_install() {
  local tool_id=$1
  local label=$2
  local vendor_url=$3
  local printed=0

  printf '       os: %s\n' "$OS_NAME"

  case "$tool_id" in
    gh)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install gh\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt update && sudo apt install gh\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install gh\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S github-cli\n'
          printed=1
        fi
      fi
      ;;
    glab)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install glab\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt update && sudo apt install glab || see vendor install\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install glab || see vendor install\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S glab\n'
          printed=1
        fi
      fi
      ;;
    jq)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install jq\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install jq\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install jq\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S jq\n'
          printed=1
        fi
      fi
      ;;
    ripgrep)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install ripgrep\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install ripgrep\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install ripgrep\n'
          printed=1
        fi
        if has_yum; then
          printf '       suggest (RHEL/yum): sudo yum install ripgrep\n'
          printed=1
        fi
        if has_zypper; then
          printf '       suggest (openSUSE): sudo zypper install ripgrep\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S ripgrep\n'
          printed=1
        fi
      fi
      if [[ "$OS_FAMILY" == freebsd ]] && has_pkg; then
        printf '       suggest (FreeBSD): pkg install -y ripgrep\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == windows ]]; then
        if has_winget; then
          printf '       suggest (Windows/winget): winget install --id BurntSushi.ripgrep.MSVC -e\n'
          printed=1
        fi
        if has_scoop; then
          printf '       suggest (Windows/Scoop): scoop install ripgrep\n'
          printed=1
        fi
        if has_choco; then
          printf '       suggest (Windows/Chocolatey): choco install ripgrep -y\n'
          printed=1
        fi
      fi
      ;;
    silver_searcher)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install the_silver_searcher\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install silversearcher-ag\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install the_silver_searcher\n'
          printed=1
        fi
        if has_yum; then
          printf '       suggest (RHEL/yum): sudo yum install the_silver_searcher\n'
          printed=1
        fi
        if has_zypper; then
          printf '       suggest (openSUSE): sudo zypper install the_silver_searcher\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S silver-searcher-git\n'
          printed=1
        fi
      fi
      if [[ "$OS_FAMILY" == freebsd ]] && has_pkg; then
        printf '       suggest (FreeBSD): pkg install -y silver-searcher\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == windows ]]; then
        if has_scoop; then
          printf '       suggest (Windows/Scoop): scoop install ag\n'
          printed=1
        fi
        if has_choco; then
          printf '       suggest (Windows/Chocolatey): choco install ag -y\n'
          printed=1
        fi
        if has_winget; then
          printf '       suggest (Windows/winget): winget install --id ggreer.the_silver_searcher -e\n'
          printed=1
        fi
      fi
      ;;
    ack)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install ack\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install ack\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install ack\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S ack\n'
          printed=1
        fi
      fi
      if [[ "$OS_FAMILY" == windows ]]; then
        if has_choco; then
          printf '       suggest (Windows/Chocolatey): choco install ack -y\n'
          printed=1
        fi
        if has_scoop; then
          printf '       suggest (Windows/Scoop): scoop install ack\n'
          printed=1
        fi
      fi
      ;;
    ugrep)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install ugrep\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install ugrep\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install ugrep\n'
          printed=1
        fi
        if has_yum; then
          printf '       suggest (RHEL/yum): sudo yum install ugrep\n'
          printed=1
        fi
        if has_zypper; then
          printf '       suggest (openSUSE): sudo zypper install ugrep\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S ugrep\n'
          printed=1
        fi
      fi
      if [[ "$OS_FAMILY" == freebsd ]] && has_pkg; then
        printf '       suggest (FreeBSD): pkg install -y ugrep\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == windows ]]; then
        if has_winget; then
          printf '       suggest (Windows/winget): winget install --id Genivia.ugrep -e\n'
          printed=1
        fi
        if has_scoop; then
          printf '       suggest (Windows/Scoop): scoop install ugrep\n'
          printed=1
        fi
        if has_choco; then
          printf '       suggest (Windows/Chocolatey): choco install ugrep -y\n'
          printed=1
        fi
      fi
      ;;
    parallel)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install parallel\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        if has_apt; then
          printf '       suggest (Debian/Ubuntu): sudo apt install parallel\n'
          printed=1
        fi
        if has_dnf; then
          printf '       suggest (Fedora/RHEL): sudo dnf install parallel\n'
          printed=1
        fi
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S parallel\n'
          printed=1
        fi
      fi
      ;;
    circleci)
      if [[ "$OS_FAMILY" == darwin ]] && has_brew; then
        printf '       suggest (macOS/Homebrew): brew install circleci\n'
        printed=1
      fi
      if [[ "$OS_FAMILY" == linux ]]; then
        printf '       suggest (Linux): see CircleCI local CLI install docs (often curl-based)\n'
        printed=1
      fi
      ;;
    *)
      ;;
  esac

  if [[ "$printed" -eq 0 ]]; then
    printf '       suggest: install %s from %s\n' "$label" "$vendor_url"
  else
    printf '       vendor: %s\n' "$vendor_url"
  fi
}

check_tool() {
  local binary=$1
  local tool_id=$2
  local label=$3
  local vendor_url=$4

  if command -v "$binary" >/dev/null 2>&1; then
    printf 'ok   %s (%s)\n' "$binary" "$label"
    return 0
  fi

  printf 'MISSING %s (%s)\n' "$binary" "$label"
  suggest_install "$tool_id" "$label" "$vendor_url"
  return 1
}

check_group() {
  local group=$1
  local missing=0
  case "$group" in
    github|github-access)
      check_tool gh gh "GitHub CLI" "https://cli.github.com/" || missing=$((missing + 1))
      ;;
    gitlab|git)
      check_tool glab glab "GitLab CLI" "https://gitlab.com/gitlab-org/cli/" || missing=$((missing + 1))
      ;;
    circleci)
      check_tool circleci circleci "CircleCI CLI" "https://circleci.com/docs/local-cli/" || missing=$((missing + 1))
      ;;
    jira|confluence)
      check_tool jq jq "JSON filter (optional)" "https://jqlang.org/" || true
      ;;
    investigate|repository-technical-analysis|diagnose)
      check_tool jq jq "JSON filter (optional)" "https://jqlang.org/" || true
      printf 'note: repository text search — LITERAL-CODE-SEARCH.md (agent_config.py --literal-search-policy; check_skill_prereqs.sh literal-search)\n'
      ;;
    parallel-tests|private-parallel-tests|private-service-parallel-tests)
      check_tool parallel parallel "GNU parallel (optional)" "https://www.gnu.org/software/parallel/" || true
      ;;
    fast-grep|literal-search)
      printf 'os: %s\n' "$OS_NAME"
      local fast_missing=0
      local offer_tools=(ripgrep:rg:ripgrep ugrep:ugrep:ugrep silver_searcher:ag:"The Silver Searcher")
      local entry tool_id binary label
      for entry in "${offer_tools[@]}"; do
        IFS=: read -r tool_id binary label <<<"$entry"
        if command -v "$binary" >/dev/null 2>&1; then
          printf 'ok   %s (%s)\n' "$binary" "$label"
          continue
        fi
        printf 'MISSING %s (%s)\n' "$binary" "$label"
        if ! print_fast_grep_install "$tool_id"; then
          case "$tool_id" in
            ripgrep) suggest_install ripgrep "$label" "https://github.com/BurntSushi/ripgrep" ;;
            ugrep) suggest_install ugrep "$label" "https://github.com/Genivia/ugrep" ;;
            silver_searcher) suggest_install silver_searcher "$label" "https://github.com/ggreer/the_silver_searcher" ;;
          esac
        fi
        [[ "$tool_id" == ripgrep ]] && fast_missing=$((fast_missing + 1))
      done
      if command -v git >/dev/null 2>&1; then
        printf 'ok   git (git grep, fast scoped)\n'
      else
        printf 'MISSING git (git grep, fast scoped)\n'
        fast_missing=$((fast_missing + 1))
      fi
      if command -v ack >/dev/null 2>&1; then
        printf 'ok   ack (ack3, moderate)\n'
      else
        printf 'MISSING ack (ack3, moderate)\n'
      fi
      if command -v grep >/dev/null 2>&1; then
        printf 'ok   grep (POSIX, slowest host)\n'
      else
        printf 'MISSING grep (POSIX, slowest host)\n'
        fast_missing=$((fast_missing + 1))
      fi
      printf 'note: ask the user before installing; use install_cmd or suggest lines for their OS (brew/apt/dnf/yum/pacman/zypper/winget/scoop/choco/pkg)\n'
      printf 'note: do not install packages yourself unless the user explicitly asks\n'
      if [[ "$fast_missing" -gt 0 ]]; then
        printf 'note: if install is declined, fall back to the next ok tier (git grep, grep) or agent Grep tool\n'
      fi
      ;;
    *)
      echo "unknown skill/group: $group" >&2
      return 2
      ;;
  esac
  return "$missing"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

detect_os

targets=()
if [[ "${1:-}" == "--all" ]]; then
  targets=(github gitlab git circleci jira confluence investigate literal-search parallel-tests)
elif [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
else
  targets=("$@")
fi

total_missing=0
seen=""
for raw in "${targets[@]}"; do
  group=$raw
  case "$raw" in
    github-pr-comment-analysis|github-issue-triage) group=github ;;
    gitlab-mr-comment-analysis) group=gitlab ;;
    private-parallel-tests|private-service-parallel-tests) group=parallel-tests ;;
    repository-technical-analysis|diagnose) group=investigate ;;
  esac
  case " $seen " in
    *" $group "*) continue ;;
  esac
  seen="$seen $group"
  echo "==> $group"
  check_group "$group" || total_missing=$((total_missing + $?))
done

if [[ "$total_missing" -gt 0 ]]; then
  echo ""
  echo "Some required or recommended tools are missing. Ask the user to install using the suggestion that matches their OS, then run check_skill_config.sh for auth/defaults (see AGENTS.md)."
  exit 1
fi

exit 0
