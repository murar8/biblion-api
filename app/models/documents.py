from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import EmailStr, Field
from pymongo import IndexModel


class UserDocument(Document):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    passwordHash: bytes
    passwordUpdatedAt: Optional[datetime]
    name: Optional[str]
    verified: Optional[bool]

    verificationCode: Optional[UUID]
    verificationCodeIat: Optional[datetime]

    resetCode: Optional[UUID]
    resetCodeIat: Optional[datetime]

    createdAt: datetime
    updatedAt: datetime

    class Settings:
        use_revision = True
        name = "users"
        indexes = [
            IndexModel(
                "email",
                name="unique_email",
                unique=True,
            ),
            IndexModel(
                "name",
                name="unique_name",
                unique=True,
                partialFilterExpression={"name": {"$type": "string"}},
            ),
        ]


class PostDocument(Document):
    id: str
    content: str
    name: Optional[str]
    language: Optional[str]

    createdAt: datetime
    updatedAt: datetime

    creator: Link[UserDocument]

    class Settings:
        use_revision = True
        name = "posts"
