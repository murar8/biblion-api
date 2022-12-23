from typing import Optional
from uuid import UUID

from pydantic import BaseModel, NonNegativeInt, conint, constr

NAME_MAX_LEN = 256
LANGUAGE_MAX_LEN = 16
CONTENT_MAX_LEN = 65536
PAGE_SIZE_LIMIT = 32


class GetPostsParams(BaseModel):
    skip: Optional[NonNegativeInt] = 0
    limit: Optional[conint(ge=0, le=PAGE_SIZE_LIMIT)] = 0
    ownerId: Optional[UUID]
    language: Optional[constr(max_length=LANGUAGE_MAX_LEN)]


class CreatePostRequest(BaseModel):
    content: constr(max_length=CONTENT_MAX_LEN)
    name: Optional[constr(max_length=NAME_MAX_LEN)]
    language: Optional[constr(max_length=LANGUAGE_MAX_LEN)]
