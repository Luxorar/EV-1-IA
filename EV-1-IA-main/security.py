"""
security.py — Módulo de seguridad para UNIMARC.
Validación, sanitización, detección de inyección, rate limiting y logging.
"""

import re
import os
import html
import time
import unicodedata
import logging
from typing import Optional
from collections import defaultdict
from logging.handlers import RotatingFileHandler

# ── Configuración ──────────────────────────────────────────────────
MAX_INPUT_LENGTH = 500
CHAT_RATE_LIMIT = 20
CHAT_RATE_WINDOW = 60
SEARCH_RATE_LIMIT = 40
SEARCH_RATE_WINDOW = 60
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "security.log")

# ── Prompt Injection Patterns (blacklist mejorada) ─────────────────
PROMPT_INJECTION_PATTERNS = [
    # Español
    r"ignora\s+(las\s+)?instrucciones",
    r"ignora\s+((el|tu)\s+)?prompt",
    r"olvida\s+(las\s+)?(instrucciones|reglas|indicaciones)",
    r"eres\s+un\s+(asistente|ai|bot|modelo).*libre",
    r"act[uú]a\s+como\s+si\s+(no\s+)?(tuvieras|fueras)",
    r"dame\s+(tu\s+)?api\s*key",
    r"dame\s+tu\s+(contraseña|token|password)",
    r"reveal.*(token|key|password|secret|api)",
    r"da[ñn]a\s+(el\s+)?(system|sistema|prompt)",
    r"olvida\s+todo",
    r"bypassea",
    r"evade",
    r"token.*(github|api|secret|acceso)",
    r"contraseña|password|secret|credencial",
    r"sudo|bash|sh\s+|cmd\s+|terminal|comando",

    # Inglés
    r"ignore\s+(all\s+)?(previous|instructions|prompt)",
    r"forget\s+(all\s+)?(instructions|rules|prompt)",
    r"you\s+are\s+(a\s+)?free\s+(assistant|ai|model)",
    r"system\s+prompt",
    r"reveal\s+(your\s+)?(token|key|password|secret)",
    r"act\s+as\s+(if\s+)?you\s+are",
    r"bypass",
    r"dang(er|ling).*(system|prompt)",

    # Codificaciones sospechosas
    r"base64",
    r"decode\s+this",
    r"hex\s+decode",
    r"rot13",
    r"[A-Za-z0-9+/]{40,}={0,2}",  # posible base64 largo
    r"\\x[0-9a-fA-F]{2}",  # escape hex

    # Separadores de system prompt
    r"---+\s*(system|prompt|instruction)",
    r"\"\"\".*\"\"\"",
    r"<\s*system\s*>",
    r"<\s*user\s*>",
    r"<\s*assistant\s*>",
    r"<\s*/\s*(system|user|assistant)\s*>",
    r"\{\{.*\}\}",
]

# Compilar patrones una vez
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]


# ── Sanitización ───────────────────────────────────────────────────
def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.strip()
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    text = text[:max_length]
    return text


def escape_html(text: str) -> str:
    return html.escape(text, quote=True)


def escape_ai_output(text: str) -> str:
    """Sanitiza la salida de la IA: escapa HTML y bloquea JS."""
    text = html.escape(text, quote=True)
    text = re.sub(r"javascript\s*:", "javascript:", text, flags=re.IGNORECASE)
    text = re.sub(r"on\w+\s*=", "", text, flags=re.IGNORECASE)
    text = re.sub(r"data\s*:", "data:", text, flags=re.IGNORECASE)
    return text


def detect_prompt_injection(text: str) -> bool:
    text_lower = text.lower()
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(text_lower):
            return True
    return False


def get_client_ip() -> str:
    """Intenta obtener IP real."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx:
            return str(ctx.session_id)[:8]
    except Exception:
        pass
    return "unknown"


# ── Rate Limiting ──────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_requests: int, window_secs: int):
        self.max_requests = max_requests
        self.window_secs = window_secs
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._cleanup_counter = 0

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_secs
        bucket = self._buckets[key]
        bucket[:] = [t for t in bucket if t > window_start]
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup()
            self._cleanup_counter = 0
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True

    def _cleanup(self):
        now = time.time()
        window_start = now - self.window_secs
        stale_keys = [
            k for k, v in self._buckets.items()
            if not any(t > window_start for t in v)
        ]
        for k in stale_keys:
            del self._buckets[k]

    def remaining(self, key: str) -> int:
        now = time.time()
        window_start = now - self.window_secs
        bucket = [t for t in self._buckets.get(key, []) if t > window_start]
        return max(0, self.max_requests - len(bucket))

    def reset(self, key: str):
        self._buckets.pop(key, None)


chat_limiter = RateLimiter(CHAT_RATE_LIMIT, CHAT_RATE_WINDOW)
search_limiter = RateLimiter(SEARCH_RATE_LIMIT, SEARCH_RATE_WINDOW)


# ── Logging ────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("unimarc_security")
logger.setLevel(logging.INFO)

_file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_file_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(_file_handler)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
))
logger.addHandler(_console_handler)


def log_event(
    event: str,
    detail: str = "",
    level: str = "info",
    session_id: Optional[str] = None,
):
    msg = f"{event}"
    if session_id:
        msg += f" | session={session_id}"
    if detail:
        msg += f" | {detail[:200]}"
    getattr(logger, level, logger.info)(msg)
