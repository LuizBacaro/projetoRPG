"""
security.py
SRP: Funções de criptografia, JWT e verificação de autenticação
SOLID: Single Responsibility — segurança centralizada
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# ── Configuração de hash de senhas ────────────────────────────────────────
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ── Algoritmo JWT ────────────────────────────────────────────────────────────
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_senha(senha: str) -> str:
    """Criptografa uma senha usando bcrypt."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_stored: str) -> bool:
    """Verifica se uma senha corresponde ao hash armazenado."""
    try:
        return pwd_context.verify(senha, hash_stored)
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {str(e)}")
        return False


def criar_token(
    data: Dict[str, Any],
    secret_key: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um JWT token com payload customizado."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Erro ao criar token JWT: {str(e)}")
        raise


def decodificar_token(
    token: str,
    secret_key: str
) -> Optional[Dict[str, Any]]:
    """Decodifica e valida um JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token JWT inválido ou expirado: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao decodificar token: {str(e)}")
        return None


def extrair_email_do_token(
    token: str,
    secret_key: str
) -> Optional[str]:
    """Extrai o email (subject) do payload de um token JWT."""
    payload = decodificar_token(token, secret_key)
    if payload is None:
        return None

    email = payload.get("sub")
    if not email:
        logger.warning("Token JWT não contém 'sub' (email)")
        return None

    return email