from sqlalchemy import select

from database import new_session, SongsTable
from schemas import SSongAdd, SSong


class SongsRepository:
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
    async def get_all_songs(cls):
        async with new_session() as session:
            query = select(SongsTable)
            result = await session.execute(query)
            songs_list = result.scalars().all()

            return songs_list


