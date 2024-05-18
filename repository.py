from typing import Optional

from sqlalchemy import select

import database
from database import new_session, SongsTable
from schemas import SSongAdd


class SongsRepository:
    @classmethod
    async def clear_db(cls) -> bool:
        await database.delete_tables()
        await database.create_tables()
        return True

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

        # async with new_session() as session:
        #     query = select(SongsTable)
        #     result = await session.execute(query)
        #     song_list = result.scalars().all()
        #     for song in song_list:
        #         if yt_id == song.youtube_id:
        #             return True, song.id
        # 11111111
        #     return False, None

    @classmethod
    async def get_all_songs(cls):
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query)
            song_list = result.scalars().all()

            return song_list


