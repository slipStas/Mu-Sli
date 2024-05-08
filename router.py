import emoji

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pytube import YouTube

from repository import SongsRepository
from schemas import SSongAdd, SSong, AddSongResponce, SearchURL, SongInfo

router = APIRouter(prefix="/song", tags=["Songs"])


def load_song(url: str) -> SongInfo:
    yt = YouTube(url, use_oauth=True)
    # print(f"=============tags: {yt.streams.all}")
    stream = yt.streams.get_by_itag(140)
    # full_sec = int(yt.stream_monostate.duration / 60)
    # remained = int(yt.stream_monostate.duration - full_sec) % 60
    # duration = str(full_sec) + ":" + str(remained)
    duration = yt.stream_monostate.duration
    print(f"\tduration -> {duration}, title: {yt.author}| {yt.title}")
    if yt.author == "":
        file_name = yt.title.replace("\\", "")\
            .replace("/", "").replace("\'", "")\
            .replace("\"", "").replace("|", "")
    else:
        file_name = yt.author\
                        .replace("\\", "")\
                        .replace("/", "")\
                        .replace("\'", "")\
                        .replace("\"", "")\
                        .replace("|", "") + " - " + \
                    yt.title\
                        .replace("\\", "")\
                        .replace("/", "")\
                        .replace("\'", "")\
                        .replace("\"", "")\
                        .replace(".", "")\
                        .replace("|", "")

    file_name = give_emoji_free_text(file_name) + ".mp4a"
    stream.download("data/", filename=file_name)
    song_info = SongInfo(name=file_name,
                         duration=duration,
                         ok=True)
    return song_info


def give_emoji_free_text(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text


# @router.post("")
# async def add_song(song: Annotated[SSongAdd, Depends()]) -> AddSongResponce:
#     song_id = await SongsRepository.add_song(song)
#     songs_dict = await SongsRepository.get_all_songs()
#
#     songs_responce = AddSongResponce(songs_count=len(songs_dict),
#                                      songs_id=song_id)
#
#     return songs_responce


# @router.get("")
# async def get_songs() -> list[SSong]:
#     songs_array = await SongsRepository.get_all_songs()
#
#     return songs_array


@router.post("/search")
async def get_songs(url: Annotated[SearchURL, Depends()]) -> SongInfo:
    song_info = load_song(url=url.url)

    return song_info


@router.post("", response_class=FileResponse)
async def search(file_name: Annotated[SongInfo, Depends()]):
    print(f"\tyou are want to search: {file_name.name}")
    path = f"data/{file_name.name}"
    print(f"\t{path}")

    return path


