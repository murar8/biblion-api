from typing import Optional
from typing_extensions import Self

from pydantic import BaseModel


class PostResponse(BaseModel):
    id: str
    ownerId: str
    content: str
    name: Optional[str]
    language: Optional[str]

    @staticmethod
    def from_mongo(post: dict[str, any]) -> Self:
        post["id"] = post.pop("_id")
        return PostResponse(**post)
