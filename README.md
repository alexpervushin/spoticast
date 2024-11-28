# Spoticast 🎵

Spoticast — это Telegram бот, который превращает ваш канал в музыкальный статус, синхронизируясь с Spotify в реальном времени.

## Основная идея 🎯

Бот синхронизирует ваш Spotify с Telegram каналом, обновляя имя и фото канала в зависимости от текущей песни.

## Особенности 🚀

- **Обновления в реальном времени**: Меняет имя канала на название текущей песни
- **Фото канала**: Ставит обложку альбома как фото канала
- **Информация о треке**: Показывает детали песни, такие как:
  - Название и исполнитель
  - Альбом
  - Дата выхода
  - Длительность
  - Ссылки на:
    - Spotify
    - Яндекс Музыка
    - VK Музыка
    - YouTube

## Технологии 💻

### Основные
- Python
- FastAPI
- SQLAlchemy
- Aiogram

### Сервисы
- API Spotify
- Telegram Bot API

### Базы данных
- PostgreSQL
- SQLite (fallback)

### Библиотеки
- Pydantic
- aiohttp
- logging
- uvicorn

### Инфраструктура
- Docker
- Docker Compose
- Асинхронная архитектура

## Начало работы 🚀

### Предварительные требования

- Docker и Docker Compose
- [Аккаунт Spotify Developer](https://developer.spotify.com/)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/alexpervushin/spoticast.git
cd spoticast
```

2. Создайте файл `.env` в корневой директории:
```env
# Telegram settings
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
ADMIN_USER_ID=your_admin_id

# Spotify settings
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback

# Database settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=spoticast_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Uvicorn settings
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_LOG_LEVEL=info
```

3. Запустите проект через Docker Compose:
```bash
docker compose up -d
```

### Использование

1. **Настройка бота**:
   - Найдите вашего бота в Telegram (@your_bot_username)
   - Отправьте команду `/start`
   - Авторизуйтесь через Spotify, нажав на кнопку "Login to Spotify"

2. **Подключение канала**:
   - Создайте канал в Telegram
   - Добавьте бота как администратора канала
   - Используйте команду `/setchannel` для настройки канала
   - Перешлите боту любое сообщение из канала, чтобы он смог получить ID канала

3. **Управление**:
   - `/start` - Запуск бота и авторизация Spotify
   - `/toggle` - Включение/выключение обновлений
   - `/setchannel` - Настройка канала для обновлений
   - `/mychannel` - Информация о подключенном канале
   - `/listusers` - Список пользователей бота (только для админа)

## Вопросы и ответы 🤔

### Как получить Spotify Client ID и Client Secret?
1. Авторизуйтесь на [Spotify Developer](https://developer.spotify.com/)
2. Перейдите в [Dashboard](https://developer.spotify.com/dashboard/)
3. Создайте новое приложение
4. Скопируйте Client ID и Client Secret
5. Добавьте Redirect URI в настройках приложения

## TODO 📝
- [ ] Добавить Яндекс Музыку, VK Музыку, YouTube и др.
- [ ] Добавить тесты
- [ ] Локализация
- [ ] Статистика
- [ ] Рефакторинг и оптимизация кода
- [ ] Безопасность

## Лицензия 📄
[MIT](LICENSE)
