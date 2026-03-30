"""Middleware para limitar tamanho de requests HTTP."""

from fastapi.responses import JSONResponse
from starlette.datastructures import Headers


class RequestTooLargeError(Exception):
    """Erro interno usado para abortar leitura de requests acima do limite."""


class RequestSizeLimitMiddleware:
    """Bloqueia requests com corpo maior que o permitido."""

    def __init__(self, app, max_request_size: int, max_json_body_size: int):
        self.app = app
        self.max_request_size = max_request_size
        self.max_json_body_size = min(max_request_size, max_json_body_size)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") in {"GET", "HEAD", "OPTIONS"}:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        content_type = headers.get("content-type", "").lower()
        limit = self.max_json_body_size if "application/json" in content_type else self.max_request_size

        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > limit:
                    response = JSONResponse(
                        status_code=413,
                        content={"detail": "Payload maior que o limite permitido"},
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass

        bytes_received = 0

        async def limited_receive():
            nonlocal bytes_received
            message = await receive()
            if message["type"] == "http.request":
                bytes_received += len(message.get("body", b""))
                if bytes_received > limit:
                    raise RequestTooLargeError()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestTooLargeError:
            response = JSONResponse(
                status_code=413,
                content={"detail": "Payload maior que o limite permitido"},
            )
            await response(scope, receive, send)