import streamlit as st
from chat_engine import consultar

st.markdown("## Asistente UNIMARC")
st.markdown("Pregúntame sobre productos, precios, ubicación en la tienda y más.")

MAX_HISTORY = 30

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) > MAX_HISTORY:
    st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ej: ¿Dónde encuentro arroz?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Uni está pensando...")
        full_response = ""
        try:
            for chunk in consultar(prompt):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception:
            placeholder.markdown("Lo siento, ocurrió un error. Intenta de nuevo.")
