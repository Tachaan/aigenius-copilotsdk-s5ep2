"""Lab 06 — attach an MCP server.

Uses the Microsoft Learn MCP server over HTTP — the same one this repo already
configures for VS Code in .vscode/mcp.json — so there is nothing extra to
install.
"""

import os

from copilot import CopilotClient, PermissionHandler, SessionEvent, SessionEventType

from sdk_labs import model_picker
from sdk_labs._common import IdleWaiter, flatten

MCP_EVENT_TYPES = {
    SessionEventType.SESSION_MCP_SERVERS_LOADED,
    SessionEventType.SESSION_MCP_SERVER_STATUS_CHANGED,
    SessionEventType.MCP_TOOLS_LIST_CHANGED,
}


def _format_tool_name(
    name: str | None,
    mcp_server_name: str | None = None,
    mcp_tool_name: str | None = None,
) -> str:
    if mcp_server_name and mcp_tool_name:
        return f"{mcp_server_name}/{mcp_tool_name}"
    return name or ""


async def run(requested_model_id: str | None) -> int:
    print("== Lab 06: mcp ==\n")

    async with CopilotClient() as client:
        model_id = await model_picker.pick(client, requested_model_id)
        if model_id is None:
            return 1

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

        async with session:
            waiter = IdleWaiter()
            trace_events = os.environ.get("SDKLABS_TRACE_EVENTS") == "1"
            invoked_tools: set[str] = set()
            mcp_tools: set[str] = set()
            tool_call_names: dict[str, str] = {}

            def on_event(evt: SessionEvent) -> None:
                if trace_events:
                    print(f"  [event] {evt.type.value}")

                # Surface whether the configured server actually connected —
                # without this, a failed server is indistinguishable from a
                # model that simply chose not to call a tool.
                if evt.type in MCP_EVENT_TYPES:
                    print(f"  [mcp] {evt.type.value}")

                elif evt.type is SessionEventType.TOOL_EXECUTION_START:
                    tool_name = _format_tool_name(
                        evt.data.tool_name, evt.data.mcp_server_name, evt.data.mcp_tool_name
                    )
                    if not tool_name:
                        return

                    if evt.data.tool_call_id:
                        tool_call_names[evt.data.tool_call_id] = tool_name

                    # Only a tool carrying an MCP server name came from MCP.
                    # Built-ins such as web_fetch must not count, or an
                    # unreachable server still reports success.
                    if evt.data.mcp_server_name:
                        mcp_tools.add(tool_name)

                    invoked_tools.add(tool_name)
                    print(f"  [tool] {evt.type.value}: {tool_name}")

                elif evt.type is SessionEventType.TOOL_EXECUTION_COMPLETE:
                    completed = tool_call_names.get(evt.data.tool_call_id or "")
                    if completed:
                        print(
                            f"  [tool] {evt.type.value}: {completed} (success={not evt.data.error})"
                        )

                elif evt.type is SessionEventType.EXTERNAL_TOOL_REQUESTED:
                    if evt.data.tool_name:
                        print(f"  [tool-request] {evt.type.value}: {evt.data.tool_name}")

                elif evt.type is SessionEventType.ASSISTANT_MESSAGE:
                    if evt.data.content:
                        print(f"\nAssistant: {flatten(evt.data.content)}")
                    for req in evt.data.tool_requests or []:
                        tool_name = _format_tool_name(
                            req.name,
                            getattr(req, "mcp_server_name", None),
                            getattr(req, "mcp_tool_name", None),
                        )
                        if tool_name:
                            print(f"  [tool-request] {evt.type.value}: {tool_name}")

                elif evt.type is SessionEventType.SESSION_ERROR:
                    print(f"ERROR: {evt.data.message}")

                waiter.handle(evt)

            session.on(on_event)

            print("Prompt: asking the model to consult Microsoft Learn docs\n")
            await session.send(
                "Using the Microsoft Learn tools available to you, "
                "what is Azure Container Apps? Answer in two sentences."
            )

            await waiter.wait()

    if not mcp_tools:
        print()
        print("⚠️  No MCP tool was invoked.")
        if invoked_tools:
            print(f"    The model used non-MCP tool(s) instead: {', '.join(sorted(invoked_tools))}")
        print("    The answer may have come from the model's own knowledge or a built-in")
        print("    tool rather than Microsoft Learn. Check the server is reachable and that")
        print("    its tools were loaded — look for the [mcp] lines above.")
        return 1

    print()
    print(f"✅ MCP tool(s) invoked: {', '.join(sorted(mcp_tools))}")
    return 0
