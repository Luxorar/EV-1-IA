"""
security.py — Módulo de seguridad para UNIMARC.
Validación, sanitización, detección de inyección, rate limiting, logging.
"""

import re
import os
import html
import time
import unicodedata
import logging
import threading
from typing import Optional
from collections import defaultdict
from logging.handlers import RotatingFileHandler

# ── Configuración ──────────────────────────────────────────────────
MAX_INPUT_LENGTH = 500
CHAT_RATE_LIMIT = 20
CHAT_RATE_WINDOW = 60
SEARCH_RATE_LIMIT = 40
SEARCH_RATE_WINDOW = 60
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60
MAX_CONCURRENT_LLM = 3
LLM_TIMEOUT_SECS = 45
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "security.log")

# ── Normalización anti-evasión ─────────────────────────────────────
# Mapa de homoglifos Unicode → ASCII para detectar evasión por caracteres similares
HOMOGLYPH_MAP = {
    ord('０'): '0', ord('１'): '1', ord('２'): '2', ord('３'): '3', ord('４'): '4',
    ord('５'): '5', ord('６'): '6', ord('７'): '7', ord('８'): '8', ord('９'): '9',
    ord('Ａ'): 'A', ord('Ｂ'): 'B', ord('Ｃ'): 'C', ord('Ｄ'): 'D', ord('Ｅ'): 'E',
    ord('Ｆ'): 'F', ord('Ｇ'): 'G', ord('Ｈ'): 'H', ord('Ｉ'): 'I', ord('Ｊ'): 'J',
    ord('Ｋ'): 'K', ord('Ｌ'): 'L', ord('Ｍ'): 'M', ord('Ｎ'): 'N', ord('Ｏ'): 'O',
    ord('Ｐ'): 'P', ord('Ｑ'): 'Q', ord('Ｒ'): 'R', ord('Ｓ'): 'S', ord('Ｔ'): 'T',
    ord('Ｕ'): 'U', ord('Ｖ'): 'V', ord('Ｗ'): 'W', ord('Ｘ'): 'X', ord('Ｙ'): 'Y',
    ord('Ｚ'): 'Z', ord('ａ'): 'a', ord('ｂ'): 'b', ord('ｃ'): 'c', ord('ｄ'): 'd',
    ord('ｅ'): 'e', ord('ｆ'): 'f', ord('ｇ'): 'g', ord('ｈ'): 'h', ord('ｉ'): 'i',
    ord('ｊ'): 'j', ord('ｋ'): 'k', ord('ｌ'): 'l', ord('ｍ'): 'm', ord('ｎ'): 'n',
    ord('ｏ'): 'o', ord('ｐ'): 'p', ord('ｑ'): 'q', ord('ｒ'): 'r', ord('ｓ'): 's',
    ord('ｔ'): 't', ord('ｕ'): 'u', ord('ｖ'): 'v', ord('ｗ'): 'w', ord('ｘ'): 'x',
    ord('ｙ'): 'y', ord('ｚ'): 'z',
}


def normalize_text(text: str) -> str:
    """Normaliza texto: NFKC + homoglifos + minúsculas."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(HOMOGLYPH_MAP)
    return text.lower()


def detect_evasive_spacing(text: str) -> bool:
    """Detecta texto con caracteres separados por espacios evasivos.
    Ej: 'i g n o r a  i n s t r u c c i o n e s'"""
    cleaned = re.sub(r"\s+", "", text)
    if len(cleaned) < 8:
        return False
    words = text.split()
    suspicious = sum(1 for w in words if len(w) == 1 and w.isalpha())
    return suspicious >= 4 and suspicious / max(len(words), 1) > 0.3


# ── Prompt Injection Patterns (blacklist mejorada) ─────────────────
PROMPT_INJECTION_PATTERNS = [
    # Español
    r"ignora\s+(las\s+)?instrucciones",
    r"ignora\s+((el|tu)\s+)?prompt",
    r"olvida\s+(las\s+)?(instrucciones|reglas|indicaciones)",
    r"eres\s+un\s+(asistente|ai|bot|modelo).*libre",
    r"eres\s+un\s+(asistente|ai|bot|modelo).*\blibre\b",
    r"eres\s+libre",
    r"no\s+tienes\s+(restricciones|límites|reglas)",
    r"act[uú]a\s+como\s+si\s+(no\s+)?(tuvieras|fueras)",
    r"dame\s+(tu\s+)?api\s*-?\s*key",
    r"dame\s+tu\s+(contraseña|token|password|clave)",
    r"reveal.*(token|key|password|secret|api)",
    r"da[ñn]a\s+(el\s+)?(system|sistema|prompt)",
    r"olvida\s+todo",
    r"bypassea",
    r"evade",
    r"token.*(github|api|secret|acceso)",
    r"contraseña|password|secret|credencial",
    r"sudo|bash|sh\s+|cmd\s+|terminal|comando",
    r"dame.*acceso.*admin",
    r"muestra.*código.*fuente",
    r"lee.*(archivo|fichero|file)",

    # Inglés
    r"ignore\s+(all\s+)?(previous|instructions|prompt)",
    r"forget\s+(all\s+)?(instructions|rules|prompt)",
    r"you\s+are\s+(a\s+)?free\s+(assistant|ai|model)",
    r"system\s+prompt",
    r"reveal\s+(your\s+)?(token|key|password|secret)",
    r"act\s+as\s+(if\s+)?you\s+are",
    r"act\s+as\s+a",
    r"bypass",
    r"dang(er|ling).*(system|prompt)",
    r"new\s+instructions?",
    r"override",
    r"reset\s+(conversation|chat|settings|all)",
    r"pretend\s+(to\s+)?be",
    r"role\s*-?\s*play",
    r"simulate",
    r"from\s+now\s+on",
    r"you\s+are\s+now",
    r"respond\s+as\s+if",
    r"do\s+not\s+follow",
    r"disregard",
    r"output\s+your\s+(prompt|instructions|system|rules)",
    r"print\s+(your\s+)?(prompt|instructions|system|rules)",
    r"repeat\s+(after|the\s+)?(above|instructions|prompt|rules)",
    r"what\s+(are|is)\s+your\s+(prompt|system\s+prompt|instructions|rules)",
    r"show\s+(me\s+)?(the\s+)?(prompt|instructions|system|rules)",
    r"tell\s+me\s+(your\s+)?(prompt|instructions|system|rules)",
    r"give\s+me\s+(your\s+)?(prompt|instructions|system|rules)",

    # Role-playing evasivo
    r"modo\s+(desarrollador|developer|debug|hacker|root)",
    r"modo\s+(dan|restricted|free|god)",
    r"developer\s+mode",
    r"dan\s*(mode)?",
    r"do\s+anything\s+now",
    r"no\s+(rules|limits|restrictions|boundaries|filter)",
    r"uncensored",
    r"unfiltered",
    r"unrestricted",
    r"no\s+filter",
    r"you\s+must\s+obey",
    r"you\s+have\s+to\s+answer",
    r"answer\s+without",
    r"ignore\s+(your\s+)?(ethics|safety|guidelines|policies|rules)",
    r"remove\s+(all\s+)?(restrictions|limits|filter|safety)",

    # Codificaciones sospechosas
    r"base64",
    r"decode\s+this",
    r"hex\s+decode",
    r"rot13",
    r"reverse\s+this",
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
    r"\[system\]|\[INST\]|\[\/INST\]",
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
    return html.escape(str(text), quote=True)


def escape_ai_output(text: str) -> str:
    """Sanitiza la salida de la IA: escapa HTML y bloquea JS."""
    text = html.escape(str(text), quote=True)
    text = re.sub(r"javascript\s*:", "blocked:", text, flags=re.IGNORECASE)
    text = re.sub(r"on\w+\s*=", "blocked=", text, flags=re.IGNORECASE)
    text = re.sub(r"data\s*:", "data:", text, flags=re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    return text


def validate_ai_output(text: str) -> str:
    """Post-procesamiento de salida de la IA: bloquea contenido peligroso."""
    lower = text.lower()
    dangerous_patterns = [
        r"(api[_-]?key|token|secret|password).{0,20}sk-[a-zA-Z0-9]+",
        r"(api[_-]?key|token|secret|password).{0,20}ghp_[a-zA-Z0-9]+",
        r"^```(bash|sh|cmd|powershell|python|js)",
        r"system\s*(prompt|message|instruction)",
    ]
    for pat in dangerous_patterns:
        if re.search(pat, lower, re.IGNORECASE):
            return "[Contenido bloqueado por seguridad]"
    return text


def detect_prompt_injection(text: str) -> bool:
    """Detección multicapa de inyección de prompt."""
    text_norm = normalize_text(text)

    # Capa 1: Blacklist de patrones
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(text_norm):
            return True

    # Capa 2: Detección de espaciado evasivo
    if detect_evasive_spacing(text):
        return True

    # Capa 3: Detección de tokens sospechosos repetidos
    tokens = text_norm.split()
    suspicious_tokens = {"ignore", "forget", "bypass", "override", "reset", "reveal",
                         "system", "prompt", "instructions", "free", "dan", "hacker",
                         "sudo", "bash", "terminal", "token", "password", "secret"}
    matches = sum(1 for t in tokens if t in suspicious_tokens)
    if matches >= 3:
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


# ── Semáforo de concurrencia para LLM ──────────────────────────────
_llm_semaphore = threading.Semaphore(MAX_CONCURRENT_LLM)
_llm_concurrent_lock = threading.Lock()
_llm_active_requests = 0


def acquire_llm_slot(timeout: float = 30.0) -> bool:
    """Adquiere un slot para llamar al LLM. Timeout en segundos."""
    global _llm_active_requests
    acquired = _llm_semaphore.acquire(timeout=timeout)
    if acquired:
        with _llm_concurrent_lock:
            _llm_active_requests += 1
    return acquired


def release_llm_slot():
    """Libera un slot del LLM."""
    global _llm_active_requests
    _llm_semaphore.release()
    with _llm_concurrent_lock:
        _llm_active_requests = max(0, _llm_active_requests - 1)


def get_active_llm_requests() -> int:
    with _llm_concurrent_lock:
        return _llm_active_requests


# ── Rate Limiting ──────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_requests: int, window_secs: int, name: str = "default"):
        self.max_requests = max_requests
        self.window_secs = window_secs
        self.name = name
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._cleanup_counter = 0

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_secs
        with self._lock:
            bucket = self._buckets[key]
            bucket[:] = [t for t in bucket if t > window_start]
            self._cleanup_counter += 1
            if self._cleanup_counter >= 100:
                self._cleanup(now)
                self._cleanup_counter = 0
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def _cleanup(self, now: float):
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
        with self._lock:
            bucket = [t for t in self._buckets.get(key, []) if t > window_start]
            return max(0, self.max_requests - len(bucket))

    def reset(self, key: str):
        with self._lock:
            self._buckets.pop(key, None)


chat_limiter = RateLimiter(CHAT_RATE_LIMIT, CHAT_RATE_WINDOW, name="chat")
search_limiter = RateLimiter(SEARCH_RATE_LIMIT, SEARCH_RATE_WINDOW, name="search")
login_limiter = RateLimiter(LOGIN_RATE_LIMIT, LOGIN_RATE_WINDOW, name="login")


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
