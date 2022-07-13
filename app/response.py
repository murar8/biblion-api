from typing import Optional
from typing_extensions import Self

from pydantic import BaseModel


class PostResponse(BaseModel):
    id: str
    ownerId: Optional[str]
    name: Optional[str]
    language: Optional[str]
    content: str
    createdAt: str
    updatedAt: str

    @staticmethod
    def from_mongo(post: dict[str, any]) -> Self:
        post["id"] = post.pop("_id")
        post["createdAt"] = post.pop("createdAt").isoformat()
        post["updatedAt"] = post.pop("updatedAt").isoformat()
        return PostResponse(**post)
