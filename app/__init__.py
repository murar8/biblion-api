import os
from http import HTTPStatus

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.posts.router import router as posts_router
from app.users.router import router as users_router

app = FastAPI(
    title="Biblion",
    version=os.environ.get("VERSION", default="development"),
    # We need to make sure each route handler has a unique name across the
    # whole project since we only use the route name to generate a unique id.
    # Also see https://fastapi.tiangolo.com/advanced/generate-clients
    generate_unique_id_function=lambda route: route.name,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEBSITE_BASE_URL")],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Respond with the correct format for pydantic validator errors.
# See https://github.com/tiangolo/fastapi/issues/1474
@app.exception_handler(ValidationError)
async def validation_exception_handler(_, exception: ValidationError):
    errors = [
        {**error, "loc": ["query"] + list(error["loc"])} for error in exception.errors()
    ]
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={"error": errors}
    )


router = APIRouter(prefix="/v1")
router.include_router(posts_router, prefix="/posts", tags=["posts"])
router.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(router)
