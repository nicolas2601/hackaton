"""Entry point for MCP server."""
import uvicorn

from mcp_server.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)