from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from Doc_Unimarc import Productos

app = Flask(__name__)
CORS(app)

# Simulación del chatbot sin requerir OpenAI
def buscar_productos(query):
    """Buscar productos relevantes basado en la query"""
    query_lower = query.lower()
    resultados = []
    
    for producto in Productos:
        if any(word in producto.lower() for word in query_lower.split()):
            resultados.append(producto)
    
    return resultados[:3]

def generar_respuesta(query, productos):
    """Generar respuesta basada en productos encontrados"""
    if not productos:
        return f"Lo siento, no encontré productos relacionados con '{query}'. Intenta preguntando por otros productos como: leche, pan, arroz, queso, jamón, etc."
    
    respuesta = f"Encontré los siguientes productos relacionados con '{query}':\n\n"
    for producto in productos:
        respuesta += f"• {producto}\n"
    
    respuesta += "\n¿Deseas conocer más detalles de algún producto?"
    return respuesta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'response': 'Por favor ingresa una consulta.'})
    
    productos = buscar_productos(query)
    respuesta = generar_respuesta(query, productos)
    
    return jsonify({'response': respuesta})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)