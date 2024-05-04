from typing import Annotated

from fastapi import APIRouter, Depends

from repository import SongsRepository
from schemas import SSongAdd, SSong, AddSongResponce

router = APIRouter(prefix="/song", tags=["Songs"])


@router.post("")
async def add_song(song: Annotated[SSongAdd, Depends()]) -> AddSongResponce:
    song_id = await SongsRepository.add_song(song)
    songs_dict = await SongsRepository.get_all_songs()

    songs_responce = AddSongResponce(songs_count=len(songs_dict),
                                     songs_id=song_id)

    return songs_responce


@router.get("")
async def get_songs() -> list[SSong]:
    songs_array = await SongsRepository.get_all_songs()

    return songs_array


