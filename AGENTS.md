# EV-1-IA — Unimarc AI Assistant

## Entrypoints
- **Streamlit app (primary):** `streamlit run main.py` — multipage with navigation sidebar + login
- **Flask API (secondary):** `python flask_app.py` — REST API on `127.0.0.1:5000`

## Repo state
- **No tests, no linter, no typechecker** — zero config for any
- `.env` committed with live secrets (`GITHUB_TOKEN`, `LANGSMITH_API_KEY`) — **rotate them**
- `.gitignore` covers `.venv`, `__pycache__`, `.env`
- Python 3.11

## Security
- `security.py` — input sanitization, prompt injection detection (~90 patterns), rate limiting (chat 20/min, login 5/min), LLM concurrency (max 3), audit logging to `logs/security.log`
- `flask_app.py` — HTTP Basic Auth + rate limiting + security headers (CSP, HSTS, X-Frame-Options)

## Architecture
- `main.py` — Streamlit entry, auth (user/pass from `.env`, 30min timeout), sidebar with mascot "Uni" + radio + session timer
- `app.py` — Home page with hero, offers, categories
- `chat_engine.py` — RAG engine: FAISS vector store + OpenAI `text-embedding-3-small` + `gpt-4o-mini` via GitHub Azure AI endpoint. Uses `GITHUB_TOKEN` as API key. Streaming + security pipeline.
- `flask_app.py` — Flask REST API wrapper around `chat_engine.consultar()`
- `Doc_Unimarc.py` — hardcoded product list (~50 items), parsed by `utils.py`
- `utils.py` — product parsing, category classification, random offer generation, radio station URLs (5 Chilean stations via streamtheworld), CSS injection from `static/styles.css`
- `pages/01_Productos.py` — product catalog with search + category filter
- `pages/02_Ofertas.py` — random simulated offers (random.sample + random discount)
- `pages/03_Chat_IA.py` — chat UI calling `chat_engine.consultar()`
- `pages/04_Radio.py` — radio station selector (audio plays from `main.py` sidebar)
- `pages/05_Lista_Inteligente.py` — smart shopping list with quantities and subtotals

## Production deployment (20-100 concurrent users)
- **Nginx reverse proxy** (`nginx.conf`) — balancea con `ip_hash` para sticky sessions, soporta WebSocket
- **Escalado horizontal** con Docker Compose: `docker compose up --scale ev1ia=5 -d`
- **Healthcheck** en Dockerfile (HTTP GET a `/` cada 30s)
- **Config Streamlit** en `.streamlit/config.toml`:
  - `maxMessageSize = 200`, `enableCORS = false`, `enableXsrfProtection = false`
- **Entrada:** Nginx en puerto `:80` (público) → upstream `ev1ia:8080`
- **Límite real:** ~10 usuarios por contenedor Streamlit. Con `--scale ev1ia=10` llegas a ~100

## API dependencies
- Requires `GITHUB_TOKEN` in `.env` (GitHub token with Azure AI access)
- OpenAI models served via `https://models.inference.ai.azure.com` (not direct OpenAI)
- LangSmith tracing enabled via `LANGSMITH_API_KEY`

## Key quirks
- `utils.get_ofertas()` uses `random.sample` — results change every rerun
- Radio audio only works from `main.py` sidebar (persists across pages), not standalone
- Product data is static — no database, no real inventory integration
- No real offer/pricing logic — discounts are random
