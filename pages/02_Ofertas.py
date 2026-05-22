"""
02_Ofertas.py — Página de ofertas UNIMARC.

Genera ofertas simuladas con descuentos aleatorios sobre
los productos del catálogo.
"""

import streamlit as st
import utils

utils.inject_css()

st.markdown("## Ofertas y promociones")

productos = utils.get_productos()
ofertas = utils.get_ofertas(productos, n=15)

cols = st.columns(3)
for i, of in enumerate(ofertas):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="offer-card">
            <div style="font-size:1.1rem;font-weight:600;">{of['producto']}</div>
            <div style="font-size:.85rem;opacity:.8;margin-bottom:.5rem;">{of['marca']}</div>
            <div class="orig">{of['precio_original_formatted']}</div>
            <div class="offer-price">{of['precio_oferta_formatted']}</div>
            <div class="badge">-{of['descuento']}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="ad-banner">
    <h2>No pierdas estas ofertas</h2>
    <p>Válidas hasta agotar stock. Precios exclusivos online y en tiendas UNIMARC.</p>
</div>
""", unsafe_allow_html=True)
