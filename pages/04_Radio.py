"""
04_Radio.py — Panel de control de Radio UNIMARC.

Muestra la emisora actual con opción de cambiarla.
El audio se reproduce desde el sidebar de main.py
para que suene en todas las páginas.
"""

import streamlit as st
import utils

utils.inject_css()

estacion_actual = st.session_state.get("radio_station", list(utils.ESTACIONES.keys())[0])

st.markdown(f"""
<div style="text-align:center;padding:2rem;background:#f9f9f9;border-radius:16px;margin-bottom:1.5rem;">
    <div style="font-size:3rem;margin-bottom:.5rem;">🎵</div>
    <h2 style="margin:0;">{estacion_actual}</h2>
    <p style="color:#888;">La música se reproduce desde la barra lateral</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Cambiar emisora")
nueva = st.selectbox(
    "Seleccionar emisora",
    list(utils.ESTACIONES.keys()),
    index=list(utils.ESTACIONES.keys()).index(estacion_actual),
    label_visibility="collapsed",
)
if nueva != estacion_actual:
    st.session_state.radio_station = nueva
    st.rerun()

if st.button("Recargar reproductor"):
    st.rerun()

st.markdown("""
<div class="ad-banner" style="margin-top:2rem;">
    <h2>Mientras escuchas, revisa nuestras ofertas</h2>
    <p>Productos con descuentos exclusivos esperando por ti.</p>
</div>
""", unsafe_allow_html=True)
st.page_link("pages/02_Ofertas.py", label="Ver ofertas actuales", icon="🏷️")
