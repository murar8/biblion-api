from typing import Optional

from pydantic import BaseModel, EmailStr, constr, root_validator

NAME_MAX_LEN = 32
PASSWORD_MAX_LEN = 256


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: Optional[constr(min_length=1, max_length=NAME_MAX_LEN)]
    password: constr(min_length=1, max_length=PASSWORD_MAX_LEN)


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[constr(max_length=NAME_MAX_LEN)]


class LoginUserRequest(BaseModel):
    email: Optional[EmailStr]
    name: Optional[constr(min_length=1, max_length=NAME_MAX_LEN)]
    password: constr(min_length=1, max_length=PASSWORD_MAX_LEN)

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
