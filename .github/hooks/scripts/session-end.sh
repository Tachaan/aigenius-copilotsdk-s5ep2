#!/bin/bash
# session-end.sh — sessionEnd hook
# Finalises the audit log with a session summary.

INPUT=$(cat)
REASON=$(echo "$INPUT" | jq -r '.reason // "unknown"')

AUDIT_COUNT=0
if [ -f logs/agent-audit.jsonl ]; then
  AUDIT_COUNT=$(wc -l < logs/agent-audit.jsonl | tr -d ' ')
fi

DENIAL_COUNT=0
if [ -f logs/security-denials.log ]; then
  DENIAL_COUNT=$(wc -l < logs/security-denials.log | tr -d ' ')
fi

echo "───────────────────────────────────────────────────────" >> logs/session.log
echo "SESSION END" >> logs/session.log
echo "  Time:     $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> logs/session.log
echo "  Reason:   $REASON" >> logs/session.log
echo "  Actions:  $AUDIT_COUNT tool executions logged" >> logs/session.log
echo "  Denials:  $DENIAL_COUNT security denials" >> logs/session.log
echo "═══════════════════════════════════════════════════════" >> logs/session.log
