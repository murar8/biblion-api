from fastapi import Depends, FastAPI
from providers.auth import get_jwt


app = FastAPI(title="Biblion", version="0.1.0")


@app.get("/", dependencies=[Depends(get_jwt)])
async def root():
    return "Hello, world!"
