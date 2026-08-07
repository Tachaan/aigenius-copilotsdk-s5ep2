#!/bin/bash
# audit-logger.sh — postToolUse hook
# Logs every tool execution to a structured JSONL audit trail.
# Designed for retail compliance: PCI-DSS, SOC2 evidence collection.

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs' | head -c 500)
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')
CWD=$(echo "$INPUT" | jq -r '.cwd')

# Categorise the operation for retail analytics
case "$TOOL_NAME" in
  bash)   CATEGORY="command-execution" ;;
  edit)   CATEGORY="code-edit" ;;
  create) CATEGORY="file-creation" ;;
  view)   CATEGORY="code-read" ;;
  grep|glob) CATEGORY="code-search" ;;
  *)      CATEGORY="other" ;;
esac

mkdir -p logs

jq -nc \
  --arg ts "$TIMESTAMP" \
  --arg tool "$TOOL_NAME" \
  --arg args "$TOOL_ARGS" \
  --arg cat "$CATEGORY" \
  --arg cwd "$CWD" \
  --arg logged "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{timestamp: $ts, logged_at: $logged, tool: $tool, category: $cat, args: $args, cwd: $cwd}' \
  >> logs/agent-audit.jsonl
