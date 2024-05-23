import os.path

import emoji

from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pytube import YouTube, Stream

from repository import SongsRepository
from schemas import SSongAdd, SSong, SearchURL, SongInfo, AddSongResponce

from datetime import datetime

router = APIRouter(prefix="/song", tags=["Songs"])


async def __load_song(url: str) -> (Optional[SSongAdd], Optional[Stream], Optional[int], Optional[int]):
    yt = YouTube(url)
    print(yt.author, yt.title, yt.video_id)
    is_yt_id, id_db, duration_db, file_size_db = await SongsRepository.check_yt_id(yt_id=yt.video_id)

    if yt.author == "":
        title_yt = yt.title.replace("—", "-")
        title_array = title_yt.split("-")
        author_raw = title_array[0].replace("\\", "") \
            .replace("/", "") \
            .replace("\'", "") \
            .replace("\"", "") \
            .replace("|", "") \
            .replace(":", "") \
            .replace("*", "") \
            .replace("?", "") \
            .replace("<", "") \
            .replace(">", "")
        title_raw = title_array[1].replace("\\", "") \
            .replace("/", "") \
            .replace("\'", "") \
            .replace("\"", "") \
            .replace("|", "") \
            .replace(":", "") \
            .replace("*", "") \
            .replace("?", "") \
            .replace("<", "") \
            .replace(">", "")
        author = give_emoji_free_text(author_raw)
        title = give_emoji_free_text(title_raw)
    else:
        title_yt = yt.title.replace("—", "-")
        title_array = title_yt.split("-")
        if len(title_array) > 1:
            author_raw = title_array[0].replace("\\", "") \
                .replace("/", "") \
                .replace("\'", "") \
                .replace("\"", "") \
                .replace("|", "") \
                .replace(":", "") \
                .replace("*", "") \
                .replace("?", "") \
                .replace("<", "") \
                .replace(">", "")
            title_raw = title_array[1].replace("\\", "") \
                .replace("/", "") \
                .replace("\'", "") \
                .replace("\"", "") \
                .replace("|", "") \
                .replace(":", "") \
                .replace("*", "") \
                .replace("?", "") \
                .replace("<", "") \
                .replace(">", "")
            author = give_emoji_free_text(author_raw)
            title = give_emoji_free_text(title_raw)
        else:
            author_raw = yt.author.replace("\\", "") \
                .replace("/", "") \
                .replace("\'", "") \
                .replace("\"", "") \
                .replace("|", "") \
                .replace(":", "") \
                .replace("*", "") \
                .replace("?", "") \
                .replace("<", "") \
                .replace(">", "")
            title_raw = yt.title.replace("\\", "") \
                .replace("/", "") \
                .replace("\'", "") \
                .replace("\"", "") \
                .replace("|", "") \
                .replace(":", "") \
                .replace("*", "") \
                .replace("?", "") \
                .replace("<", "") \
                .replace(">", "")
            author = give_emoji_free_text(author_raw)
            title = give_emoji_free_text(title_raw)

    file_name = f"{author} - {title}.mp3"

    if not is_yt_id:
        print(f"loading stream...")
        try:
            stream = yt.streams.get_audio_only()
            duration = yt.stream_monostate.duration

            song_add = SSongAdd(author=author,
                                title=title,
                                file_name=file_name,
                                youtube_id=yt.video_id,
                                duration=duration,
                                file_size=file_size_db)

            return song_add, stream, id_db, file_size_db
        except Exception as error:
            print(f"exception error: {error}")
            return None, None, None, None
    else:
        print("not loading stream...")
        song_add = SSongAdd(author=author,
                            title=title,
                            file_name=file_name,
                            youtube_id=yt.video_id,
                            duration=duration_db,
                            file_size=file_size_db)

        return song_add, None, id_db, file_size_db


def give_emoji_free_text(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text


@router.get("")
async def get_song_list() -> list[SSong]:
    songs_array = await SongsRepository.get_all_songs()

    return songs_array


@router.delete("")
async def clear_bd() -> dict:
    is_cleared = await SongsRepository.clear_db()
    if is_cleared:
        status = "ok"
    else:
        status = "fail"

    return {"status": status}


@router.post("/search")
async def search_songs(url: Annotated[SearchURL, Depends()]) -> AddSongResponce:
    song_add, stream, id_db, file_size_db = await __load_song(url=url.url)
    if song_add is not None:
        ssong_add = SSongAdd(author=song_add.author,
                             title=song_add.title,
                             file_name=song_add.file_name,
                             youtube_id=song_add.youtube_id,
                             duration=song_add.duration,
                             file_size=file_size_db)

        time_start = datetime.now()

        if stream is None:
            print("not loading song!")
            song = SSong(id=id_db,
                         is_id_in_db=True,
                         author=song_add.author,
                         title=song_add.title,
                         file_name=song_add.file_name,
                         youtube_id=song_add.youtube_id,
                         duration=song_add.duration,
                         file_size=song_add.file_size)
            time_stop = datetime.now()
            time_dif = time_stop - time_start
            print(f"load time = {time_dif}")

            song_responce = AddSongResponce(result="ok",
                                            song=song,
                                            error=None)

            return song_responce
        else:
            print("loading song...")
            stream.download("data/", filename=song_add.file_name)
            file_size = os.path.getsize(f"./data/{song_add.file_name}")
            ssong_add.file_size = file_size
            print(f"size of file: {ssong_add.file_size}")
            song_id = await SongsRepository.add_song(ssong_add)
            song = SSong(id=song_id,
                         is_id_in_db=False,
                         author=song_add.author,
                         title=song_add.title,
                         file_name=song_add.file_name,
                         youtube_id=song_add.youtube_id,
                         duration=song_add.duration,
                         file_size=song_add.file_size)
            time_stop = datetime.now()
            time_dif = time_stop - time_start
            print(f"load time = {time_dif}, file size = {ssong_add.file_size}")

            song_responce = AddSongResponce(result="ok",
                                            song=song,
                                            error=None)

            return song_responce
    else:
        song_responce = AddSongResponce(result="not ok",
                                        song=None,
                                        error="song error from server")

        return song_responce


@router.post("", response_class=FileResponse)
async def get_song_data(file_name: Annotated[SongInfo, Depends()]):
    print(f"\tyou are want to search: {file_name.file_name}")
    path = f"data/{file_name.file_name}"
    print(f"\t{path}")

    return path
