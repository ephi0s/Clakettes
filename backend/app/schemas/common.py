"""Shared pagination base schema."""

from pydantic import BaseModel


class PageBase(BaseModel):
    total: int
    page: int
    size: int
    pages: int
