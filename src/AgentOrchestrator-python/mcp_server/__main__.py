"""Entry point: ``python -m mcp_server``.

Speaks MCP over stdio, which is how ``CopilotChatService`` launches it. Nothing
here may write to stdout — that stream carries the protocol. Logging goes to
stderr by default, so leave it that way.
"""

import sys

from mcp_server.server import build_server


def main() -> int:
    try:
        server = build_server()
    except FileNotFoundError as ex:
        print(ex, file=sys.stderr)
        return 1

    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
