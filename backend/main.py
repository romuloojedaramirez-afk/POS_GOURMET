"""
GourmetPOS ERP - Backend FastAPI
Versión 2.0 Profesional
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from typing import List
import asyncio
import json
import os

from .database import engine, Base, SessionLocal
from .models import *  # noqa: F401,F403
from .seed_data import seed_database
from .routes import mesas, menu, pedidos, caja, clientes, reportes, whatsapp_webhook, config


# ── LIFESPAN ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


# ── APP ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GourmetPOS ERP",
    description="Sistema ERP completo para restaurantes con WhatsApp integrado",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── WEBSOCKET MANAGER ─────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast({"tipo": "ping", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ── RUTAS API ──────────────────────────────────────────────────────────────────

app.include_router(mesas.router,               prefix="/api/mesas",      tags=["Mesas"])
app.include_router(menu.router,                prefix="/api/menu",       tags=["Menu"])
app.include_router(pedidos.router,             prefix="/api/pedidos",    tags=["Pedidos"])
app.include_router(caja.router,                prefix="/api/caja",       tags=["Caja"])
app.include_router(clientes.router,            prefix="/api/clientes",   tags=["Clientes"])
app.include_router(reportes.router,            prefix="/api/reportes",   tags=["Reportes"])
app.include_router(whatsapp_webhook.router,    prefix="/api/whatsapp",   tags=["WhatsApp"])
app.include_router(config.router,              prefix="/api/config",     tags=["Config"])


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0", "app": "GourmetPOS ERP"}


# ── SERVIR FRONTEND ────────────────────────────────────────────────────────────

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
