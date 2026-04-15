"""FastMCP Server for Manufactura Santander 4.0.

Exposes tools for AI agents to query production data from Django.
"""
import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastmcp import FastMCP

log = structlog.get_logger()

MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgres://manufactura:manufactura_dev_password@postgres:5432/manufactura_dev"
)

mcp = FastMCP("manufactura-mcp")


@mcp.tool()
async def get_production_summary(tenant_id: str) -> dict:
    """Get production summary for a tenant.

    Args:
        tenant_id: Tenant identifier

    Returns:
        Summary of active orders, production lines, and alerts
    """
    log.info("get_production_summary", tenant_id=tenant_id)
    return {
        "tenant_id": tenant_id,
        "active_orders": 0,
        "production_lines": 0,
        "active_alerts": 0,
        "message": "Production summary - MCP server active"
    }


@mcp.tool()
async def get_machine_status(tenant_id: str, machine_id: str | None = None) -> dict:
    """Get machine operational status.

    Args:
        tenant_id: Tenant identifier
        machine_id: Optional specific machine ID

    Returns:
        Machine status information
    """
    log.info("get_machine_status", tenant_id=tenant_id, machine_id=machine_id)
    return {
        "tenant_id": tenant_id,
        "machines": [],
        "message": "Machine status - MCP server active"
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("mcp_server_startup", port=MCP_SERVER_PORT)
    yield
    log.info("mcp_server_shutdown")


# FastAPI app for uvicorn - serves both HTTP and MCP
app = FastAPI(title="manufactura-mcp", lifespan=lifespan)

# Mount MCP to FastAPI
mcp.mount("/mcp", app)


# Entry point for uvicorn
def get_app():
    return app


# Alias for docker-compose reference
server = app
app_var = app