from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from typing import Optional, List


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, telegram_id: int) -> User:
        user = User(telegram_id=telegram_id)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def save_refresh_token(self, telegram_id: int, refresh_token: str) -> bool:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            user = User(telegram_id=telegram_id)
            self.session.add(user)
        user.spotify_refresh_token = refresh_token
        await self.session.commit()
        return True

    async def save_channel_id(self, telegram_id: int, channel_id: str) -> bool:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        user.channel_id = channel_id
        await self.session.commit()
        return True

    async def get_all_users(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_configured_users(self) -> List[int]:
        result = await self.session.execute(
            select(User.telegram_id).where(
                User.spotify_refresh_token.isnot(None), User.channel_id.isnot(None)
            )
        )
        return [row[0] for row in result.all()]

    async def toggle_updates(self, telegram_id: int) -> bool:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        
        user.updates_enabled = not user.updates_enabled
        await self.session.commit()
        return user.updates_enabled
