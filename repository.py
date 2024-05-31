import os
from typing import Optional

import emoji
from pytube import Stream, YouTube
from sqlalchemy import select
from sqlalchemy.sql.expression import true

import database
import max_size_singltone
from database import new_session, SongsTable, UsingBytesTable
from schemas import SSongAdd, UsingBytes, SSong, IsEnoughFreeSpace, FreeSpaceErrorEnum, AddSongResponce, \
    LoadStreamResponce


class SongsRepository:
    @classmethod
    async def clear_db(cls) -> bool:
        responce = True
        folder = "./data"
        song_list = await SongsRepository.get_all_songs()
        ssong_list = {}
        for song in song_list:
            ssong = SSongAdd(author=song.author,
                             title=song.title,
                             file_name=song.file_name,
                             youtube_id=song.youtube_id,
                             duration=song.duration,
                             file_size_db=song.file_size_db,
                             is_in_data=song.is_in_data)
            ssong_list[ssong.file_name] = ssong
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            file_name = file_path.split("/")[2]
            if file_name in ssong_list and ssong_list[file_name].is_in_data is True:
                os.remove(file_path)
                print(f"remove file: {file_name}")
            elif file_name in ssong_list and ssong_list[file_name].is_in_data is False:
                print(f"file is in db, but is not in data")
            else:
                print("error from key!!!")
                responce = False

        if responce:
            await database.delete_tables()
            await database.create_tables()
        return responce

    @classmethod
    async def add_song(cls, song_data: SSongAdd, file_data: UsingBytes) -> int:
        async with new_session() as session:
            songs_dict = song_data.model_dump()
            song = SongsTable(**songs_dict)
            session.add(song)
            await session.flush()
            await session.commit()

            query = select(UsingBytesTable)
            result = await session.execute(query)
            using_bytes = result.scalars().first()
            if using_bytes is not None:
                using_bytes.files_size += song.file_size_db
                using_bytes.files_count += 1
                await session.commit()
            else:
                size = file_data.model_dump()
                sizes = UsingBytesTable(**size)
                session.add(sizes)
                await session.commit()

            return song.id

    @classmethod
    async def add_file_size(cls, size: int) -> bool:
        async with new_session() as session:
            query = select(UsingBytesTable)
            result = await session.execute(query)
            using_bytes = result.scalars().first()
            if using_bytes is not None:
                using_bytes.files_size += size
                using_bytes.files_count += 1
                await session.commit()
                return True
            else:
                return False

    @classmethod
    async def check_yt_id(cls, yt_id: str) -> (bool, Optional[str], Optional[SSong]):
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query.where(SongsTable.youtube_id == yt_id))
            song_list = result.scalars().first()
            if song_list is not None:
                song = SSong(author=song_list.author,
                             title=song_list.title,
                             file_name=song_list.file_name,
                             youtube_id=song_list.youtube_id,
                             duration=song_list.duration,
                             file_size_db=song_list.file_size_db,
                             is_in_data=song_list.is_in_data,
                             id=song_list.id)
                return True, song

            return False, None

    @classmethod
    async def is_enough_free_space(cls, file_size: int) -> IsEnoughFreeSpace:
        async with new_session() as session:
            query = select(UsingBytesTable)
            result = await session.execute(query)
            size = result.scalars().first()
            if size is not None:
                max_size = size.max_data_size
                need_size = size.files_size + file_size
                if max_size > need_size:
                    print(f"size ok, max size {max_size}, filled now {size.files_size}, needed {file_size}")
                    responce = IsEnoughFreeSpace(status=True, error=None)

                    return responce
                elif file_size >= max_size / 3:
                    print(f"file size is too match... {str(round(file_size / 1024 / 1024, 2))}Mb")
                    responce = IsEnoughFreeSpace(status=False, error=FreeSpaceErrorEnum.very_big_file)

                    return responce
                else:
                    print(f"size NOT ok, max size {max_size}, filled now {size.files_size}, needed {file_size}")
                    responce = IsEnoughFreeSpace(status=False, error=FreeSpaceErrorEnum.not_enough_space)

                    return responce
            else:
                print("something with UsingBytesTable data... ERROR!!!")
                responce = IsEnoughFreeSpace(status=True, error=FreeSpaceErrorEnum.db_error)

                return responce

    @classmethod
    async def free_up_space(cls) -> bool:
        need_size = max_size_singltone.MaxSize.max_size / 2

        removing_size = 0
        status = True

        async with new_session() as session:
            query = select(SongsTable).filter(SongsTable.is_in_data.is_(true()))
            result = await session.execute(query)
            song_list = result.scalars().all()
            if song_list is not None:
                folder = "./data"
                for song in song_list:
                    file_path = os.path.join(folder, song.file_name)
                    if need_size > removing_size:
                        print("\t--- removing file...")
                        print(f"need size: {need_size}")
                        print(f"remo size: {removing_size}")
                        try:
                            os.remove(file_path)
                            removing_size += song.file_size_db
                            song.is_in_data = False
                            print(f"remove file: {song.file_name}, removing size: {removing_size}")
                        except Exception as error:
                            print(f"file deleting error: {error}")
                            need_size = 0
                            status = False
                    else:
                        print("=-0987675567890-=")
                        break
                await session.commit()
                using_bytes = await SongsRepository.change_files_size(change_size=removing_size, is_removing=True)
                if using_bytes is None:
                    status = False
            else:
                status = False

            return status

    @classmethod
    async def download_song(cls, stream: Stream, ssong_add: SSongAdd, db_id: Optional[str]) -> AddSongResponce:
        download_path = stream.download("data/", filename=ssong_add.file_name)
        if download_path is not None:
            is_in_data = True
        else:
            is_in_data = False
        ssong_add.is_in_data = is_in_data
        file_size = os.path.getsize(f"./data/{ssong_add.file_name}")
        ssong_add.file_size_db = file_size
        print(f"size of file: {ssong_add.file_size_db}")
        print(f"ssongAdd = {ssong_add.file_name}, {ssong_add.is_in_data}, {ssong_add.youtube_id}, {db_id}")
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query.where(SongsTable.youtube_id == ssong_add.youtube_id))
            song = result.scalars().first()

            if song is None:
                print(f"first loading song: {ssong_add.file_name}")
                file_data = UsingBytes(files_size=file_size,
                                       files_count=1,
                                       max_data_size=max_size_singltone.MaxSize.max_size)

                song_id = await SongsRepository.add_song(ssong_add, file_data=file_data)
                song = SSong(id=song_id,
                             author=ssong_add.author,
                             title=ssong_add.title,
                             file_name=ssong_add.file_name,
                             youtube_id=ssong_add.youtube_id,
                             duration=ssong_add.duration,
                             file_size_db=ssong_add.file_size_db,
                             is_in_data=ssong_add.is_in_data)
                print(f"file size = {ssong_add.file_size_db}")

                song_responce = AddSongResponce(result="ok",
                                                song=song,
                                                error=None)

                return song_responce
            else:
                print(f"not first loading song: {ssong_add.file_name}")
                print(f"song = {song}, db_id {db_id}")
                song.is_in_data = is_in_data
                print(f"234567890- {song.duration}")
                ssong = SSong(id=song.id,
                              author=song.author,
                              title=song.title,
                              file_name=song.file_name,
                              youtube_id=song.youtube_id,
                              duration=song.duration,
                              file_size_db=song.file_size_db,
                              is_in_data=song.is_in_data)
                song_responce = AddSongResponce(result="ok",
                                                song=ssong,
                                                error=None)
                await session.commit()

                await SongsRepository.change_files_size(change_size=song.file_size_db, is_removing=False)

                return song_responce

    @classmethod
    async def get_all_songs(cls) -> Optional[list[SSong]]:
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query)
            song_list = result.scalars().all()
            if song_list is not None:
                return song_list
            else:
                print("-= ERROR =-")
                return None

    @classmethod
    async def get_all_songs_in_data(cls) -> Optional[list[SSong]]:
        async with new_session() as session:
            query = select(SongsTable).filter(SongsTable.is_in_data.is_(true()))
            result = await session.execute(query)
            song_list = result.scalars().all()
            if song_list is not None:
                return song_list

            return None

    @classmethod
    async def get_filled_bytes(cls):
        async with new_session() as session:
            query = select(UsingBytesTable)
            result = await session.execute(query)
            using_bytes = result.scalars().all()
            if len(using_bytes) > 0:
                return using_bytes[0]
            else:
                return None

    @classmethod
    async def make_bytes(cls, data: UsingBytes) -> int:
        async with new_session() as session:
            datas = data.model_dump()
            using_bytes = UsingBytesTable(**datas)
            session.add(using_bytes)
            await session.commit()

            return using_bytes.files_count

    @classmethod
    async def change_max_size(cls, data: UsingBytes) -> Optional[UsingBytes]:
        async with new_session() as session:
            query = select(UsingBytesTable)
            result = await session.execute(query)
            using_bytes = result.scalars().first()
            if using_bytes is not None:
                using_bytes.max_data_size = data.max_data_size
                await session.commit()
                max_size_singltone.MaxSize.max_size = data.max_data_size
                return using_bytes
            else:
                return None

    @classmethod
    async def change_files_size(cls, change_size: int, is_removing: bool) -> Optional[UsingBytes]:
        async with new_session() as session:
            query = select(UsingBytesTable)
            result = await session.execute(query)
            using_bytes = result.scalars().first()
            if using_bytes is not None:
                if is_removing:
                    new_size = using_bytes.files_size - change_size
                    print(f"new___size after removing = {new_size}")
                    using_bytes.files_size = new_size
                    max_size_singltone.MaxSize.max_size = using_bytes.max_data_size
                else:
                    new_size = using_bytes.files_size + change_size
                    print(f"new___size after adding = {new_size}")
                    using_bytes.files_size = new_size
                    max_size_singltone.MaxSize.max_size = using_bytes.max_data_size
                await session.commit()
                return using_bytes
            else:
                return None

    @classmethod
    async def load_stream(cls, yt: YouTube, song: Optional[SSong]) -> LoadStreamResponce:
        print(f"loading stream...")
        try:
            stream = yt.streams.get_audio_only()

            if song is None:
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
                    author = SongsRepository.give_emoji_free_text(author_raw)
                    title = SongsRepository.give_emoji_free_text(title_raw)
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
                        author = SongsRepository.give_emoji_free_text(author_raw)
                        title = SongsRepository.give_emoji_free_text(title_raw)
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
                        author = SongsRepository.give_emoji_free_text(author_raw)
                        title = SongsRepository.give_emoji_free_text(title_raw)

                duration = yt.stream_monostate.duration
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
            else:
                song_add = SSongAdd(author=song.author,
                                    title=song.title,
                                    file_name=song.file_name,
                                    youtube_id=song.youtube_id,
                                    duration=song.duration,
                                    file_size_db=song.file_size_db,
                                    is_in_data=song.is_in_data)
                stream_responce = LoadStreamResponce(song=song_add,
                                                     stream=stream,
                                                     id_db=song.id,
                                                     file_size=song.file_size_db,
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

    @classmethod
    def give_emoji_free_text(cls, text_raw: str):
        allchars = [str for str in text_raw]
        emoji_list = [c for c in allchars if c in emoji.EMOJI_DATA]
        clean_text = ' '.join([str for str in text_raw.split() if not any(i in str for i in emoji_list)])
        return clean_text
