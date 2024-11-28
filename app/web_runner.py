import uvicorn
from app.web import web_app
from app.config import get_settings
from app.database import init_db
import asyncio

settings = get_settings()

async def main():
    await init_db()
    
    config = uvicorn.Config(
        web_app,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        log_level=settings.UVICORN_LOG_LEVEL
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main()) 