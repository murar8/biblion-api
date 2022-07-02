from fastapi import FastAPI

from .routers import posts

app = FastAPI(title="Biblion", version="0.1.0")

app.include_router(posts.router, prefix="/posts")
