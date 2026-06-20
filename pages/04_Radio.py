"""
04_Radio.py — Panel de control de Radio UNIMARC.

Muestra la emisora actual con opción de cambiarla.
El audio se reproduce desde el sidebar de main.py
para que suene en todas las páginas.
"""

import streamlit as st
import utils
from security import escape_html

utils.inject_css()

estacion_actual = st.session_state.get("radio_station", list(utils.ESTACIONES.keys())[0])

st.markdown(f"""
<div class="radio-card">
    <div class="radio-icon">🎵</div>
    <div class="radio-waves">
        <span></span><span></span><span></span><span></span><span></span>
    </div>
    <h2>{escape_html(estacion_actual)}</h2>
    <p class="status">La música se reproduce desde la barra lateral</p>
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
<div class="ad-banner">
    <h2>Mientras escuchas, revisa nuestras ofertas</h2>
    <p>Productos con descuentos exclusivos esperando por ti.</p>
</div>
""", unsafe_allow_html=True)
st.page_link("pages/02_Ofertas.py", label="Ver ofertas actuales", icon="🏷️")
