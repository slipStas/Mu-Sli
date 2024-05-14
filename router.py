import emoji

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pytube import YouTube, Stream

from repository import SongsRepository
from schemas import SSongAdd, SSong, SearchURL, SongInfo

router = APIRouter(prefix="/song", tags=["Songs"])


def __load_song(url: str) -> (SSongAdd, Stream):
    yt = YouTube(url, use_oauth=True)
    stream = yt.streams.get_by_itag(140)
    duration = yt.stream_monostate.duration
    print(f"\tduration -> {duration}, title: {yt.author}| {yt.title}")
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
    # stream.download("data/", filename=file_name)
    song_add = SSongAdd(author=author,
                        title=title,
                        file_name=file_name,
                        youtube_id=yt.video_id,
                        duration=duration)

    return song_add, stream


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


@router.get("")
async def get_song_list() -> list[SSong]:
    songs_array = await SongsRepository.get_all_songs()

    return songs_array


@router.post("/search")
async def search_songs(url: Annotated[SearchURL, Depends()]) -> SSong:
    song_add, stream = __load_song(url=url.url)
    ssong_add = SSongAdd(author=song_add.author,
                         title=song_add.title,
                         file_name=song_add.file_name,
                         youtube_id=song_add.youtube_id,
                         duration=song_add.duration)

    is_yt_id, id_db = await SongsRepository.check_yt_id(yt_id=song_add.youtube_id)

    if is_yt_id:
        print("not loading song!")
        song_responce = SSong(id=id_db,
                              is_id_in_db=is_yt_id,
                              author=song_add.author,
                              title=song_add.title,
                              file_name=song_add.file_name,
                              youtube_id=song_add.youtube_id,
                              duration=song_add.duration)

        return song_responce
    else:
        stream.download("data/", filename=song_add.file_name)
        print("loading song...")
        song_id = await SongsRepository.add_song(ssong_add)
        song_responce = SSong(id=song_id,
                              is_id_in_db=is_yt_id,
                              author=song_add.author,
                              title=song_add.title,
                              file_name=song_add.file_name,
                              youtube_id=song_add.youtube_id,
                              duration=song_add.duration)

        return song_responce


@router.post("", response_class=FileResponse)
async def get_song_data(file_name: Annotated[SongInfo, Depends()]):
    print(f"\tyou are want to search: {file_name.name}")
    path = f"data/{file_name.name}"
    print(f"\t{path}")

    return path
