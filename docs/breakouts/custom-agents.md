# Custom Agents

This page documents the repository-scoped custom agents in `.github/agents/`.
Each agent is an `.agent.md` file with YAML frontmatter plus instructions that
specialise Copilot for review, security, accessibility, or PR summaries.

## `.agent.md` format

Custom agents use Markdown files with frontmatter at the top:

```yaml
---
name: dotnet-reviewer
description: Senior .NET code reviewer specializing in C# best practices
tools: ['agent', 'read', 'search']
model: claude-sonnet-4.6
---
```

The `name` is the handle, `description` tells Copilot when the agent is useful,
`tools` declares the surfaces the agent may use, and `model` pins a model when
present. The Markdown body contains the role, review checklist, output format,
and any cross-validation instructions.

## `dotnet-reviewer`

- **Path**: `.github/agents/dotnet-reviewer.agent.md`
- **Description**: Senior .NET code reviewer specializing in C# best
  practices, security, and performance.
- **Tools**: `agent`, `read`, `search`
- **Pinned model**: `claude-sonnet-4.6`
- **Triggers**: Use when a change needs .NET-specific review, especially for
  security, performance, nullable reference types, async usage, disposal, or
  EF Core patterns.
- **Example invocation**:

  ```text
  @dotnet-reviewer review the changes in AgentHQDemo.Api for async and EF Core issues
  ```

The agent also instructs itself to run `security-scanner` as a subagent after
its review, then report both sets of findings directly.

## `security-scanner`

- **Path**: `.github/agents/security-scanner.agent.md`
- **Description**: Security-focused code reviewer that identifies
  vulnerabilities and compliance issues.
- **Tools**: `agent`, `read`, `search`
- **Pinned model**: `GPT-5.3-Codex ` as written in the file.
- **Triggers**: Use when reviewing for OWASP Top 10 issues, input validation,
  authentication and authorisation, sensitive data exposure, unsafe parsing,
  or insufficient logging.
- **Example invocation**:

  ```text
  @security-scanner check the chat and transaction endpoints for OWASP issues
  ```

The agent asks for each finding to include severity, CWE when applicable,
location, attack scenario, remediation, and references. If UI code is present,
it instructs itself to run `accessibility-auditor` as a subagent.

## `pr-summary`

- **Path**: `.github/agents/pr-summary.agent.md`
- **Description**: Generates concise, informative PR summaries from code
  changes.
- **Tools**: `agent`, `read`, `search`
- **Pinned model**: none declared.
- **Triggers**: Use when preparing a pull request description, summarising a
  diff, or grouping changes by features, fixes, tests, docs, and configuration.
- **Example invocation**:

  ```text
  @pr-summary summarise this PR and call out reviewer risks
  ```

The expected output includes a one-line summary, grouped change overview, key
files changed, impact assessment, and testing notes. It also asks for
`dotnet-reviewer` cross-validation and only includes Critical and High
findings in a final code quality section.

## `accessibility-auditor`

- **Path**: `.github/agents/accessibility-auditor.agent.md`
- **Description**: Use this agent when the user asks to review code for
  accessibility issues or compliance.
- **Tools**: `read`, `search`
- **Pinned model**: none declared.
- **Triggers**: The description explicitly lists phrases such as "check this
  code for accessibility issues", "review for WCAG compliance", "audit for
  accessibility problems", "find accessibility violations", and "is this
  accessible?"
- **Example invocation**:

  ```text
  @accessibility-auditor review the Blazor components for WCAG 2.1 AA issues
  ```

The agent checks semantic HTML, ARIA, keyboard navigation, colour contrast,
focus states, form labels, motion, media alternatives, and responsive behaviour.

## Shared and review-specific instructions

`.github/copilot-instructions.md` is the shared standard for all assistants in
this repository. It describes the .NET 10 retail analytics app, coding
conventions, Copilot SDK patterns, testing expectations, and security rules.

`.github/copilot-review-instructions.md` is narrower. It provides review-time
context, including the GitHub Copilot SDK v1.0.9 namespace
`GitHub.Copilot`, explicit `session.On<T>(...)` usage, SSE streaming rules,
model discovery expectations, and intentional demo code smells that reviewers
should not flag unless explicitly asked.

## Known issues

`security-scanner.agent.md` pins `model: GPT-5.3-Codex ` with non-standard
casing and a trailing space. Verify the accepted model identifier before
depending on that agent, because an invalid model id could cause it to fail to
start.

## Related

- [Architecture](./architecture.md)
- [Hooks and governance](./hooks-and-governance.md)
- [Skills](./skills.md)
- [Shared Copilot instructions](../../.github/copilot-instructions.md)
- [Review instructions](../../.github/copilot-review-instructions.md)
- [Agents folder](../../.github/agents/)
