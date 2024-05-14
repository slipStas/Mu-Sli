from pydantic import BaseModel
from fastapi.responses import FileResponse


class SSongAdd(BaseModel):
    author: str
    title: str
    file_name: str
    youtube_id: str
    duration: int


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

