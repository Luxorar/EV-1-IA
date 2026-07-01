"""
01_Productos.py — Catálogo de productos UNIMARC.

Muestra todos los productos importados desde Doc_Unimarc.py
en un grid de tarjetas con buscador y filtro por categoría.
"""

import streamlit as st
import utils
from security import escape_html

st.markdown("## Productos")

productos = utils.get_productos()
categorias = sorted(set(p["categoria"] for p in productos))

busqueda = st.text_input("Buscar producto o marca", placeholder="Ej: leche, arroz, soprole...")

cat_opciones = ["Todas"] + categorias
cat_default = 0
if "cat_filter" in st.session_state and st.session_state.cat_filter in cat_opciones:
    cat_default = cat_opciones.index(st.session_state.cat_filter)
cat_filter = st.selectbox("Filtrar por categoría", cat_opciones, index=cat_default)
if "cat_filter" in st.session_state:
    del st.session_state.cat_filter

filtrados = productos
if cat_filter != "Todas":
    filtrados = [p for p in filtrados if p["categoria"] == cat_filter]
if busqueda:
    q = busqueda.lower()
    filtrados = [p for p in filtrados if q in p["producto"].lower() or q in p["marca"].lower()]

if not filtrados:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;color:#888;">
        <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
        <h3 style="color:#555;">No encontramos «{escape_html(busqueda)}»</h3>
        <p>Prueba con: <strong>leche</strong>, <strong>arroz</strong>, <strong>pan</strong>, <strong>huevos</strong>, <strong>aceite</strong>...</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"**{len(filtrados)}** producto(s) encontrado(s)")
    st.markdown('<div class="product-grid">', unsafe_allow_html=True)
    for p in filtrados:
        inicial = escape_html(p['producto'][0].upper() if p['producto'] else "🛒")
        nombre = escape_html(p['producto'])
        marca = escape_html(p['marca'])
        categoria = escape_html(p['categoria'])
        precio = escape_html(p['precio'])
        st.markdown(f"""
        <div class="product-card-wrapper">
            <div class="product-card">
                <div class="product-icon">{inicial}</div>
                <div class="category-badge">{categoria}</div>
                <h3>{nombre}</h3>
                <div class="brand">{marca}</div>
                <div class="price">{precio}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
