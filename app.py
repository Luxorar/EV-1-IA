"""
app.py — Página principal de UNIMARC.

Muestra el hero con ofertas destacadas, categorías y
anuncios. Ejecutar con: streamlit run main.py
"""

import streamlit as st
import utils
from security import escape_html

st.markdown("""
<div class="hero">
    <h1>UNIMARC</h1>
    <p>El supermercado de todos — Ofertas, productos y asistencia con IA</p>
</div>
""", unsafe_allow_html=True)

productos = utils.get_productos()
if "ofertas_home" not in st.session_state:
    st.session_state.ofertas_home = utils.get_ofertas(productos, n=6)
ofertas = st.session_state.ofertas_home

st.markdown("## Ofertas destacadas")
st.markdown('<div class="offer-grid">', unsafe_allow_html=True)
for of in ofertas[:3]:
    st.markdown(f"""
    <div class="offer-card">
        <div class="product-name">{escape_html(of['producto'])}</div>
        <div class="brand">{escape_html(of['marca'])}</div>
        <div class="orig">{escape_html(of['precio_original_formatted'])}</div>
        <div class="offer-price">{escape_html(of['precio_oferta_formatted'])}</div>
        <div class="badge">-{escape_html(str(of['descuento']))}%</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="ad-banner">
    <h2>Despacho gratis en compras sobre $40.000</h2>
    <p>Válido en todas las comunas con cobertura. Revisa términos y condiciones en tu tienda UNIMARC.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Categorías")
cats = {}
for p in productos:
    cats.setdefault(p["categoria"], []).append(p)

iconos = {
    "Lácteos": "🥛", "Panadería y Cereales": "🍞", "Cárnicos y Huevos": "🥩",
    "Frutas y Verduras": "🥦", "Abarrotes": "🥫", "Bebidas": "🥤",
    "Limpieza y Cuidado": "🧹",
}

cols = st.columns(3)
for i, (cat, items) in enumerate(sorted(cats.items())):
    with cols[i % 3]:
        ico = iconos.get(cat, "📦")
        if st.button(f"{ico}\n\n**{cat}**\n\n{len(items)} productos", key=f"cat_{cat}", use_container_width=True):
            st.session_state.cat_filter = cat
            st.switch_page("pages/01_Productos.py")

st.page_link("pages/01_Productos.py", label="Ver todos los productos", icon="🛒")
