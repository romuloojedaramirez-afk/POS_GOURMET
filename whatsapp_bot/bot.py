"""
GourmetPOS - Bot WhatsApp Principal
Integra el Pipeline Johnson con los 10 Prompts IA
"""
import asyncio
import httpx
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .pipeline import PipelineJohnson

# Configuración del bot
WA_TOKEN    = os.getenv("WA_TOKEN", "")
WA_PHONE_ID = os.getenv("WA_PHONE_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GEMINI_KEY  = os.getenv("GEMINI_API_KEY", "")

pipeline = PipelineJohnson(api_key=GEMINI_KEY)


async def enviar_a_backend(telefono: str, mensaje: str, nombre: str = "Cliente"):
    """Envía un mensaje simulado al backend para procesamiento."""
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{BACKEND_URL}/api/whatsapp/simular",
                json={"telefono": telefono, "mensaje": mensaje, "nombre": nombre},
                timeout=15,
            )
            return r.json()
        except Exception as e:
            print(f"[BOT] Error enviando al backend: {e}")
            return {"error": str(e)}


async def demo_interactivo():
    """
    Demo interactivo del bot en la consola.
    Simula una conversación completa con el pipeline IA.
    """
    print("\n" + "="*60)
    print("  GourmetPOS WhatsApp Bot - Demo Interactivo")
    print("  Pipeline Johnson + 10 Prompts IA")
    print("="*60)

    if not GEMINI_KEY:
        print("\n⚠️  GEMINI_API_KEY no configurada. Usando respuestas de plantilla.")
        print("   Para activar IA: configura GEMINI_API_KEY en .env\n")
    else:
        print(f"\n✅ Gemini IA activo")

    print("\nEste demo simula mensajes de WhatsApp al backend.")
    print("Asegúrate de que el backend esté corriendo en http://localhost:8000\n")

    # Datos de demo
    restaurante = {"nombre": "El Buen Sabor", "moneda": "S/", "igv": "0.18",
                   "yape": "944 123 456", "plin": "944 456 789"}
    cliente = {"nombre": "Carlos García", "telefono": "+51987654321",
               "total_pedidos": 5, "ultimo_pedido": "Lomo Saltado",
               "platos_favoritos": "Lomo Saltado, Ceviche", "historial": "Lomo Saltado x3, Ceviche x2", "puntos_fidelidad": 45}

    print("─"*60)
    print("DEMO 1: Bienvenida Inteligente (Prompt 1)")
    print("─"*60)
    resp = await pipeline.bienvenida(cliente, restaurante)
    print(f"Bot: {resp}\n")

    print("─"*60)
    print("DEMO 2: Clasificador de Intención (Prompt 2)")
    print("─"*60)
    mensajes_test = ["quiero pedir un lomo saltado", "cuánto cuesta el ceviche", "ya pagué con yape"]
    for msg in mensajes_test:
        resultado = await pipeline.clasificar(msg, "menu_categorias")
        print(f"Mensaje: '{msg}'")
        print(f"  → Intención: {resultado.get('intencion')} | Entidad: {resultado.get('entidad')} | Confianza: {resultado.get('confianza')}")
    print()

    print("─"*60)
    print("DEMO 3: Recomendador Personal (Prompt 3)")
    print("─"*60)
    menu_demo = [
        {"nombre": "Lomo Saltado", "precio": 28, "emoji": "🥩"},
        {"nombre": "Ceviche Clásico", "precio": 22, "emoji": "🐟"},
        {"nombre": "Ají de Gallina", "precio": 22, "emoji": "🍲"},
        {"nombre": "Pollo a la Brasa", "precio": 45, "emoji": "🍗"},
    ]
    resp = await pipeline.recomendar(cliente, menu_demo, restaurante)
    print(f"Bot: {resp}\n")

    print("─"*60)
    print("DEMO 4: Descriptor de Plato (Prompt 4)")
    print("─"*60)
    producto_demo = {"nombre": "Lomo Saltado", "descripcion": "Lomo de res con papas fritas, tomate y cebolla", "precio": 28, "emoji": "🥩", "tiempo_prep": 15}
    resp = await pipeline.describir_plato(producto_demo, restaurante)
    print(f"Bot: {resp}\n")

    print("─"*60)
    print("DEMO 5: Confirmación de Pedido (Prompt 6)")
    print("─"*60)
    carrito_demo = [
        {"nombre": "Lomo Saltado", "emoji": "🥩", "cantidad": 2, "precio": 28, "subtotal": 56},
        {"nombre": "Inca Kola", "emoji": "🥤", "cantidad": 1, "precio": 5, "subtotal": 5},
    ]
    resp = await pipeline.confirmar_pedido(carrito_demo, restaurante)
    print(f"Bot: {resp}\n")

    print("─"*60)
    print("DEMO 6: Fidelización (Prompt 10)")
    print("─"*60)
    resp = await pipeline.fidelizar(cliente, carrito_demo, restaurante)
    print(f"Bot: {resp}\n")

    print("="*60)
    print("Demo completado. El bot está listo para uso en producción.")
    print("="*60)


async def test_backend_connection():
    """Verifica que el backend esté disponible."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{BACKEND_URL}/api/health", timeout=5)
            data = r.json()
            print(f"✅ Backend conectado: {data.get('app')} v{data.get('version')}")
            return True
    except Exception as e:
        print(f"❌ Backend no disponible en {BACKEND_URL}: {e}")
        return False


async def flujo_demo_whatsapp():
    """Simula un flujo completo de cliente por WhatsApp vía el backend."""
    print("\n🚀 Simulando flujo completo de WhatsApp...\n")

    pasos = [
        ("+51912345678", "hola", "María López"),
        ("+51912345678", "ver_menu", "María López"),
        ("+51912345678", "cat_2", "María López"),
        ("+51912345678", "prod_1", "María López"),
        ("+51912345678", "qty_2_1", "María López"),
        ("+51912345678", "no_bebida", "María López"),
        ("+51912345678", "pagar_ahora", "María López"),
        ("+51912345678", "pago_yape", "María López"),
    ]

    for tel, msg, nombre in pasos:
        print(f"📱 [{nombre}] → '{msg}'")
        resultado = await enviar_a_backend(tel, msg, nombre)
        print(f"   → Backend: {resultado}\n")
        await asyncio.sleep(0.5)

    print("✅ Flujo simulado completado. Revisa la pantalla de cocina.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GourmetPOS WhatsApp Bot")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demo de prompts IA")
    parser.add_argument("--flujo", action="store_true", help="Simular flujo completo WhatsApp")
    parser.add_argument("--test", action="store_true", help="Verificar conexión al backend")
    args = parser.parse_args()

    if args.demo:
        asyncio.run(demo_interactivo())
    elif args.flujo:
        asyncio.run(flujo_demo_whatsapp())
    elif args.test:
        asyncio.run(test_backend_connection())
    else:
        print("Uso: python -m whatsapp_bot.bot --demo | --flujo | --test")
        print("\nEl bot se activa automáticamente cuando el backend recibe mensajes WhatsApp.")
        print("Configura el webhook en Meta Business Manager con la URL:")
        print(f"  {os.getenv('BACKEND_URL', 'https://tu-dominio.com')}/api/whatsapp/webhook")
