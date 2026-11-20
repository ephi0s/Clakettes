"""Small HTTP helpers shared by routers and middleware."""

from fastapi import Request


def client_ip(request: Request) -> str:
    """Return the client address, or ``"unknown"`` when the request has no peer."""
    return request.client.host if request.client else "unknown"
