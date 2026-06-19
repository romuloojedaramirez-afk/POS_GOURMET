from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
import os
from ..database import get_db
from ..models import ConversacionWhatsApp, Cliente, Pedido, ConfigRestaurante
from ..schemas import WhatsAppIncoming, WhatsAppEnviar, ConversacionOut
from ..services.whatsapp_service import WhatsAppService

router = APIRouter()


def get_wa_service(db: Session = Depends(get_db)) -> WhatsAppService:
    token = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_token").first()
    phone_id = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_phone_id").first()
    return WhatsAppService(
        token=token.valor if token else os.getenv("WA_TOKEN", ""),
        phone_id=phone_id.valor if phone_id else os.getenv("WA_PHONE_ID", ""),
        db=db,
    )


# ── VERIFICACIÓN META ─────────────────────────────────────────────────────────

@router.get("/webhook")
async def verificar_webhook(request: Request):
    """Verificación del webhook de Meta WhatsApp Cloud API."""
    params = dict(request.query_params)
    verify_token = os.getenv("WA_VERIFY_TOKEN", "gormetpos2024")

    if (params.get("hub.mode") == "subscribe" and
            params.get("hub.verify_token") == verify_token):
        return int(params["hub.challenge"])
    raise HTTPException(status_code=403, detail="Verificación fallida")


# ── RECEPCIÓN META WEBHOOK ────────────────────────────────────────────────────

@router.post("/webhook")
async def recibir_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Recibe mensajes de WhatsApp Cloud API de Meta."""
    try:
        body = await request.json()
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        for msg in messages:
            telefono = msg.get("from", "")
            tipo = msg.get("type", "text")
            nombre = contacts[0].get("profile", {}).get("name", "Cliente") if contacts else "Cliente"

            texto = ""
            if tipo == "text":
                texto = msg.get("text", {}).get("body", "")
            elif tipo == "interactive":
                interactivo = msg.get("interactive", {})
                if interactivo.get("type") == "button_reply":
                    texto = interactivo["button_reply"]["id"]
                elif interactivo.get("type") == "list_reply":
                    texto = interactivo["list_reply"]["id"]

            if telefono and texto:
                background_tasks.add_task(
                    procesar_mensaje_background, telefono, texto, nombre, db
                )

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def procesar_mensaje_background(telefono: str, mensaje: str, nombre: str, db: Session):
    service = WhatsAppService(
        token=os.getenv("WA_TOKEN", ""),
        phone_id=os.getenv("WA_PHONE_ID", ""),
        db=db,
    )
    await service.procesar_mensaje(telefono, mensaje, nombre)


# ── ENDPOINT MANUAL (PRUEBAS) ─────────────────────────────────────────────────

@router.post("/simular")
async def simular_mensaje(
    data: WhatsAppIncoming,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Simula recibir un mensaje de WhatsApp (para pruebas sin Meta API)."""
    background_tasks.add_task(
        procesar_mensaje_background, data.telefono, data.mensaje, data.nombre, db
    )
    return {"ok": True, "mensaje": "Procesando..."}


@router.post("/enviar")
async def enviar_mensaje_manual(
    data: WhatsAppEnviar,
    db: Session = Depends(get_db)
):
    """Envía un mensaje manual de WhatsApp."""
    service = get_wa_service(db)
    resultado = await service.enviar_texto(data.telefono, data.mensaje)
    return resultado


# ── CONVERSACIONES ────────────────────────────────────────────────────────────

@router.get("/conversaciones", response_model=List[ConversacionOut])
def listar_conversaciones(db: Session = Depends(get_db)):
    return db.query(ConversacionWhatsApp).filter(
        ConversacionWhatsApp.activa == True
    ).order_by(ConversacionWhatsApp.updated_at.desc()).limit(50).all()


@router.get("/conversaciones/{conv_id}")
def detalle_conversacion(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(ConversacionWhatsApp).filter(ConversacionWhatsApp.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    datos = json.loads(conv.datos_pedido_json or "{}")
    return {
        "id": conv.id,
        "telefono": conv.telefono,
        "nombre": conv.nombre,
        "estado_flujo": conv.estado_flujo,
        "datos_pedido": datos,
        "ultimo_mensaje": conv.ultimo_mensaje,
        "activa": conv.activa,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
    }


@router.delete("/conversaciones/{conv_id}")
def resetear_conversacion(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(ConversacionWhatsApp).filter(ConversacionWhatsApp.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    conv.estado_flujo = "inicio"
    conv.datos_pedido_json = "{}"
    conv.activa = False
    db.commit()
    return {"ok": True}
