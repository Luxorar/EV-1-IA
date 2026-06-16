# EV-1-IA
LUIS VILLALÓN, VICTOR ARAUS
SECCIÓN 001D


<img width="30" height="38" alt="image" src="https://github.com/user-attachments/assets/168a2dac-ac76-4385-a6c3-86a13b37aa39" />

✨ IL1.1 – Formulación de Prompts para Modelos de Lenguaje

📌 Nombre y breve descripción

Unimarc es una empresa dedicada al comercio de productos alimenticios, mercadería y artículos para el hogar, con presencia en distintas ciudades de Chile.

🛑 Identificación y descripción del problema/desafío

Los clientes suelen desconocer la ubicación exacta y la disponibilidad de stock de los productos que buscan, lo que genera pérdida de tiempo, insatisfacción y consultas constantes al personal de tienda.

💡 Solución del problema

La propuesta consiste en implementar un asistente de inteligencia artificial que actúe como un “parche digital” dentro de la experiencia de compra. Este asistente mostrará los productos en sus respectivas ubicaciones, junto con sus precios actualizados, respondiendo siempre de manera clara y formal.

⚖️ Restricciones

La IA debe responder exclusivamente en lenguaje formal.
Las respuestas deben ser directas y precisas, enfocadas únicamente en la consulta realizada por el cliente.

🚀 Motivación para el uso de agentes de IA, LLMs y RAG

El uso de agentes inteligentes, LLMs y técnicas RAG permite ofrecer una experiencia más efectiva y amigable para los usuarios, integrando datos internos (inventario y mapas de góndolas) con fuentes externas (catálogos de proveedores). Esto asegura respuestas confiables, relevantes y en tiempo real, mejorando la satisfacción del cliente y optimizando la operación de la tienda.


🎯 Objetivos concretos y medibles

Reducir en un 30% el tiempo promedio de búsqueda de productos en tienda.
Aumentar en un 20% la satisfacción del cliente medida en encuestas internas.
Disminuir en un 15% las consultas presenciales al personal sobre ubicación de productos.
Garantizar que el 100% de los precios mostrados estén sincronizados con el sistema de inventario.

📊 Datos disponibles o simulables

Inventario digital de Unimarc: base de datos con productos, precios y stock.
Mapas de pasillos y góndolas: información de ubicación física de cada producto.
Historial de compras de clientes: datos anonimizados para sugerencias personalizadas.
Catálogos externos de proveedores: para validar disponibilidad y precios.

🔄 Pipeline RAG (ejemplo paso a paso)

Entrada del usuario: el cliente pregunta por un producto (“¿Dónde encuentro arroz integral?”).

Recuperación interna: el sistema busca en la base de datos de inventario y mapas de góndolas.

Recuperación externa: consulta catálogos de proveedores si el producto no está disponible.

Procesamiento LLM: el modelo organiza la información y genera una respuesta clara y formal.

Salida al usuario: se muestra ubicación exacta del pasillo, precio actualizado y alternativas si no hay stock.
