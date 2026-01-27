#!/usr/bin/env python3
"""MCP Server: Ontological Orchestration Portal
   Delegates to orchestrator.py (the Real Work)"""

# Ontological imports
import os
import sys
import asyncio
sys.path.insert(0, '.')
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from orchestrator import app as OrchestratorMind  # The Philosopher's Engine

async def _run_stdio():
    async with stdio_server() as (read_stream, write_stream):
        await OrchestratorMind.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="state-orchestrator-mcp",
                server_version="0.1.0",
                capabilities=OrchestratorMind.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def _run_http():
    app.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "3000")),
        path="/mcp",
    )

if __name__ == "__main__":
    import asyncio
    transport = os.environ.get("MCP_TRANSPORT", "http").lower()
    if transport == "stdio":
        asyncio.run(_run_stdio())
    else:
        _run_http()
