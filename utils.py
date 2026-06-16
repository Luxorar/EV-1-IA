"""
utils.py — Funciones compartidas para la app UNIMARC.

Importa los productos desde Doc_Unimarc.py, los parsea,
clasifica por categorías, genera ofertas simuladas e
inyecta estilos CSS.
"""

import streamlit as st
import random
from Doc_Unimarc import Productos

CATEGORY_KEYWORDS = {
    "Lácteos": ["yogur", "leche", "queso", "mantequilla", "mantejar", "requesón"],
    "Panadería y Cereales": ["pan", "galletas", "biscotes", "avena", "cereal", "harina"],
    "Cárnicos y Huevos": ["huevos", "jamón", "mortadela", "pavo", "pollo", "carne", "salchichas", "atún"],
    "Frutas y Verduras": ["palta", "tomate", "cebolla", "papas", "manzanas", "banano", "naranja"],
    "Abarrotes": ["aceite", "mayonesa", "kétchup", "mostaza", "mermelada", "miel", "azúcar", "arroz", "fideos", "chocolate", "café"],
    "Bebidas": ["cerveza", "vino", "agua", "jugo", "refresco", "cola"],
    "Limpieza y Cuidado": ["papel tissue", "jabón", "detergente", "suavizante", "pasta dental", "desodorante", "shampoo"],
}

def get_category(producto):
    p = producto.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in p for kw in keywords):
            return cat
    return "Otros"

def parse_producto(p):
    d = {}
    for part in p.split(","):
        if ":" in part:
            key, val = part.split(":", 1)
            d[key.strip()] = val.strip()
    nombre = d.get("producto", "")
    d["categoria"] = get_category(nombre)
    precio_str = d.get("precio", "$0")
    d["precio_num"] = int(precio_str.replace("$", "").replace(".", ""))
    return d

def get_productos():
    return [parse_producto(p) for p in Productos]

def get_ofertas(productos, n=12):
    ofertas = []
    muestra = random.sample(productos, min(n, len(productos)))
    for p in muestra:
        desc = random.choice([10, 15, 20, 25, 30, 50])
        po = p["precio_num"]
        of = int(po * (1 - desc / 100))
        ofertas.append({
            **p,
            "descuento": desc,
            "precio_original_formatted": f"${po:,}",
            "precio_oferta_formatted": f"${of:,}",
        })
    return ofertas

ESTACIONES = {
    "FM Dos — Música variada": "https://playerservices.streamtheworld.com/api/livestream-redirect/FMDOSAAC_SC",
    "Radio Concierto — Pop & Rock": "https://playerservices.streamtheworld.com/api/livestream-redirect/CONCIERTOAAC_SC",
    "Radio Corazón — Romántica": "https://playerservices.streamtheworld.com/api/livestream-redirect/CORAZONAAC_SC",
    "Los 40 Chile — Éxitos": "https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_CHILEAAC_SC",
    "Radio Pudahuel — Clásicos": "https://playerservices.streamtheworld.com/api/livestream-redirect/PUDAHUELAAC_SC",
}

STYLES = """
<style>
    .hero {
        background: linear-gradient(135deg, #E30613 0%, #ff4444 60%, #ff6b6b 100%);
        padding: 3rem 2rem; border-radius: 16px; color: white; text-align: center; margin-bottom: 2rem;
    }
    .hero h1 { font-size: 2.5rem; margin: 0; }
    .hero p { font-size: 1.2rem; opacity: 0.9; }

    .product-card {
        background: white; border: 1px solid #eee; border-radius: 12px; padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform .2s, box-shadow .2s;
    }
    .product-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
    .product-card h3 { margin: 0 0 .2rem; font-size: 1rem; }
    .product-card .brand { color: #666; font-size: .85rem; }
    .product-card .price { color: #E30613; font-size: 1.3rem; font-weight: 700; margin: .4rem 0; }
    .product-card .category-badge {
        background: #f0f0f0; padding: .15rem .6rem; border-radius: 20px;
        font-size: .75rem; color: #555; display: inline-block;
    }

    .offer-card {
        background: linear-gradient(135deg, #E30613 0%, #ff4444 100%); border-radius: 12px;
        padding: 1.5rem; color: white; margin-bottom: 1rem;
    }
    .offer-card .orig { text-decoration: line-through; opacity: .6; font-size: .9rem; }
    .offer-card .offer-price { font-size: 1.8rem; font-weight: 800; margin: .3rem 0; }
    .offer-card .badge {
        background: rgba(255,255,255,.2); padding: .25rem .8rem; border-radius: 20px;
        font-weight: 700; font-size: .9rem; display: inline-block;
    }

    .ad-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px;
        padding: 2rem; color: white; text-align: center; margin: 1rem 0;
    }
    .ad-banner h2 { color: #FFD700; margin: 0 0 .5rem; }
</style>
"""

def inject_css():
    st.markdown(STYLES, unsafe_allow_html=True)
