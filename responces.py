from pydantic import BaseModel


class AddSongResponce(BaseModel):
    result: str
    songs_count: int
    songs_id: int


