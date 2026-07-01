import streamlit as st
from security import escape_html
from chat_engine import consultar


def user_msg_html(content):
    return f"""<div class="chat-msg-user">
        <div class="chat-bubble">{escape_html(content)}</div>
        <div class="chat-avatar">👤</div>
    </div>"""


def bot_msg_html(content):
    return f"""
    <div class="chat-msg-bot">
        <div class="bot-avatar-container">
            <div class="uni-mascot" style="width:40px; height:40px; border-radius:10px; box-shadow:none; animation: floatMascot 3s ease-in-out infinite;">
                <div class="uni-face" style="width:30px; height:24px; border-radius:6px; padding: 0 4px;">
                </div>
            </div>
        </div>
        <div class="chat-bubble" style="background-color: #ffffff; border: 1px solid rgba(227, 24, 55, 0.1); color: #212529;">
            {content}
        </div>
    </div>
    """


st.markdown("## Asistente UNIMARC")
st.markdown("Pregúntame sobre productos, precios, ubicación en la tienda y más.")

MAX_HISTORY = 30

if "messages" not in st.session_state:
    st.session_state.messages = []

# Limitar historial en sesión para evitar DoS por memoria
if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(user_msg_html(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(bot_msg_html(msg["content"]), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ej: ¿Dónde encuentro arroz?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(user_msg_html(prompt), unsafe_allow_html=True)

    try:
        response_container = st.empty()
        response_container.markdown("""
        <div class="chat-msg-bot">
            <div class="bot-avatar-container">
                <div class="uni-mascot" style="width:36px;height:36px;border-radius:10px;box-shadow:none;animation:talkMascot 0.4s ease-in-out infinite,glowPulse 2s ease-in-out infinite;">
                    <div class="uni-arm-left" style="width:12px;height:22px;top:10px;left:-8px;"></div>
                    <div class="uni-arm-right" style="width:12px;height:22px;top:10px;right:-8px;"></div>
                    <div class="uni-face" style="width:26px;height:22px;border-radius:6px;padding:0 4px;">
                    </div>
                </div>
            </div>
            <div class="chat-bubble" style="background:#f0f0f0;border:none;color:#888;">
                <span class="typing-dots">Uni está pensando<span>.</span><span>.</span><span>.</span></span>
            </div>
        </div>
        <style>
        @keyframes dotPulse { 0%,20% { opacity:0; } 50% { opacity:1; } 80%,100% { opacity:0; } }
        .typing-dots span { animation: dotPulse 1.4s infinite; font-size:1.5rem; line-height:0; }
        .typing-dots span:nth-child(2) { animation-delay:0.2s; }
        .typing-dots span:nth-child(3) { animation-delay:0.4s; }
        </style>
        """, unsafe_allow_html=True)
        full_response = ""
        for chunk in consultar(prompt):
            full_response += chunk
            response_container.markdown(
                bot_msg_html(full_response + "▌"), unsafe_allow_html=True
            )
        response_container.markdown(
            bot_msg_html(full_response), unsafe_allow_html=True
        )
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception:
        st.error("Error inesperado al conectar con el asistente. Revisa la terminal para más detalles.")
