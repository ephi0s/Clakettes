"""JWKS helper for validating peer node tokens (Fase 3)."""

import httpx


class JwksService:
    async def fetch(self, url: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
