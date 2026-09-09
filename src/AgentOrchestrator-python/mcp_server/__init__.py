"""Read-only MCP server exposing the retail database to Copilot chat.

Mirrors ``AgentHQDemo.McpServer`` in the .NET track.
"""

from mcp_server.server import build_server

__all__ = ["build_server"]
