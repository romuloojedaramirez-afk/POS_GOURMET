"""
Biblioteca completa de Gastronomía Peruana — todas las regiones.
Datos iniciales para GourmetPOS.
"""
from .models import Categoria, Producto, Mesa, ConfigRestaurante


CONFIG_INICIAL = [
    ("nombre",            "GourmetPOS Restaurante",  "Nombre del restaurante"),
    ("ruc",               "20512345678",              "RUC"),
    ("direccion",         "Av. Larco 123, Miraflores, Lima", "Dirección"),
    ("telefono",          "+51 01 123 4567",          "Teléfono"),
    ("moneda",            "S/",                       "Símbolo moneda"),
    ("igv",               "0.18",                     "IGV 18%"),
    ("yape",              "944 123 456",              "Número Yape"),
    ("plin",              "944 123 456",              "Número Plin"),
    ("whatsapp",          "51944123456",              "WhatsApp bot"),
    ("logo_url",          "",                         "URL del logo"),
    ("imagen_menu_url",   "",                         "URL imagen menú del día"),
    ("color_primario",    "#FF6B35",                  "Color primario"),
    ("lat",               "-12.1211",                 "Latitud restaurante"),
    ("lon",               "-77.0297",                 "Longitud restaurante"),
    ("mensaje_bienvenida","¡Bienvenido! 🍽️ Somos GourmetPOS. ¿En qué te puedo ayudar?", "Mensaje bienvenida"),
    ("gemini_api_key",    "",                         "Google Gemini API Key"),
    ("whatsapp_token",    "",                         "Meta WhatsApp Cloud API Token"),
    ("whatsapp_phone_id", "",                         "Meta WhatsApp Phone ID"),
    ("whatsapp_verify_token","gormetpos2024",         "Meta Verify Token"),
]

# ══════════════════════════════════════════════════════════════════════════════
#   CATEGORÍAS — Organizadas por tipo de plato y región
# ══════════════════════════════════════════════════════════════════════════════
CATEGORIAS = [
    # (nombre,                        emoji, color,    orden)
    ("🥗 Entradas & Piqueos",         "🥗",  "#00D4A1",  1),
    ("🍲 Sopas & Caldos",             "🍲",  "#FFB800",  2),
    ("🐟 Cevichería & Mariscos",      "🐟",  "#4FC3F7",  3),
    ("🍽️ Criollo — Lima & Costa",     "🍽️",  "#FF6B35",  4),
    ("🏔️ Andino — Sierra & Andes",   "🏔️",  "#7C6FFF",  5),
    ("🌿 Amazónico — Selva",          "🌿",  "#25D366",  6),
    ("🌶️ Regional — Ciudades",        "🌶️",  "#FF4D6A",  7),
    ("🍗 Pollos & Parrillas",         "🍗",  "#FF8C00",  8),
    ("🍱 Menús Ejecutivos",           "🍱",  "#9C27B0",  9),
    ("🍰 Postres Peruanos",           "🍰",  "#E91E63", 10),
    ("🥤 Bebidas & Refrescos",        "🥤",  "#03A9F4", 11),
]

# ══════════════════════════════════════════════════════════════════════════════
#   PRODUCTOS — Biblioteca completa por categoría
#   (nombre, descripción, precio, emoji, destacado, tiempo_prep)
# ══════════════════════════════════════════════════════════════════════════════
PRODUCTOS = {

    # ─────────────────────────────────────────────────────────────────────────
    "🥗 Entradas & Piqueos": [
        ("Causa Limeña",           "Papa amarilla sazonada rellena de atún, pollo o mariscos", 16.0, "🥔", True,  15),
        ("Papa a la Huancaína",    "Papa sancochada con salsa de ají amarillo y queso fresco",  14.0, "🥔", True,  10),
        ("Ocopa Arequipeña",       "Papa con salsa de ají mirasol, maní y queso fresco",       14.0, "🌿", False, 10),
        ("Anticuchos de Corazón",  "Brochetas de corazón de res marinado en ají panca, x4",   20.0, "🍢", True,  15),
        ("Tequeños de Queso",      "Bastones de masa rellenos de queso crema, x6",             14.0, "🧀", False, 12),
        ("Choclo con Queso",       "Choclo tierno hervido con queso fresco de Cajamarca",      10.0, "🌽", False,  8),
        ("Solterito de Queso",     "Ensalada arequipeña de habas, choclo, queso y olivas",     14.0, "🥗", False, 10),
        ("Tamales Criollos",       "Masa de maíz con pollo o cerdo, envueltos en hoja, x2",   16.0, "🌯", True,  20),
        ("Humitas",                "Masa de choclo con queso, envuelta en hoja de choclo, x2", 14.0, "🌽", False, 15),
        ("Picarones Mini",         "Pequeños buñuelos de zapallo y camote con miel, x6",       10.0, "🍩", False, 15),
        ("Ensalada de Palta",      "Palta cremosa con tomate, cebolla y limón",                12.0, "🥑", True,   8),
        ("Croquetas de Quinua",    "Croquetas crujientes de quinua con hierbas andinas",       12.0, "🟡", False, 15),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🍲 Sopas & Caldos": [
        ("Sopa a la Minuta",       "Caldo de res con fideos, huevo y verduras, estilo limeño", 16.0, "🍜", True,  20),
        ("Aguadito de Pollo",      "Arroz caldoso con pollo, culantro, ají y verduras",        18.0, "🍲", True,  25),
        ("Sopa de Quinua",         "Caldo andino con quinua, papa y hierbas de la sierra",     14.0, "🌾", False, 20),
        ("Caldo de Gallina",       "Caldo de gallina criolla con fideos, huevo y papa",        20.0, "🐔", True,  30),
        ("Parihuela",              "Sopa de mariscos con ají panca, congrio y mariscos",       28.0, "🦞", True,  25),
        ("Chupe de Camarones",     "Sopa cremosa de camarones con leche y ají amarillo",       32.0, "🦐", True,  30),
        ("Inchicapi Amazónico",    "Sopa de gallina con maíz molido y maní, estilo selva",    18.0, "🌿", False, 30),
        ("Caldo de Cabeza",        "Caldo de res especiado con maíz y garbanzos",             16.0, "🍖", False, 35),
        ("Sopa de Maní",           "Sopa cusqueña con maní, fideos y papas nativas",          16.0, "🥜", False, 25),
        ("Locro de Zapallo",       "Guiso andino de zapallo con queso y ají",                 14.0, "🎃", False, 20),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🐟 Cevichería & Mariscos": [
        ("Ceviche Clásico",        "Pescado fresco en leche de tigre con ají limo, cebolla",  26.0, "🐟", True,  15),
        ("Ceviche Mixto",          "Pescado, camarones y pulpo en leche de tigre",            32.0, "🦐", True,  15),
        ("Leche de Tigre",         "Shot del caldo del ceviche con chicharrón de calamar",    14.0, "🐯", True,   8),
        ("Tiradito de Lenguado",   "Corte fino de lenguado con salsa de ají amarillo",        28.0, "🐡", True,  12),
        ("Choritos a la Chalaca",  "Mejillones con sarsa criolla y limón",                    22.0, "🦪", True,  10),
        ("Jalea Mixta",            "Fritura de mariscos y pescado con sarsa y yuca",          32.0, "🦑", True,  20),
        ("Arroz con Mariscos",     "Arroz cremoso con mix de mariscos frescos",               30.0, "🦐", True,  25),
        ("Chaufa de Mariscos",     "Arroz chino saltado con mariscos y kion",                 28.0, "🦐", False, 20),
        ("Pulpo al Olivo",         "Pulpo cocido con salsa de olivo negro",                   36.0, "🐙", True,  15),
        ("Conchas Negras",         "Conchas negras de Tumbes en su salsa, x6",               28.0, "🐚", True,  10),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🍽️ Criollo — Lima & Costa": [
        ("Lomo Saltado",           "Lomo fino de res salteado con tomate, cebolla y papas",  30.0, "🥩", True,  20),
        ("Ají de Gallina",         "Pollo desmenuzado en salsa de ají amarillo con nueces",  24.0, "🍲", True,  20),
        ("Carapulcra",             "Guiso de papa seca con cerdo y maní, receta ancestral",  22.0, "🍖", False, 35),
        ("Seco de Res",            "Guiso de res con cilantro, chicha de jora y pallares",   24.0, "🍖", True,  30),
        ("Tallarín Verde con Lomo","Pasta en salsa de albahaca y queso con lomo saltado",    28.0, "🍝", True,  20),
        ("Arroz con Leche",        "Arroz cremoso al estilo criollo con canela y clavo",     10.0, "🍚", False, 20),
        ("Tacu Tacu con Bistec",   "Torta de frijoles y arroz con bistec apanado",           28.0, "🥩", True,  25),
        ("Chicharrón de Cerdo",    "Cerdo frito crujiente con camote y sarsa criolla",       26.0, "🐷", True,  20),
        ("Pepián de Pato",         "Guiso norteño de pato con maíz molido y ají especias",  28.0, "🦆", False, 35),
        ("Sopa Seca con Carapulcra","Combo limeño: fideos secos + carapulcra",               26.0, "🍝", True,  30),
        ("Bistec a lo Pobre",      "Bistec con arroz, frijoles, huevo frito y plátano",     26.0, "🥩", True,  20),
        ("Enrollado de Pollo",     "Rollo de pollo relleno con aceitunas y huevo",           22.0, "🌯", False, 25),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🏔️ Andino — Sierra & Andes": [
        ("Pachamanca",             "Carnes y tubérculos cocidos bajo tierra con piedras calientes", 45.0, "🪨", True,  90),
        ("Cuy al Horno",           "Cuy entero horneado con hierbas andinas y papas nativas", 42.0, "🐹", True,  45),
        ("Rocoto Relleno",         "Rocoto arequipeño relleno de carne molida y queso",      26.0, "🌶️", True,  35),
        ("Olluquito con Charqui",  "Guiso andino de ollucos con carne seca de llama",        22.0, "🥕", True,  25),
        ("Adobo Arequipeño",       "Cerdo marinado en chicha con ají especias, horneado",    26.0, "🍖", True,  40),
        ("Sancochado Serrano",     "Hervido de res, papa, choclo y verduras andinas",        22.0, "🍲", False, 35),
        ("Kapchi de Setas",        "Guiso cusqueño de hongos con habas y queso",             18.0, "🍄", False, 25),
        ("Trucha a la Plancha",    "Trucha del lago Titicaca a la plancha con papas",        28.0, "🐟", True,  20),
        ("Timpo Puneño",           "Caldo de chuño con charqui y verduras de Puno",         20.0, "🍲", False, 30),
        ("Chicharrón de Chancho",  "Cerdo frito serrano con mote y sarsa andina",           24.0, "🐷", True,  25),
        ("Estofado de Alpaca",     "Guiso tierno de alpaca con verduras y especias andinas", 30.0, "🦙", False, 40),
        ("Papa Rellena Serrana",   "Papa rellena de carne molida con pasas y aceituna",     18.0, "🥔", True,  20),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🌿 Amazónico — Selva": [
        ("Juane de Arroz",         "Masa de arroz con pollo y aceitunas en hoja de bijao",  20.0, "🌿", True,  35),
        ("Tacacho con Cecina",     "Bolas de plátano verde machacado con tocino ahumado",   22.0, "🍌", True,  20),
        ("Inchicapi de Gallina",   "Sopa amazónica de gallina con maíz y maní",             20.0, "🐔", True,  30),
        ("Patarashca de Dorado",   "Pescado amazónico cocido en hoja con ajíes de la selva",26.0, "🐟", True,  25),
        ("Cecina Frita",           "Carne de cerdo ahumada y salada frita, estilo selva",   20.0, "🥓", True,  15),
        ("Chaufa Amazónico",       "Arroz chino con cecina, tacacho y ajíes amazónicos",   24.0, "🍚", False, 20),
        ("Timbuche",               "Caldo de pescado amazónico con plátano y yuca",         16.0, "🐟", False, 25),
        ("Ninajuane",              "Juane de maíz con pollo en hoja de maíz tostada",       18.0, "🌽", False, 30),
        ("Aguajina",               "Helado cremoso de aguaje, fruta típica amazónica",       8.0, "🌴", False, 10),
        ("Ensalada de Chonta",     "Ensalada refrescante de corazón de palmito",            14.0, "🌿", False, 10),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🌶️ Regional — Ciudades": [
        # Arequipa
        ("Chupe de Camarones Aqp", "Sopa espesa de camarones del río Chili con leche",     34.0, "🦐", True,  35),
        ("Adobo Arequipeño Trad.", "Cerdo en adobo de chicha, ají especial de Arequipa",   28.0, "🍖", True,  40),
        # Cusco
        ("Chiriuchu Cusqueño",     "Plato bandera: cuy, cecina, maíz, queso, rocoto",      36.0, "🌶️", True,  20),
        ("Kapchi de Habas",        "Guiso cusqueño de habas con leche y queso",             18.0, "🫘", False, 20),
        # Trujillo / Norte
        ("Shambar Trujillano",     "Caldo norteño de trigo con menestras y cerdo",         20.0, "🌾", True,  35),
        ("Arroz con Pato Norteño", "Arroz verde con pato marinado en chicha y culantro",   30.0, "🦆", True,  35),
        ("Seco de Cabrito Norteño","Cabrito tierno en caldo de chicha, estilo Trujillo",   30.0, "🐐", True,  40),
        # Piura / Tumbes
        ("Seco de Chabelo",        "Plato piurano: cecina, plátano, pallares y ají",       26.0, "🍖", False, 30),
        ("Majado de Yuca",         "Yuca machacada con cebolla, ají y chicharrón",         16.0, "🥔", False, 15),
        # Cajamarca
        ("Caldo Verde Cajamarquino","Caldo de papa con queso y menta, estilo Cajamarca",  16.0, "🍲", False, 20),
        ("Cuy con Papas Cajamarca","Cuy dorado en manteca con papas sancochadas",         38.0, "🐹", True,  40),
        # Ica
        ("Tejas de Ica",           "Dulce de pecanas cubiertas de fondant, x4",           10.0, "🍬", False, 10),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🍗 Pollos & Parrillas": [
        ("Pollo a la Brasa Entero","Pollo entero a la brasa con papas fritas y ensalada",  48.0, "🍗", True,  45),
        ("Pollo a la Brasa Medio", "Medio pollo a la brasa con papas fritas y ensalada",  26.0, "🍗", True,  40),
        ("Pollo a la Brasa Cuarto","Cuarto de pollo a la brasa con papas y ensalada",     16.0, "🍗", True,  35),
        ("Parrilla Mixta Personal","Res, pollo y chorizo con papas y chimichurri",        38.0, "🥩", True,  30),
        ("Parrilla Mixta Familiar","Parrilla completa para 4 personas",                  120.0, "🍖", True,  45),
        ("Alitas BBQ",             "Alitas de pollo en salsa BBQ ahumada, x8",            22.0, "🍗", True,  25),
        ("Costillas de Res",       "Costillas de res a la parrilla con salsa criolla",    36.0, "🥩", False, 40),
        ("Brocheta de Pollo",      "Pollo marinado en ají amarillo a las brasas",         18.0, "🍢", True,  20),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🍱 Menús Ejecutivos": [
        ("Menú del Día A",         "Sopa + Plato de fondo a elección + Refresco",          18.0, "🍱", True,  25),
        ("Menú del Día B",         "Entrada + Plato de fondo + Postre + Bebida",           25.0, "🍱", True,  30),
        ("Menú Ejecutivo Premium", "Ceviche + Plato + Postre + 2 bebidas",                35.0, "🍱", True,  30),
        ("Menú Familiar x4",       "4 platos a elección + 4 bebidas + postre compartido", 85.0, "🍱", False, 35),
        ("Menú Almuerzo Criollo",  "Causa + Lomo Saltado o Ají de Gallina + Chicha",      28.0, "🍱", True,  25),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🍰 Postres Peruanos": [
        ("Suspiro Limeño",         "Manjar blanco con merengue italiano, receta tradicional", 10.0, "🍮", True,  15),
        ("Arroz con Leche",        "Arroz cremoso con leche condensada, canela y clavo",  10.0, "🍚", True,  25),
        ("Mazamorra Morada",       "Postre de maíz morado con frutas y canela",            9.0, "🍇", True,  25),
        ("Picarones",              "Buñuelos de zapallo con miel de chancaca, x4",        10.0, "🍩", True,  20),
        ("Tres Leches",            "Bizcocho bañado en tres leches con nata",             13.0, "🎂", False, 20),
        ("Mousse de Maracuyá",     "Mousse cremoso de maracuyá fresco con merengue",      12.0, "🍊", False, 15),
        ("Crema Volteada",         "Flan peruano de caramelo y leche",                    11.0, "🍮", True,  20),
        ("Helado de Lúcuma",       "Helado artesanal del fruto peruano lúcuma",           10.0, "🍦", True,   5),
        ("Helado de Aguaje",       "Helado amazónico de aguaje y coco",                    9.0, "🌴", False,  5),
        ("Tejas de Pecana",        "Dulces de pecana con fondant de lúcuma, x4",          12.0, "🍬", False,  5),
        ("Ranfañote",              "Postre criollo de pan, chancaca, coco y pasas",         9.0, "🍮", False, 10),
        ("Buñuelos de Viento",     "Buñuelos ligeros con miel de panela y canela",        10.0, "🍩", False, 15),
    ],

    # ─────────────────────────────────────────────────────────────────────────
    "🥤 Bebidas & Refrescos": [
        # Gaseosas
        ("Inca Kola 500ml",        "La bebida peruana de sabor único",                     5.0, "🟡", True,   2),
        ("Coca Cola 500ml",        "Bebida gaseosa refrescante",                           5.0, "🔴", True,   2),
        ("Sprite 500ml",           "Gaseosa de limón refrescante",                         5.0, "🟢", False,  2),
        # Bebidas tradicionales peruanas
        ("Chicha Morada",          "Bebida de maíz morado con manzana, membrillo y canela", 7.0, "🍇", True,   5),
        ("Chicha de Jora",         "Bebida fermentada tradicional de maíz",                 7.0, "🌽", False,  5),
        ("Emoliente",              "Infusión de cebada, linaza y hierbas medicinales",      6.0, "🌿", False,  5),
        ("Masato",                 "Bebida amazónica de yuca fermentada",                   6.0, "🌿", False,  5),
        ("Chapo",                  "Bebida de plátano maduro cocido, estilo selva",         6.0, "🍌", False,  5),
        # Jugos y refrescos
        ("Limonada Peruana",       "Limonada cremosa con leche evaporada y hierbabuena",   8.0, "🍋", True,   5),
        ("Maracuyá Frozen",        "Refresco helado de maracuyá natural",                   8.0, "🧃", True,   5),
        ("Jugo de Lúcuma",         "Jugo natural del fruto andino lúcuma con leche",        9.0, "🥛", False,  5),
        ("Agua de Coco",           "Agua de coco natural amazónico",                        7.0, "🥥", False,  2),
        # Aguas
        ("Agua Mineral 625ml",     "San Mateo sin gas",                                    4.0, "💧", True,   2),
        ("Agua con Gas 625ml",     "San Mateo con gas",                                    4.0, "💧", False,  2),
        # Cocteles sin alcohol
        ("Sour de Maracuyá",       "Coctel sin alcohol de maracuyá con limón y espuma",   10.0, "🍹", True,  10),
        ("Chilcano Mocktail",      "Ginger ale con limón y bitters, sin alcohol",           9.0, "🍹", False,  5),
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
#   FUNCIÓN PRINCIPAL DE SEED
# ══════════════════════════════════════════════════════════════════════════════

def seed_database(db):
    """Puebla la BD con la biblioteca completa de gastronomía peruana."""

    # ── Config
    if db.query(ConfigRestaurante).count() == 0:
        for clave, valor, desc in CONFIG_INICIAL:
            db.add(ConfigRestaurante(clave=clave, valor=valor, descripcion=desc))
        db.flush()

    # ── Categorías y Productos
    if db.query(Categoria).count() == 0:
        cat_map = {}
        for nombre, emoji, color, orden in CATEGORIAS:
            cat = Categoria(nombre=nombre, emoji=emoji, color=color, orden=orden, activo=True)
            db.add(cat)
            db.flush()
            cat_map[nombre] = cat.id

        for cat_nombre, productos in PRODUCTOS.items():
            cat_id = cat_map.get(cat_nombre)
            if not cat_id:
                continue
            for idx, prod_data in enumerate(productos):
                nombre, desc, precio, emoji, destacado, tiempo = prod_data
                db.add(Producto(
                    categoria_id = cat_id,
                    nombre       = nombre,
                    descripcion  = desc,
                    precio       = precio,
                    emoji        = emoji,
                    destacado    = destacado,
                    disponible   = True,
                    tiempo_prep  = tiempo,
                    orden        = idx + 1,
                ))

    # ── Mesas (16 mesas, 4 personas c/u + 2 mesas grandes)
    if db.query(Mesa).count() == 0:
        for num in range(1, 15):
            db.add(Mesa(numero=num, capacidad=4))
        db.add(Mesa(numero=15, capacidad=8))   # Mesa grande
        db.add(Mesa(numero=16, capacidad=10))  # Mesa familiar

    db.commit()
    print(f"[SEED] ✅ BD inicializada con {len(CATEGORIAS)} categorías y {sum(len(v) for v in PRODUCTOS.values())} platos peruanos")
