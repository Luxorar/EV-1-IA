"""
03_Chat_IA.py — Asistente virtual UNIMARC con IA.

Interfaz conversacional conectada al motor RAG (chat_engine.py).
El usuario puede preguntar por productos, precios, ubicación
en tienda, usando FAISS + GPT-4o-mini.
"""

import streamlit as st
import utils

utils.inject_css()

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
        from chat_engine import consultar
        with st.chat_message("assistant"):
            response = st.write_stream(consultar(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"Error al conectar con el asistente: {e}")
        st.info("Asegúrate de que el archivo `.env` tenga configurado `GITHUB_TOKEN` y `OPENAI_BASE_URL`.")
