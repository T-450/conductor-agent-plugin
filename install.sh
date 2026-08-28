#!/usr/bin/env bash

# ==============================================================================
# Conductor Universal Installer (Linux, macOS, WSL)
# Spec-Driven Development (SDD) for Pi, Claude Code, Copilot, & Antigravity
# ==============================================================================

set -e

REPO_URL="https://github.com/T-450/conductor-agent-plugin.git"
DEFAULT_INSTALL_DIR="$HOME/.conductor"
BIN_DIR="$HOME/.local/bin"

# Styling
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}"
echo "========================================================"
echo "          CONDUCTOR UNIVERSAL AGENT INSTALLER           "
echo "========================================================"
echo -e "${RESET}"

MODE="global"
HARNESS_ALL=false
SPECIFIC_HARNESS=""
UNINSTALL=false

# Parse command line flags
for arg in "$@"; do
  case $arg in
    --local|-l)
      MODE="local"
      ;;
    --global|-g)
      MODE="global"
      ;;
    --all|-a)
      HARNESS_ALL=true
      ;;
    --harness=*)
      SPECIFIC_HARNESS="${arg#*=}"
      ;;
    --uninstall)
      UNINSTALL=true
      ;;
    --help|-h)
      echo "Usage: ./install.sh [options]"
      echo ""
      echo "Options:"
      echo "  --global, -g         Install globally for user AI agent harnesses (default)"
      echo "  --local, -l          Scaffold Conductor into the current project workspace"
      echo "  --all, -a            Configure all supported harnesses without prompt"
      echo "  --harness=<name>     Configure a specific harness (pi, claude, copilot, gemini)"
      echo "  --uninstall          Remove Conductor symlinks and registrations"
      echo "  --help, -h           Show this help message"
      exit 0
      ;;
    *)
      ;;
  esac
done

# Detect Source Directory
SCRIPT_DIR=""
if [ -f "bin/conductor" ] && [ -f "plugin.json" ]; then
  SCRIPT_DIR="$(pwd)"
elif [ -n "${BASH_SOURCE[0]}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ "$UNINSTALL" = true ]; then
  echo -e "${YELLOW}Uninstalling Conductor...${RESET}"
  if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/bin/conductor" ]; then
    node "$SCRIPT_DIR/bin/conductor" uninstall
  elif [ -f "$DEFAULT_INSTALL_DIR/bin/conductor" ]; then
    node "$DEFAULT_INSTALL_DIR/bin/conductor" uninstall
  fi
  if [ -d "$DEFAULT_INSTALL_DIR" ]; then
    rm -rf "$DEFAULT_INSTALL_DIR"
    echo -e "Removed managed directory: ${DEFAULT_INSTALL_DIR}"
  fi
  echo -e "${GREEN}Conductor uninstalled successfully.${RESET}"
  exit 0
fi

if [ "$MODE" = "local" ]; then
  echo -e "${BOLD}Running Local Project Scaffolding...${RESET}"
  SRC="$SCRIPT_DIR"
  if [ -z "$SRC" ] || [ ! -d "$SRC/skills" ]; then
    SRC="$DEFAULT_INSTALL_DIR"
    if [ ! -d "$SRC" ]; then
      echo -e "${YELLOW}Fetching Conductor source to ${SRC}...${RESET}"
      git clone --depth 1 "$REPO_URL" "$SRC"
    fi
  fi
  node "$SRC/bin/conductor" install --local
  exit 0
fi

# Global Installation Mode
SRC_DIR=""
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills" ]; then
  SRC_DIR="$SCRIPT_DIR"
  echo -e "Using local repository at: ${BOLD}${SRC_DIR}${RESET}"
else
  SRC_DIR="$DEFAULT_INSTALL_DIR"
  if [ -d "$SRC_DIR/.git" ]; then
    echo -e "Updating managed installation at ${BOLD}${SRC_DIR}${RESET}..."
    (cd "$SRC_DIR" && git pull --ff-only)
  else
    echo -e "Cloning Conductor into ${BOLD}${SRC_DIR}${RESET}..."
    mkdir -p "$SRC_DIR"
    git clone --depth 1 "$REPO_URL" "$SRC_DIR"
  fi
fi

# Detect Harness Environments
DETECT_PI=false
DETECT_CLAUDE=false
DETECT_COPILOT=false
DETECT_GEMINI=false

if command -v omp >/dev/null 2>&1 || [ -d "$HOME/.omp" ]; then
  DETECT_PI=true
fi
if command -v claude >/dev/null 2>&1 || [ -d "$HOME/.claude" ]; then
  DETECT_CLAUDE=true
fi
if command -v gh >/dev/null 2>&1 || command -v copilot >/dev/null 2>&1 || [ -d "$HOME/.config/github-copilot" ]; then
  DETECT_COPILOT=true
fi
if command -v agy >/dev/null 2>&1 || command -v gemini >/dev/null 2>&1 || [ -d "$HOME/.gemini" ]; then
  DETECT_GEMINI=true
fi

# Override with specific harness if specified
if [ -n "$SPECIFIC_HARNESS" ]; then
  DETECT_PI=false
  DETECT_CLAUDE=false
  DETECT_COPILOT=false
  DETECT_GEMINI=false
  case $SPECIFIC_HARNESS in
    pi|omp) DETECT_PI=true ;;
    claude) DETECT_CLAUDE=true ;;
    copilot|gh) DETECT_COPILOT=true ;;
    gemini|agy) DETECT_GEMINI=true ;;
  esac
elif [ "$HARNESS_ALL" = true ]; then
  DETECT_PI=true
  DETECT_CLAUDE=true
  DETECT_COPILOT=true
  DETECT_GEMINI=true
fi

echo -e "\n${BOLD}Configuring AI Agent Harnesses:${RESET}"

# 1. Pi / Oh-My-Pi Configuration
if [ "$DETECT_PI" = true ]; then
  echo -e "  -> Configuring ${GREEN}Pi / Oh-My-Pi${RESET}..."
  mkdir -p "$HOME/.omp/plugins/cache/plugins"
  mkdir -p "$HOME/.omp/agent/skills"
  mkdir -p "$HOME/.omp/agent/commands"
  
  # Register in installed_plugins.json
  PLUGINS_JSON="$HOME/.omp/plugins/installed_plugins.json"
  if [ ! -f "$PLUGINS_JSON" ]; then
    echo "{}" > "$PLUGINS_JSON"
  fi

  python3 -c "
import json, os
p = os.path.expanduser('~/.omp/plugins/installed_plugins.json')
try:
    with open(p, 'r') as f:
        data = json.load(f)
except Exception:
    data = {}
data['conductor@conductor-marketplace'] = [{
    'scope': 'user',
    'installPath': '$SRC_DIR',
    'version': '1.2.0'
}]
with open(p, 'w') as f:
    json.dump(data, f, indent=2)
" || true

  # Link skills to ~/.omp/agent/skills
  for skill in "$SRC_DIR"/skills/*; do
    if [ -d "$skill" ]; then
      sname=$(basename "$skill")
      ln -sfn "$skill" "$HOME/.omp/agent/skills/$sname" 2>/dev/null || true
    fi
  done

  # Link commands to ~/.omp/agent/commands
  for cmd in "$SRC_DIR"/commands/*.md; do
    if [ -f "$cmd" ]; then
      cname=$(basename "$cmd")
      ln -sfn "$cmd" "$HOME/.omp/agent/commands/$cname" 2>/dev/null || true
    fi
  done
fi

# 2. Claude Code Configuration
if [ "$DETECT_CLAUDE" = true ]; then
  echo -e "  -> Configuring ${GREEN}Claude Code${RESET}..."
  mkdir -p "$HOME/.claude/plugins"
  mkdir -p "$HOME/.claude/commands"
  ln -sfn "$SRC_DIR" "$HOME/.claude/plugins/conductor" 2>/dev/null || true
  for cmd in "$SRC_DIR"/commands/*.md; do
    if [ -f "$cmd" ]; then
      cname=$(basename "$cmd")
      ln -sfn "$cmd" "$HOME/.claude/commands/$cname" 2>/dev/null || true
    fi
  done
fi

# 3. Gemini CLI / Antigravity Configuration
if [ "$DETECT_GEMINI" = true ]; then
  echo -e "  -> Configuring ${GREEN}Gemini CLI & Antigravity${RESET}..."
  mkdir -p "$HOME/.gemini/config/plugins"
  mkdir -p "$HOME/.gemini/config/agents"
  mkdir -p "$HOME/.gemini/config/commands"
  ln -sfn "$SRC_DIR" "$HOME/.gemini/config/plugins/conductor" 2>/dev/null || true
  for agent in "$SRC_DIR"/agents/*.md; do
    if [ -f "$agent" ]; then
      aname=$(basename "$agent")
      ln -sfn "$agent" "$HOME/.gemini/config/agents/$aname" 2>/dev/null || true
    fi
  done
  for cmd in "$SRC_DIR"/commands/*.md; do
    if [ -f "$cmd" ]; then
      cname=$(basename "$cmd")
      ln -sfn "$cmd" "$HOME/.gemini/config/commands/$cname" 2>/dev/null || true
    fi
  done
fi

# 4. GitHub Copilot CLI Configuration
if [ "$DETECT_COPILOT" = true ]; then
  echo -e "  -> Configuring ${GREEN}GitHub Copilot CLI${RESET}..."
  mkdir -p "$HOME/.config/github-copilot"
  ln -sfn "$SRC_DIR/.github/copilot-instructions.md" "$HOME/.config/github-copilot/conductor-instructions.md" 2>/dev/null || true
fi

# Link Terminal Binary
echo -e "\n${BOLD}Setting up Terminal CLI Bridge:${RESET}"
mkdir -p "$BIN_DIR"
ln -sf "$SRC_DIR/bin/conductor" "$BIN_DIR/conductor"
echo -e "  -> Linked ${BOLD}${BIN_DIR}/conductor${RESET}"

# Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo -e "${YELLOW}[NOTE] ${BIN_DIR} is not in your current PATH.${RESET}"
  echo -e "Add this to your ~/.bashrc or ~/.zshrc:"
  echo -e "  ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}\n"
fi

# Run Health Diagnostic
echo -e "\n${BOLD}Running Conductor Doctor Verification...${RESET}"
node "$SRC_DIR/bin/conductor" doctor

echo -e "${GREEN}${BOLD}Installation Complete!${RESET}"
echo -e "Start using Conductor in your terminal or agent sessions:"
echo -e "  - Terminal: ${BOLD}conductor status${RESET} or ${BOLD}conductor doctor${RESET}"
echo -e "  - In Agent:  ${BOLD}/conductor-setup${RESET} or ${BOLD}/conductor-new-track${RESET}\n"
