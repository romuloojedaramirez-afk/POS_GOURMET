"""
Servicio WhatsApp Business Cloud API.
Maneja el flujo completo: bienvenida → menú → producto → pago → cocina.
"""
import httpx
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import (
    ConversacionWhatsApp, Cliente, Pedido, DetallePedido,
    Producto, Categoria, EstadoPedido, CanalPedido, ConfigRestaurante
)


class WhatsAppService:

    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, token: str, phone_id: str, db: Session):
        self.token = token
        self.phone_id = phone_id
        self.db = db
        self._config_cache = {}

    def _cfg(self, clave: str, default: str = "") -> str:
        if clave not in self._config_cache:
            row = self.db.query(ConfigRestaurante).filter(
                ConfigRestaurante.clave == clave
            ).first()
            self._config_cache[clave] = row.valor if row else default
        return self._config_cache[clave]

    async def enviar_texto(self, telefono: str, texto: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "text",
            "text": {"body": texto}
        }
        return await self._post(payload)

    async def enviar_botones(self, telefono: str, cuerpo: str, botones: list) -> dict:
        """Envía mensaje con botones interactivos (máx 3)."""
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": cuerpo},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": b["id"], "title": b["titulo"][:20]}}
                        for b in botones[:3]
                    ]
                }
            }
        }
        return await self._post(payload)

    async def enviar_lista(self, telefono: str, cuerpo: str, boton: str, secciones: list) -> dict:
        """Envía mensaje con lista de opciones."""
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": cuerpo},
                "action": {
                    "button": boton,
                    "sections": secciones
                }
            }
        }
        return await self._post(payload)

    async def _post(self, payload: dict) -> dict:
        if not self.token or not self.phone_id:
            print(f"[WA-SIM] → {payload}")
            return {"simulated": True}
        url = f"{self.BASE_URL}/{self.phone_id}/messages"
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10,
            )
            return r.json()

    # ── FLUJO PRINCIPAL ───────────────────────────────────────────────────────

    async def procesar_mensaje(self, telefono: str, mensaje: str, nombre: str):
        conv = self._obtener_conv(telefono, nombre)
        datos = json.loads(conv.datos_pedido_json or "{}")
        msg = mensaje.strip().lower()

        handler = {
            "inicio": self._flujo_inicio,
            "menu_categorias": self._flujo_categorias,
            "menu_productos": self._flujo_productos,
            "detalle_producto": self._flujo_detalle_producto,
            "agregar_complemento": self._flujo_complementos,
            "confirmar_pedido": self._flujo_confirmacion,
            "seleccionar_pago": self._flujo_pago,
            "pedido_enviado": self._flujo_post_pago,
        }.get(conv.estado_flujo, self._flujo_inicio)

        nuevo_estado, nuevos_datos = await handler(telefono, msg, datos)

        conv.estado_flujo = nuevo_estado
        conv.datos_pedido_json = json.dumps(nuevos_datos, ensure_ascii=False)
        conv.ultimo_mensaje = mensaje
        conv.updated_at = datetime.utcnow()
        self.db.commit()

    # ── ESTADOS DEL FLUJO ─────────────────────────────────────────────────────

    async def _flujo_inicio(self, tel: str, msg: str, datos: dict):
        nombre_rest = self._cfg("nombre", "GourmetPOS")
        await self.enviar_botones(
            tel,
            f"¡Hola! 👋 Bienvenido a *{nombre_rest}* 🍽️\n\n"
            "¿Qué deseas hacer hoy?",
            [
                {"id": "ver_menu", "titulo": "📋 Ver Menú"},
                {"id": "mis_pedidos", "titulo": "📦 Mis Pedidos"},
                {"id": "contactar", "titulo": "📞 Contactar"},
            ]
        )
        return "menu_categorias", {}

    async def _flujo_categorias(self, tel: str, msg: str, datos: dict):
        if msg in ["hola", "inicio", "menu", "menú", "start", "/start"]:
            return await self._flujo_inicio(tel, msg, datos)

        categorias = self.db.query(Categoria).filter(Categoria.activo == True).order_by(Categoria.orden).all()

        if not categorias:
            await self.enviar_texto(tel, "❌ No hay categorías disponibles en este momento.")
            return "inicio", {}

        secciones = [{
            "title": "Categorías del Menú",
            "rows": [
                {"id": f"cat_{c.id}", "title": f"{c.emoji} {c.nombre}"[:24]}
                for c in categorias
            ]
        }]

        await self.enviar_lista(
            tel,
            "🍽️ *Nuestro Menú*\nSelecciona una categoría para ver los platos:",
            "Ver Categorías",
            secciones
        )
        return "menu_productos", datos

    async def _flujo_productos(self, tel: str, msg: str, datos: dict):
        if not msg.startswith("cat_"):
            await self.enviar_texto(tel, "Por favor selecciona una categoría del menú 👆")
            return "menu_productos", datos

        try:
            cat_id = int(msg.replace("cat_", ""))
        except ValueError:
            return "menu_categorias", datos

        productos = self.db.query(Producto).filter(
            Producto.categoria_id == cat_id,
            Producto.disponible == True
        ).all()

        if not productos:
            await self.enviar_texto(tel, "😔 No hay productos disponibles en esta categoría.")
            return "menu_categorias", datos

        secciones = [{
            "title": "Selecciona un plato",
            "rows": [
                {
                    "id": f"prod_{p.id}",
                    "title": f"{p.emoji} {p.nombre}"[:24],
                    "description": f"S/ {p.precio:.2f}"[:72]
                }
                for p in productos
            ]
        }]

        await self.enviar_lista(tel, "Elige tu plato:", "Ver Platos", secciones)
        datos["cat_id"] = cat_id
        return "detalle_producto", datos

    async def _flujo_detalle_producto(self, tel: str, msg: str, datos: dict):
        if not msg.startswith("prod_"):
            await self.enviar_texto(tel, "Por favor selecciona un producto 👆")
            return "detalle_producto", datos

        try:
            prod_id = int(msg.replace("prod_", ""))
        except ValueError:
            return "menu_productos", datos

        prod = self.db.query(Producto).filter(Producto.id == prod_id).first()
        if not prod:
            await self.enviar_texto(tel, "❌ Producto no disponible.")
            return "menu_categorias", datos

        moneda = self._cfg("moneda", "S/")
        texto = (
            f"{prod.emoji} *{prod.nombre}*\n"
            f"_{prod.descripcion}_\n\n"
            f"💰 *{moneda} {prod.precio:.2f}*\n"
            f"⏱️ Tiempo de preparación: ~{prod.tiempo_prep} min\n\n"
            "¿Cuántas unidades deseas?"
        )
        await self.enviar_botones(
            tel, texto,
            [
                {"id": f"qty_1_{prod_id}", "titulo": "1️⃣ Una"},
                {"id": f"qty_2_{prod_id}", "titulo": "2️⃣ Dos"},
                {"id": f"qty_3_{prod_id}", "titulo": "3️⃣ Tres"},
            ]
        )
        datos["prod_seleccionado"] = prod_id
        return "agregar_complemento", datos

    async def _flujo_complementos(self, tel: str, msg: str, datos: dict):
        if msg.startswith("qty_"):
            partes = msg.split("_")
            if len(partes) >= 3:
                cantidad = int(partes[1])
                prod_id = int(partes[2])
                prod = self.db.query(Producto).filter(Producto.id == prod_id).first()

                carrito = datos.get("carrito", [])
                carrito.append({
                    "prod_id": prod_id,
                    "nombre": prod.nombre if prod else "Producto",
                    "precio": prod.precio if prod else 0,
                    "cantidad": cantidad,
                    "subtotal": round((prod.precio if prod else 0) * cantidad, 2),
                    "emoji": prod.emoji if prod else "🍽️",
                })
                datos["carrito"] = carrito

        bebidas = self.db.query(Producto).join(Categoria).filter(
            Categoria.nombre.ilike("%bebida%"),
            Producto.disponible == True
        ).limit(3).all()

        if bebidas:
            secciones = [{
                "title": "Bebidas",
                "rows": [
                    {
                        "id": f"beb_{b.id}",
                        "title": f"{b.emoji} {b.nombre}"[:24],
                        "description": f"S/ {b.precio:.2f}"[:72]
                    }
                    for b in bebidas
                ]
            }]
            await self.enviar_lista(
                tel,
                "🥤 ¿Deseas agregar una bebida?",
                "Agregar Bebida",
                secciones
            )
            await self.enviar_botones(
                tel, "O bien continúa con tu pedido:",
                [{"id": "no_bebida", "titulo": "✅ Sin bebida"}, {"id": "ver_menu", "titulo": "➕ Agregar más"}]
            )
        else:
            await self._mostrar_resumen(tel, datos)
            return "confirmar_pedido", datos

        return "confirmar_pedido", datos

    async def _flujo_confirmacion(self, tel: str, msg: str, datos: dict):
        if msg.startswith("beb_"):
            try:
                beb_id = int(msg.replace("beb_", ""))
                beb = self.db.query(Producto).filter(Producto.id == beb_id).first()
                if beb:
                    carrito = datos.get("carrito", [])
                    carrito.append({
                        "prod_id": beb.id,
                        "nombre": beb.nombre,
                        "precio": beb.precio,
                        "cantidad": 1,
                        "subtotal": beb.precio,
                        "emoji": beb.emoji,
                    })
                    datos["carrito"] = carrito
            except ValueError:
                pass

        if msg == "ver_menu":
            return await self._flujo_categorias(tel, msg, datos)

        await self._mostrar_resumen(tel, datos)
        return "seleccionar_pago", datos

    async def _mostrar_resumen(self, tel: str, datos: dict):
        carrito = datos.get("carrito", [])
        if not carrito:
            await self.enviar_texto(tel, "🛒 Tu carrito está vacío. Selecciona un producto del menú.")
            return

        moneda = self._cfg("moneda", "S/")
        igv_rate = float(self._cfg("igv", "0.18"))
        subtotal = sum(i["subtotal"] for i in carrito)
        igv = round(subtotal * igv_rate, 2)
        total = round(subtotal + igv, 2)

        lineas = [f"{i['emoji']} {i['nombre']} x{i['cantidad']} = {moneda} {i['subtotal']:.2f}" for i in carrito]
        resumen = "\n".join(lineas)

        datos["subtotal"] = subtotal
        datos["igv"] = igv
        datos["total"] = total

        await self.enviar_botones(
            tel,
            f"🧾 *Resumen de tu Pedido*\n\n{resumen}\n\n"
            f"Subtotal: {moneda} {subtotal:.2f}\n"
            f"IGV (18%): {moneda} {igv:.2f}\n"
            f"*Total: {moneda} {total:.2f}*\n\n"
            "¿Cómo deseas pagar?",
            [
                {"id": "pagar_ahora", "titulo": "💳 Pagar Ahora"},
                {"id": "modificar", "titulo": "✏️ Modificar"},
            ]
        )

    async def _flujo_pago(self, tel: str, msg: str, datos: dict):
        if msg == "modificar":
            return await self._flujo_categorias(tel, msg, datos)

        moneda = self._cfg("moneda", "S/")
        yape = self._cfg("yape", "N/D")
        plin = self._cfg("plin", "N/D")
        total = datos.get("total", 0)

        await self.enviar_botones(
            tel,
            f"💰 Total a pagar: *{moneda} {total:.2f}*\n\n"
            f"📱 *Yape:* {yape}\n"
            f"📱 *Plin:* {plin}\n\n"
            "Elige tu método de pago:",
            [
                {"id": "pago_yape", "titulo": "💜 Yape"},
                {"id": "pago_plin", "titulo": "🔵 Plin"},
                {"id": "pago_efectivo", "titulo": "💵 Efectivo"},
            ]
        )
        return "pedido_enviado", datos

    async def _flujo_post_pago(self, tel: str, msg: str, datos: dict):
        metodo_map = {
            "pago_yape": "yape",
            "pago_plin": "plin",
            "pago_efectivo": "efectivo",
            "pago_tarjeta": "tarjeta",
        }
        metodo = metodo_map.get(msg, "efectivo")
        datos["metodo_pago"] = metodo

        pedido_id = await self._registrar_pedido(tel, datos)
        moneda = self._cfg("moneda", "S/")
        total = datos.get("total", 0)

        await self.enviar_texto(
            tel,
            f"✅ *¡Pago Confirmado!*\n\n"
            f"🎉 Hemos recibido tu pedido #{pedido_id}\n"
            f"💰 Total: {moneda} {total:.2f}\n"
            f"💳 Método: {metodo.upper()}\n\n"
            f"⏱️ Tiempo estimado: 30-40 min\n\n"
            f"📍 ¡Tu pedido ya está en la cocina! Te avisaremos cuando esté listo. 👨‍🍳"
        )

        return "inicio", {}

    # ── HELPER: REGISTRAR PEDIDO EN BD ────────────────────────────────────────

    async def _registrar_pedido(self, telefono: str, datos: dict) -> int:
        cliente = self.db.query(Cliente).filter(Cliente.telefono == telefono).first()
        if not cliente:
            conv = self.db.query(ConversacionWhatsApp).filter(
                ConversacionWhatsApp.telefono == telefono
            ).first()
            cliente = Cliente(
                nombre=conv.nombre if conv else "Cliente WhatsApp",
                telefono=telefono,
            )
            self.db.add(cliente)
            self.db.flush()

        from datetime import datetime as dt
        total_count = self.db.query(Pedido).count()
        ticket = f"WA-{dt.now().strftime('%Y%m%d')}-{total_count + 1:04d}"

        pedido = Pedido(
            cliente_id=cliente.id,
            canal=CanalPedido.whatsapp,
            estado=EstadoPedido.pendiente,
            subtotal=datos.get("subtotal", 0),
            igv=datos.get("igv", 0),
            total=datos.get("total", 0),
            numero_ticket=ticket,
        )
        self.db.add(pedido)
        self.db.flush()

        for item in datos.get("carrito", []):
            self.db.add(DetallePedido(
                pedido_id=pedido.id,
                producto_id=item["prod_id"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio"],
                subtotal=item["subtotal"],
            ))

        cliente.total_pedidos += 1
        self.db.commit()
        return pedido.id

    def _obtener_conv(self, telefono: str, nombre: str) -> ConversacionWhatsApp:
        conv = self.db.query(ConversacionWhatsApp).filter(
            ConversacionWhatsApp.telefono == telefono
        ).first()
        if not conv:
            conv = ConversacionWhatsApp(telefono=telefono, nombre=nombre)
            self.db.add(conv)
            self.db.flush()
        else:
            if nombre and nombre != "Cliente":
                conv.nombre = nombre
        return conv
