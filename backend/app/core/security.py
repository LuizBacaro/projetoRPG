"""
Security
SRP: geração e validação de tokens JWT
Lê SECRET_KEY de settings (via .env) — nunca hardcoded
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# ── Configurações ─────────────────────────────────────────────────────────────
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera hash bcrypt — trunca em 72 bytes (limite do bcrypt)."""
    return pwd_context.hash(senha[:72])


def verificar_senha(senha: str, hash_: str) -> bool:
    """Verifica senha contra o hash bcrypt armazenado."""
    return pwd_context.verify(senha[:72], hash_)


def criar_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria JWT assinado com SECRET_KEY do .env."""
    payload = data.copy()
    expire  = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> Optional[dict]:
    """Decodifica e valida JWT. Retorna None se inválido ou expirado."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None