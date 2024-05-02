from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Song(BaseModel):
    id: int
    artist: str
    title: str
    path: str
    youtube_link: str


@app.get("/songs")
def get_songs() -> dict:
    song_one = Song(id=1, artist="Anya Nami", title="Wake me up", path="data/", youtube_link="www.youtube.com/wqerty")
    song_two = Song(id=2, artist="Anya Singltone", title="Wale up", path="data/", youtube_link="www.youtube.com/wqeyuio")

    songs_array = [song_one, song_two]

    return {"data": songs_array}

