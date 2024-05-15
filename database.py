from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///songs.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class SongsTable(Model):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str]
    title: Mapped[str]
    file_name: Mapped[str]
    youtube_id: Mapped[str]
    duration: Mapped[int]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

