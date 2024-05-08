from pydantic import BaseModel
from fastapi.responses import FileResponse


class SSongAdd(BaseModel):
    artist: str
    title: str
    path: str
    youtube_link: str


class SSong(SSongAdd):
    id: int


class AddSongResponce(BaseModel):
    result: str = "ok"
    songs_count: int
    songs_id: int


class SearchURL(BaseModel):
    url: str


class SongInfo(BaseModel):
    name: str
    duration: int
    ok: bool

