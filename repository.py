import os
from typing import Optional

from sqlalchemy import select

import database
from database import new_session, SongsTable
from schemas import SSongAdd


class SongsRepository:
    @classmethod
    async def clear_db(cls) -> bool:
        responce = True
        folder = "./data"
        song_list = await SongsRepository.get_all_songs()
        ssong_list = {}
        # files_list = []
        for song in song_list:
            # print(f"song -- {song.author}")
            ssong = SSongAdd(author=song.author,
                             title=song.title,
                             file_name=song.file_name,
                             youtube_id=song.youtube_id,
                             duration=song.duration)
            ssong_list[ssong.file_name] = ssong
            # print(f"add:{ssong.file_name}: {ssong.duration}")
        # print(ssong_list)
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            file_name = file_path.split("/")[2]
            # print(f"file name:{file_name}|")
            # os.remove(file_path)
            if file_name in ssong_list:
                os.remove(file_path)
                print(f"remove file: {file_name}")
            else:
                print("error from key!!!")
                responce = False

        if responce:
            await database.delete_tables()
            await database.create_tables()
        return responce

    @classmethod
    async def add_song(cls, data: SSongAdd) -> int:
        async with new_session() as session:
            songs_dict = data.model_dump()
            song = SongsTable(**songs_dict)
            session.add(song)
            await session.flush()
            await session.commit()

            return song.id

    @classmethod
    async def check_yt_id(cls, yt_id: str) -> (bool, Optional[str], Optional[int]):
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query.where(SongsTable.youtube_id == yt_id))
            song_list = result.scalars().first()
            if song_list is not None:
                return True, song_list.id, song_list.duration

            return False, None, None

    @classmethod
    async def get_all_songs(cls):
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query)
            song_list = result.scalars().all()

            return song_list
