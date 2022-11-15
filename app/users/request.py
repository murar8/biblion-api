from typing import Optional

from pydantic import BaseModel, EmailStr, Field, root_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: str = Field(min_length=1)


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    password: Optional[str] = Field(min_length=1)


class LoginUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    password: str

    @root_validator()
    def validate_identifier(cls, values):
        email: str = values.get("email")
        name: str = values.get("name")

        if not email and not name:
            raise ValueError("Either user email or name must be supplied.")

        return values
