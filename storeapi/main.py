from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storeapi.database import database
from storeapi.routers.post import router as post_router
from storeapi.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post_router, prefix="/api")
app.include_router(user_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("storeapi.main:app", host="0.0.0.0", port=8088, reload=True)
