"""Entry point — runs FastMCP (port 8765) and /chat FastAPI (port 8766) concurrently."""
import asyncio
import os

import uvicorn

from mcp_server.chat_api import app as chat_app
from mcp_server.server import mcp

MCP_PORT = int(os.getenv("MCP_PORT", "8765"))
CHAT_PORT = int(os.getenv("CHAT_PORT", "8766"))


async def _run_chat():
    cfg = uvicorn.Config(chat_app, host="0.0.0.0", port=CHAT_PORT, log_level="info")
    await uvicorn.Server(cfg).serve()


async def _run_mcp():
    # FastMCP's run_async exposes streamable-http transport on the given port.
    await mcp.run_async(transport="streamable-http", host="0.0.0.0", port=MCP_PORT)


async def main():
    await asyncio.gather(_run_mcp(), _run_chat())


if __name__ == "__main__":
    asyncio.run(main())
