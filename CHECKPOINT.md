# Instagram Tracker — чекпоинты

## Выбранная архитектура

Проект использует **JSON-БД** вместо SQLAlchemy/SQLite. Это максимально просто и покрывает текущую цель: получить списки followers/following и сравнивать их между снимками.

### Почему JSON

- Не нужно писать миграции.
- Снимки — это просто файлы на диске.
- Сравнение делается в Python через множества (`set`).
- Легко добавить SQLite позже, если масштабирование потребуется.

### Стек

- Python 3.13+
- `instagrapi` — доступ к Instagram
- `Typer` — CLI
- `Rich` — красивый вывод в консоль
- `python-dotenv` + `pydantic` — конфигурация
- `APScheduler` — автосинхронизация в будущем
- JSON-файлы — хранение данных

---

## Структура проекта

```text
instagram-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py                 # точка входа Typer
│   ├── commands/               # CLI-команды
│   │   ├── sync.py
│   │   ├── status.py
│   │   ├── followers.py
│   │   ├── following.py
│   │   ├── not_following_back.py
│   │   ├── i_dont_follow_back.py
│   │   ├── history.py
│   │   └── stats.py
│   ├── config/                 # настройки, логирование
│   │   ├── settings.py
│   │   └── logger.py
│   ├── instagram/              # обертка над instagrapi
│   │   └── client.py
│   ├── services/               # бизнес-логика
│   │   ├── sync_service.py
│   │   └── analytics_service.py
│   ├── storage/                # работа с JSON-файлами
│   │   ├── __init__.py
│   │   └── json_db.py
│   └── utils/                  # мелкие хелперы
│       ├── dt.py
│       └── filesystem.py
├── data/                       # JSON-БД + session.json
│   ├── snapshots/              # папки со снимками
│   ├── accounts.json           # кэш username -> user_id
│   └── index.json              # индекс снимков
├── logs/                       # логи
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Структура JSON-БД

### `data/snapshots/YYYY-MM-DD_HH-MM-SS/`

Каждый снимок — отдельная папка с тремя файлами:

#### `followers.json`

```json
[
  {"user_id": "123", "username": "alice", "full_name": "Alice"},
  {"user_id": "456", "username": "bob", "full_name": "Bob"}
]
```

#### `following.json`

Формат такой же, как `followers.json`.

#### `meta.json`

```json
{
  "timestamp": "2026-07-10T20-30-00",
  "followers_count": 150,
  "following_count": 200
}
```

### `data/accounts.json`

Глобальный кэш аккаунтов. Нужен, чтобы переименования username не ломали историю.

```json
{
  "123": {"username": "alice", "full_name": "Alice"},
  "456": {"username": "bob", "full_name": "Bob"}
}
```

### `data/index.json`

Индекс всех снимков.

```json
[
  {
    "timestamp": "2026-07-10T20-30-00",
    "dir": "2026-07-10_20-30-00",
    "followers_count": 150,
    "following_count": 200
  }
]
```

---

## Чекпоинты

### Этап 1. Подготовка окружения

- [x] Создать папку проекта и инициализировать git.
- [x] Создать workspace-файл.
- [x] Создать `.env.example`, `.gitignore`, `requirements.txt`.
- [ ] Создать `.env` из `.env.example` и заполнить свои данные.
- [ ] Создать виртуальное окружение и установить зависимости:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```
- [ ] Настроить базовое логирование (`app/config/logger.py`).

### Этап 2. JSON-хранилище

- [ ] Реализовать `app/storage/json_db.py` с минимальным API:
  - [ ] `_ensure_data_dirs()` — создает `data/snapshots/`, `logs/`.
  - [ ] `load_index() -> list` — загружает `data/index.json` или возвращает `[]`.
  - [ ] `save_index(index: list)` — сохраняет `data/index.json`.
  - [ ] `load_accounts() -> dict` — загружает `data/accounts.json` или возвращает `{}`.
  - [ ] `save_accounts(accounts: dict)` — сохраняет `data/accounts.json`.
  - [ ] `save_snapshot(timestamp, followers, following, meta)` — создает папку снимка и файлы.
  - [ ] `load_snapshot(timestamp) -> dict` — возвращает `{followers, following, meta}`.
  - [ ] `list_snapshots() -> list` — возвращает индекс, отсортированный по времени.
  - [ ] `latest_snapshot() -> dict | None` — последний снимок.
- [ ] Написать тест на сохранение/загрузку снимка.

### Этап 3. Instagram-клиент

- [ ] Создать `app/instagram/client.py`:
  - [ ] `InstagramClient(config)` — принимает настройки.
  - [ ] `login_or_load_session()` — пытается загрузить `session.json`; если нет — логинится и сохраняет.
  - [ ] `get_user_id(username) -> str` — получает user_id целевого аккаунта.
  - [ ] `get_followers(user_id, amount=0) -> list[dict]` — возвращает список словарей с `user_id`, `username`, `full_name`.
  - [ ] `get_following(user_id, amount=0) -> list[dict]` — аналогично.
  - [ ] Обработка ошибок: нет сети, капча, 2FA, неверный пароль, бан.
- [ ] Первый ручной тест: получить followers/following своего аккаунта.

### Этап 4. Синхронизация

- [ ] Создать `app/services/sync_service.py`:
  - [ ] `SyncService(client, storage)`.
  - [ ] `run()` — логин, получение данных, сохранение снимка, обновление `accounts.json`, обновление `index.json`.
- [ ] Создать команду `app/commands/sync.py`:
  - [ ] `tracker sync` — запускает синхронизацию.
  - [ ] Выводит progress через `Rich`.
- [ ] Проверить, что после `sync` появляется папка в `data/snapshots/`.

### Этап 5. CLI-команды аналитики

- [ ] `app/commands/status.py` — `tracker status`.
  - Дата последнего снимка, followers_count, following_count.
- [ ] `app/commands/followers.py` — `tracker followers`.
  - Список подписчиков из последнего снимка.
- [ ] `app/commands/following.py` — `tracker following`.
  - Список подписок из последнего снимка.
- [ ] `app/commands/not_following_back.py` — `tracker not-following-back`.
  - Ты подписан, а тебя нет.
- [ ] `app/commands/i_dont_follow_back.py` — `tracker i-dont-follow-back`.
  - На тебя подписаны, а ты нет.
- [ ] `app/commands/stats.py` — `tracker stats`.
  - Динамика followers/following по всем снимкам.
- [ ] Подключить все команды в `app/main.py`.

### Этап 6. История изменений

- [ ] Создать `app/services/analytics_service.py`:
  - [ ] `diff(snap_a, snap_b) -> dict` — подписался/отписался, ты подписался/отписался.
  - [ ] `not_following_back(snap) -> list`.
  - [ ] `i_dont_follow_back(snap) -> list`.
  - [ ] `mutual(snap) -> list`.
- [ ] `app/commands/history.py` — `tracker history`.
  - [ ] По умолчанию сравнивает два последних снимка.
  - [ ] Опционально `--from` и `--to` для выбора снимков.
- [ ] Добавить красивый вывод через `Rich` (таблицы, цвета).

### Этап 7. Автосинхронизация и расширения (опционально)

- [ ] Подключить `APScheduler` для ежедневного `sync`.
- [ ] Telegram-бот для уведомлений.
- [ ] FastAPI Web UI.
- [ ] PySide6 GUI.
- [ ] Экспорт CSV/Excel.
- [ ] Графики динамики подписчиков.
- [ ] Избранные аккаунты.

---

## Первый шаг при новой сессии

1. Открыть workspace: `C:\projects\instagram-tracker.code-workspace`.
2. Скопировать `.env.example` в `.env` и заполнить:
   ```text
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password
   TARGET_USERNAME=your_username
   SESSION_PATH=data/session.json
   DATA_DIR=data
   LOG_LEVEL=INFO
   LOG_DIR=logs
   ```
3. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Начать с **этапа 2** — реализовать `app/storage/json_db.py`.

---

## Заметки

- `session.json` и `data/*.json` не коммитятся в git (см. `.gitignore`).
- Пароль не хранится — после первого логина используется только `session.json`.
- Пока цель минимальна: получить данные и сравнить. Всё остальное — по твоему запросу.
