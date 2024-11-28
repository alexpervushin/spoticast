from .models import Base
from .connection import engine, get_session
from .repository import UserRepository


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = ["init_db", "get_session", "UserRepository"]
