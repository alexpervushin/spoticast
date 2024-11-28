from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from app.services.spotify import SpotifyService
from app.database.repository import UserRepository
from app.database.connection import get_session
from app.config import get_settings
from app.logger import logger

settings = get_settings()
app = FastAPI()
spotify_service = SpotifyService()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/login")
async def spotify_login():
    logger.info("Initiating Spotify login process")
    auth_url = spotify_service.get_auth_url("")
    return {"auth_url": auth_url}


@app.get("/callback")
async def spotify_callback(code: str, state: str):
    logger.info(f"Received Spotify callback with state: {state}")
    try:
        refresh_token = await spotify_service.exchange_code_for_token(code)
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Failed to get refresh token")

        telegram_id = int(state)
        async for session in get_session():
            user_repo = UserRepository(session)
            await user_repo.save_refresh_token(telegram_id, refresh_token)

        return RedirectResponse(
            url=f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=auth_success"
        )
    except Exception as e:
        logger.error(f"Error in spotify_callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
