from pydantic import BaseModel


class SSongAdd(BaseModel):
    author: str
    title: str
    file_name: str
    youtube_id: str
    duration: int


class SSong(SSongAdd):
    id: int


class SSongResponce(SSongAdd):
    id: int
    is_id_in_db: bool


class AddSongResponce(BaseModel):
    result: str = "ok"
    songs_count: int
    songs_id: int


class SearchURL(BaseModel):
    url: str


class SongInfo(BaseModel):
    file_name: str
    duration: int
    youtube_id: str

