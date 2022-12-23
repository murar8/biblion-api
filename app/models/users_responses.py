from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    verified: bool
    createdAt: datetime
    updatedAt: datetime

    @staticmethod
    def from_mongo(user: dict[str, any]) -> UserResponse:
        user["id"] = user.pop("_id")
        user["createdAt"] = user.pop("createdAt").isoformat()
        user["updatedAt"] = user.pop("updatedAt").isoformat()
        return UserResponse(**user)
