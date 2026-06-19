"""
flask_app.py — Servidor Flask independiente para UNIMARC.

Ejecutar con: python flask_app.py
Sirve el chat vía API REST en http://localhost:5000
Usa el motor RAG real (FAISS + GPT-4o-mini) desde chat_engine.py.
"""

import os
import re
import time
from collections import defaultdict

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from chat_engine import consultar as rag_consultar

app = Flask(__name__)

# ── CORS Restrictivo ───────────────────────────────────────────────
CORS(app, resources={
    r"/chat": {
        "origins": [
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"],
    }
})

# ── Autenticación HTTP Basic ───────────────────────────────────────
AUTH_USER = os.getenv("AUTH_USER")
AUTH_PASS = os.getenv("AUTH_PASS")


def check_auth(username, password):
    return username == AUTH_USER and password == AUTH_PASS


def authenticate():
    return (
        jsonify({"error": "Autenticación requerida"}),
        401,
        {"WWW-Authenticate": 'Basic realm="UNIMARC API"'},
    )


# ── Sanitización ───────────────────────────────────────────────────
def sanitize(text: str, max_len: int = 500) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()[:max_len]
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    return text


# ── Rate Limiting (en memoria) ─────────────────────────────────────
RATE_LIMIT = 30
RATE_WINDOW = 60
_requests: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_WINDOW
    bucket = _requests[ip]
    bucket[:] = [t for t in bucket if t > window_start]
    if len(bucket) >= RATE_LIMIT:
        return True
    bucket.append(now)
    return False


# ── Headers de Seguridad ───────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' https://upload.wikimedia.org; "
        "media-src https://playerservices.streamtheworld.com; "
        "connect-src 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


# ── Rutas ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    ip = request.remote_addr or "unknown"

    if is_rate_limited(ip):
        return jsonify({"error": "Demasiadas solicitudes. Espera un momento."}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    query = sanitize(data.get("query", ""))
    session_id = data.get("session_id", "flask_session")
    if not query:
        return jsonify({"response": "Por favor ingresa una consulta válida."})

    # Usar el motor RAG real en lugar del buscador por palabras
    try:
        respuesta_completa = "".join(list(rag_consultar(query, session_id=session_id)))
        return jsonify({"response": respuesta_completa})
    except Exception as e:
        return jsonify({"response": f"Error al procesar la consulta: {e}"}), 500


if __name__ == "__main__":
    print("Servidor Flask UNIMARC iniciado en http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
