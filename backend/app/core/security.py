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


def hash_senha(senha: str) -> str:
    """
    Criptografa uma senha usando bcrypt.

    Args:
        senha: Senha em texto plano

    Returns:
        Hash seguro da senha
    """
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_stored: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.

    Args:
        senha: Senha em texto plano
        hash_stored: Hash armazenado no banco

    Returns:
        True se válida, False caso contrário
    """
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
    """
    Cria um JWT token com payload customizado.

    Args:
        data: Payload do token (ex: {"sub": "user@email.com"})
        secret_key: Chave secreta para assinar o token
        expires_delta: Tempo de expiração customizado (padrão: 24h)

    Returns:
        Token JWT codificado

    Example:
        >>> token = criar_token({"sub": "user@email.com"}, "secret-key")
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Erro ao criar token JWT: {str(e)}")
        raise


def decodificar_token(
    token: str,
    secret_key: str
) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um JWT token.

    Args:
        token: Token JWT para decodificar
        secret_key: Chave secreta usada para assinar

    Returns:
        Dict com payload do token, ou None se inválido/expirado

    Example:
        >>> payload = decodificar_token(token, "secret-key")
        >>> if payload:
        ...     email = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.warning(f"Token JWT inválido: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao decodificar token: {str(e)}")
        return None


def extrair_email_do_token(
    token: str,
    secret_key: str
) -> Optional[str]:
    """
    Extrai o email (subject) do payload de um token JWT.

    Args:
        token: Token JWT
        secret_key: Chave secreta

    Returns:
        Email extraído, ou None se inválido

    Example:
        >>> email = extrair_email_do_token(token, "secret-key")
    """
    payload = decodificar_token(token, secret_key)
    if payload is None:
        return None

    email = payload.get("sub")
    if not email:
        logger.warning("Token JWT não contém 'sub' (email)")
        return None

    return email