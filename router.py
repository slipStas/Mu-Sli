import os.path

import emoji

from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pytube import YouTube

import max_size_singltone
from repository import SongsRepository
from schemas import (SSongAdd, SSong, SearchURL, SongInfo, AddSongResponce, UsingBytes, LoadStreamResponce,
                     FreeSpaceErrorEnum)

from datetime import datetime

router_songs = APIRouter(prefix="/song", tags=["Songs"])
router_size = APIRouter(prefix="/size", tags=["Sizes"])


async def __load_song(url: str) -> LoadStreamResponce:
    try:
        yt = YouTube(url)
        print(yt.author, yt.title, yt.video_id)
        is_yt_id, song = await SongsRepository.check_yt_id(yt_id=yt.video_id)

        if not is_yt_id:
            print(f"loading stream...")
            try:
                stream = yt.streams.get_audio_only()
                duration = yt.stream_monostate.duration

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

                song_add = SSongAdd(author=author,
                                    title=title,
                                    file_name=file_name,
                                    youtube_id=yt.video_id,
                                    duration=duration,
                                    file_size_db=None,
                                    is_in_data=False)
                stream_responce = LoadStreamResponce(song=song_add,
                                                     stream=stream,
                                                     id_db=None,
                                                     file_size=stream.filesize,
                                                     error=None)
                return stream_responce
            except Exception as error:
                print(f"exception error: {error}")
                stream_responce = LoadStreamResponce(song=None,
                                                     stream=None,
                                                     id_db=None,
                                                     file_size=None,
                                                     error=error)
                return stream_responce
        elif song is not None:
            print("not loading stream...")
            song_add = SSongAdd(author=song.author,
                                title=song.title,
                                file_name=song.file_name,
                                youtube_id=song.youtube_id,
                                duration=song.duration,
                                file_size_db=song.file_size_db,
                                is_in_data=song.is_in_data)
            stream_responce = LoadStreamResponce(song=song_add,
                                                 stream=None,
                                                 id_db=song.id,
                                                 file_size=song_add.file_size_db,
                                                 error=None)
            return stream_responce
        else:
            print("--==SOMETHING WRONG WITH SSONG==--")
            error = Exception("SOMETHING WRONG!!!")
            stream_responce = LoadStreamResponce(song=None,
                                                 stream=None,
                                                 id_db=None,
                                                 file_size=None,
                                                 error=error)
            return stream_responce
    except Exception as error:
        print(f"problems with link: {error}")
        stream_responce = LoadStreamResponce(song=None,
                                             stream=None,
                                             id_db=None,
                                             file_size=None,
                                             error=error)
        return stream_responce


def give_emoji_free_text(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text


@router_songs.get("")
async def get_song_list() -> Optional[list[SSong]]:
    songs_array = await SongsRepository.get_all_songs()

    return songs_array


@router_songs.delete("")
async def clear_bd() -> dict:
    is_cleared = await SongsRepository.clear_db()
    if is_cleared:
        status = "ok"
    else:
        status = "fail"

    return {"status": status}


@router_songs.post("/search")
async def search_songs(url: Annotated[SearchURL, Depends()]) -> AddSongResponce:
    load_stream_responce: LoadStreamResponce = await __load_song(url=url.url)
    stream = load_stream_responce.get_stream
    song_add = load_stream_responce.get_song
    id_db = load_stream_responce.get_id_db
    if song_add is not None:
        ssong_add = SSongAdd(author=song_add.author,
                             title=song_add.title,
                             file_name=song_add.file_name,
                             youtube_id=song_add.youtube_id,
                             duration=song_add.duration,
                             file_size_db=load_stream_responce.get_file_size,
                             is_in_data=song_add.is_in_data)

        time_start = datetime.now()

        if stream is None:
            print(f"not loading song!file size: {song_add.file_size_db} bytes")
            song = SSong(id=id_db,
                         is_id_in_db=True,
                         author=song_add.author,
                         title=song_add.title,
                         file_name=song_add.file_name,
                         youtube_id=song_add.youtube_id,
                         duration=song_add.duration,
                         file_size_db=song_add.file_size_db,
                         is_in_data=song_add.is_in_data)
            time_stop = datetime.now()
            time_dif = time_stop - time_start
            print(f"load time = {time_dif}")

            song_responce = AddSongResponce(result="ok",
                                            song=song,
                                            error=None)

            return song_responce
        else:
            print("loading song...")
            is_free_space = await SongsRepository.is_enough_free_space(ssong_add.file_size_db)
            if is_free_space.get_status:
                song_responce = await SongsRepository.download_song(stream=stream,
                                                                    ssong_add=ssong_add)

                return song_responce
            else:
                if is_free_space.get_error == FreeSpaceErrorEnum.very_big_file:
                    song_responce = AddSongResponce(result="not ok",
                                                    song=None,
                                                    error="very big file... can't download it!")

                    return song_responce
                elif is_free_space.get_error == FreeSpaceErrorEnum.not_enough_space:
                    if await SongsRepository.free_up_space():
                        song_responce = await SongsRepository.download_song(stream=stream,
                                                                            ssong_add=ssong_add)

                        return song_responce
                elif is_free_space.get_error == FreeSpaceErrorEnum.db_error:
                    song_responce = AddSongResponce(result="not ok",
                                                    song=None,
                                                    error="db error...")

                    return song_responce
                else:
                    print("some error without status...")

                    song_responce = AddSongResponce(result="not ok",
                                                    song=None,
                                                    error="Error error...")

                    return song_responce
    else:
        song_responce = AddSongResponce(result="not ok",
                                        song=None,
                                        error="song error from server")

        return song_responce


@router_songs.post("", response_class=FileResponse)
async def get_song_data(file_name: Annotated[SongInfo, Depends()]):
    print(f"\tyou are want to search: {file_name.file_name}")
    path = f"data/{file_name.file_name}"
    if os.path.isfile(path=path):
        print(f"\t{path}")

        return path
    else:
        print(f"file {file_name.file_name} is not in data!!! ERROR")
        error_path = FileResponse(status_code=210, filename="no_file.txt", path="data/no_file.txt") # = "data/no_file.txt"
        # error_path.status_code = FileResponse(status_code=333, path=path)
        return error_path


@router_size.post("")
async def set_max_size(new_max_size: int) -> Optional[UsingBytes]:
    max_size_singltone.MaxSize.max_size = new_max_size
    old_bytes = await SongsRepository.get_filled_bytes()
    if old_bytes is not None:
        old_bytes.max_data_size = new_max_size
        new_bytes = UsingBytes(files_size=old_bytes.files_size,
                               files_count=old_bytes.files_count,
                               max_data_size=max_size_singltone.MaxSize.max_size)
        await SongsRepository.change_max_size(new_bytes)
    else:
        new_bytes = UsingBytes(files_size=0,
                               files_count=0,
                               max_data_size=new_max_size)
        await SongsRepository.change_max_size(new_bytes)
    responce = await get_sizes()
    return responce


@router_size.get("")
async def get_sizes() -> Optional[UsingBytes]:
    sizes = await SongsRepository.get_filled_bytes()
    if sizes is not None:
        round_size = str(round(sizes.files_size / 1024 / 1024, 2))
        max_size = str(round(sizes.max_data_size / 1024 / 1024, 2))
        print(f"files size: {round_size}/{max_size}Mb")

        return sizes
    else:
        return None
