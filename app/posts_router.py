from datetime import datetime
from http import HTTPStatus

from motor.core import AgnosticDatabase
from fastapi import APIRouter, Depends, HTTPException
import pymongo


from .request import CreatePostRequest, GetPostsParams, UpdatePostRequest
from .response import PaginatedResponse, PostResponse
from .shortid import generate_shortid
from .access_token import AccessToken
from .providers.auth import get_jwt
from .providers.database import get_db

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PostResponse])
async def get_posts(
    query: GetPostsParams = Depends(), db: AgnosticDatabase = Depends(get_db)
):
    sort_key = query.sort_key if query.sort_key != "id" else "_id"
    sort_order = pymongo.ASCENDING if query.sort_order == "asc" else pymongo.DESCENDING
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
        find["ownerId"] = {"$eq": query.ownerId}
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
