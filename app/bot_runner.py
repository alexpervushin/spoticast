import asyncio
from aiogram import Bot, Dispatcher
from app.bot import register_handlers
from app.config import get_settings
from app.database import init_db
from app.logger import logger

settings = get_settings()

async def main():
    await init_db()
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    await register_handlers(dp, bot)
    
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 