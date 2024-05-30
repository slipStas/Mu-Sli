from typing import Optional
from enum import Enum
from pydantic import BaseModel
from pytube import Stream


class SSongAdd(BaseModel):
    author: str
    title: str
    file_name: str
    youtube_id: str
    duration: int
    file_size_db: Optional[int]
    is_in_data: bool


class SSong(SSongAdd):
    id: int


class AddSongResponce(BaseModel):
    result: str = "ok"
    song: Optional[SSong]
    error: Optional[str]


class SearchURL(BaseModel):
    url: str


class SongInfo(BaseModel):
    file_name: str
    duration: int
    youtube_id: str


class Bytes(BaseModel):
    files_size: int
    files_count: int
    max_data_size: int


class UsingBytes(Bytes):
    pass


class LoadStreamResponce:
    __song: Optional[SSongAdd]
    __stream: Optional[Stream]
    __id_db: Optional[int]
    __file_size: Optional[int]
    __error: Optional[Exception]

    def __init__(self, song: Optional[SSongAdd],
                 stream: Optional[Stream],
                 id_db: Optional[int],
                 file_size: Optional[int],
                 error: Optional[Exception]):
        self.__song = song
        self.__stream = stream
        self.__id_db = id_db
        self.__file_size = file_size
        self.__error = error

    @property
    def get_song(self):
        return self.__song

    @property
    def get_file_size(self):
        return self.__file_size

    @property
    def get_stream(self):
        return self.__stream

    @property
    def get_id_db(self):
        return self.__id_db


class FreeSpaceErrorEnum(Enum):
    very_big_file = 1
    not_enough_space = 2
    db_error = 3


class IsEnoughFreeSpace:
    __status: bool
    __error: Optional[FreeSpaceErrorEnum]

    def __init__(self, status: bool, error: Optional[FreeSpaceErrorEnum]):
        self.__status = status
        self.__error = error

    @property
    def get_status(self):
        return self.__status

    @property
    def get_error(self):
        return self.__error


