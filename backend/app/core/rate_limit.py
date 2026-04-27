"""[SHIM DE COMPATIBILIDADE] app.core.rate_limit

Re-exporta middleware canônico de `app.shared.core.rate_limit` enquanto o
hub é consolidado em `app/shared/`.
"""

from app.shared.core.rate_limit import RateLimitMiddleware, RateLimitRule, SlidingWindowLimiter

__all__ = ["RateLimitMiddleware", "RateLimitRule", "SlidingWindowLimiter"]
