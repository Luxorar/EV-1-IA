import streamlit as st
import utils
from security import escape_html
from chat_engine import consultar

utils.inject_css()


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

if "messages" not in st.session_state:
    st.session_state.messages = []

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
    except Exception as e:
        st.error(f"Error al conectar con el asistente: {e}")
        st.info("Asegúrate de que el archivo `.env` tenga configurado `GITHUB_TOKEN` y `OPENAI_BASE_URL`.")
