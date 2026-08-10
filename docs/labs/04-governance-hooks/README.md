# Lab 04 — Governance hooks

**Goal:** make the `preToolUse` security gate genuinely block access to a
secrets file, watch the audit logger record activity, and learn why a
misconfigured hook is more dangerous than no hook at all.

**Time:** ~20 minutes

**Prerequisites:** [Lab 03](../03-custom-agents/) complete. `jq` installed —
the hook scripts depend on it.

## Step 1 — See how hooks are wired

```bash
cat .github/hooks/retail-governance.json
ls -l .github/hooks/scripts/
```

Four lifecycle events, each mapped to a script:

| Event | Script | Purpose |
|:------|:-------|:--------|
| `sessionStart` | `session-init.sh` | Announce policy, start the audit trail |
| `preToolUse` | `security-gate.sh` | **Allow or deny** a tool call before it runs |
| `postToolUse` | `audit-logger.sh` | Record what actually happened |
| `sessionEnd` | `session-end.sh` | Close out and summarise the session |

Each entry declares a `type`, the `bash` script to run, a working directory,
and a `timeoutSec`.

Only `preToolUse` can *stop* anything. The others observe.

## Step 2 — A cautionary tale

This repository shipped for a while with a broken gate. The config pointed at:

```
./.github/hooks/scripts/security-gate-notworking.sh
```

…but the file on disk was `security-gate.sh`. The referenced script **did not
exist**.

The gate did not error. It did not warn. It simply never ran — every tool call
sailed through unchecked, while the repo looked fully governed. The old `.env`
even carried a comment claiming "the preToolUse hook should BLOCK access to
this file". It would not have.

This has been corrected, and it's the most important lesson in the lab:

> ⚠️ **A silently misconfigured control is worse than a missing one**, because
> it manufactures confidence. Always prove your gate fires.

Confirm the reference is now correct:

```bash
grep -o '"bash": "[^"]*"' .github/hooks/retail-governance.json
```

Every path listed must exist in `.github/hooks/scripts/`.

## Step 3 — Read the gate

```bash
cat .github/hooks/scripts/security-gate.sh
```

The contract is simple — JSON in on stdin, a decision out on stdout:

```bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs')
```

It denies in three situations:

1. **Destructive bash** — `rm -rf /`, `DROP TABLE`, `mkfs.`, fork bombs
2. **Secret access** — commands mentioning `.env`, `credentials`, `secrets`,
   `.pem`, `.key`, or `password`
3. **Out-of-bounds writes** — `edit`/`create` outside `src/`, `tests/`,
   `docs/`, or `.github/`

And emits one of:

```json
{"permissionDecision":"allow"}
{"permissionDecision":"deny","permissionDecisionReason":"..."}
```

⚠️ Note it exits `0` even when denying. The *decision* travels in the JSON
payload, not the exit code — a non-zero exit would look like a broken hook
rather than a deliberate refusal.

## Step 4 — Prove the gate blocks a secret

Make sure the scripts are executable and the log directory exists:

```bash
chmod +x .github/hooks/scripts/*.sh
mkdir -p logs
```

Now test it directly by piping in the JSON a real tool call would send:

```bash
echo '{"toolName":"bash","toolArgs":{"command":"cat .env"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

Expected:

```json
{"permissionDecision":"deny","permissionDecisionReason":"Access to credential/secret files blocked by security policy"}
```

That's the gate working — the same check that previously never ran.

## Step 5 — Test the other paths

Destructive command:

```bash
echo '{"toolName":"bash","toolArgs":{"command":"rm -rf /"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `"Destructive command blocked by retail governance policy"`

Write outside the allowed directories:

```bash
echo '{"toolName":"create","toolArgs":{"path":"/etc/hosts"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `"File edits restricted to src/, tests/, docs/, and .github/ directories"`

And a legitimate call, which must pass:

```bash
echo '{"toolName":"bash","toolArgs":{"command":"dotnet build"}}' \
  | ./.github/hooks/scripts/security-gate.sh
```

→ `{"permissionDecision":"allow"}`

⚠️ **Always test the allow case too.** A gate that denies everything passes
every "did it block?" test while making the repo unusable.

## Step 6 — Inspect the denial log

```bash
cat logs/security-denials.log
```

Each refusal is appended with a UTC timestamp, the tool, and the reason:

```
2026-08-10T11:04:35Z DENIED tool=bash reason="Access to credential/secret files blocked by security policy"
```

This is the artefact a compliance reviewer asks for: evidence that the control
exists *and* evidence of it firing.

## Step 7 — Try it against a real secrets file

The repo ships [`.env.example`](../../../.env.example) — placeholders only, no
real credentials. `.env` itself is gitignored and must never be committed.

```bash
cp .env.example .env
echo '{"toolName":"bash","toolArgs":{"command":"cat .env"}}' \
  | ./.github/hooks/scripts/security-gate.sh
rm .env
```

Still denied — the gate matches on the command text, so it refuses regardless
of whether the file happens to exist.

## Step 8 — Run a session with hooks active

```bash
copilot -p "List the files in the src directory" --allow-all-tools
```

Then check what the audit logger captured:

```bash
ls -la logs/
tail -20 logs/*.jsonl 2>/dev/null || tail -20 logs/*.log 2>/dev/null
```

💡 Hooks are configured per-session by the CLI. If nothing appears, confirm the
CLI is picking up `.github/hooks/retail-governance.json` for this repository.

## Step 9 — Disabling hooks

While developing a hook you'll want it off. Either rename the config:

```bash
mv .github/hooks/retail-governance.json .github/hooks/retail-governance.json.off
# restore with the reverse
```

…or comment out an individual event by removing its array entry.

⚠️ Never disable a gate in a shared branch and forget to restore it — that
recreates exactly the silent-failure situation from Step 2. Consider adding a
CI check that asserts every `bash` path in the config exists on disk.

## ✅ Checkpoint

- [x] You can name the four hook events and which one can deny
- [x] You proved the gate blocks secrets, destructive commands, and stray writes
- [x] You confirmed legitimate calls still pass
- [x] You found the denial log evidence
- [x] You can explain why the broken reference was dangerous

## 💡 Extra credit

Add a rule to `security-gate.sh` blocking `git push --force` on `main`. Test
both that it denies the force push and that an ordinary `git push` still
passes.

## Related

- Next: [Lab 05 — Extend the API](../05-extend-api/)
- [Breakout: Hooks and governance](../../breakouts/hooks-and-governance.md)
- [`AGENTS.md`](../../../AGENTS.md) — repository rules for AI agents
