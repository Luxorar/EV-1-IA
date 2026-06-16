"""
chat_engine.py — Motor RAG del asistente UNIMARC.

Importa el motor completo desde Unimarc.ipynb y expone
`consultar()` para la interfaz Streamlit.
"""

from dotenv import load_dotenv

load_dotenv()

import import_ipynb  # noqa: F401
import Unimarc  # noqa: F811


def consultar(consulta: str, session_id: str = "web_session"):
    """Consulta al asistente RAG y devuelve la respuesta en streaming."""
    relevante = Unimarc.buscar_vectorial(consulta)
    contexto = "\n".join(relevante) if relevante else "Producto no encontrado"
    input_text = f"{consulta}\n\nBuscando datos...\n{contexto}"
    config = {"configurable": {"session_id": session_id}}
    for chunk in Unimarc.conversation.stream({"input": input_text}, config):
        yield chunk.content
