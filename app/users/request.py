from typing import Optional

from pydantic import BaseModel, EmailStr, constr, root_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: constr(min_length=1)


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]


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
    password: constr(min_length=1)
