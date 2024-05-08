from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import delete_tables, create_tables
from router import router as songs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("database was drop!")
    # await create_tables()
    # print("create database!")

    print("reload server!!!...")
    yield
    print("shutdown...")

app = FastAPI(lifespan=lifespan)
app.include_router(songs_router)


