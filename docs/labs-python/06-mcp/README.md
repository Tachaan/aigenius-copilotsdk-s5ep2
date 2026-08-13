# Lab 06 — MCP

**Goal:** attach a Model Context Protocol server so the agent can use tools you
did not write, and — just as importantly — learn how to *prove* those tools were
actually used.

**Time:** ~20 minutes

**Prerequisites:** [Lab 05](../05-sessions/) complete.

## Step 1 — Why MCP

In [Lab 03](../03-tools/) you wrote a tool with `@define_tool`. That is the
right approach when the capability lives in your own codebase.

MCP is for the other case: a capability someone else already built and runs.
Instead of writing and maintaining an integration, you point the session at a
server that speaks the protocol, and its tools become available to the model.

This lab uses the **Microsoft Learn** MCP server over HTTP — the same one this
repository already configures for VS Code — so there is nothing to install.

## Step 2 — Configure the server

Open
[`mcp_sample.py`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/src/AgentOrchestrator-python/sdk_labs/mcp_sample.py)
and find the session configuration:

```python
session = await client.create_session(
    model=model_id,
    streaming=False,
    mcp_servers={
        "microsoft.docs.mcp": {
            "type": "http",
            "url": "https://learn.microsoft.com/api/mcp",
            "tools": ["*"],
        }
    },
    on_permission_request=PermissionHandler.approve_all,
)
```

💡 **Plain dictionaries are the API here.** `MCPServerConfig` is a `TypedDict`
union, not a class you instantiate. The .NET SDK requires an
`IDictionary<string, McpServerConfig>` and rejects a loose dictionary at compile
time; Python just takes the literal.

The union has two shapes:

| Shape | Required fields | Use when |
|:------|:----------------|:---------|
| `MCPHTTPServerConfig` | `type` (`"http"` or `"sse"`), `url`, `tools` | The server is reachable over the network |
| `MCPStdioServerConfig` | `type` (`"local"` or `"stdio"`), `command`, `tools` | The server runs as a local subprocess |

⚠️ **`tools` is required, not optional.** Use `["*"]` to allow everything the
server publishes, or list specific tool names to narrow it. Omitting the key is
a type error.

⚠️ **`on_permission_request` matters here too.** As in
[Lab 03](../03-tools/), Python denies tool calls when no handler is supplied.
`PermissionHandler.approve_all` is fine for a lab; it is not fine for anything
touching real data.

## Step 3 — Run it

```bash
cd src/AgentOrchestrator-python
uv run python -m sdk_labs mcp
```

Verified output:

```text
== Lab 06: mcp ==

Model: claude-haiku-4.5
Prompt: asking the model to consult Microsoft Learn docs

  [mcp] session.mcp_server_status_changed
  [mcp] session.mcp_servers_loaded
  [mcp] session.mcp_server_status_changed
  [tool-request] assistant.message: microsoft.docs.mcp/microsoft_docs_search
  [tool] tool.execution_start: microsoft.docs.mcp/microsoft_docs_search
  [tool] tool.execution_complete: microsoft.docs.mcp/microsoft_docs_search (success=True)

Assistant: Let me fetch the main Azure Container Apps documentation page for a clearer overview:
  [tool-request] assistant.message: microsoft.docs.mcp/microsoft_docs_fetch
  [tool] tool.execution_start: microsoft.docs.mcp/microsoft_docs_fetch
  [tool] tool.execution_complete: microsoft.docs.mcp/microsoft_docs_fetch (success=True)

Assistant: **Azure Container Apps** is a serverless platform for running containerized applications without managing underlying infrastructure—you provide your container, and Azure handles the servers, orchestration, and deployment. It automatically scales based on demand (HTTP traffic, events, or resource load) and supports microservices, APIs, background jobs, and event-driven workloads with built-in features like traffic splitting, secrets management, and HTTPS ingress.

✅ MCP tool(s) invoked: microsoft.docs.mcp/microsoft_docs_fetch, microsoft.docs.mcp/microsoft_docs_search
```

Two real MCP tools ran — `microsoft_docs_search` to find relevant pages, then
`microsoft_docs_fetch` to read one. The final line confirms it and the sample
exits **zero**.

💡 **The .NET track records a different result.** In that run the Learn server
loaded but never surfaced its tools, so the model fell back to the built-in
`web_fetch` and the sample exited non-zero. Same server, same protocol,
different outcome — which is precisely why the next step exists.

## Step 4 — Prove the tools were actually used

This is the real lesson of the lab. Azure Container Apps is public knowledge, so
a model can produce a confident, plausible, correctly-cited answer **without
calling any MCP tool at all**. A good answer is not evidence.

The sample subscribes to the events that constitute actual evidence:

- `session.mcp_servers_loaded` — the configuration was accepted
- `session.mcp_server_status_changed` — the server connection changed state
- `mcp.tools_list_changed` — the server published its tool list
- `tool.execution_start` / `tool.execution_complete` — a tool actually ran

The critical detail is how a tool is judged to be *MCP*. `tool.execution_start`
carries an `mcp_server_name`, and only executions where that is set are counted:

```python
# Only a tool carrying an MCP server name came from MCP.
# Built-ins such as web_fetch must not count, or an
# unreachable server still reports success.
if evt.data.mcp_server_name:
    mcp_tools.add(tool_name)

invoked_tools.add(tool_name)
```

If nothing MCP ran, the sample says so and exits non-zero:

```python
if not mcp_tools:
    print("⚠️  No MCP tool was invoked.")
    if invoked_tools:
        print(f"    The model used non-MCP tool(s) instead: {', '.join(sorted(invoked_tools))}")
    return 1
```

⚠️ **Counting the wrong thing is worse than not checking.** An earlier version
counted *any* tool execution and cheerfully reported
`✅ MCP tool(s) invoked: web_fetch` — success for a tool with nothing to do with
MCP. That manufactures confidence in a broken integration.

💡 Set `SDKLABS_TRACE_EVENTS=1` to print every event, not just the MCP-relevant
ones, when you are debugging a server that will not connect:

```bash
SDKLABS_TRACE_EVENTS=1 uv run python -m sdk_labs mcp
```

## Step 5 — Compare with the editor configuration

This repository already configures the same server for VS Code in
[`.vscode/mcp.json`](https://github.com/vicperdana/aigenius-copilotsdk-s5ep2/blob/main/.vscode/mcp.json):

```json
{
  "servers": {
    "microsoft.docs.mcp": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

That file is for the editor. The `mcp_servers=` argument is for the Copilot SDK
session running inside your app or sample. Different consumers, same server,
same protocol.

That is the point of MCP: one protocol, many clients. The same tool server can
serve an editor, a CLI, a test harness, or an application agent.

## ⚠️ Traps

- **`tools` is mandatory** in both config shapes; use `["*"]` for everything
- **Omitting `on_permission_request`** causes tool calls to be denied in Python
- **The Learn server is reached over the network.** If it is unreachable the
  model has no MCP tools and may quietly answer from its own knowledge — hence
  the non-zero exit
- **A plausible answer is not proof.** Only `mcp_server_name` on a tool
  execution proves an MCP tool ran
- **MCP servers are third-party code** and can expose powerful capabilities. Vet
  the server, its permissions, and its data access before pointing an agent that
  handles real work at it

## 💡 Extra credit

1. Narrow `tools` from `["*"]` to a single tool name and watch the model adapt
2. Add a second MCP server and compare how the model chooses between toolsets
3. Pass the server name in `disabled_mcp_servers=[...]`, rerun the same prompt,
   and compare the answer with and without Learn tools available
4. Swap the HTTP config for a stdio one — `{"type": "stdio", "command": "...",
   "tools": ["*"]}` — against any local MCP server you have
5. Explore `mcp_oauth_token_storage`, `github_mcp_tool_config`, and
   `enable_mcp_apps` for authenticated or richer MCP scenarios

## ✅ Checkpoint

You can now explain:

- [x] How MCP differs from the tools you wrote yourself in Lab 03
- [x] When to use the HTTP config shape versus the stdio one
- [x] That `mcp_servers` takes plain dictionaries because the configs are
      `TypedDict`s, and that `tools` is required
- [x] Why a plausible answer is not proof that MCP tools were called
- [x] How `mcp_server_name` distinguishes a real MCP tool from a built-in
- [x] How `.vscode/mcp.json` and SDK configuration target the same server

## Related

- Previous: [Lab 05 — Sessions](../05-sessions/)
- Next: [Lab 07 — Wrap-up](../07-wrap-up/)
- [Demo: Copilot SDK integration](../../demos-python/01-copilot-sdk-integration.md)
- [Troubleshooting](../../breakouts/troubleshooting.md)
