from typing import Optional

from pydantic import BaseModel


class CreatePostRequest(BaseModel):
    content: str
    name: Optional[str]
    language: Optional[str]


class UpdatePostRequest(BaseModel):
    content: Optional[str]
    name: Optional[str]
    language: Optional[str]
