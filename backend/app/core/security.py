"""[SHIM DE COMPATIBILIDADE] app.core.security

Re-exporta funções canônicas de `app.shared.core.security` enquanto o hub
é consolidado em `app/shared/`.
"""

from app.shared.core.security import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    ALGORITHM,
    criar_token,
    decodificar_token,
    extrair_email_do_token,
    hash_senha,
    verificar_senha,
)

__all__ = [
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_HOURS",
    "hash_senha",
    "verificar_senha",
    "criar_token",
    "decodificar_token",
    "extrair_email_do_token",
]
