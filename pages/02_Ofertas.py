"""
02_Ofertas.py — Página de ofertas UNIMARC.

Genera ofertas simuladas con descuentos aleatorios sobre
los productos del catálogo.
"""

import streamlit as st
import utils
from security import escape_html

utils.inject_css()

st.markdown("## Ofertas y promociones")

productos = utils.get_productos()
ofertas = utils.get_ofertas(productos, n=15)

st.markdown('<div class="offer-grid">', unsafe_allow_html=True)
for of in ofertas:
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
    <h2>No pierdas estas ofertas</h2>
    <p>Válidas hasta agotar stock. Precios exclusivos online y en tiendas UNIMARC.</p>
</div>
""", unsafe_allow_html=True)
