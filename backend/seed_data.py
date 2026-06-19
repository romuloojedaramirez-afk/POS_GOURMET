"""Datos iniciales para la base de datos."""
from .models import Categoria, Producto, Mesa, ConfigRestaurante


CONFIG_INICIAL = [
    ("nombre", "El Buen Sabor", "Nombre del restaurante"),
    ("ruc", "20512345678", "RUC o NIT"),
    ("direccion", "Av. España 123, Trujillo", "Dirección"),
    ("telefono", "+51 044 123456", "Teléfono"),
    ("moneda", "S/", "Símbolo de moneda"),
    ("igv", "0.18", "Porcentaje IGV"),
    ("yape", "944 123 456", "Número Yape"),
    ("plin", "944 123 456", "Número Plin"),
    ("whatsapp", "51944123456", "Número WhatsApp bot"),
    ("logo_url", "", "URL del logo"),
    ("color_primario", "#FF6B35", "Color primario"),
    ("mensaje_bienvenida", "¡Bienvenido a El Buen Sabor! 🍽️ ¿En qué te puedo ayudar?", "Mensaje bienvenida WA"),
    ("gemini_api_key", "", "API Key de Google Gemini"),
    ("whatsapp_token", "", "Token Meta WhatsApp Cloud API"),
    ("whatsapp_phone_id", "", "Phone ID Meta WhatsApp"),
]

CATEGORIAS_INICIALES = [
    ("🥗 Entradas", "🥗", "#00D4A1", 1),
    ("🍽️ Platos de Fondo", "🍽️", "#FF6B35", 2),
    ("🍕 Menús Ejecutivos", "🍕", "#FFB800", 3),
    ("🍰 Postres", "🍰", "#FF4081", 4),
    ("🥤 Bebidas", "🥤", "#4FC3F7", 5),
]

PRODUCTOS_INICIALES = {
    "🥗 Entradas": [
        ("Ceviche Clásico", "Pescado fresco marinado en limón con ají, cebolla y cilantro", 22.0, "🐟", True),
        ("Causa Rellena", "Causa de papa amarilla con atún y mayonesa", 16.0, "🥔", False),
        ("Tequeños de Queso", "Bastones de masa con queso derretido, 6 unidades", 14.0, "🧀", False),
        ("Anticuchos de Corazón", "Brochetas de corazón de res marinado, 3 unidades", 18.0, "🍢", False),
    ],
    "🍽️ Platos de Fondo": [
        ("Lomo Saltado", "Lomo de res salteado con tomate, cebolla y papas fritas", 28.0, "🥩", True),
        ("Ají de Gallina", "Pollo desmenuzado en salsa de ají amarillo con arroz", 22.0, "🍲", True),
        ("Arroz con Leche", "Arroz cremoso con pollo a la brasa y verduras", 20.0, "🍗", False),
        ("Pollo a la Brasa", "Pollo entero a la brasa con papas fritas y ensalada", 45.0, "🍗", True),
        ("Seco de Cordero", "Guiso de cordero con cilantro, pallares y arroz", 26.0, "🍖", False),
        ("Arroz con Mariscos", "Arroz cremoso con mix de mariscos frescos", 32.0, "🦐", True),
        ("Tallarin Verde con Pollo", "Tallarines en salsa de albahaca con pollo frito", 19.0, "🍝", False),
    ],
    "🍕 Menús Ejecutivos": [
        ("Menú Ejecutivo A", "Sopa + Plato de fondo + Refresco", 18.0, "🍱", True),
        ("Menú Ejecutivo B", "Entrada + Plato de fondo + Postre + Bebida", 25.0, "🍱", True),
        ("Menú Familiar", "4 platos de fondo a elección + 4 bebidas", 80.0, "🍱", False),
    ],
    "🍰 Postres": [
        ("Suspiro Limeño", "Postre tradicional de manjar con merengue italiano", 10.0, "🍮", True),
        ("Tres Leches", "Bizcocho húmedo bañado en tres tipos de leche", 12.0, "🎂", False),
        ("Mousse de Maracuyá", "Mousse cremoso de maracuyá fresco", 10.0, "🍊", False),
        ("Picarones", "Buñuelos de zapallo con miel de chancaca, 4 unidades", 8.0, "🍩", True),
    ],
    "🥤 Bebidas": [
        ("Inca Kola", "Bebida gaseosa peruana 500ml", 5.0, "🥤", True),
        ("Coca Cola", "Bebida gaseosa 500ml", 5.0, "🥤", True),
        ("Chicha Morada", "Bebida natural de maíz morado con frutas", 7.0, "🍇", True),
        ("Limonada", "Limonada natural con hierba buena", 7.0, "🍋", False),
        ("Agua Mineral", "Agua San Mateo 625ml", 4.0, "💧", True),
        ("Maracuyá Frozen", "Refresco helado de maracuyá", 8.0, "🧃", False),
    ],
}


def seed_database(db):
    """Puebla la base de datos con datos iniciales si está vacía."""

    # Config
    if db.query(ConfigRestaurante).count() == 0:
        for clave, valor, desc in CONFIG_INICIAL:
            db.add(ConfigRestaurante(clave=clave, valor=valor, descripcion=desc))

    # Categorías y productos
    if db.query(Categoria).count() == 0:
        cat_map = {}
        for nombre, emoji, color, orden in CATEGORIAS_INICIALES:
            cat = Categoria(nombre=nombre, emoji=emoji, color=color, orden=orden)
            db.add(cat)
            db.flush()
            cat_map[nombre] = cat.id

        for cat_nombre, productos in PRODUCTOS_INICIALES.items():
            cat_id = cat_map.get(cat_nombre)
            if not cat_id:
                continue
            for nombre, desc, precio, emoji, destacado in productos:
                db.add(Producto(
                    categoria_id=cat_id,
                    nombre=nombre,
                    descripcion=desc,
                    precio=precio,
                    emoji=emoji,
                    destacado=destacado,
                ))

    # Mesas
    if db.query(Mesa).count() == 0:
        for num in range(1, 17):
            db.add(Mesa(numero=num, capacidad=4))

    db.commit()
