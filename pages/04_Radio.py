"""
04_Radio.py — Panel informativo de Radio UNIMARC.

Muestra la emisora actual y ecualizador animado.
El control y audio están en la barra lateral (main.py).
"""

import streamlit as st
import utils
from security import escape_html

estacion_actual = st.session_state.get("radio_station", list(utils.ESTACIONES.keys())[0])

st.markdown("## Radio UNIMARC")

st.markdown(f"""
<div class="radio-card">
    <div class="radio-icon">🎵</div>
    <div class="radio-waves">
        <span></span><span></span><span></span><span></span><span></span>
    </div>
    <h2>{escape_html(estacion_actual)}</h2>
    <p class="status">🔊 Reproduciendo desde la barra lateral</p>
    <p style="color:#999;font-size:0.85rem;">
        Cambia de emisora en el panel izquierdo
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Emisoras disponibles")
for nombre in utils.ESTACIONES.keys():
    ico = "🎵" if nombre == estacion_actual else "🔇"
    st.markdown(f"{ico} **{nombre}**")

st.markdown("""
<div class="ad-banner">
    <h2>Música mientras compras</h2>
    <p>Disfruta de tus emisoras favoritas mientras exploras productos y ofertas.</p>
</div>
""", unsafe_allow_html=True)

st.page_link("pages/02_Ofertas.py", label="Ver ofertas actuales", icon="🏷️")
