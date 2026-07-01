"""
main.py — Punto de entrada de la app UNIMARC con autenticación.

Configura st.navigation() para la navegación entre páginas
y la sidebar compartida con logo, enlaces y radio.
Protección mediante login con usuario/contraseña.
"""

import os
import time
import random
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="UNIMARC — El Supermercado de Todos", layout="wide")

import utils
from security import log_event, get_client_ip, escape_html, login_limiter

# ── Frases promocionales de Uni ────────────────────────────────────
FRASES_UNI = [
    "🔥 ¡Leche Colún a $1.050! Llévala ya",
    "🛒 Despacho gratis sobre $40.000",
    "💰 Arroz Nuestra Cocina desde $1.800",
    "🐓 Pollo Ariztía $3.900 el kilo",
    "🥩 Carne molida $6.500 el kilo",
    "🍞 Pan de molde Todo Día $2.500",
    "🥚 Huevos 12u $3.200 — calidad Avícola Chile",
    "🧀 Queso fresco Colún $4.200",
    "🥤 Refresco Coca Cola 2L $2.400",
    "🍷 Vino Santa Carolina $5.900",
    "🧹 Detergente Ala $4.800 — 1kg",
    "🧴 Shampoo Pantene $4.500 — 400ml",
    "⭐ ¡Nuevos productos cada semana!",
    "🎵 Compra con música en Radio UNIMARC",
    "🤖 Pregúntale a Uni, tu asistente IA",
    "📋 Planifica tu compra con la Lista Inteligente",
    "🏷️ Ofertas de hasta 50% descuento",
    "🚚 Despacho a domicilio en tu comuna",
    "🥑 Palta Hass $1.500 la unidad",
    "🍎 Manzanas Gala $2.200 el kilo",
    "🧈 Mantequilla Soprole $3.500",
    "☕ Café Nuestra Cocina — el mejor precio",
    "🍪 Galletas Oreo $2.600 — 150g",
    "🧁 Yogur Soprole desde $1.200",
    "💧 Agua Cachantun 6x1.5L $3.800",
    "🥩 Jamón Fuentetaja $3.800 — 200g",
    "🐟 Atún Austral $1.700 la lata",
    "🧂 Aceite Cocinero 1L $2.900",
]

# Tiempo entre cambio de frases (segundos)
CAMBIO_FRASE_SEG = 9

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
            st.markdown(f"""
            <div class="login-card">
                <img src="data:image/webp;base64,{utils.get_logo_base64()}" class="login-logo" alt="UNIMARC">
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
    st.markdown(f"""
    <div class="sidebar-logo">
        <img src="data:image/webp;base64,{utils.get_logo_base64()}" alt="UNIMARC">
    </div>
    """, unsafe_allow_html=True)

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

    # ── Mascota Uni con frases rotativas ──────────────────────────────
    if "uni_phrase" not in st.session_state:
        st.session_state.uni_phrase = random.choice(FRASES_UNI)
        st.session_state.uni_phrase_time = time.time()
        st.session_state.uni_expression = "happy"

    # Rotar frase cada CAMBIO_FRASE_SEG segundos
    now = time.time()
    if now - st.session_state.uni_phrase_time > CAMBIO_FRASE_SEG:
        nuevas = [f for f in FRASES_UNI if f != st.session_state.uni_phrase]
        st.session_state.uni_phrase = random.choice(nuevas)
        st.session_state.uni_phrase_time = now
        st.session_state.uni_expression = random.choice(["happy", "wink", "happy", "surprise"])

    frase_actual = st.session_state.uni_phrase
    expresion = st.session_state.uni_expression

    st.markdown(f"""
    <div class="mascot-container">
        <div class="uni-speech-bubble">
            <span class="uni-speech-text">{frase_actual}</span>
        </div>
        <div class="uni-mascot">
            <div class="uni-arm-left"></div>
            <div class="uni-arm-right"></div>
            <div class="uni-face expression-{expresion}">
                <div class="uni-mouth"></div>
            </div>
        </div>
        <div class="uni-name">¡Hola, soy Uni!</div>
        <div class="uni-tagline">Tu asistente Inteligente 2026 🤖</div>
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
