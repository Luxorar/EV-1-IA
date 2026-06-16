"""
01_Productos.py — Catálogo de productos UNIMARC.

Muestra todos los productos importados desde Doc_Unimarc.py
en un grid de tarjetas con buscador y filtro por categoría.
"""

import streamlit as st
import utils

utils.inject_css()

st.markdown("## Productos")

productos = utils.get_productos()
categorias = sorted(set(p["categoria"] for p in productos))

busqueda = st.text_input("Buscar producto o marca", placeholder="Ej: leche, arroz, soprole...")
cat_filter = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)

filtrados = productos
if cat_filter != "Todas":
    filtrados = [p for p in filtrados if p["categoria"] == cat_filter]
if busqueda:
    q = busqueda.lower()
    filtrados = [p for p in filtrados if q in p["producto"].lower() or q in p["marca"].lower()]

st.markdown(f"**{len(filtrados)}** producto(s) encontrado(s)")

cols = st.columns(3)
for i, p in enumerate(filtrados):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="product-card" style="margin-bottom:1rem;">
            <div class="category-badge">{p['categoria']}</div>
            <h3>{p['producto']}</h3>
            <div class="brand">{p['marca']}</div>
            <div class="price">{p['precio']}</div>
        </div>
        """, unsafe_allow_html=True)
