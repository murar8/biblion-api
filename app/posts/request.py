from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, root_validator, validator


class GetPostsParams(BaseModel):
    token: Optional[Any] = Field(default=None)
    count: Optional[int] = Field(default=None, gt=0)
    sort: str = Field(default="id:asc")
    createdAt: Optional[str] = Field(default=None)
    updatedAt: Optional[str] = Field(default=None)
    ownerId: Optional[str] = Field(default=None, min_length=1)
    language: Optional[str] = Field(default=None, min_length=1)

    @property
    def sort_key(self):
        return self.sort.split(":", 1)[0]

    @property
    def sort_order(self):
        return self.sort.split(":", 1)[1]

    @property
    def created_at_cmp(self):
        return self.createdAt.split(":", 1)[0]

    @property
    def created_at_ts(self):
        ts = self.createdAt.split(":", 1)[1]
        return datetime.fromisoformat(ts)

    @property
    def updated_at_cmp(self):
        return self.updatedAt.split(":", 1)[0]

    @property
    def updated_at_ts(self):
        ts = self.updatedAt.split(":", 1)[1]
        return datetime.fromisoformat(ts)

    @validator("sort")
    def validate_sort(cls, sort):
        if ":" not in sort:
            raise ValueError(f"Invalid sort param: '{sort}'")

        [key, order] = sort.split(":", 1)

        if key not in ["id", "name", "createdAt", "updatedAt"]:
            raise ValueError(f"Invalid sort key: '{key}'")

        if order not in ["asc", "desc"]:
            raise ValueError(f"Invalid sort order: '{order}'")

        return sort

    @root_validator()
    def validate_timestamps(cls, values):
        for timestamp in ["createdAt", "updatedAt"]:
            value = values.get(timestamp)

            if not value:
                continue

            if ":" not in value:
                raise ValueError(f"Invalid {timestamp} filter: '{timestamp}'")

            [comparator, date] = value.split(":", 1)

            if comparator not in ["lt", "lte", "eq", "gte", "gt"]:
                raise ValueError(f"Invalid {timestamp} comparator: '{comparator}'")

            try:
                datetime.fromisoformat(date)
            except:
                raise ValueError(f"Invalid {timestamp} date: '{date}'")

        return values

    @root_validator()
    def validate_token(cls, values):
        token = values.get("token")

        sort = values.get("sort")
        sort_key = sort.split(":", 1)[0] if sort else "id"

        if not token:
            return values

        if sort_key in ["createdAt", "updatedAt"]:
            try:
                values["token"] = datetime.fromisoformat(token)
            except:
                raise ValueError("Continuation token must be an ISO8601 date string.")

        if sort_key in ["id", "name"]:
            if not isinstance(token, str) or not len(token):
                raise ValueError(f"Continuation token must be a non-empty string.")

        return values


class CreatePostRequest(BaseModel):
    content: str
    name: Optional[str]
    language: Optional[str]


class UpdatePostRequest(BaseModel):
    content: Optional[str]
    name: Optional[str]
    language: Optional[str]
