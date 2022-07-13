from fastapi import FastAPI

from .posts_router import router as posts_router

app = FastAPI(title="Biblion", version="0.1.0")

app.include_router(posts_router, prefix="/posts")
