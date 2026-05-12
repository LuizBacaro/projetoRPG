"""Helpers para logging estruturado de eventos de segurança."""

import logging
from typing import Any, Optional

from starlette.requests import Request

security_logger = logging.getLogger("app.security")


def get_client_ip(request: Optional[Request]) -> str:
    """Extrai o IP do cliente priorizando headers de proxy reverso."""
    if request is None:
        return "unknown"

    cf_connecting_ip = request.headers.get("cf-connecting-ip")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def log_security_event(
    event: str,
    outcome: str,
    *,
    request: Optional[Request] = None,
    user_email: Optional[str] = None,
    actor_email: Optional[str] = None,
    target: Optional[str] = None,
    reason: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    level: int = logging.INFO,
) -> None:
    """Emite uma linha de log estruturada para eventos de segurança."""
    client_ip = get_client_ip(request)
    parts = [
        f"event={event}",
        f"outcome={outcome}",
        f"ip={client_ip}",
    ]

    if user_email:
        parts.append(f"user={user_email}")
    if actor_email:
        parts.append(f"actor={actor_email}")
    if target:
        parts.append(f"target={target}")
    if reason:
        parts.append(f"reason={reason}")
    if details:
        for key in sorted(details):
            value = details[key]
            parts.append(f"{key}={value}")

    security_logger.log(level, " ".join(parts))
