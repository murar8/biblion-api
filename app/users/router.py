import uuid
from datetime import datetime
from http import HTTPStatus

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.database import Database

from app.providers.auth import get_jwt
from app.providers.config import get_config
from app.providers.database import get_db
from app.users.request import CreateUserRequest, LoginUserRequest, UpdateUserRequest
from app.users.response import UserResponse
from app.util.access_token import AccessToken
from app.util.config import Config

router = APIRouter()


@router.get("/{uid}", response_model=UserResponse)
async def get_user(uid: str, database: Database = Depends(get_db)):
    user = await database.users.find_one({"_id": uuid.UUID(uid)})

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return UserResponse.from_mongo(user)


@router.post("/", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(
    body: CreateUserRequest,
    database: Database = Depends(get_db),
):
    user = await database.users.find_one(
        {"$or": [{"email": body.email}, {"name": body.name}]}
    )

    if user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT)

    created_at = datetime.utcnow()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(body.password.encode(), salt)

    document = {
        "_id": uuid.uuid4(),
        "email": body.email,
        "name": body.name,
        "password_hash": password_hash,
        "verified": False,
        "createdAt": created_at,
        "updatedAt": created_at,
    }

    res = await database.users.insert_one(document=document)
    user = await database.users.find_one({"_id": res.inserted_id})

    return UserResponse.from_mongo(user)


@router.patch("/{uid}", response_model=UserResponse)
async def update_user(
    uid: str,
    body: UpdateUserRequest,
    jwt: AccessToken = Depends(get_jwt),
    database: Database = Depends(get_db),
):
    if uid != jwt.sub:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    document = {"updatedAt": datetime.utcnow()}

    if body.name:
        document["name"] = body.name

    if body.email:
        document["email"] = body.email

    if body.password:
        salt = bcrypt.gensalt()
        document["password_hash"] = bcrypt.hashpw(body.password.encode(), salt)

    result = await database.users.update_one(
        {"_id": uuid.UUID(uid)}, {"$set": document}
    )

    if not result.matched_count:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    user = await database.users.find_one({"_id": uuid.UUID(uid)})
    return UserResponse.from_mongo(user)


@router.post("/login", response_model=UserResponse)
async def login_user(
    body: LoginUserRequest,
    response: Response,
    database: Database = Depends(get_db),
    config: Config = Depends(get_config),
):
    user = await database.users.find_one(
        {"$or": [{"email": body.email}, {"name": body.name}]}
    )

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"]):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    response.set_cookie(
        key="access_token",
        value=AccessToken.encode(str(user["_id"]), config.jwt),
        secure=True,
        httponly=True,
        max_age=config.jwt.expiration,
    )

    return UserResponse.from_mongo(user)
