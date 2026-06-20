"""
chat_engine.py — Motor RAG del asistente UNIMARC.

Importa el motor completo desde Unimarc.ipynb y expone
`consultar()` para la interfaz Streamlit.
"""

import re

from dotenv import load_dotenv

load_dotenv()

from security import (
    sanitize_input, detect_prompt_injection, log_event,
    chat_limiter, get_client_ip, escape_ai_output,
    validate_ai_output, acquire_llm_slot, release_llm_slot,
    LLM_TIMEOUT_SECS,
)

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

    # Control de concurrencia: límite de requests simultáneas al LLM
    if not acquire_llm_slot(timeout=LLM_TIMEOUT_SECS):
        log_event("LLM_CONCURRENCY_LIMIT", detail=consulta[:50],
                  session_id=rate_key, level="warning")
        yield "El servicio está saturado. Intenta de nuevo en un momento."
        return

    log_event("CHAT_QUERY", detail=consulta[:100],
              session_id=rate_key, level="info")

    try:
        relevante = Unimarc.buscar_vectorial(consulta)
        contexto = "\n".join(relevante) if relevante else "Producto no encontrado"
        # Sanitizar contexto RAG antes de inyectarlo al prompt
        contexto = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", contexto)
        input_text = f"{consulta}\n\nBuscando datos...\n{contexto}"
        config = {"configurable": {"session_id": session_id}}
        chunks = []
        for chunk in Unimarc.conversation.stream({"input": input_text}, config):
            safe_chunk = escape_ai_output(chunk.content)
            chunks.append(safe_chunk)
        full_response = "".join(chunks)
        validated = validate_ai_output(full_response)
        if validated != full_response:
            log_event("AI_OUTPUT_BLOCKED", detail=validated[:100],
                      session_id=rate_key, level="warning")
            yield validated
        else:
            for safe_chunk in chunks:
                yield safe_chunk
    except Exception:
        log_event("CHAT_ERROR", detail=consulta[:100],
                  session_id=rate_key, level="error")
        yield "Error al procesar la consulta. Por favor intenta de nuevo."
    finally:
        release_llm_slot()
