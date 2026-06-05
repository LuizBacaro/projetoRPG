"""
Armazenamento em memória de state OAuth e códigos de troca únicos (frontend ↔ API).

Adequado para instância única (Render free). Para múltiplas réplicas, migrar para Redis.
"""

from __future__ import annotations

import secrets
import time
from threading import Lock
from typing import Any, Dict, Optional

_lock = Lock()
_oauth_states: Dict[str, float] = {}
_exchange_codes: Dict[str, tuple[float, Dict[str, Any]]] = {}


def _purge(expiry_map: Dict[str, float]) -> None:
    now = time.time()
    stale = [k for k, exp in expiry_map.items() if exp <= now]
    for k in stale:
        expiry_map.pop(k, None)


def _purge_exchanges() -> None:
    now = time.time()
    stale = [k for k, (exp, _) in _exchange_codes.items() if exp <= now]
    for k in stale:
        _exchange_codes.pop(k, None)


def criar_oauth_state(ttl_seconds: int = 600) -> str:
    state = secrets.token_urlsafe(32)
    with _lock:
        _purge(_oauth_states)
        _oauth_states[state] = time.time() + ttl_seconds
    return state


def consumir_oauth_state(state: str) -> bool:
    if not state:
        return False
    with _lock:
        _purge(_oauth_states)
        exp = _oauth_states.pop(state, None)
    return exp is not None and exp > time.time()


def criar_exchange_code(payload: Dict[str, Any], ttl_seconds: int) -> str:
    code = secrets.token_urlsafe(32)
    with _lock:
        _purge_exchanges()
        _exchange_codes[code] = (time.time() + ttl_seconds, payload)
    return code


def consumir_exchange_code(code: str) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    with _lock:
        _purge_exchanges()
        entry = _exchange_codes.pop(code, None)
    if entry is None:
        return None
    exp, payload = entry
    if exp <= time.time():
        return None
    return payload
