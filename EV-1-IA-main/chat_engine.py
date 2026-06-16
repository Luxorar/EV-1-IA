"""
chat_engine.py — Motor RAG del asistente UNIMARC.

Importa el motor completo desde Unimarc.ipynb y expone
`consultar()` para la interfaz Streamlit.
"""

from dotenv import load_dotenv

load_dotenv()

from security import sanitize_input, detect_prompt_injection, log_event, chat_limiter, get_client_ip, escape_ai_output

import import_ipynb  # noqa: F401
import Unimarc  # noqa: F811


def consultar(consulta: str, session_id: str = "web_session"):
    """Consulta al asistente RAG y devuelve la respuesta en streaming."""

    consulta = sanitize_input(consulta, max_length=500)

    if not consulta:
        yield "Por favor ingresa una consulta válida."
        return

    ip_key = get_client_ip()
    rate_key = f"{ip_key}:{session_id}"

    if not chat_limiter.is_allowed(rate_key):
        log_event("RATE_LIMIT_EXCEEDED", detail=consulta[:50],
                  session_id=rate_key, level="warning")
        yield "Demasiadas solicitudes. Por favor espera un momento antes de continuar."
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
