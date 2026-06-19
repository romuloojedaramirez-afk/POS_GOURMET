"""
GourmetPOS - Pipeline Johnson para WhatsApp
Procesamiento inteligente de mensajes con IA (Google Gemini)
"""
import os
import json
import asyncio
from typing import Optional
from .prompts import PROMPTS

try:
    import google.generativeai as genai
    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False
    print("[IA] google-generativeai no instalado. Usando respuestas de plantilla.")


class PipelineJohnson:
    """
    Pipeline de procesamiento de mensajes de WhatsApp.
    Usa Google Gemini para generar respuestas inteligentes.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.modelo = None
        self._inicializar_ia()

    def _inicializar_ia(self):
        if not GEMINI_DISPONIBLE or not self.api_key:
            return
        try:
            genai.configure(api_key=self.api_key)
            self.modelo = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 500,
                }
            )
            print("[IA] Google Gemini inicializado correctamente ✅")
        except Exception as e:
            print(f"[IA] Error inicializando Gemini: {e}")

    async def generar_respuesta(self, nombre_prompt: str, variables: dict) -> str:
        """
        Genera una respuesta IA usando el prompt especificado.

        Args:
            nombre_prompt: Clave del prompt en PROMPTS dict
            variables: Variables para rellenar el prompt

        Returns:
            Texto de respuesta generado
        """
        prompt_template = PROMPTS.get(nombre_prompt)
        if not prompt_template:
            return f"[Error: Prompt '{nombre_prompt}' no encontrado]"

        try:
            prompt_final = prompt_template.format(**variables)
        except KeyError as e:
            return f"[Error en variables del prompt: {e}]"

        if self.modelo:
            return await self._llamar_gemini(prompt_final)
        else:
            return self._respuesta_fallback(nombre_prompt, variables)

    async def _llamar_gemini(self, prompt: str) -> str:
        """Llama a la API de Google Gemini de forma asíncrona."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.modelo.generate_content(prompt)
            )
            return response.text.strip()
        except Exception as e:
            print(f"[IA] Error en Gemini: {e}")
            return self._respuesta_error()

    def _respuesta_error(self) -> str:
        return "Disculpa, tuve un problema técnico. ¿Podrías repetir tu mensaje? 🙏"

    def _respuesta_fallback(self, nombre_prompt: str, variables: dict) -> str:
        """Respuestas de plantilla cuando Gemini no está disponible."""
        fallbacks = {
            "bienvenida": (
                f"¡Hola {variables.get('nombre_cliente', 'amigo')}! 👋\n"
                f"Bienvenido a {variables.get('nombre_restaurante', 'nuestro restaurante')} 🍽️\n"
                "¿En qué te puedo ayudar hoy?"
            ),
            "clasificador": json.dumps({
                "intencion": "ver_menu",
                "confianza": 0.7,
                "entidad": None,
                "urgencia": "media",
                "sentimiento": "neutral",
                "accion_recomendada": "Mostrar menú"
            }),
            "recomendador": (
                "🌟 Te recomiendo hoy:\n\n"
                "1. 🥩 Lomo Saltado - ¡Nuestro clásico favorito!\n"
                "2. 🐟 Ceviche Clásico - Fresquísimo\n"
                "3. 🍲 Ají de Gallina - El favorito de todos\n\n"
                "¿Te animas con alguno? 😊"
            ),
            "descriptor": (
                f"✨ *{variables.get('nombre_plato', 'Plato')}*\n\n"
                f"{variables.get('descripcion_base', 'Delicioso plato preparado con ingredientes frescos.')}\n\n"
                f"💰 Precio: {variables.get('moneda', 'S/')} {variables.get('precio', '0.00')}\n"
                f"⏱️ Tiempo: ~{variables.get('tiempo_prep', '15')} minutos"
            ),
            "alergias": (
                "Entendemos tus necesidades dietéticas 🌱\n"
                "Nuestro equipo se asegurará de preparar tu pedido de forma segura.\n"
                "¿Me puedes indicar específicamente qué debes evitar?"
            ),
            "confirmacion": (
                f"✅ *Resumen de tu pedido:*\n\n"
                f"{variables.get('items_pedido', '—')}\n\n"
                f"*Total: {variables.get('moneda', 'S/')} {variables.get('total', '0.00')}*\n\n"
                "¿Procedemos con el pago? 💳"
            ),
            "pagos": (
                f"💳 *Proceso de Pago*\n\n"
                f"Total: {variables.get('moneda', 'S/')} {variables.get('total', '0.00')}\n\n"
                f"📱 Yape: {variables.get('numero_yape', 'N/D')}\n"
                f"📱 Plin: {variables.get('numero_plin', 'N/D')}\n\n"
                "Envía la captura cuando hayas pagado ✅"
            ),
            "estado": (
                f"📍 *Estado de tu Pedido #{variables.get('numero_pedido', '')}*\n\n"
                f"Estado: {variables.get('estado', 'Procesando')}\n"
                f"⏱️ Tiempo estimado: {variables.get('tiempo_estimado', '30-40')} minutos\n\n"
                "¡Ya casi está listo! 👨‍🍳"
            ),
            "quejas": (
                "Lamentamos mucho esta situación 😔\n"
                "Entendemos tu molestia y nos hacemos completamente responsables.\n\n"
                "Para solucionar esto AHORA:\n"
                "✅ Te enviamos el plato correcto sin costo adicional\n\n"
                "¿Esto te parece bien? Tu satisfacción es nuestra prioridad 🙏"
            ),
            "fidelizacion": (
                f"🎉 ¡Excelente elección {variables.get('nombre_cliente', '')}!\n\n"
                f"⭐ Puntos actuales: {variables.get('puntos_actuales', 0)}\n\n"
                "¿Te gustaría agregar algo más?\n"
                "🥤 Una bebida complementa perfectamente tu pedido\n\n"
                "¡Gracias por elegirnos! 💙"
            ),
        }
        return fallbacks.get(nombre_prompt, "¿En qué te puedo ayudar? 😊")

    # ── MÉTODOS ESPECÍFICOS POR PROMPT ────────────────────────────────────────

    async def bienvenida(self, cliente: dict, restaurante: dict) -> str:
        from datetime import datetime
        hora = datetime.now().hour
        periodo = "mañana" if hora < 12 else ("tarde" if hora < 19 else "noche")
        return await self.generar_respuesta("bienvenida", {
            "nombre_restaurante": restaurante.get("nombre", "GourmetPOS"),
            "nombre_cliente": cliente.get("nombre", "amigo"),
            "telefono": cliente.get("telefono", ""),
            "total_pedidos": cliente.get("total_pedidos", 0),
            "ultimo_pedido": cliente.get("ultimo_pedido", "ninguno"),
            "platos_favoritos": cliente.get("platos_favoritos", "aún no conocemos tus preferencias"),
            "hora_actual": f"Buenas {periodo}",
            "es_nuevo": "Sí" if cliente.get("total_pedidos", 0) == 0 else "No",
        })

    async def clasificar(self, mensaje: str, estado_flujo: str) -> dict:
        resultado = await self.generar_respuesta("clasificador", {
            "mensaje": mensaje,
            "estado_flujo": estado_flujo,
        })
        try:
            inicio = resultado.find('{')
            fin = resultado.rfind('}') + 1
            if inicio >= 0 and fin > inicio:
                return json.loads(resultado[inicio:fin])
        except Exception:
            pass
        return {"intencion": "otro", "confianza": 0.5, "entidad": None, "urgencia": "baja",
                "sentimiento": "neutral", "accion_recomendada": "Procesar manualmente"}

    async def recomendar(self, cliente: dict, menu: list, restaurante: dict) -> str:
        from datetime import datetime
        mes = datetime.now().month
        temporada = "verano" if mes in [12, 1, 2] else ("otoño" if mes in [3, 4, 5] else "invierno" if mes in [6, 7, 8] else "primavera")
        menu_simple = [f"{p.get('emoji','')} {p.get('nombre','')} - {p.get('precio',0)}" for p in menu[:20]]
        return await self.generar_respuesta("recomendador", {
            "nombre_restaurante": restaurante.get("nombre", "GourmetPOS"),
            "historial_pedidos": cliente.get("historial", "Sin historial previo"),
            "hora_actual": datetime.now().strftime("%H:%M"),
            "temporada": temporada,
            "menu_disponible": "\n".join(menu_simple),
        })

    async def describir_plato(self, producto: dict, config: dict) -> str:
        return await self.generar_respuesta("descriptor", {
            "nombre_plato": producto.get("nombre", ""),
            "descripcion_base": producto.get("descripcion", ""),
            "precio": producto.get("precio", 0),
            "moneda": config.get("moneda", "S/"),
            "tiempo_prep": producto.get("tiempo_prep", 15),
        })

    async def manejar_alergia(self, mensaje: str, menu: list, restaurante: dict) -> str:
        menu_ingredientes = [f"- {p.get('nombre')}: {p.get('descripcion','')}" for p in menu[:20]]
        return await self.generar_respuesta("alergias", {
            "nombre_restaurante": restaurante.get("nombre", "GourmetPOS"),
            "mensaje_cliente": mensaje,
            "menu_con_ingredientes": "\n".join(menu_ingredientes),
        })

    async def confirmar_pedido(self, carrito: list, config: dict) -> str:
        igv_rate = float(config.get("igv", 0.18))
        subtotal = sum(i.get("subtotal", 0) for i in carrito)
        igv = round(subtotal * igv_rate, 2)
        total = round(subtotal + igv, 2)
        moneda = config.get("moneda", "S/")
        items_text = "\n".join([
            f"  {i.get('emoji','🍽️')} {i.get('nombre','')} x{i.get('cantidad',1)} = {moneda} {i.get('subtotal',0):.2f}"
            for i in carrito
        ])
        return await self.generar_respuesta("confirmacion", {
            "nombre_restaurante": config.get("nombre", "GourmetPOS"),
            "items_pedido": items_text,
            "subtotal": f"{subtotal:.2f}",
            "igv": f"{igv:.2f}",
            "total": f"{total:.2f}",
            "moneda": moneda,
        })

    async def guiar_pago(self, metodo: str, total: float, mensaje: str, config: dict) -> str:
        return await self.generar_respuesta("pagos", {
            "nombre_restaurante": config.get("nombre", "GourmetPOS"),
            "total": f"{total:.2f}",
            "metodo_pago": metodo,
            "numero_yape": config.get("yape", "N/D"),
            "numero_plin": config.get("plin", "N/D"),
            "mensaje_cliente": mensaje,
            "moneda": config.get("moneda", "S/"),
        })

    async def estado_pedido(self, pedido: dict) -> str:
        from datetime import datetime
        minutos = int((datetime.utcnow() - pedido.get("created_at", datetime.utcnow())).total_seconds() / 60) if "created_at" in pedido else 0
        items_text = ", ".join([f"{i.get('nombre','')} x{i.get('cantidad',1)}" for i in pedido.get("detalles", [])])
        return await self.generar_respuesta("estado", {
            "nombre_restaurante": pedido.get("restaurante", "GourmetPOS"),
            "numero_pedido": pedido.get("numero_ticket", pedido.get("id", "?")),
            "estado": pedido.get("estado", "pendiente"),
            "items": items_text,
            "minutos_transcurridos": minutos,
            "tiempo_estimado": pedido.get("tiempo_estimado", 30),
            "canal": pedido.get("canal", "whatsapp"),
        })

    async def manejar_queja(self, queja: str, cliente: dict, pedido: dict, config: dict) -> str:
        return await self.generar_respuesta("quejas", {
            "nombre_restaurante": config.get("nombre", "GourmetPOS"),
            "queja": queja,
            "total_pedidos": cliente.get("total_pedidos", 0),
            "datos_pedido": json.dumps(pedido, ensure_ascii=False, default=str),
        })

    async def fidelizar(self, cliente: dict, carrito: list, config: dict) -> str:
        moneda = config.get("moneda", "S/")
        total = sum(i.get("subtotal", 0) for i in carrito)
        puntos = cliente.get("puntos_fidelidad", 0)
        puntos_recompensa = 100
        porcentaje = min(100, int((puntos / puntos_recompensa) * 100))
        complementos = "una bebida refrescante o un postre dulce"
        return await self.generar_respuesta("fidelizacion", {
            "nombre_restaurante": config.get("nombre", "GourmetPOS"),
            "nombre_cliente": cliente.get("nombre", "amigo"),
            "puntos_actuales": puntos,
            "puntos_para_recompensa": max(0, puntos_recompensa - puntos),
            "pedido_actual": ", ".join([i.get("nombre", "") for i in carrito]),
            "total_pedido": f"{total:.2f}",
            "total_pedidos": cliente.get("total_pedidos", 0),
            "complementos_sugeridos": complementos,
            "promociones": "Sin promociones activas",
            "porcentaje_recompensa": porcentaje,
            "moneda": moneda,
        })
