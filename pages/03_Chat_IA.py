

import logging
import time
import random
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List



import streamlit as st
import utils
from dotenv import load_dotenv

load_dotenv()
import import_ipynb  # noqa: F401
import Unimarc

# --- Configuracion de logging estructurado con timestamps ---

formato_log = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

manejador_consola = logging.StreamHandler()
manejador_consola.setFormatter(formato_log)

logger = logging.getLogger("observabilidad")
logger.setLevel(logging.DEBUG)
logger.addHandler(manejador_consola)


# --- Recolector de metricas ---

@dataclass
class RegistroMetrica:
    """Registro individual de una interaccion."""
    timestamp: str
    tiempo_respuesta_ms: float
    tokens_entrada: int
    tokens_salida: int
    exitoso: bool
    modelo: str


class RecolectorMetricas:
    """Recolecta y resume metricas de rendimiento de un agente."""

    def __init__(self):
        self.registros: List[RegistroMetrica] = []

    def registrar(self, tiempo_ms: float, tokens_in: int, tokens_out: int,
                  exitoso: bool, modelo: str = "gpt-4o-mini"):
        registro = RegistroMetrica(
            timestamp=datetime.now().isoformat(),
            tiempo_respuesta_ms=round(tiempo_ms, 2),
            tokens_entrada=tokens_in,
            tokens_salida=tokens_out,
            exitoso=exitoso,
            modelo=modelo,
        )
        self.registros.append(registro)

    def resumen(self) -> dict:
        """Devuelve un resumen con estadisticas agregadas."""
        if not self.registros:
            return {"total_peticiones": 0}

        tiempos = [r.tiempo_respuesta_ms for r in self.registros]
        total_tokens = sum(r.tokens_entrada + r.tokens_salida for r in self.registros)
        errores = sum(1 for r in self.registros if not r.exitoso)

        return {
            "total_peticiones": len(self.registros),
            "tiempo_promedio_ms": round(sum(tiempos) / len(tiempos), 2),
            "tiempo_maximo_ms": round(max(tiempos), 2),
            "tiempo_minimo_ms": round(min(tiempos), 2),
            "total_tokens": total_tokens,
            "tasa_errores_pct": round((errores / len(self.registros)) * 100, 2),
        }
  
utils.inject_css()


def consultar(consulta: str, session_id: str = "web_session"):
    logger.info(f"Consultando: {consulta}")
    relevante = Unimarc.buscar_vectorial(consulta)
    contexto = "\n".join(relevante) if relevante else "Producto no encontrado"
    input_text = f"{consulta}\n\nBuscando datos...\n{contexto}"
    config = {"configurable": {"session_id": session_id}}
    for chunk in Unimarc.conversation.stream({"input": input_text}, config):
        yield chunk.content


st.markdown("## Asistente UNIMARC")
st.markdown("Pregúntame sobre productos, precios, ubicación en la tienda y más.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ej: ¿Dónde encuentro arroz?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            response = st.write_stream(consultar(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
        logger.info(f"Respuesta generada para: {prompt[:60]}")
    except Exception as e:
        logger.error(f"Error en consulta '{prompt}': {e}")  
        st.error(f"Error al conectar con el asistente: {e}")
        st.info("Asegúrate de que el archivo `.env` tenga configurado `GITHUB_TOKEN` y `OPENAI_BASE_URL`.")
