from datetime import datetime
from http import HTTPStatus

from motor.core import AgnosticDatabase
from fastapi import APIRouter, Depends, HTTPException


from ..request import CreatePostRequest, UpdatePostRequest
from ..response import PostResponse
from ..shortid import generate_shortid
from ..access_token import AccessToken
from ..providers.auth import get_jwt
from ..providers.database import get_db

router = APIRouter()


@router.get("/{id}", response_model=PostResponse)
async def get_post(id: str, db: AgnosticDatabase = Depends(get_db)):
    if post := await db.posts.find_one({"_id": id}):
        return PostResponse.from_mongo(post)
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_jwt),
    db: AgnosticDatabase = Depends(get_db),
):
    while True:
        id = generate_shortid()

        if await db.posts.find_one({"_id": id}):
            continue

        createdAt = datetime.utcnow()
        document = {
            "_id": id,
            "ownerId": jwt.sub,
            "createdAt": createdAt,
            "updatedAt": createdAt,
            **body.dict(),
        }
        await db.posts.insert_one(document=document)

        post = await db.posts.find_one({"_id": id})
        return PostResponse.from_mongo(post)


@router.patch("/{id}", response_model=PostResponse)
async def update_post(
    id: str,
    body: UpdatePostRequest,
    jwt: AccessToken = Depends(get_jwt),
    db: AgnosticDatabase = Depends(get_db),
):
    where = {"_id": id, "ownerId": jwt.sub}
    update = {"$set": {**body.dict(exclude_unset=True), "updatedAt": datetime.utcnow()}}
    result = await db.posts.update_one(where, update)
    post = await db.posts.find_one({"_id": id})

    if not result.matched_count:
        if post:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return PostResponse.from_mongo(post)
