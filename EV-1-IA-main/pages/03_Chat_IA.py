import streamlit as st
import utils
from dotenv import load_dotenv

load_dotenv()
from security import (
    sanitize_input, detect_prompt_injection, escape_html,
    escape_ai_output, log_event, chat_limiter, get_client_ip
)
import import_ipynb
import Unimarc

utils.inject_css()


def consultar(consulta: str, session_id: str = "web_session"):
    consulta = sanitize_input(consulta, max_length=500)
    if not consulta:
        yield "Por favor ingresa una consulta válida."
        return

    ip_key = get_client_ip()
    rate_key = f"{ip_key}:{session_id}"

    if not chat_limiter.is_allowed(rate_key):
        remaining = chat_limiter.remaining(rate_key)
        log_event("RATE_LIMIT_EXCEEDED", detail=consulta[:50],
                  session_id=rate_key, level="warning")
        yield f"Demasiadas solicitudes. Espera {remaining}s antes de continuar."
        return

    if detect_prompt_injection(consulta):
        log_event("PROMPT_INJECTION_DETECTED", detail=consulta[:100],
                  session_id=rate_key, level="warning")
        yield "No puedo procesar esa solicitud. Por favor haz una pregunta sobre productos de UNIMARC."
        return

    log_event("CHAT_QUERY", detail=consulta[:100],
              session_id=rate_key, level="info")

    relevante = Unimarc.buscar_vectorial(consulta)
    contexto = "\n".join(relevante) if relevante else "Producto no encontrado"
    input_text = f"{consulta}\n\nBuscando datos...\n{contexto}"
    config = {"configurable": {"session_id": session_id}}
    try:
        for chunk in Unimarc.conversation.stream({"input": input_text}, config):
            yield escape_ai_output(chunk.content)
    except Exception as e:
        log_event("CHAT_ERROR", detail=str(e)[:100],
                  session_id=rate_key, level="error")
        yield f"Error al procesar la consulta: {e}"


def user_msg_html(content):
    return f"""<div class="chat-msg-user">
        <div class="chat-bubble">{escape_html(content)}</div>
        <div class="chat-avatar">👤</div>
    </div>"""


def bot_msg_html(content):
    return f"""<div class="chat-msg-bot">
        <div class="chat-avatar">🛒</div>
        <div class="chat-bubble">{content}</div>
    </div>"""


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
