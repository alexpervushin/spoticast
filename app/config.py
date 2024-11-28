from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str
    ADMIN_USER_ID: int

    # Spotify settings
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_AUTH_URL: str = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL: str = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_URL: str = "https://api.spotify.com/v1"
    SPOTIFY_REDIRECT_URI: str
    SPOTIFY_SCOPES: str = "user-read-currently-playing user-read-playback-state"
    SPOTIFY_UPDATE_INTERVAL: int = 10  # seconds

    # File settings
    TEMP_ALBUM_COVER: str = "album_cover.jpg"

    # Database settings
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = "localhost"
    POSTGRES_PORT: Optional[str] = "5432"

    # Uvicorn settings
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    UVICORN_LOG_LEVEL: str = "info"

    MAX_MESSAGE_LENGTH: int = 4096

    @property
    def DATABASE_URL(self) -> str:
        """
        Constructs the database URL from individual components.
        Falls back to SQLite if PostgreSQL settings are not provided.
        """
        if all(
            [
                self.POSTGRES_USER,
                self.POSTGRES_PASSWORD,
                self.POSTGRES_DB,
                self.POSTGRES_HOST,
                self.POSTGRES_PORT,
            ]
        ):
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return "sqlite+aiosqlite:///data/spoticast.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
