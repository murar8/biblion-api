from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    data: list[T]
    token: Optional[str] = Field(
        default=None,
        description="Continuation token to define the starting offset of the query.",
    )


class PostResponse(BaseModel):
    id: str
    ownerId: Optional[str]
    name: Optional[str]
    language: Optional[str]
    content: str
    createdAt: str
    updatedAt: str

    @staticmethod
    def from_mongo(post: dict[str, any]) -> PostResponse:
        post["id"] = post.pop("_id")
        post["createdAt"] = post.pop("createdAt").isoformat()
        post["updatedAt"] = post.pop("updatedAt").isoformat()
        return PostResponse(**post)
