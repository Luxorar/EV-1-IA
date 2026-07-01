"""
flask_app.py — Servidor Flask independiente para UNIMARC.

Ejecutar con: python flask_app.py
Sirve el chat vía API REST en http://localhost:5000
Usa el motor RAG real (FAISS + GPT-4o-mini) desde chat_engine.py.
"""

import os
import functools
import time
from collections import defaultdict

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from chat_engine import consultar as rag_consultar
from security import sanitize_input as security_sanitize, log_event
from openai import (
    BadRequestError, RateLimitError,
    APITimeoutError, APIConnectionError, AuthenticationError,
)

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


# ── Decorador de autenticación ─────────────────────────────────────
def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            log_event("FLASK_AUTH_FAILED", detail=f"IP={request.remote_addr}", level="warning")
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# ── Rate Limiting (en memoria, con X-Forwarded-For) ───────────────
RATE_LIMIT = 30
RATE_WINDOW = 60
_requests: dict[str, list[float]] = defaultdict(list)


def get_client_ip():
    """Obtiene IP real desde X-Forwarded-For si está detrás de nginx."""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


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
@requires_auth
def chat():
    ip = get_client_ip()

    if is_rate_limited(ip):
        log_event("FLASK_RATE_LIMIT", detail=f"IP={ip}", level="warning")
        return jsonify({"error": "Demasiadas solicitudes. Espera un momento."}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    query = security_sanitize(data.get("query", ""))
    session_id = data.get("session_id", "flask_session")
    if not query:
        return jsonify({"response": "Por favor ingresa una consulta válida."})

    try:
        respuesta_completa = "".join(list(rag_consultar(query, session_id=session_id)))
        return jsonify({"response": respuesta_completa})
    except BadRequestError:
        log_event("FLASK_LLM_BAD_REQUEST", detail=f"IP={ip}", level="warning")
        return jsonify({"response": "Tu pregunta activó los filtros de seguridad. Reformúlala."}), 400
    except RateLimitError:
        log_event("FLASK_LLM_RATE_LIMIT", detail=f"IP={ip}", level="warning")
        return jsonify({"response": "Servicio de IA saturado. Espera unos segundos."}), 429
    except (APITimeoutError, APIConnectionError):
        log_event("FLASK_LLM_UNAVAILABLE", detail=f"IP={ip}", level="error")
        return jsonify({"response": "Servicio de IA no disponible. Intenta más tarde."}), 503
    except AuthenticationError:
        log_event("FLASK_LLM_AUTH_ERROR", detail=f"IP={ip}", level="error")
        return jsonify({"response": "Error de configuración del servicio de IA."}), 500
    except Exception:
        log_event("FLASK_CHAT_ERROR", detail=f"IP={ip}", level="error")
        return jsonify({"response": "Error interno al procesar la consulta."}), 500


if __name__ == "__main__":
    print("Servidor Flask UNIMARC iniciado en http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
