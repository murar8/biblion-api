import asyncio
from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from app.access_token import AccessToken
from app.models.database import Post, User
from app.models.posts_requests import CreatePostRequest, GetPostsParams
from app.models.posts_responses import PaginatedResponse, PostResponse
from app.providers.access_token import get_access_token
from app.providers.logged_user import get_logged_user
from app.util.shortid import generate_shortid

posts_router = APIRouter()


@posts_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    post = await Post.get(post_id)

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    return PostResponse.from_mongo(post)


@posts_router.get("/", response_model=PaginatedResponse[PostResponse])
async def get_posts(query: GetPostsParams = Depends()):
    find = {}

    if query.creatorId:
        find["creator"] = {"$eq": query.creatorId}
    if query.language:
        find["language"] = {"$eq": query.language}

    # We want the posts to always be sorted in a deterministic order to
    # preserve pagination.
    sort = ["-updatedAt", "-createdAt", "+id"]

    data, total_count = await asyncio.gather(
        Post.find(find).sort(sort).skip(query.skip).limit(query.limit).to_list(),
        Post.find(find).count(),
    )

    posts = list(map(PostResponse.from_mongo, data))
    has_more = total_count - query.skip - query.limit > 0

    return PaginatedResponse(data=posts, hasMore=has_more, totalCount=total_count)


@posts_router.post("/", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    body: CreatePostRequest,
    user: User = Depends(get_logged_user),
):
    if not user.verified:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User not verified."
        )

    # We use short ids to make it easy for users to share posts by id, so we
    # have to take into account the (unlikely) possibility of having two ids clashing.
    while True:
        post_id = generate_shortid()
        created_at = datetime.utcnow()

        post = Post(
            id=post_id,
            creator=user.id,
            createdAt=created_at,
            updatedAt=created_at,
            **body.dict()
        )

        try:
            await post.insert()
        except DuplicateKeyError:
            continue

        return PostResponse.from_mongo(post)


@posts_router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    body: CreatePostRequest,
    jwt: AccessToken = Depends(get_access_token),
):
    post = await Post.get(post_id)

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    if post.creator.ref.id != jwt.sub:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Current user is not the owner of the post.",
        )

    post.content = body.content
    post.name = body.name
    post.language = body.language
    post.updatedAt = datetime.utcnow()

    await post.save()

    return PostResponse.from_mongo(post)


@posts_router.delete("/{post_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    post_id: str,
    jwt: AccessToken = Depends(get_access_token),
):
    post = await Post.get(post_id)

    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")

    if post.creator.ref.id != jwt.sub:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Current user is not the owner of the post.",
        )

    await post.delete()
