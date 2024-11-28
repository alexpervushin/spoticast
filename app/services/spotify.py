from aiohttp import ClientSession
import base64
from typing import Optional, Dict, Any
from app.config import get_settings
from app.logger import logger

settings = get_settings()


class SpotifyService:
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.auth_url = settings.SPOTIFY_AUTH_URL
        self.token_url = settings.SPOTIFY_TOKEN_URL
        self.api_url = settings.SPOTIFY_API_URL
        self.redirect_uri = settings.SPOTIFY_REDIRECT_URI

    def get_auth_url(self, state: str) -> str:
        """Generate Spotify authorization URL"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": settings.SPOTIFY_SCOPES,
            "state": state,
        }

        auth_url = f"{self.auth_url}"
        if params:
            auth_url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

        return auth_url

    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for refresh token"""
        try:
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            async with ClientSession() as session:
                async with session.post(
                    self.token_url,
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                ) as response:
                    token_data = await response.json()
                    return token_data.get("refresh_token")
        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Get new access token using refresh token"""
        try:
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            async with ClientSession() as session:
                async with session.post(
                    self.token_url,
                    headers={"Authorization": f"Basic {auth_header}"},
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    },
                ) as response:
                    token_data = await response.json()
                    return token_data.get("access_token")
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return None

    async def get_current_track(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user's currently playing track"""
        try:
            async with ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/me/player/currently-playing",
                    headers={"Authorization": f"Bearer {access_token}"},
                ) as response:
                    if response.status == 204:
                        return None

                    track_data = await response.json()
                    return {
                        "title": track_data["item"]["name"],
                        "artists": ", ".join(
                            [artist["name"] for artist in track_data["item"]["artists"]]
                        ),
                        "album": track_data["item"]["album"]["name"],
                        "release_date": track_data["item"]["album"]["release_date"],
                        "duration_ms": track_data["item"]["duration_ms"],
                        "album_cover_url": track_data["item"]["album"]["images"][0][
                            "url"
                        ],
                        "track_url": track_data["item"]["external_urls"]["spotify"],
                    }
        except Exception as e:
            logger.error(f"Error fetching current track: {str(e)}")
            return None

    async def download_album_cover(self, url: str) -> Optional[str]:
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        cover_filename = settings.TEMP_ALBUM_COVER
                        with open(cover_filename, "wb") as f:
                            f.write(await response.read())
                        return cover_filename
            return None
        except Exception as e:
            logger.error(f"Error downloading album cover: {str(e)}")
            return None
