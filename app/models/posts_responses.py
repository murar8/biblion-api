from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel
from pydantic.generics import GenericModel

from app.models.database import Post

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
    creatorId: UUID
    name: Optional[str]
    language: Optional[str]
    content: str
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(post: Post) -> PostResponse:
        return PostResponse(**post.dict(), creatorId=post.creator.ref.id)
