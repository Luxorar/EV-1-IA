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

def inject_css():
    import os
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
