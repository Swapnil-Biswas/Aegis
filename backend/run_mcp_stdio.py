"""
AEGIS MCP Server STDIO Entrypoint.
Enables local MCP clients (Cursor, Claude Desktop, Antigravity) to connect via standard I/O.
"""

import sys
import os
import asyncio

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.mcp.server import mcp_server


def main():
    """Runs the AEGIS MCP server using the official STDIO transport."""
    asyncio.run(mcp_server.run_stdio_async())


if __name__ == "__main__":
    main()

