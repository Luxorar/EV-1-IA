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
        cols = st.columns([.3, 3, 2, 1, 1.5])
        with cols[0]:
            hecho = st.checkbox("", key=f"chk_{idx}",
                                value=item.get("comprado", False))
            st.session_state.lista[idx]["comprado"] = hecho
        with cols[1]:
            estilo = "text-decoration:line-through;color:#999;" if hecho else ""
            st.markdown(f"<span style='{estilo}'><strong>{item['producto']}</strong><br><small>{item['marca']}</small></span>",
                        unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"× {item['cantidad']}")
        with cols[3]:
            if st.button("✕", key=f"del_{idx}"):
                st.session_state.lista.pop(idx)
                st.rerun()
        with cols[4]:
            st.markdown(f"**${subtotal:,}**")
        st.markdown("---")

    st.markdown(f"""
    <div style="background:#E30613;color:white;padding:1rem 1.5rem;border-radius:12px;
                display:flex;justify-content:space-between;align-items:center;margin-top:.5rem;">
        <span style="font-size:1.1rem;">Total estimado</span>
        <span style="font-size:1.8rem;font-weight:800;">${total:,}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Limpiar lista", type="secondary"):
        st.session_state.lista = []
        st.rerun()

st.markdown("""
<div class="club-banner" style="margin-top:2rem;">
    <h2>¿Repites esta compra?</h2>
    <p>Guarda tu lista para la próxima visita (próximamente)</p>
    <span class="btn">Guardar lista</span>
</div>
""", unsafe_allow_html=True)
