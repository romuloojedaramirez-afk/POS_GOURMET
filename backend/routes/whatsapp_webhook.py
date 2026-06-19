"""
WhatsApp Webhook Routes — API completa.

ENDPOINTS:
  GET  /webhook              ← Verificación Meta (obligatorio)
  POST /webhook              ← Recibe mensajes de Meta Cloud API
  POST /simular              ← Pruebas sin Meta API (simulador)
  POST /enviar               ← Envío manual de texto
  POST /enviar-botones       ← Envío manual con botones
  POST /enviar-imagen        ← Envío de imagen con caption
  POST /envio-masivo         ← Envía a todos los contactos de la BD
  POST /envio-menu-dia       ← Envía menú del día a todos los contactos
  GET  /contactos            ← Lista de teléfonos de la BD
  GET  /menu-datos           ← Menú completo cargado desde la BD (JSON)
  GET  /conversaciones       ← Lista de conversaciones activas
  GET  /conversaciones/{id}  ← Detalle de una conversación
  DELETE /conversaciones/{id}← Resetear conversación
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import json
import os

from ..database import get_db
from ..models import ConversacionWhatsApp, Cliente, ConfigRestaurante
from ..schemas import ConversacionOut
from ..services.whatsapp_service import WhatsAppService

router = APIRouter()


# ── Schemas de entrada ────────────────────────────────────────────────────────

class MsgSimular(BaseModel):
    telefono: str
    mensaje:  str
    nombre:   str = "Cliente"

class MsgTexto(BaseModel):
    telefono: str
    mensaje:  str

class MsgBotones(BaseModel):
    telefono: str
    cuerpo:   str
    botones:  list        # [{"id": str, "title": str}]
    header:   str = None
    footer:   str = None

class MsgImagen(BaseModel):
    telefono:  str
    imagen_url: str
    caption:   str = ""

class MsgMasivo(BaseModel):
    mensaje:  str
    tipo:     str = "texto"  # "texto" | "botones"
    botones:  list = []

class MsgMenuDia(BaseModel):
    pass  # usa config de la BD


# ── Fábrica del servicio ──────────────────────────────────────────────────────

def _wa_service(db: Session = Depends(get_db)) -> WhatsAppService:
    """Crea WhatsAppService leyendo token y phone_id de la BD o variables de entorno."""
    tk  = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_token").first()
    pid = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_phone_id").first()
    return WhatsAppService(
        token    = (tk.valor  if tk  else None) or os.getenv("WA_TOKEN",    ""),
        phone_id = (pid.valor if pid else None) or os.getenv("WA_PHONE_ID", ""),
        db       = db,
    )


# ── VERIFICACIÓN META ─────────────────────────────────────────────────────────

@router.get("/webhook")
async def verificar_webhook(request: Request):
    """Meta llama a este endpoint para verificar el webhook al configurarlo."""
    params       = dict(request.query_params)
    verify_token = os.getenv("WA_VERIFY_TOKEN", "gormetpos2024")
    if (params.get("hub.mode") == "subscribe" and
            params.get("hub.verify_token") == verify_token):
        return int(params["hub.challenge"])
    raise HTTPException(status_code=403, detail="Token de verificación incorrecto")


# ── WEBHOOK DE MENSAJES ENTRANTES (Meta Cloud API) ────────────────────────────

@router.post("/webhook")
async def recibir_mensaje_meta(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Meta envía aquí cada mensaje que llega al número de WhatsApp Business.
    Soporta: texto, button_reply (botones), list_reply (listas).
    """
    try:
        body     = await request.json()
        entry    = body.get("entry",   [{}])[0]
        changes  = entry.get("changes",[{}])[0]
        value    = changes.get("value", {})
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        for msg in messages:
            telefono = msg.get("from", "")
            tipo     = msg.get("type", "text")
            nombre   = "Cliente"
            if contacts:
                nombre = contacts[0].get("profile", {}).get("name", "Cliente")

            texto = ""
            if tipo == "text":
                texto = msg.get("text", {}).get("body", "")
            elif tipo == "interactive":
                ia = msg.get("interactive", {})
                if ia.get("type") == "button_reply":
                    texto = ia["button_reply"]["id"]
                elif ia.get("type") == "list_reply":
                    texto = ia["list_reply"]["id"]
            elif tipo == "image":
                # Si el cliente envía una imagen, la procesamos como confirmación de pago
                texto = "pago_imagen"

            if telefono and texto:
                background_tasks.add_task(
                    _procesar_bg, telefono, texto, nombre, db
                )

        return {"status": "ok"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def _procesar_bg(telefono: str, mensaje: str, nombre: str, db: Session):
    """Tarea de fondo: procesa el mensaje. Lee token de la BD primero, luego env vars."""
    tk  = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_token").first()
    pid = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == "whatsapp_phone_id").first()
    svc = WhatsAppService(
        token    = (tk.valor  if tk  else None) or os.getenv("WA_TOKEN",    ""),
        phone_id = (pid.valor if pid else None) or os.getenv("WA_PHONE_ID", ""),
        db       = db,
    )
    await svc.procesar_mensaje(telefono, mensaje, nombre)


# ── SIMULADOR (sin Meta API) ──────────────────────────────────────────────────

@router.post("/simular")
async def simular_mensaje(
    data: MsgSimular,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Simula recibir un mensaje de WhatsApp.
    El bot responde igual que con la API real, pero los mensajes se muestran
    en la consola en lugar de enviarse por WhatsApp.
    """
    background_tasks.add_task(
        _procesar_bg, data.telefono, data.mensaje, data.nombre, db
    )
    return {"ok": True, "procesando": f"{data.telefono} → '{data.mensaje}'"}


# ── ENVÍOS MANUALES ───────────────────────────────────────────────────────────

@router.post("/enviar")
async def enviar_texto_manual(data: MsgTexto, db: Session = Depends(get_db)):
    """Envía un mensaje de texto a un número específico."""
    svc = _wa_service(db)
    res = await svc.enviar_texto(data.telefono, data.mensaje)
    return {"ok": True, "resultado": res}


@router.post("/enviar-botones")
async def enviar_botones_manual(data: MsgBotones, db: Session = Depends(get_db)):
    """Envía mensaje con botones interactivos (máx 3 botones)."""
    svc = _wa_service(db)
    res = await svc.enviar_botones(
        data.telefono, data.cuerpo, data.botones,
        data.header, data.footer
    )
    return {"ok": True, "resultado": res}


@router.post("/enviar-imagen")
async def enviar_imagen_manual(data: MsgImagen, db: Session = Depends(get_db)):
    """Envía una imagen con caption a un número específico."""
    svc = _wa_service(db)
    res = await svc.enviar_imagen(data.telefono, data.imagen_url, data.caption)
    return {"ok": True, "resultado": res}


# ── ENVÍO MASIVO ──────────────────────────────────────────────────────────────

@router.post("/envio-masivo")
async def envio_masivo(data: MsgMasivo, db: Session = Depends(get_db)):
    """
    Envía un mensaje a TODOS los contactos de la base de datos.
    Fuente de datos: tabla Cliente + ConversacionWhatsApp.
    tipo = 'texto' → texto plano
    tipo = 'botones' → mensaje con botones interactivos
    """
    svc = _wa_service(db)
    if data.tipo == "botones" and data.botones:
        resultado = await svc.envio_masivo_botones(data.mensaje, data.botones)
    else:
        resultado = await svc.envio_masivo_texto(data.mensaje)
    return {"ok": True, **resultado}


@router.post("/envio-menu-dia")
async def envio_menu_dia(db: Session = Depends(get_db)):
    """
    Envía el menú del día a todos los contactos:
    1. Imagen del restaurante (si hay URL configurada)
    2. Botones: Ver Menú, Mis Pedidos, Ubicación
    """
    svc = _wa_service(db)
    resultado = await svc.envio_menu_del_dia()
    return {"ok": True, **resultado}


# ── DATOS DEL MENÚ (lo que absorbe la IA y el bot) ───────────────────────────

@router.get("/menu-datos")
def obtener_menu_datos(db: Session = Depends(get_db)):
    """
    Devuelve el menú completo cargado desde la BD en formato JSON.
    Este es exactamente el JSON que el bot usa para construir
    los mensajes interactivos de WhatsApp (listas y botones).
    """
    svc  = _wa_service(db)
    menu = svc.cargar_menu()
    # Convertir para serialización JSON
    return {
        "fuente": "base_de_datos",
        "tablas": ["Categoria", "Producto"],
        "total_categorias": len(menu),
        "total_productos":  sum(len(v["productos"]) for v in menu.values()),
        "menu": {
            str(cat_id): info
            for cat_id, info in menu.items()
        }
    }


# ── CONTACTOS (base de datos de teléfonos) ────────────────────────────────────

@router.get("/contactos")
def listar_contactos(db: Session = Depends(get_db)):
    """
    Devuelve todos los números de teléfono de la BD.
    Fuente: tabla Cliente (campo telefono) + ConversacionWhatsApp.
    Estos son los contactos que reciben los envíos masivos.
    """
    svc       = _wa_service(db)
    contactos = svc.cargar_contactos()
    return {
        "total":     len(contactos),
        "fuente":    ["Cliente", "ConversacionWhatsApp"],
        "contactos": contactos
    }


# ── CONVERSACIONES ────────────────────────────────────────────────────────────

@router.get("/conversaciones")
def listar_conversaciones(db: Session = Depends(get_db)):
    """Lista todas las conversaciones activas con estado del pipeline."""
    convs = db.query(ConversacionWhatsApp).filter(
        ConversacionWhatsApp.activa == True
    ).order_by(ConversacionWhatsApp.updated_at.desc()).limit(50).all()

    return [
        {
            "id":            c.id,
            "telefono":      c.telefono,
            "nombre":        c.nombre,
            "estado_flujo":  c.estado_flujo,
            "ultimo_mensaje":c.ultimo_mensaje,
            "activa":        c.activa,
            "created_at":    c.created_at.isoformat(),
            "updated_at":    c.updated_at.isoformat(),
        }
        for c in convs
    ]


@router.get("/conversaciones/{conv_id}")
def detalle_conversacion(conv_id: int, db: Session = Depends(get_db)):
    """Detalle completo de una conversación incluyendo carrito actual."""
    conv = db.query(ConversacionWhatsApp).filter(
        ConversacionWhatsApp.id == conv_id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    datos = json.loads(conv.datos_pedido_json or "{}")
    return {
        "id":            conv.id,
        "telefono":      conv.telefono,
        "nombre":        conv.nombre,
        "estado_flujo":  conv.estado_flujo,
        "datos_pedido":  datos,
        "ultimo_mensaje":conv.ultimo_mensaje,
        "activa":        conv.activa,
        "created_at":    conv.created_at.isoformat(),
        "updated_at":    conv.updated_at.isoformat(),
    }


@router.delete("/conversaciones/{conv_id}")
def resetear_conversacion(conv_id: int, db: Session = Depends(get_db)):
    """Resetea una conversación al estado inicial."""
    conv = db.query(ConversacionWhatsApp).filter(
        ConversacionWhatsApp.id == conv_id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    conv.estado_flujo      = "inicio"
    conv.datos_pedido_json = "{}"
    conv.activa            = False
    db.commit()
    return {"ok": True, "mensaje": "Conversación reseteada"}
