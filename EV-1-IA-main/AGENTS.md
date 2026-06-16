# EV-1-IA — Unimarc AI Assistant

## Entrypoints
- **Streamlit app (primary):** `streamlit run main.py` — multipage with navigation sidebar
- **Flask app (secondary, conflicting branch):** `python app.py` — serves `templates/index.html` at `localhost:5000`

## Merge conflicts to resolve
- `app.py` — Streamlit (HEAD) vs Flask (incoming) versions conflicted
- `requirements.txt` — headers/======/footers markers present (delete lines 112-118)

## Repo state
- **No tests, no linter, no typechecker** — zero config for any
- **Broken Docker CMD:** `Dockerfile` line 23 runs `python Unimarc.py` (file doesn't exist)
- `.env` committed with live secrets (`GITHUB_TOKEN`, `LANGSMITH_API_KEY`) — rotate them
- `.gitignore` covers `.venv`, `__pycache__`, `.env`
- Python 3.11 (from `__pycache__/`), venv at `.venv/`

## Architecture
- `main.py` — Streamlit entry, `st.navigation()` routes to 5 pages in `pages/`
- `chat_engine.py` — RAG engine: FAISS vector store + OpenAI `text-embedding-3-small` + `gpt-4o-mini` via GitHub Azure AI endpoint (`OPENAI_BASE_URL` in `.env`). Uses `GITHUB_TOKEN` as API key. Streaming responses.
- `Doc_Unimarc.py` — hardcoded product list (~50 items), parsed by `utils.py`
- `utils.py` — product parsing, category classification, random offer generation, radio station URLs (5 Chilean stations via streamtheworld), CSS injection
- `pages/01_Productos.py` — product catalog with search + category filter
- `pages/02_Ofertas.py` — random simulated offers (random.sample + random discount)
- `pages/03_Chat_IA.py` — chat UI calling `chat_engine.consultar()`
- `pages/04_Radio.py` — radio station selector (audio plays from `main.py` sidebar)
- `pages/05_Lista_Inteligente.py` — smart shopping list with quantities and subtotals

## API dependencies
- Requires `GITHUB_TOKEN` in `.env` (GitHub token with Azure AI access)
- OpenAI models served via `https://models.inference.ai.azure.com` (not direct OpenAI)
- LangSmith tracing enabled via `LANGSMITH_API_KEY`

## Key quirks
- `utils.get_ofertas()` uses `random.sample` — results change every rerun
- Radio audio only works from `main.py` sidebar (persists across pages), not standalone
- Product data is static — no database, no real inventory integration
- No real offer/pricing logic — discounts are random
