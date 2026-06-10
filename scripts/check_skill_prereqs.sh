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
    *) OS_FAMILY=other ;;
  esac
}

has_brew() { command -v brew >/dev/null 2>&1; }
has_apt() { command -v apt-get >/dev/null 2>&1; }
has_dnf() { command -v dnf >/dev/null 2>&1; }
has_yum() { command -v yum >/dev/null 2>&1; }
has_pacman() { command -v pacman >/dev/null 2>&1; }
has_zypper() { command -v zypper >/dev/null 2>&1; }

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
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S ripgrep\n'
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
        if has_pacman; then
          printf '       suggest (Arch): sudo pacman -S silver-searcher-git\n'
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
    github)
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
      if ! command -v rg >/dev/null 2>&1 && ! command -v ag >/dev/null 2>&1; then
        printf 'MISSING rg or ag (fast search, optional)\n'
        suggest_install ripgrep "ripgrep" "https://github.com/BurntSushi/ripgrep"
        printf '       alt: '
        suggest_install silver_searcher "The Silver Searcher" "https://github.com/ggreer/the_silver_searcher"
        missing=$((missing + 1))
      else
        command -v rg >/dev/null 2>&1 && printf 'ok   rg (fast search)\n' || printf 'ok   ag (fast search)\n'
      fi
      ;;
    parallel-tests|private-parallel-tests|private-service-parallel-tests)
      check_tool parallel parallel "GNU parallel (optional)" "https://www.gnu.org/software/parallel/" || true
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
  targets=(github gitlab git circleci jira confluence investigate parallel-tests)
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
