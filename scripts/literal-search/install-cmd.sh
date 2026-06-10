#!/usr/bin/env bash
set -euo pipefail

# Print one OS-appropriate install command for a fast-grep host tool.
# Usage: install-cmd.sh <tool_id>
# tool_id: ripgrep | ugrep | silver_searcher | ack
# Exit 0 when a concrete command is printed; exit 1 when only vendor guidance is available.

usage() {
  cat <<'EOF'
Usage: install-cmd.sh <tool_id>

tool_id:
  ripgrep          ripgrep (rg)
  ugrep            ugrep
  silver_searcher  The Silver Searcher (ag)
  ack              ack 3

Prints one install command for the detected OS and package manager.
EOF
}

OS_NAME=""
OS_FAMILY=""

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
has_pacman() { command -v pacman >/dev/null 2>&1; }
has_winget() { command -v winget >/dev/null 2>&1; }
has_scoop() { command -v scoop >/dev/null 2>&1; }
has_choco() { command -v choco >/dev/null 2>&1; }
has_yum() { command -v yum >/dev/null 2>&1; }
has_zypper() { command -v zypper >/dev/null 2>&1; }
has_pkg() { command -v pkg >/dev/null 2>&1; }

print_cmd() {
  printf '%s\n' "$1"
}

tool_id="${1:-}"
if [[ -z "$tool_id" || "$tool_id" == "-h" || "$tool_id" == "--help" ]]; then
  usage
  exit 2
fi

detect_os

case "$tool_id" in
  ripgrep)
    case "$OS_FAMILY" in
      darwin)
        has_brew && print_cmd "brew install ripgrep" && exit 0
        ;;
      linux)
        if has_apt; then print_cmd "sudo apt update && sudo apt install -y ripgrep"; exit 0; fi
        if has_dnf; then print_cmd "sudo dnf install -y ripgrep"; exit 0; fi
        if has_yum; then print_cmd "sudo yum install -y ripgrep"; exit 0; fi
        if has_zypper; then print_cmd "sudo zypper install -y ripgrep"; exit 0; fi
        if has_pacman; then print_cmd "sudo pacman -S --noconfirm ripgrep"; exit 0; fi
        ;;
      freebsd)
        has_pkg && print_cmd "pkg install -y ripgrep" && exit 0
        ;;
      windows)
        if has_winget; then print_cmd "winget install --id BurntSushi.ripgrep.MSVC -e"; exit 0; fi
        if has_scoop; then print_cmd "scoop install ripgrep"; exit 0; fi
        if has_choco; then print_cmd "choco install ripgrep -y"; exit 0; fi
        ;;
    esac
    echo "install-cmd: see https://github.com/BurntSushi/ripgrep#installation" >&2
    exit 1
    ;;
  ugrep)
    case "$OS_FAMILY" in
      darwin)
        has_brew && print_cmd "brew install ugrep" && exit 0
        ;;
      linux)
        if has_apt; then print_cmd "sudo apt update && sudo apt install -y ugrep"; exit 0; fi
        if has_dnf; then print_cmd "sudo dnf install -y ugrep"; exit 0; fi
        if has_yum; then print_cmd "sudo yum install -y ugrep"; exit 0; fi
        if has_zypper; then print_cmd "sudo zypper install -y ugrep"; exit 0; fi
        if has_pacman; then print_cmd "sudo pacman -S --noconfirm ugrep"; exit 0; fi
        ;;
      freebsd)
        has_pkg && print_cmd "pkg install -y ugrep" && exit 0
        ;;
      windows)
        if has_winget; then print_cmd "winget install --id Genivia.ugrep -e"; exit 0; fi
        if has_scoop; then print_cmd "scoop install ugrep"; exit 0; fi
        if has_choco; then print_cmd "choco install ugrep -y"; exit 0; fi
        ;;
    esac
    echo "install-cmd: see https://github.com/Genivia/ugrep#install" >&2
    exit 1
    ;;
  silver_searcher)
    case "$OS_FAMILY" in
      darwin)
        has_brew && print_cmd "brew install the_silver_searcher" && exit 0
        ;;
      linux)
        if has_apt; then print_cmd "sudo apt update && sudo apt install -y silversearcher-ag"; exit 0; fi
        if has_dnf; then print_cmd "sudo dnf install -y the_silver_searcher"; exit 0; fi
        if has_yum; then print_cmd "sudo yum install -y the_silver_searcher"; exit 0; fi
        if has_zypper; then print_cmd "sudo zypper install -y the_silver_searcher"; exit 0; fi
        if has_pacman; then print_cmd "sudo pacman -S --noconfirm silver-searcher-git"; exit 0; fi
        ;;
      freebsd)
        has_pkg && print_cmd "pkg install -y silver-searcher" && exit 0
        ;;
      windows)
        if has_scoop; then print_cmd "scoop install ag"; exit 0; fi
        if has_choco; then print_cmd "choco install ag -y"; exit 0; fi
        if has_winget; then print_cmd "winget install --id ggreer.the_silver_searcher -e"; exit 0; fi
        ;;
    esac
    echo "install-cmd: see https://github.com/ggreer/the_silver_searcher#installing" >&2
    exit 1
    ;;
  ack)
    case "$OS_FAMILY" in
      darwin)
        has_brew && print_cmd "brew install ack" && exit 0
        ;;
      linux)
        if has_apt; then print_cmd "sudo apt update && sudo apt install -y ack"; exit 0; fi
        if has_dnf; then print_cmd "sudo dnf install -y ack"; exit 0; fi
        if has_yum; then print_cmd "sudo yum install -y ack"; exit 0; fi
        if has_pacman; then print_cmd "sudo pacman -S --noconfirm ack"; exit 0; fi
        ;;
      freebsd)
        has_pkg && print_cmd "pkg install -y ack" && exit 0
        ;;
      windows)
        if has_choco; then print_cmd "choco install ack -y"; exit 0; fi
        if has_scoop; then print_cmd "scoop install ack"; exit 0; fi
        ;;
    esac
    echo "install-cmd: see https://beyondgrep.com/install/" >&2
    exit 1
    ;;
  *)
    echo "install-cmd: unknown tool_id: $tool_id" >&2
    usage >&2
    exit 2
    ;;
esac
