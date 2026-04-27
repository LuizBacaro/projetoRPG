"""[SHIM DE COMPATIBILIDADE] app.shared.core.security_audit

Re-exporta helpers canônicos de `app.shared.core.security_audit` enquanto o
hub é consolidado em `app/shared/`.
"""

from app.shared.core.security_audit import get_client_ip, log_security_event

__all__ = ["get_client_ip", "log_security_event"]
