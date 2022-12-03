import uuid
from datetime import datetime
from http import HTTPStatus

import pymongo
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from app.posts.request import CreatePostRequest, GetPostsParams, UpdatePostRequest
from app.posts.response import PaginatedResponse, PostResponse
from app.providers.access_token import get_access_token
from app.providers.database import get_database
from app.util.access_token import AccessToken
from app.util.shortid import generate_shortid

router = APIRouter()


@router.get("/{uid}", response_model=PostResponse)
async def get_post(uid: str, database: Database = Depends(get_database)):
    post = await database.posts.find_one({"_id": uid})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return PostResponse.from_mongo(post)


@router.get("/", response_model=PaginatedResponse[PostResponse])
async def get_posts(
    query: GetPostsParams = Depends(), database: Database = Depends(get_database)
):
    find = {}

    if query.ownerId:
        find["ownerId"] = {"$eq": query.ownerId}
    if query.language:
        find["language"] = {"$eq": query.language}

    total_count = await database.posts.count_documents(find)

    cursor = database.posts.find(find)

    # We want the posts to always be sorted in a deterministic order to
    # preserve pagination.
    cursor.sort(
        [
            ("updatedAt", pymongo.DESCENDING),
            ("createdAt", pymongo.DESCENDING),
            ("_id", pymongo.ASCENDING),
        ]
    )

    cursor.skip(query.skip)
    cursor.limit(query.limit)

    data: list[PostResponse] = []

    async for post in cursor:
        data.append(PostResponse.from_mongo(post))

    return PaginatedResponse(
        data=data,
        hasMore=total_count - query.skip - query.limit > 0,
        totalCount=total_count,
    )


@router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
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
            "ownerId": uuid.UUID(jwt.sub),
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
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
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
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    post = await database.posts.find_one({"_id": uid})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    if post["ownerId"] != uuid.UUID(jwt.sub):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    await database.posts.delete_one({"_id": uid})
