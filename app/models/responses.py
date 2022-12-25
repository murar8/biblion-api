from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing_extensions import Self

from app.models.documents import PostDocument, UserDocument

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


class GetPostsItem(BaseModel):
    id: str
    name: Optional[str]
    language: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(post: PostDocument) -> Self:
        return GetPostsItem(**post.dict())


GetPostsResponse = PaginatedResponse[GetPostsItem]


class PostResponse(BaseModel):
    id: str
    creatorId: UUID
    name: Optional[str]
    language: Optional[str]
    content: str
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(post: PostDocument) -> Self:
        return PostResponse(**post.dict(), creatorId=post.creator.ref.id)


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    verified: bool
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(user: UserDocument) -> Self:
        return UserResponse(**user.dict())
