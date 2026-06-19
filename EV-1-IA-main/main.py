"""
main.py — Punto de entrada de la app UNIMARC con autenticación.

Configura st.navigation() para la navegación entre páginas
y la sidebar compartida con logo, enlaces y radio.
Protección mediante login con usuario/contraseña.
"""

import os
import time
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="UNIMARC — El Supermercado de Todos", layout="wide")

import utils
from security import log_event, get_client_ip, escape_html, login_limiter

# ── Autenticación ──────────────────────────────────────────────────
AUTH_USER = os.getenv("AUTH_USER")
AUTH_PASS = os.getenv("AUTH_PASS")
if not AUTH_USER or not AUTH_PASS:
    st.error("Error de configuración: credenciales de autenticación no configuradas. "
             "Define AUTH_USER y AUTH_PASS en el archivo .env")
    st.stop()
SESSION_TIMEOUT = 1800  # 30 minutos

def check_auth():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
        st.session_state.auth_time = None

    if st.session_state.auth_user:
        elapsed = time.time() - st.session_state.auth_time
        if elapsed > SESSION_TIMEOUT:
            st.session_state.auth_user = None
            st.session_state.auth_time = None
            log_event("SESSION_TIMEOUT", level="info",
                      session_id=get_client_ip())
            st.rerun()

    if not st.session_state.auth_user:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="login-card">
                <h1>UNIMARC</h1>
                <p class="subtitle">Acceso restringido — Ingresa tus credenciales</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("Usuario", placeholder="admin")
                password = st.text_input("Contraseña", type="password",
                                         placeholder="••••••••")
                submitted = st.form_submit_button("Ingresar",
                                                   use_container_width=True,
                                                   type="primary")

            if submitted:
                login_ip = get_client_ip()
                if not login_limiter.is_allowed(login_ip):
                    log_event("LOGIN_RATE_LIMIT", level="warning",
                              session_id=login_ip)
                    st.error("Demasiados intentos de inicio de sesión. Espera un minuto.")
                    st.stop()
                if username == AUTH_USER and password == AUTH_PASS:
                    st.session_state.auth_user = username
                    st.session_state.auth_time = time.time()
                    log_event("LOGIN_SUCCESS", level="info",
                              session_id=get_client_ip())
                    st.rerun()
                else:
                    log_event("LOGIN_FAILED", level="warning",
                              session_id=get_client_ip(),
                              detail=f"user={escape_html(username)}")
                    st.error("Usuario o contraseña incorrectos.")

            st.markdown("""
            <div style="text-align:center;color:#bbb;font-size:0.75rem;margin-top:2rem;">
                UNIMARC IA v1.0
            </div>
            """, unsafe_allow_html=True)
        st.stop()

check_auth()

# ── Barra lateral con cierre de sesión ─────────────────────────────
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="sidebar-brand">
            UNIMARC
            <small>El supermercado de todos</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Salir", type="secondary", use_container_width=True):
            log_event("LOGOUT", level="info", session_id=get_client_ip())
            st.session_state.auth_user = None
            st.session_state.auth_time = None
            st.rerun()

    # Insertar presentación de la mascota institucional en el Sidebar
    st.markdown("""
    <div class="mascot-container">
        <div class="uni-mascot">
            <div class="uni-face"></div>
        </div>
        <div style="text-align: center; margin-top: 0.75rem;">
            <strong style="color: #E31837; font-size: 1.1rem;">¡Hola, soy Uni!</strong>
            <p style="color: #6c757d; font-size: 0.85rem; margin: 0.2rem 0 0 0;">
                Tu asistente Unimarc 2026. Listo para ayudarte a ahorrar.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navegación
    home = st.Page("app.py", title="Inicio", icon="🏠")
    productos = st.Page("pages/01_Productos.py", title="Productos", icon="🛒")
    ofertas = st.Page("pages/02_Ofertas.py", title="Ofertas", icon="🏷️")
    chat = st.Page("pages/03_Chat_IA.py", title="Chat IA", icon="🤖")
    radio = st.Page("pages/04_Radio.py", title="Radio", icon="🎵")
    lista = st.Page("pages/05_Lista_Inteligente.py", title="Lista Inteligente", icon="📋")

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
    url_safe = escape_html(url)
    label_safe = escape_html(estacion)
    audio_html = f"""
    <div class="sidebar-radio">
        <audio controls autoplay>
            <source src="{url_safe}" type="audio/aac">
            <source src="{url_safe}" type="audio/mpeg">
        </audio>
        <div class="sidebar-radio-label">{label_safe}</div>
    </div>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

    if st.session_state.auth_time:
        remaining = int(SESSION_TIMEOUT - (time.time() - st.session_state.auth_time))
        mins = remaining // 60
        secs = remaining % 60
        if mins > 0 or secs > 0:
            st.markdown(f"""
            <div class="sidebar-timer">Sesión: {mins:02d}:{secs:02d}</div>
            """, unsafe_allow_html=True)

utils.inject_css()

pg.run()
