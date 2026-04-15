"""CacaoTrace MCP server — tools over the Django REST API.

Exposes 5 MCP tools consumed by LLMs to answer cacaocultor questions:
    - get_finca_info
    - get_lote_sensors
    - get_cosechas
    - get_controles_fitosanitarios
    - get_mercados_exportacion
"""
import os

import httpx
from fastmcp import FastMCP

mcp = FastMCP("cacaotrace")
API_URL = os.getenv("API_URL", "http://backend:8000")
SERVICE_TOKEN = os.getenv("MCP_API_TOKEN", "")


def _headers() -> dict:
    return {"Authorization": f"Bearer {SERVICE_TOKEN}"} if SERVICE_TOKEN else {}


@mcp.tool()
async def get_finca_info(finca_id: int) -> dict:
    """Datos de una finca: nombre, municipio, lat, lng, variedades, área, certificaciones."""
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            f"{API_URL}/api/fincas/publicas/", params={"id": finca_id}
        )
        try:
            return r.json()
        except Exception:
            return {"error": "invalid response", "status": r.status_code}


@mcp.tool()
async def get_lote_sensors(lote_id: int, tipo: str = "", limit: int = 30) -> dict:
    """Últimos N datos IoT de un lote.

    tipo: temp_suelo | hum_suelo | temp_ferm | hum_secado | ph_suelo.
    """
    params: dict = {"lote_id": lote_id, "limit": limit}
    if tipo:
        params["tipo"] = tipo
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            f"{API_URL}/api/sensors/", params=params, headers=_headers()
        )
        try:
            data = r.json()
        except Exception:
            return {"error": "invalid response", "status": r.status_code}
        if isinstance(data, dict) and "results" in data:
            data = data["results"]
        if not isinstance(data, list):
            return {"count": 0, "data": [], "raw": data}
        return {"count": len(data), "data": data[:limit]}


@mcp.tool()
async def get_cosechas(finca_id: int, año: int = 0) -> dict:
    """Historial de cosechas de una finca (kg baba, kg seco, días fermentación, calidad)."""
    params: dict = {"finca_id": finca_id}
    if año:
        params["año"] = año
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            f"{API_URL}/api/cosechas/", params=params, headers=_headers()
        )
        try:
            return r.json()
        except Exception:
            return {"error": "invalid response", "status": r.status_code}


@mcp.tool()
async def get_controles_fitosanitarios(lote_id: int) -> dict:
    """Historial fitosanitario de un lote (plagas, tratamientos, fechas, resultados)."""
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            f"{API_URL}/api/controles/",
            params={"lote_id": lote_id},
            headers=_headers(),
        )
        try:
            return r.json()
        except Exception:
            return {"error": "invalid response", "status": r.status_code}


@mcp.tool()
async def get_mercados_exportacion(
    variedad: str = "", pais_destino: str = ""
) -> dict:
    """Datos de mercado exportador de cacao: precios, destinos, regulaciones EUDR."""
    data: dict = {
        "precios_cop_kg": {
            "corriente": [8000, 10000],
            "fino_aroma_trazable": [15000, 25000],
            "premium_certificado": [25000, 40000],
        },
        "precios_export_usd_ton": {
            "corriente": [2500, 3000],
            "fino_aroma": [4000, 6000],
            "premium": [6000, 10000],
        },
        "destinos_principales_2025": [
            {"pais": "EEUU", "share": 37.1},
            {"pais": "Malasia"},
            {"pais": "México"},
            {"pais": "Costa Rica"},
            {"pais": "Bélgica"},
            {"pais": "Alemania"},
        ],
        "regulaciones": {
            "EUDR": (
                "Obligatorio para PYMES desde jun 2026 (posible extensión jun 2027, "
                "Reg UE 2025/2650). Requiere geolocalización parcelas + prueba "
                "no-deforestación + diligencia debida."
            ),
            "ICA": "Certificación fitosanitaria obligatoria para exportar desde Colombia.",
        },
        "contexto": (
            "Santander produce 41% del cacao nacional. 95% es fino de aroma (ICCO)."
        ),
    }
    if variedad:
        data["filtro_variedad"] = variedad
    if pais_destino:
        data["filtro_destino"] = pais_destino
    return data


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
