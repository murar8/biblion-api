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
async def get_posts(
    query: GetPostsParams = Depends(), database: Database = Depends(get_db)
):
    sort_key = query.sort_key if query.sort_key != "id" else "_id"
    sort_order = pymongo.ASCENDING if query.sort_order == "asc" else pymongo.DESCENDING

    # We want the sort order to always be fully deterministic so we don't incur
    # in pagination issues.
    sort = (
        [(sort_key, sort_order)]
        if sort_key == "_id"
        else [(sort_key, sort_order), ("_id", pymongo.ASCENDING)]
    )

    find = {}

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

    cursor = database.posts.find(find)
    cursor.sort(sort)
    if query.count:
        cursor.limit(query.count)

    items = [PostResponse.from_mongo(post) async for post in cursor]
    token = items[-1].dict()[query.sort_key] if len(items) else None

    return PaginatedResponse(data=items, token=token)


@router.get("/{uid}", response_model=PostResponse)
async def get_post(uid: str, database: Database = Depends(get_db)):
    post = await database.posts.find_one({"_id": uid})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return PostResponse.from_mongo(post)


@router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_jwt),
    database: Database = Depends(get_db),
):
    # We use short ids to make it easy for users to share posts by id, so we
    # have to take into account the (unlikely) possibility of having two ids clashing.
    while True:
        uid = generate_shortid()

        if await database.posts.find_one({"_id": uid}):
            continue

        created_at = datetime.utcnow()
        document = {
            "_id": uid,
            "ownerId": jwt.sub,
            "createdAt": created_at,
            "updatedAt": created_at,
            **body.dict(),
        }
        await database.posts.insert_one(document=document)

        post = await database.posts.find_one({"_id": uid})
        return PostResponse.from_mongo(post)


@router.patch("/{uid}", response_model=PostResponse)
async def update_post(
    uid: str,
    body: UpdatePostRequest,
    jwt: AccessToken = Depends(get_jwt),
    database: Database = Depends(get_db),
):
    owner_id = uuid.UUID(jwt.sub)

    where = {"_id": uid, "ownerId": owner_id}
    update = {"$set": {**body.dict(exclude_unset=True), "updatedAt": datetime.utcnow()}}
    await database.posts.update_one(where, update)
    post = await database.posts.find_one({"_id": uid})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if post["ownerId"] != owner_id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    return PostResponse.from_mongo(post)


@router.delete("/{uid}", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    uid: str,
    jwt: AccessToken = Depends(get_jwt),
    database: Database = Depends(get_db),
):
    post = await database.posts.find_one({"_id": uid})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if post["ownerId"] != uuid.UUID(jwt.sub):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    await database.posts.delete_one({"_id": uid})
