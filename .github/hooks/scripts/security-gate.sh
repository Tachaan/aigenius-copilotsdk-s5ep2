#!/bin/bash
# security-gate.sh — preToolUse hook
# Blocks dangerous commands and enforces file edit boundaries.
# Retail governance: only allow edits in src/ and tests/ directories.

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs')

DENIED=false
REASON=""

# --- Block dangerous bash commands ---
if [ "$TOOL_NAME" = "bash" ]; then
  COMMAND=$(echo "$TOOL_ARGS" | jq -r '.command // empty')

  if echo "$COMMAND" | grep -qEi "rm -rf /|rm -rf \.|DROP TABLE|DROP DATABASE|format |mkfs\.|:(){"; then
    DENIED=true
    REASON="Destructive command blocked by retail governance policy"
  fi

  if echo "$COMMAND" | grep -qEi "\.env|credentials|secrets|\.pem|\.key|password"; then
    DENIED=true
    REASON="Access to credential/secret files blocked by security policy"
  fi
fi

# --- Enforce file edit boundaries ---
if [ "$TOOL_NAME" = "edit" ] || [ "$TOOL_NAME" = "create" ]; then
  FILE_PATH=$(echo "$TOOL_ARGS" | jq -r '.path // empty')

  # Top-level project files that legitimately need editing. Matched against the
  # repo-relative path, so /etc/README.md is still refused.
  ALLOWED_ROOT_FILES='^(README\.md|AGENTS\.md|mkdocs\.yml)$'
  REL_PATH="${FILE_PATH#"$PWD"/}"

  if [ -n "$FILE_PATH" ]; then
    if [[ ! "$FILE_PATH" =~ (src/|tests/|docs/|\.github/) ]] \
       && [[ ! "$REL_PATH" =~ $ALLOWED_ROOT_FILES ]]; then
      DENIED=true
      REASON="File edits restricted to src/, tests/, docs/, .github/, and top-level project docs"
    fi
  fi
fi

# --- Output decision ---
if [ "$DENIED" = true ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) DENIED tool=$TOOL_NAME reason=\"$REASON\"" >> logs/security-denials.log
  echo "{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$REASON\"}"
  exit 0
fi

echo '{"permissionDecision":"allow"}'
