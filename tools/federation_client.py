"""Lightweight Python client for Clakettes federation endpoints."""

import httpx


class FederationClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def manifest(self):
        return httpx.get(f"{self.base_url}/api/federation/manifest").json()

    def directory(self):
        return httpx.get(f"{self.base_url}/api/federation/directory").json()