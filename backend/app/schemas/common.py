"""Shared pagination base schema and media URL type."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, HttpUrl


class PageBase(BaseModel):
    total: int
    page: int
    size: int
    pages: int


def _validate_media_url(value: str) -> str:
    if not value or value.startswith("/"):
        return value
    HttpUrl(value)
    return value


MediaUrl = Annotated[str, AfterValidator(_validate_media_url)]
