from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from typing import Dict
import asyncio
import os

from app.bot.states import ChannelState
from app.bot.utils import url_encode
from app.config import get_settings
from app.logger import logger
from app.database.repository import UserRepository
from app.database.connection import get_session
from app.services.spotify import SpotifyService
from app.bot.messages import MESSAGES

settings = get_settings()
spotify_service = SpotifyService()

active_update_tasks: Dict[int, asyncio.Task] = {}
telegram_bot = None
previous_tracks: Dict[int, dict] = {}


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main keyboard with common commands"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛑 Toggle Updates"),
                KeyboardButton(text="🎯 Set Channel"),
            ],
            [KeyboardButton(text="📢 My Channel")],
        ],
        resize_keyboard=True,
        persistent=True,
    )
    return keyboard


async def register_handlers(dp, bot):
    """Register all handlers"""
    global telegram_bot
    telegram_bot = bot

    async for session in get_session():
        user_repo = UserRepository(session)
        users = await user_repo.get_all_users()
        for user in users:
            if user.updates_enabled and user.channel_id:
                task = asyncio.create_task(
                    update_channel_with_spotify_info(user.telegram_id)
                )
                active_update_tasks[user.telegram_id] = task

    dp.message.register(handle_start_command, Command("start"))
    dp.message.register(handle_toggle_command, Command("toggle"))
    dp.message.register(handle_setchannel_command, Command("setchannel"))
    dp.message.register(handle_list_users_command, Command("listusers"))
    dp.message.register(handle_mychannel_command, Command("mychannel"))

    dp.message.register(handle_toggle_command, F.text == "🛑 Toggle Updates")
    dp.message.register(handle_setchannel_command, F.text == "🎯 Set Channel")
    dp.message.register(handle_mychannel_command, F.text == "📢 My Channel")

    dp.message.register(process_channel_id, ChannelState.waiting_for_channel_id)

    dp.channel_post.register(
        remove_channel_photo_update_message,
        F.content_type == types.ContentType.NEW_CHAT_PHOTO,
    )
    dp.channel_post.register(
        remove_channel_title_update_message,
        F.content_type == types.ContentType.NEW_CHAT_TITLE,
    )


async def handle_start_command(message: Message) -> None:
    logger.info(f"Start command received from user {message.from_user.id}")

    async for session in get_session():
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_telegram_id(message.from_user.id)

    if not user or not user.spotify_refresh_token:
        auth_url = spotify_service.get_auth_url(str(message.from_user.id))
        await message.answer(
            MESSAGES["welcome"],
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Login to Spotify", url=auth_url)]
                ]
            ),
        )
    elif not user.channel_id:
        await message.answer(MESSAGES["set_channel"], reply_markup=get_main_keyboard())
    else:
        if user.updates_enabled and message.from_user.id not in active_update_tasks:
            task = asyncio.create_task(
                update_channel_with_spotify_info(message.from_user.id)
            )
            active_update_tasks[message.from_user.id] = task
        await message.answer(
            MESSAGES["bot_configured"], reply_markup=get_main_keyboard()
        )


async def handle_toggle_command(message: Message) -> None:
    logger.info(f"Toggle command received from user {message.from_user.id}")

    async for session in get_session():
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_telegram_id(message.from_user.id)

        if not user or not user.channel_id:
            await message.answer(MESSAGES["no_channel_configured"])
            return

        is_active = await user_repo.toggle_updates(message.from_user.id)

    if is_active:
        if message.from_user.id in active_update_tasks:
            active_update_tasks[message.from_user.id].cancel()

        task = asyncio.create_task(
            update_channel_with_spotify_info(message.from_user.id)
        )
        active_update_tasks[message.from_user.id] = task
        await message.answer(MESSAGES["updates_enabled"])
    else:
        if message.from_user.id in active_update_tasks:
            active_update_tasks[message.from_user.id].cancel()
            del active_update_tasks[message.from_user.id]
        await message.answer(MESSAGES["updates_disabled"])


async def handle_setchannel_command(message: Message, state: FSMContext):
    await state.set_state(ChannelState.waiting_for_channel_id)
    await message.answer(MESSAGES["forward_channel_message"])


async def process_channel_id(message: Message, state: FSMContext):
    if message.forward_from_chat and message.forward_from_chat.type == "channel":
        channel_id = str(message.forward_from_chat.id)
    else:
        channel_id = message.text.strip()

    try:
        chat = await telegram_bot.get_chat(channel_id)

        bot_member = await telegram_bot.get_chat_member(chat.id, telegram_bot.id)
        if not isinstance(bot_member, types.ChatMemberAdministrator):
            await message.answer(MESSAGES["not_admin_in_channel"])
            await state.clear()
            return

        async for session in get_session():
            user_repo = UserRepository(session)
            success = await user_repo.save_channel_id(message.from_user.id, channel_id)

        if success:
            async for session in get_session():
                user_repo = UserRepository(session)
                user = await user_repo.get_user_by_telegram_id(message.from_user.id)

            if user.updates_enabled:
                if message.from_user.id in active_update_tasks:
                    active_update_tasks[message.from_user.id].cancel()

                task = asyncio.create_task(
                    update_channel_with_spotify_info(message.from_user.id)
                )
                active_update_tasks[message.from_user.id] = task

            await message.answer(
                MESSAGES["channel_configured"].format(channel_title=chat.title)
            )
        else:
            await message.answer(MESSAGES["spotify_login_first"])
    except Exception as e:
        logger.error(f"Error setting channel: {str(e)}")
        await message.answer(MESSAGES["channel_config_error"])

    await state.clear()


async def handle_list_users_command(message: Message) -> None:
    if message.from_user.id != settings.ADMIN_USER_ID:
        await message.answer(MESSAGES["no_permission_admin"])
        return

    async for session in get_session():
        user_repo = UserRepository(session)
        users = await user_repo.get_all_users()

    if not users:
        await message.answer(MESSAGES["no_users_found"])
        return

    response = MESSAGES["database_entry_template"]
    for user in users:
        token_display = (
            "Not set"
            if not user.spotify_refresh_token
            else f"{user.spotify_refresh_token[:20]}..."
        )
        response += MESSAGES["user_entry_template"].format(
            user_id=user.telegram_id,
            token_display=token_display,
            channel_id=user.channel_id,
            updates_enabled=user.updates_enabled,
        )

    if len(response) > settings.MAX_MESSAGE_LENGTH:
        for x in range(0, len(response), settings.MAX_MESSAGE_LENGTH):
            await message.answer(response[x : x + settings.MAX_MESSAGE_LENGTH])
    else:
        await message.answer(response)


async def remove_channel_photo_update_message(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Error removing channel photo update message: {e}")


async def remove_channel_title_update_message(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Error removing channel title update message: {e}")


async def handle_mychannel_command(message: Message) -> None:
    logger.info(f"Mychannel command received from user {message.from_user.id}")

    async for session in get_session():
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_telegram_id(message.from_user.id)

    if not user or not user.channel_id:
        await message.answer(MESSAGES["no_channel_configured"])
        return

    try:
        chat = await telegram_bot.get_chat(user.channel_id)
        await message.answer(
            MESSAGES["channel_info"].format(
                title=chat.title, channel_id=user.channel_id
            )
        )
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        await message.answer(MESSAGES["channel_config_error"])


async def update_channel_with_spotify_info(user_id: int):
    logger.info(f"Updating channel info for user {user_id}")
    try:
        while True:
            try:
                async for session in get_session():
                    user_repo = UserRepository(session)
                    user = await user_repo.get_user_by_telegram_id(user_id)

                if not user or not user.channel_id or not user.updates_enabled:
                    break

                access_token = await spotify_service.refresh_access_token(
                    user.spotify_refresh_token
                )
                current_track = await spotify_service.get_current_track(access_token)

                if current_track and current_track != previous_tracks.get(user_id):
                    logger.info(
                        f"Updating channel info for: {current_track['title']} - {current_track['artists']}"
                    )

                    channel_title = (
                        f"{current_track['title']} - {current_track['artists']}"
                    )
                    await telegram_bot.set_chat_title(
                        chat_id=user.channel_id, title=channel_title[:255]
                    )

                    album_cover = await spotify_service.download_album_cover(
                        current_track["album_cover_url"]
                    )
                    if album_cover:
                        duration_min, duration_sec = divmod(
                            current_track["duration_ms"] // 1000, 60
                        )
                        search_text = url_encode(
                            f"{current_track['title']} {current_track['artists']}"
                        )

                        caption = MESSAGES["track_info_template"].format(
                            title=current_track["title"],
                            artists=current_track["artists"],
                            album=current_track["album"],
                            release_date=current_track["release_date"],
                            duration=f"{duration_min}:{duration_sec:02d}",
                            track_url=current_track["track_url"],
                            search_text=search_text,
                        )

                        await telegram_bot.send_photo(
                            chat_id=user.channel_id,
                            photo=FSInputFile(album_cover),
                            caption=caption,
                            parse_mode="Markdown",
                        )

                        await telegram_bot.set_chat_photo(
                            chat_id=user.channel_id, photo=FSInputFile(album_cover)
                        )
                        os.remove(album_cover)

                    previous_tracks[user_id] = current_track

            except Exception as e:
                logger.error(f"Error in update loop for user {user_id}: {str(e)}")
                await asyncio.sleep(30)
                continue

            await asyncio.sleep(settings.SPOTIFY_UPDATE_INTERVAL)
    except Exception as e:
        logger.error(f"Fatal error in channel update for user {user_id}: {str(e)}")
        raise
