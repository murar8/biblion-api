from http import HTTPStatus
from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from .posts_router import router as posts_router

app = FastAPI(title="Biblion", version="1.0.0")

app.include_router(posts_router, prefix="/posts")

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
