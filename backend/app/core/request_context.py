"""Contexte partagé entre la middleware et le code métier (ex. IP client
pour le journal d'audit), pour éviter de faire transiter la valeur à travers
toutes les signatures de fonctions intermédiaires."""

from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.rate_limit import client_ip

_client_ip: ContextVar[str | None] = ContextVar("client_ip", default=None)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _client_ip.set(client_ip(request))
        return await call_next(request)


def current_client_ip() -> str | None:
    return _client_ip.get()
