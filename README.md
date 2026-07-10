# Instagram Tracker

Pet-проект для отслеживания изменений подписчиков и подписок в Instagram.

## Возможности

- Хранение снимков followers/following в JSON-файлах.
- Сравнение снимков и построение отчетов.
- Событийная модель: `FOLLOWED`, `UNFOLLOWED`, `USERNAME_CHANGED`, `NAME_CHANGED`, `BECAME_PRIVATE`, `BECAME_PUBLIC`, `PROFILE_PHOTO_CHANGED`.
- Mock-режим для разработки и тестирования без Instagram.
- Архитектурный интерфейс `InstagramClient` позволяет подключить `InstagrapiClient` или импорт архива данных позже.
- CLI на `Typer` + красивый вывод на `Rich`.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Открой `config/config.json` и укажи `target_username`.

### Для работы с реальным Instagram

Создай файл `.env` рядом с `.env.example`:

```env
INSTAGRAM_USERNAME=your_login
INSTAGRAM_PASSWORD=your_password
```

Проверь вход:

```bash
python main.py login
```

Если сессия сохранится, повторный ввод пароля не понадобится.

Синхронизируй данные:

```bash
python main.py sync --instagram
```

### Mock-режим

```bash
python main.py sync --mock --date 2026-07-09
# измени data/mock/followers.json / data/mock/following.json
python main.py sync --mock --date 2026-07-10
python main.py history
```

### Импорт из файлов

```bash
python main.py sync --followers-file data/export/followers.json --following-file data/export/following.json
```

## Команды

| Команда | Описание |
|---------|----------|
| `login` | Заглушка для будущей авторизации через Instagram. |
| `sync` | Загрузить и сохранить снимок. Поддерживает `--mock`, `--followers-file`, `--following-file`, `--date`. |
| `status` | Показать последний сохраненный снимок. |
| `stats` | Статистика по всем снимкам. |
| `history` | Изменения между двумя последними снимками. |
| `report` | Показать отчет за дату. |
| `export` | Экспорт снимка в JSON или CSV. |
| `config` | Показать текущую конфигурацию. |

## Структура

```
instagram-tracker/
├── app/
│   ├── clients/         # InstagramClient Protocol + реализации
│   ├── config/          # Settings + logger
│   ├── models/          # User, Snapshot, Event
│   ├── repositories/    # Repository Protocol + JsonRepository
│   ├── services/        # SyncService, AnalyticsService, ReportService
│   ├── session/         # SessionManager
│   └── main.py          # Typer CLI
├── config/
│   ├── config.json      # настройки
│   └── session.json     # сессия Instagram (в .gitignore)
├── data/
│   ├── export/          # файлы для ArchiveClient
│   ├── mock/            # файлы для MockClient
│   ├── snapshots/       # сохраненные снимки
│   └── reports/         # отчеты
├── logs/
├── tests/
└── main.py              # точка входа
```

## Архитектура

- `InstagramClient` — `Protocol`. Реализации: `MockClient`, `ArchiveClient`, `InstagrapiClient` (заготовка).
- `Repository` — `Protocol`. Сейчас `JsonRepository`, в будущем можно заменить на `SqliteRepository`.
- `AnalyticsService` не зависит от источника данных: ему нужны только `Snapshot`.

## Тесты

```bash
pytest tests -v
```
