from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.database import User


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    verified: bool
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(user: User) -> UserResponse:
        return UserResponse(**user.dict())
