from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, NonNegativeInt, conint, constr, root_validator

POST_NAME_MAX_LEN = 256
POST_LANGUAGE_MAX_LEN = 16
POST_CONTENT_MAX_LEN = 65536

GET_POSTS_PAGE_SIZE_LIMIT = 32

USER_NAME_MAX_LEN = 32
USER_PASSWORD_MIN_LEN = 4
USER_PASSWORD_MAX_LEN = 256


class GetPostsParams(BaseModel):
    skip: Optional[NonNegativeInt] = 0
    limit: Optional[conint(ge=0, le=GET_POSTS_PAGE_SIZE_LIMIT)] = 0
    creatorId: Optional[UUID]
    language: Optional[constr(max_length=POST_LANGUAGE_MAX_LEN)]


class CreatePostRequest(BaseModel):
    content: constr(max_length=POST_CONTENT_MAX_LEN)
    name: Optional[constr(max_length=POST_NAME_MAX_LEN)]
    language: Optional[constr(max_length=POST_LANGUAGE_MAX_LEN)]


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: Optional[constr(min_length=1, max_length=USER_NAME_MAX_LEN)]
    password: constr(min_length=USER_PASSWORD_MIN_LEN, max_length=USER_PASSWORD_MAX_LEN)


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[constr(max_length=USER_NAME_MAX_LEN)]


class LoginUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    password: str

    @root_validator()
    @classmethod
    def validate_identifier(cls, values):
        email: str = values.get("email")
        name: str = values.get("name")

        if not email and not name:
            raise ValueError("Either user email or name must be supplied.")

        return values


class ResetPasswordRequest(BaseModel):
    password: constr(min_length=USER_PASSWORD_MIN_LEN, max_length=USER_PASSWORD_MAX_LEN)
