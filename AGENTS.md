# AI Agent Guidelines

This file contains instructions and guidelines for AI agents working on this
repository — GitHub Copilot, Claude, Codex, and any custom agents.

> Coding standards and architecture live in
> [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
> This file covers repository conduct: what to commit, what to leave alone,
> and how to handle issues.

## 🔒 Security Best Practices

**Never commit sensitive information to this repository:**

- API keys, tokens, or credentials
- Personal access tokens (PATs)
- Database connection strings with passwords
- Environment-specific configuration values
- Customer names, competitive analysis, or any internal-only material

`.env` is gitignored and must stay that way. No environment file is committed
to this repository — document required variables in the README instead of
checking in a sample file.

**For MCP configuration files (`mcp.json`):**

- Use placeholder values like `"YOUR_API_KEY_HERE"` or `"${API_KEY}"`
- Reference environment variables for sensitive data
- Document which environment variables are required

## 📋 Repository Guidelines

### Purpose

This repository is demo content for the **AI Genius S5E2** session. It should:

- Provide clear, runnable content for session attendees
- Support self-guided learning for people working through it later
- Stay reproducible — `dotnet build` and `dotnet test` on `src/AgentOrchestrator/AgentHQDemo.slnx` must pass from a clean clone

### What NOT to modify without permission

- License files (`LICENSE`, `LICENSE-DOCS`, `CODE_OF_CONDUCT.md`)
- Security files (`SECURITY.md`)
- GitHub workflow files in `.github/workflows/`

### Content Rules

- No large binary files (PowerPoint decks, videos, recordings) in the repo —
  link to them instead
- All README files should be kept up to date
- Unused folders containing only a placeholder README should be removed

### Intentional Demo Code Smells

This repo **deliberately** contains code issues used to demonstrate code
review and static analysis. See *Security Notes* in the [README](README.md).
**Do not "fix" these without checking first** — they are the demo:

- N+1 query in `GetTransactionsWithSegmentsAsync`
- Missing null check in `GetTransactionAsync`
- No input validation in `AddTransactionAsync`
- Hardcoded threshold in `PredictSegmentAsync`

### Issue Management

When a user reports a problem, asks a question that should be tracked, or
wants to file an issue:

1. **Discover available templates** — check `.github/ISSUE_TEMPLATE/` for any
   `.yml` or `.md` files and read them to understand the expected fields.
2. **Match the request to a template** — pick the best fit, or create a plain
   issue if none exist.
3. **Help fill in the fields** — walk through required fields interactively,
   proposing answers where possible.
4. **Create the issue** — `gh issue create --template <file>`, or
   `gh issue create` for a plain issue.
5. **Apply labels** — check `gh label list` first; don't apply labels that
   don't exist.

## ✅ Before You Push

- `dotnet build src/AgentOrchestrator/AgentHQDemo.slnx` succeeds with no warnings
- `dotnet test src/AgentOrchestrator/AgentHQDemo.slnx` passes (14 tests)
- No secrets, customer names, or internal material in the diff **or** in
  commit history
