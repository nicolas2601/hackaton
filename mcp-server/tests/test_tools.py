"""Unit tests for CacaoTrace MCP tools."""
import asyncio

import pytest

from mcp_server.server import get_mercados_exportacion


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


def test_mercados_always_returns_prices():
    data = _run(get_mercados_exportacion())
    assert "precios_cop_kg" in data
    assert "precios_export_usd_ton" in data
    assert "destinos_principales_2025" in data
    assert "regulaciones" in data
    assert "EUDR" in data["regulaciones"]


def test_mercados_filter_by_variedad():
    data = _run(get_mercados_exportacion(variedad="trinitario"))
    assert data["filtro_variedad"] == "trinitario"


def test_mercados_filter_by_destino():
    data = _run(get_mercados_exportacion(pais_destino="Alemania"))
    assert data["filtro_destino"] == "Alemania"


def test_mercados_precios_ranges_valid():
    data = _run(get_mercados_exportacion())
    for tier, rng in data["precios_cop_kg"].items():
        assert len(rng) == 2
        assert rng[0] < rng[1]
