"""FastAPI wrapper exposing /chat for the frontend.

LLM-agnostic. Stub provider ships tokens as SSE so the UI stays identical
regardless of which backend (Claude / Qwen / Gemini) is wired in.
"""
import asyncio
import json
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI(title="CacaoTrace Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROVIDER = os.getenv("LLM_PROVIDER", "stub")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MCP_URL = os.getenv("MCP_URL", "http://localhost:8765")

SYSTEM = """Eres el asistente de CacaoTrace, especializado en cacao fino de Santander, Colombia.
Hablás con Don Efraín, cacaocultor de San Vicente. Usá español colombiano natural, sin tecnicismos.
Usá las tools MCP para consultar datos reales de su finca.
Protegé la info privada — nunca la compartas públicamente."""


async def _stub_stream(messages, finca_id):
    q = messages[-1]["content"].lower() if messages else ""
    if "fermenta" in q or "sensor" in q or "lote" in q:
        yield 'data: {"role":"tool","name":"get_lote_sensors","args":{"lote_id":1}}\n\n'
        await asyncio.sleep(0.5)
    reply = (
        "Don Efraín, su fermentación del Lote Norte va bien — temperatura promedio "
        "45°C, dentro de rango. En 2 días empezaría el secado. ¿Le armo una "
        "recomendación de movimiento de la masa?"
    )
    for word in reply.split():
        yield f'data: {json.dumps({"role": "assistant", "delta": word + " "})}\n\n'
        await asyncio.sleep(0.04)
    yield "data: [DONE]\n\n"


async def _anthropic_stream(messages, finca_id):
    # TODO: wire Anthropic Messages API with MCP tool-use.
    async for chunk in _stub_stream(messages, finca_id):
        yield chunk


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    messages = body.get("messages", [])
    finca_id = body.get("finca_id", 1)
    if PROVIDER == "claude" and ANTHROPIC_KEY:
        gen = _anthropic_stream(messages, finca_id)
    else:
        gen = _stub_stream(messages, finca_id)
    return StreamingResponse(
        gen,
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )


@app.get("/health")
async def health():
    return {"ok": True, "provider": PROVIDER}
