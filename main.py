"""
main.py — Punto de entrada de la app UNIMARC.

Configura st.navigation() para la navegación entre páginas
y la sidebar compartida con logo, enlaces y radio.
"""

import streamlit as st

st.set_page_config(page_title="UNIMARC — El Supermercado de Todos", layout="wide")

import utils

utils.inject_css()

home = st.Page("app.py", title="Inicio", icon="🏠")
productos = st.Page("pages/01_Productos.py", title="Productos", icon="🛒")
ofertas = st.Page("pages/02_Ofertas.py", title="Ofertas", icon="🏷️")
chat = st.Page("pages/03_Chat_IA.py", title="Chat IA", icon="🤖")
radio = st.Page("pages/04_Radio.py", title="Radio", icon="🎵")
lista = st.Page("pages/05_Lista_Inteligente.py", title="Lista Inteligente", icon="📋")

with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:1rem 0;">
        <span style="color:#E30613;font-size:1.8rem;font-weight:900;">UNIMARC</span>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    pg = st.navigation([home, productos, ofertas, chat, radio, lista])
    st.markdown("---")

    st.markdown("### Radio UNIMARC")
    if "radio_station" not in st.session_state:
        st.session_state.radio_station = list(utils.ESTACIONES.keys())[0]
    estacion = st.selectbox(
        "Seleccionar emisora",
        list(utils.ESTACIONES.keys()),
        index=list(utils.ESTACIONES.keys()).index(st.session_state.radio_station),
        key="radio_select",
        label_visibility="collapsed",
    )
    st.session_state.radio_station = estacion
    url = utils.ESTACIONES[estacion]
    audio_html = f"""
    <audio controls autoplay style="width:100%;height:40px;">
        <source src="{url}" type="audio/aac">
        <source src="{url}" type="audio/mpeg">
    </audio>
    <p style="font-size:.75rem;color:#888;margin:2px 0 0;">{estacion}</p>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

pg.run()
