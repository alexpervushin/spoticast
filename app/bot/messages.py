# Templates
MESSAGES = {
    "welcome": "Сначала войдите в Spotify, нажав на эту ссылку",
    "set_channel": "Добавьте меня в канал и отправьте команду /setchannel",
    "spotify_login_first": "Пожалуйста, сначала войдите в Spotify используя команду /start",
    "channel_config_error": (
        "Не удалось настроить канал. Убедитесь, что:\n"
        "1. ID канала указан верно\n"
        "2. Бот добавлен в канал как администратор\n"
        "3. У бота есть права на изменение информации канала"
    ),
    "track_info_template": (
        "🎵 {title}\n"
        "👤 {artists}\n"
        "💿 {album}\n"
        "📅 {release_date}\n"
        "⏱ {duration}\n"
        "🔗 [Spotify]({track_url})\n"
        "🎧 [Яндекс Музыка](https://music.yandex.ru/search?text={search_text})\n"
        "🎵 [VK Музыка](https://vk.com/audio?q={search_text})\n"
        "▶️ [YouTube](https://www.youtube.com/results?search_query={search_text})\n\n"
    ),
    "channel_configured": "Канал успешно настроен: {channel_title}",
    "no_permission_admin": "У вас нет прав для использования этой команды.",
    "no_users_found": "Пользователи не найдены в базе данных.",
    "database_entry_template": "Записи в базе данных:\n\n",
    "user_entry_template": (
        "👤 ID пользователя: {user_id}\n"
        "🔑 Токен: {token_display}\n"
        "📢 Канал: {channel_id}\n"
        "🔄 Обновления: {updates_enabled}\n"
        "----------------------\n"
    ),
    "forward_channel_message": (
        "Пожалуйста, перешлите любое сообщение из канала, который вы хотите обновлять.\n"
        "Убедитесь, что я добавлен как администратор в этот канал!"
    ),
    "not_admin_in_channel": (
        "Мне нужны права администратора в канале для его обновления.\n"
        "Пожалуйста, добавьте меня как администратора\n"
        "Затем попробуйте /setchannel снова."
    ),
    "channel_info": "Ваш канал:\nНазвание: {title}\nID: {channel_id}",
    "no_channel_configured": "У вас еще не настроен канал. Используйте /setchannel для настройки.",
    "bot_configured": "Бот настроен! Используйте '🔄 Переключить обновления' чтобы включить/выключить обновления канала.",
    "updates_enabled": "Обновления канала включены! Ваш канал теперь будет обновляться в соответствии с вашей активностью в Spotify.",
    "updates_disabled": "Обновления канала отключены. Ваш канал больше не будет обновляться.",
}
