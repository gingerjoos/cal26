"""Custom Starlette middleware."""

from __future__ import annotations

from typing import Awaitable, Callable
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .logging import reset_request_id, set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request/response carries a stable request ID."""

    header_name = "X-Request-ID"

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(self.header_name, str(uuid4()))
        token = set_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            reset_request_id(token)
        response.headers[self.header_name] = request_id
        return response
