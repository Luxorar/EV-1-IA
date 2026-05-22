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
cols = st.columns(3)
for i, of in enumerate(ofertas[:3]):
    with cols[i]:
        st.markdown(f"""
        <div class="offer-card">
            <div style="font-size:1.1rem;font-weight:600;">{of['producto']}</div>
            <div style="font-size:.85rem;opacity:.8;">{of['marca']}</div>
            <div class="orig">{of['precio_original_formatted']}</div>
            <div class="offer-price">{of['precio_oferta_formatted']}</div>
            <div class="badge">-{of['descuento']}%</div>
        </div>
        """, unsafe_allow_html=True)

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

cols = st.columns(3)
for i, (cat, items) in enumerate(sorted(cats.items())):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="product-card" style="margin-bottom:.8rem;">
            <div style="font-weight:600;color:#E30613;">{cat}</div>
            <div style="font-size:.85rem;color:#666;">{len(items)} productos</div>
        </div>
        """, unsafe_allow_html=True)

st.page_link("pages/01_Productos.py", label="Ver todos los productos")
