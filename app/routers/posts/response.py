from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    data: list[T]
    hasMore: bool
    totalCount: int

    @classmethod
    def __concrete_name__(cls: type[Any], params: tuple[type[Any], ...]) -> str:
        """
        Make the concrete class name look nicer.
        See https://pydantic-docs.helpmanual.io/usage/models/#generic-models
        """
        return f"Paginated{params[0].__name__}"


class PostResponse(BaseModel):
    id: str
    ownerId: uuid.UUID
    name: Optional[str]
    language: Optional[str]
    content: str
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(post: dict[str, any]) -> PostResponse:
        post["id"] = post.pop("_id")
        return PostResponse(**post)
