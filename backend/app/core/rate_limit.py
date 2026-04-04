"""
rate_limit.py
Middleware de rate limiting por IP (sliding window em memória).
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import time

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


@dataclass(frozen=True)
class RateLimitRule:
    limit: int
    window_seconds: int
    scope: str


class SlidingWindowLimiter:
    """Rate limiter simples por chave usando janela deslizante."""

    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        now = time()
        cutoff = now - window_seconds

        with self._lock:
            bucket = self._buckets[key]

            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            current = len(bucket)
            if current >= limit:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                return False, retry_after, 0

            bucket.append(now)
            remaining = max(0, limit - len(bucket))
            return True, 0, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Aplica rate limiting em rotas da API com regra global e regra de login."""

    def __init__(
        self,
        app,
        api_limit_per_minute: int,
        login_limit_per_minute: int,
    ) -> None:
        super().__init__(app)
        self._limiter = SlidingWindowLimiter()
        self._api_rule = RateLimitRule(
            limit=api_limit_per_minute,
            window_seconds=60,
            scope="api",
        )
        self._login_rule = RateLimitRule(
            limit=login_limit_per_minute,
            window_seconds=60,
            scope="login",
        )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Não limita arquivos estáticos e docs.
        if not path.startswith("/api/"):
            return await call_next(request)

        rule = self._resolve_rule(request)
        client_ip = self._client_ip(request)
        key = f"{rule.scope}:{client_ip}:{request.method}:{path}"

        allowed, retry_after, remaining = self._limiter.hit(
            key=key,
            limit=rule.limit,
            window_seconds=rule.window_seconds,
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Limite de requisições excedido. Tente novamente em instantes.",
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rule.limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    def _resolve_rule(self, request: Request) -> RateLimitRule:
        if request.method == "POST" and request.url.path.endswith("/auth/login"):
            return self._login_rule
        return self._api_rule

    @staticmethod
    def _client_ip(request: Request) -> str:
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
