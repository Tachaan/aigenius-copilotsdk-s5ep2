#!/bin/bash
# session-init.sh — sessionStart hook
# Initialises the audit log for a new agent session.

INPUT=$(cat)
SOURCE=$(echo "$INPUT" | jq -r '.source // "unknown"')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')
CWD=$(echo "$INPUT" | jq -r '.cwd')

mkdir -p logs

echo "═══════════════════════════════════════════════════════" >> logs/session.log
echo "SESSION START" >> logs/session.log
echo "  Time:   $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> logs/session.log
echo "  Source: $SOURCE" >> logs/session.log
echo "  CWD:    $CWD" >> logs/session.log
echo "  User:   $(whoami)" >> logs/session.log
echo "═══════════════════════════════════════════════════════" >> logs/session.log
