"""
app.py — Página principal de UNIMARC.

Muestra el hero con ofertas destacadas, categorías y
anuncios. Ejecutar con: streamlit run main.py
"""

import streamlit as st
import utils

utils.inject_css()

st.markdown("""
<div class="hero">
    <h1>UNIMARC</h1>
    <p>El supermercado de todos — Ofertas, productos y asistencia con IA</p>
</div>
""", unsafe_allow_html=True)

productos = utils.get_productos()
ofertas = utils.get_ofertas(productos, n=6)

st.markdown("## Ofertas destacadas")
st.markdown('<div class="offer-grid">', unsafe_allow_html=True)
for of in ofertas[:3]:
    st.markdown(f"""
    <div class="offer-card">
        <div class="product-name">{of['producto']}</div>
        <div class="brand">{of['marca']}</div>
        <div class="orig">{of['precio_original_formatted']}</div>
        <div class="offer-price">{of['precio_oferta_formatted']}</div>
        <div class="badge">-{of['descuento']}%</div>
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

st.markdown('<div class="cat-grid">', unsafe_allow_html=True)
for cat, items in sorted(cats.items()):
    st.markdown(f"""
    <div class="cat-card">
        <div class="cat-name">{cat}</div>
        <div class="cat-count">{len(items)} productos</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.page_link("pages/01_Productos.py", label="Ver todos los productos", icon="🛒")