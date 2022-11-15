import uuid
from datetime import datetime
from http import HTTPStatus

import pymongo
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from app.posts.request import CreatePostRequest, GetPostsParams, UpdatePostRequest
from app.posts.response import PaginatedResponse, PostResponse
from app.providers.auth import get_jwt
from app.providers.database import get_db
from app.util.access_token import AccessToken
from app.util.shortid import generate_shortid

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PostResponse])
async def get_posts(query: GetPostsParams = Depends(), db: Database = Depends(get_db)):
    sort_key = query.sort_key if query.sort_key != "id" else "_id"
    sort_order = pymongo.ASCENDING if query.sort_order == "asc" else pymongo.DESCENDING

    # We want the sort order to always be fully deterministic so we don't incur
    # in pagination issues.
    sort = (
        [(sort_key, sort_order)]
        if sort_key == "_id"
        else [(sort_key, sort_order), ("_id", pymongo.ASCENDING)]
    )

    find = dict()

    if query.createdAt:
        find["createdAt"] = {f"${query.created_at_cmp}": query.created_at_ts}
    if query.updatedAt:
        find["updatedAt"] = {f"${query.updated_at_cmp}": query.updated_at_ts}
    if query.ownerId:
        find["ownerId"] = {"$eq": uuid.UUID(query.ownerId)}
    if query.language:
        find["language"] = {"$eq": query.language}
    if query.token:
        find[sort_key] = {"$gt": query.token}

    cursor = db.posts.find(find)
    cursor.sort(sort)
    if query.count:
        cursor.limit(query.count)

    items = [PostResponse.from_mongo(post) async for post in cursor]
    token = items[-1].dict()[query.sort_key] if len(items) else None

    return PaginatedResponse(data=items, token=token)


@router.get("/{id}", response_model=PostResponse)
async def get_post(id: str, db: Database = Depends(get_db)):
    if post := await db.posts.find_one({"_id": id}):
        return PostResponse.from_mongo(post)
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_jwt),
    db: Database = Depends(get_db),
):
    # We use short ids to make it easy for users to share posts by id, so we
    # have to take into account the (unlikely) possibility of having two ids clashing.
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
    db: Database = Depends(get_db),
):
    ownerId = uuid.UUID(jwt.sub)

    where = {"_id": id, "ownerId": ownerId}
    update = {"$set": {**body.dict(exclude_unset=True), "updatedAt": datetime.utcnow()}}
    await db.posts.update_one(where, update)
    post = await db.posts.find_one({"_id": id})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if post["ownerId"] != ownerId:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    return PostResponse.from_mongo(post)


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    id: str,
    jwt: AccessToken = Depends(get_jwt),
    db: Database = Depends(get_db),
):
    post = await db.posts.find_one({"_id": id})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if post["ownerId"] != uuid.UUID(jwt.sub):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    await db.posts.delete_one({"_id": id})
