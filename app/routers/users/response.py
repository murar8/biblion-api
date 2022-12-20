from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid.UUID
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
