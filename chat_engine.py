"""
chat_engine.py — Motor RAG del asistente UNIMARC.

Carga los productos desde Doc_Unimarc.py, crea un índice
vectorial con FAISS + OpenAI embeddings, y expone una función
`consultar()` que recibe una consulta del usuario y devuelve
un generador con la respuesta del LLM (GPT-4o-mini) en streaming.
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from Doc_Unimarc import Productos

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("GITHUB_TOKEN"),
    openai_api_base=os.getenv("OPENAI_BASE_URL"),
)

vectorstore = FAISS.from_texts(Productos, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def buscar_vectorial(query):
    return [doc.page_content for doc in retriever.invoke(query)]

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
    model="gpt-4o-mini",
    temperature=0.1,
    streaming=True,
    max_tokens=600,
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un administrador de supermercado de la cadena UNIMARC. "
     "Conoces la posición de los productos según sede y pasillo, precios y descuentos. "
     "Si el usuario pide varios productos calcula el total según la cantidad indicada. "
     "Para productos que se pesen (incontables como carne), pregunta cuánto va a llevar. "
     "RESPONDE SOLO CON LOS DATOS EN 'Buscando datos'. NO INVENTES PRODUCTOS."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

chain = prompt | llm

store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def consultar(consulta: str, session_id: str = "web_session"):
    """Consulta al asistente RAG y devuelve la respuesta en streaming."""
    relevante = buscar_vectorial(consulta)
    contexto = "\n".join(relevante) if relevante else "Producto no encontrado"
    input_text = f"{consulta}\n\nBuscando datos...\n{contexto}"
    config = {"configurable": {"session_id": session_id}}
    for chunk in conversation.stream({"input": input_text}, config):
        yield chunk.content
