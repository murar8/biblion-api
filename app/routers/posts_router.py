from datetime import datetime
from http import HTTPStatus

import pymongo
from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.access_token import AccessToken
from app.models.posts_requests import CreatePostRequest, GetPostsParams
from app.models.posts_responses import PaginatedResponse, PostResponse
from app.providers.access_token import get_access_token
from app.providers.database import get_database
from app.providers.logged_user import get_logged_user
from app.util.shortid import generate_shortid

posts_router = APIRouter()


@posts_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, database: Database = Depends(get_database)):
    post = await database.posts.find_one({"_id": post_id})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    return PostResponse.from_mongo(post)


@posts_router.get("/", response_model=PaginatedResponse[PostResponse])
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


@posts_router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    user: dict[str, any] = Depends(get_logged_user),
    database: Database = Depends(get_database),
):
    if not user["verified"]:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User not verified."
        )

    # We use short ids to make it easy for users to share posts by id, so we
    # have to take into account the (unlikely) possibility of having two ids clashing.
    while True:
        post_id = generate_shortid()
        created_at = datetime.utcnow()

        document = {
            "_id": post_id,
            "ownerId": user["_id"],
            "createdAt": created_at,
            "updatedAt": created_at,
            **body.dict(),
        }

        try:
            await database.posts.insert_one(document=document)
        except DuplicateKeyError:
            continue

        post = await database.posts.find_one({"_id": post_id})
        return PostResponse.from_mongo(post)


@posts_router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    post = await database.posts.find_one({"_id": post_id})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    if post["ownerId"] != jwt.sub:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Current user is not the owner of the post.",
        )

    post = await database.posts.find_one_and_update(
        {"_id": post_id},
        {"$set": {**body.dict(), "updatedAt": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )

    return PostResponse.from_mongo(post)


@posts_router.delete("/{post_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    post_id: str,
    jwt: AccessToken = Depends(get_access_token),
    database: Database = Depends(get_database),
):
    post = await database.posts.find_one({"_id": post_id})

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    if post["ownerId"] != jwt.sub:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Current user is not the owner of the post.",
        )

    await database.posts.delete_one({"_id": post_id})
