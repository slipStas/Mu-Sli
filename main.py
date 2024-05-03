from typing import Annotated

from fastapi import FastAPI, Depends
from pydantic import BaseModel


app = FastAPI()


class SSongAdd(BaseModel):
    artist: str
    title: str
    path: str
    youtube_link: str


class SSong(SSongAdd):
    id: int


songs_array = []


@app.post("/song")
async def add_song(song: Annotated[SSongAdd, Depends()]) -> dict:
    song = SSong(id=1, artist="Anya Nami", title="Wake1 me up", path="data/", youtube_link="www.youtube.com/wqerty")
    # song_two = SSong(id=2, artist="Anya Singltone", title="Wale up", path="data/", youtube_link="www.youtube.com/wqeyuio")
    songs_array.append(song)

    return {"result": "ok",
            "song_id": song.id}


# @app.get("/songs")
# def get_songs() -> dict:
#     song_one = SSong(id=1, artist="Anya Nami", title="Wake me up", path="data/", youtube_link="www.youtube.com/wqerty")
#     song_two = SSong(id=2, artist="Anya Singltone", title="Wale up", path="data/", youtube_link="www.youtube.com/wqeyuio")
#
#     songs_array = [song_one, song_two]
#
#     return {"data": songs_array}

