from fastapi import FastAPI
from contextlib import asynccontextmanager

import max_size_singltone
from database import delete_tables, create_tables
from router import router_songs as songs_router
from router import router_size as size_router
from repository import SongsRepository
from schemas import UsingBytes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("database was drop!")
    # await create_tables()
    # print("create database!")
    # using_bytes = UsingBytes(files_size=0,
    #                          files_count=0,
    #                          max_data_size=max_size_singltone.MaxSize.max_size)
    # files_count = await SongsRepository.make_bytes(using_bytes)
    # print(f"files count = {files_count}")

    print("reload server!!!...")
    yield
    print("shutdown...")

app = FastAPI(lifespan=lifespan)
app.include_router(songs_router)
app.include_router(size_router)


#  client "ANDROID_CREATOR"
#  python -m pip install git+https://github.com/msemple1111/pytube
#  cipher.py: line 411-   transform_plan_raw = js