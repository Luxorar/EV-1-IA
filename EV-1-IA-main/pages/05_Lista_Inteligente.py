"""
05_Lista_Inteligente.py — Agente de lista de compras UNIMARC.

Permite buscar productos del catálogo, agregarlos con una
cantidad, ver el subtotal por producto y el total acumulado.
Incluye checkboxes para marcar items como comprados.
"""

import streamlit as st
import utils

utils.inject_css()

st.markdown("## Planifica tu compra")
st.markdown("Busca productos, agrégalos con cantidad y calcula tu total.")

productos = utils.get_productos()
nombres = [p["producto"] for p in productos]

if "lista" not in st.session_state:
    st.session_state.lista = []

with st.container():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        seleccion = st.selectbox("Buscar producto", nombres, label_visibility="collapsed",
                                  placeholder="Escribe un producto...")
    with col2:
        cantidad = st.number_input("Cant.", min_value=1, value=1, step=1, label_visibility="collapsed")
    with col3:
        if st.button("Agregar", use_container_width=True):
            prod = next(p for p in productos if p["producto"] == seleccion)
            st.session_state.lista.append({
                "producto": prod["producto"],
                "marca": prod["marca"],
                "precio_unit": prod["precio_num"],
                "precio_str": prod["precio"],
                "cantidad": cantidad,
                "comprado": False,
            })
            st.rerun()

if not st.session_state.lista:
    st.info("Tu lista está vacía. Agrega productos desde el selector de arriba.")
else:
    total = 0
    for idx, item in enumerate(st.session_state.lista):
        subtotal = item["precio_unit"] * item["cantidad"]
        total += subtotal
        hecho = item.get("comprado", False)

        cols = st.columns([0.3, 3, 1.2, 0.6, 1.8])
        with cols[0]:
            nuevo_hecho = st.checkbox("", key=f"chk_{idx}", value=hecho)
            st.session_state.lista[idx]["comprado"] = nuevo_hecho
        with cols[1]:
            st.markdown(f"""
            <div class="list-item" style="margin:0;padding:0.6rem 0;border:none;box-shadow:none;">
                <div class="item-info">
                    <div>
                        <div class="name" style="text-decoration:{'line-through' if nuevo_hecho else 'none'};color:{'#bbb' if nuevo_hecho else '#222'};">{item['producto']}</div>
                        <div class="brand">{item['marca']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<span class="item-qty">× {item["cantidad"]}</span>', unsafe_allow_html=True)
        with cols[3]:
            if st.button("✕", key=f"del_{idx}"):
                st.session_state.lista.pop(idx)
                st.rerun()
        with cols[4]:
            st.markdown(f'<div style="text-align:right;font-weight:700;color:#E31837;">${subtotal:,}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="list-total">
        <span>Total estimado</span>
        <span class="amount">${total:,}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Limpiar lista", type="secondary"):
        st.session_state.lista = []
        st.rerun()

st.markdown("""
<div class="club-banner">
    <h2>¿Repites esta compra?</h2>
    <p>Guarda tu lista para la próxima visita (próximamente)</p>
    <span class="btn">Guardar lista</span>
</div>
""", unsafe_allow_html=True)
