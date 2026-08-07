---
name: demo-verifier
description: "**CRITICAL: Use this skill to verify demo capabilities.** Reads all demo scripts (docs/demo-script*.md) and cross-references every claimed capability against current GitHub documentation. Reports what is confirmed, in preview, or deprecated. MUST be invoked when reviewing demo accuracy, checking feature availability, or preparing for a live demo."
license: MIT
---

# Demo Verifier Skill

Verify that every capability demonstrated in the Agent HQ demo is currently available, in preview, or accurately described.

## When to Use

- Before a live demo — run verification to catch any deprecated or changed features
- After updating demo scripts — ensure new content references real capabilities
- When GitHub ships updates — check if demo needs refreshing
- When asked: "is this demo accurate?", "verify the demo", "check demo capabilities"

## What This Skill Does

1. Reads all demo documentation in `docs/`
2. Extracts every claimed capability and product truth
3. Cross-references against current GitHub documentation
4. Reports status of each capability

## Verification Checklist

### 🟣 Agent Freedom (Monday 1)

| # | Capability | How to Verify |
|---|-----------|---------------|
| F1 | Multi-model selection in IDE (Claude, GPT, Gemini) | Check [Copilot model docs](https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide) for available models |
| F2 | Copilot SDK streaming chat with model switching | Check [Copilot SDK docs](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-with-the-copilot-sdk) |
| F3 | Custom agents via `.github/agents/` | Check [custom agents docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-agents) |
| F4 | `copilot-instructions.md` for all models | Check [customizing instructions docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions) |
| F5 | Subagent chains (agent calls agent) | Check [subagents docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-agents) for `agents:` frontmatter |
| F6 | Copilot CLI | Check [Copilot CLI docs](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line) |
| F7 | GitHub Mobile Copilot | Check [mobile docs](https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-github-mobile) |

### 🔵 Agent Orchestration (Monday 2)

| # | Capability | How to Verify |
|---|-----------|---------------|
| O1 | Copilot CLI plan mode | Check [Copilot CLI changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) for plan mode |
| O2 | `/yolo` mode (skip confirmations) | Check CLI changelog for /yolo |
| O3 | Autopilot (persistent execution) | Check CLI changelog for autopilot |
| O4 | `/delegate` to coding agent | Check [coding agent docs](https://docs.github.com/en/copilot/using-github-copilot/using-the-copilot-coding-agent) |
| O5 | Coding agent on issues (@copilot assign) | Check coding agent docs for issue assignment |
| O6 | `/fleet` parallel agents | Check CLI changelog for /fleet |
| O7 | Agent sessions at repo level | Check coding agent docs for sessions |
| O8 | Memory in agents (copilot-instructions.md) | Check instructions docs — memory framing |
| O9 | Skills (`.github/skills/`) | Check [skills docs](https://docs.github.com/en/copilot/customizing-copilot/adding-copilot-skills) |
| O10 | Decouple coding agent from PRs | Verify private preview status |

### 🟢 Agent Controls (Monday 3)

| # | Capability | How to Verify |
|---|-----------|---------------|
| C1 | Audit log — Copilot events | Check [audit log docs](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise) for copilot events |
| C2 | Copilot Controls Page (org policies) | Check [managing policies docs](https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/managing-policies-and-features-for-copilot-in-your-organization) |
| C3 | Enterprise → org policy cascade | Check [enterprise policies docs](https://docs.github.com/en/copilot/managing-copilot/managing-copilot-for-your-enterprise/managing-policies-and-features-for-copilot-in-your-enterprise) |
| C4 | Content exclusion | Check [content exclusion docs](https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/configuring-content-exclusions-for-github-copilot) |
| C5 | CodeQL on agent-generated code | Check [code scanning docs](https://docs.github.com/en/code-security/code-scanning) |
| C6 | Secret scanning | Check [secret scanning docs](https://docs.github.com/en/code-security/secret-scanning) |
| C7 | Copilot Metrics Dashboard | Check [metrics docs](https://docs.github.com/en/copilot/rolling-out-github-copilot-at-scale/analyzing-usage-and-impact/analyzing-copilot-usage-in-your-organization-with-the-copilot-metrics-api) |
| C8 | Copilot Metrics API | Check metrics API docs |
| C9 | Model restrictions per org/team | Check managing policies docs for model settings |

## How to Run Verification

### Step 1: Read Demo Scripts
Read all files in `docs/` that contain demo steps:
- `docs/demo-script.md` (generic demo)

### Step 2: Extract Capabilities
For each demo step, identify:
- The specific GitHub feature being demonstrated
- Whether it's shown live or described conceptually
- Any version/plan requirements (Enterprise, Business, etc.)

### Step 3: Cross-Reference
For each capability, search current GitHub documentation:
- Use `web_search` to check current docs
- Verify the feature exists and works as described
- Check for any recent changes or deprecations
- Note any preview/beta status

### Step 4: Generate Report

Use this format for the verification report:

```
## Demo Verification Report
**Date:** [current date]
**Demo version:** [latest commit hash]

### Summary
- ✅ Confirmed: X capabilities
- ⚠️ Preview/Changed: X capabilities
- ❌ Deprecated/Unavailable: X capabilities

### Details

#### 🟣 Agent Freedom
| ID | Capability | Status | Notes |
|----|-----------|--------|-------|
| F1 | Multi-model in IDE | ✅ | Available in Copilot Business/Enterprise |
...

#### 🔵 Agent Orchestration
| ID | Capability | Status | Notes |
|----|-----------|--------|-------|
| O1 | CLI plan mode | ✅ | Available since v0.x |
...

#### 🟢 Agent Controls
| ID | Capability | Status | Notes |
|----|-----------|--------|-------|
| C1 | Audit log events | ✅ | Enterprise Cloud only |
...

### Recommendations
- [Any demo steps that need updating]
- [Any new features that should be added]
```

## Product Truths to Verify

These are the nine official product truths from the GitHub keynote. Each must be verifiable:

| Pillar | Product Truth | Expected Status |
|--------|--------------|-----------------|
| 🟣 Freedom | Access the latest and greatest models in the IDE | GA |
| 🟣 Freedom | Access multiple agents within GitHub, as well as in the IDE | GA |
| 🟣 Freedom | Work on your phone, the CLI, IDE, or even GitHub.com | GA |
| 🔵 Orchestration | Decouple coding agent from PRs (planning together in GitHub) | Private Preview |
| 🔵 Orchestration | Agent Sessions at the repository level | GA |
| 🔵 Orchestration | Copilot now has memory built into 1P and 3P agents | GA |
| 🟢 Controls | Copilot events now stream to the audit log for inspection | GA |
| 🟢 Controls | Copilot Controls Page | GA |
| 🟢 Controls | Copilot Metrics Dashboard & API | GA |

## Notes

- Some capabilities require GitHub Enterprise Cloud (audit log, enterprise policies)
- Copilot SDK is in technical preview — verify current access requirements
- CLI features change frequently — always check latest changelog
- Private preview features should be framed as "coming soon" in demos
