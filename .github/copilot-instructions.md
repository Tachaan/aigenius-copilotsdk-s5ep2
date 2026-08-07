# AI Instructions for Agent HQ Demo

This file provides context and coding guidelines for **all AI assistants** working in this repository—including GitHub Copilot, Claude, Codex, and custom agents.

## Project Overview

This is a **.NET 10 LTS Retail Transaction Analytics** app demonstrating modern AI-assisted development:
- Retail transactions, customer segmentation, and segment prediction
- Multi-agent workflows (Copilot, Claude, Codex working together)
- Autonomous coding agents that plan, implement, and iterate
- Enterprise governance with audit trails and policy controls
- SQLite database with EF Core for zero-config data persistence

## Repository Structure

```
src/
├── AgentHQDemo.Api/          # ASP.NET Core Web API
│   ├── Controllers/          # Chat, Transactions, Segments endpoints
│   ├── Data/                 # EF Core DbContext (SQLite)
│   ├── Services/             # RetailAnalyticsService, CopilotChatService
│   ├── Models/               # Transaction, CustomerSegment, SegmentPrediction
│   └── wwwroot/              # Chat UI
tests/
└── AgentHQDemo.Tests/        # Unit and integration tests
.github/
├── agents/                   # Custom agent definitions
├── workflows/                # CI/CD pipelines
└── copilot-instructions.md   # This file (teaches ALL agents)
```

## Coding Standards (All Agents Should Follow)

### C# Conventions
- Use **file-scoped namespaces** (C# 10+)
- Prefer **primary constructors** for simple DI (C# 12+)
- Use **collection expressions** `[]` over `new List<T>()`
- Enable **nullable reference types** — no `null` without `?`
- Use `record` types for DTOs and immutable data

### Async Patterns
- All I/O operations must be `async`
- Use `CancellationToken` in all async methods
- Prefer `ValueTask` for hot paths that often complete synchronously
- Always use `ConfigureAwait(false)` in library code

### Naming Conventions
- Async methods end with `Async` suffix
- Private fields use `_camelCase`
- Constants use `PascalCase`
- Interfaces start with `I` prefix

### Error Handling
- Use `Result<T>` pattern over exceptions for expected failures
- Log structured data with `ILogger<T>`
- Return `ProblemDetails` for API errors

## Multi-Agent Collaboration

This repo supports multiple AI agents working together:

### Available Agents
- **@copilot** — Fast code completion and general assistance
- **@claude** — Deep reasoning and security analysis
- **@codex** — Code generation and documentation
- **@dotnet-reviewer** — .NET-specific code review
- **@security-scanner** — OWASP Top 10 vulnerability detection

### When to Use Each Agent
| Task | Recommended Agent |
|------|-------------------|
| Quick code completion | @copilot |
| Architecture analysis | @claude |
| Security review | @claude or @security-scanner |
| Performance optimization | @copilot |
| Documentation | @codex |
| .NET best practices | @dotnet-reviewer |

### Collaboration Example
```
# In a PR comment:
@copilot implement rate limiting for this endpoint
@claude review security implications
@dotnet-reviewer check for .NET anti-patterns
```

## Agent Development Guidelines

### Copilot SDK Patterns
When creating agents:
```csharp
await using var client = new CopilotClient();
await client.StartAsync();

var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = "gpt-5",  // or claude-opus-4.5, gemini-2.5-pro
    Tools = [ /* AIFunctionFactory tools */ ],
    CustomAgents = [ /* Domain-specific agents */ ]
});
```

### Tool Definitions
- Use `AIFunctionFactory.Create()` for tool registration
- Include `[Description]` attributes on all parameters
- Keep tools focused — one responsibility each
- Handle tool failures gracefully with fallback responses

## Testing Requirements

- Unit tests required for all agent logic
- Mock `CopilotClient` for unit tests
- Integration tests for full SDK flow (requires auth)
- Use `FluentAssertions` for readable assertions
- Test both success and failure paths

## Common Commands

```bash
# Build the solution
dotnet build

# Run tests
dotnet test

# Run the API locally
dotnet run --project src/AgentHQDemo.Api

# Watch mode for development
dotnet watch --project src/AgentHQDemo.Api
```

## When Asked About This Project

If someone asks "How do I run this?" or "How does this work?":
1. Point them to this file for conventions
2. Explain the multi-agent architecture
3. Reference the custom agents in `.github/agents/`
4. Mention the demo showcases autonomous AI development

## Security Considerations

- Never commit secrets or API keys
- Use environment variables for sensitive configuration
- Validate all user input in API endpoints
- Sanitize file paths in MCP filesystem operations
- Log agent actions for audit trail compliance
- All AI-generated code must pass CodeQL scanning
