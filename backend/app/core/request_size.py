"""[SHIM DE COMPATIBILIDADE] app.shared.core.request_size

Re-exporta middleware canônico de `app.shared.core.request_size` enquanto o
hub é consolidado em `app/shared/`.
"""

from app.shared.core.request_size import RequestSizeLimitMiddleware, RequestTooLargeError

__all__ = ["RequestSizeLimitMiddleware", "RequestTooLargeError"]
