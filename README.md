# Instagram Tracker

Pet-проект для отслеживания изменений подписчиков и подписок в Instagram через официальный экспорт данных.

## Как это работает

1. Заказываешь официальный архив данных в Instagram.
2. Кладешь zip-архив в корень проекта.
3. Запускаешь `python main.py sync` — программа сама разархивирует и импортирует followers/following.
4. Сравниваешь снимки через `python main.py history`.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

Открой `config/config.json` и укажи `target_username`.

### Скачать архив данных Instagram

Перейди по ссылке:

```text
https://accountscenter.instagram.com/info_and_permissions/dyi/
```

Выбери:
- аккаунт Instagram,
- формат **JSON**,
- диапазон данных — можно сразу "All time".

Архив придет письмом. Скачай zip и положи в корень проекта.

### Импорт и анализ

```bash
python main.py sync
python main.py status
python main.py stats
python main.py history
```

Если нужно указать дату снимка:

```bash
python main.py sync --date 2026-07-10
```

## Команды

| Команда | Описание |
|---------|----------|
| `sync` | Импортировать followers/following из официального архива. |
| `status` | Последний сохраненный снимок. |
| `stats` | Статистика по всем снимкам. |
| `history` | Изменения между двумя последними снимками. |
| `report` | Отчет за дату. |
| `export` | Экспорт снимка в JSON или CSV. |
| `config` | Текущая конфигурация. |

## Структура

```
instagram-tracker/
├── app/
│   ├── clients/          # InstagramClient + OfficialExportClient + MockClient
│   ├── config/           # Settings + logger
│   ├── models/           # User, Snapshot, Event
│   ├── repositories/    # JsonRepository
│   ├── services/         # SyncService, AnalyticsService, ReportService
│   └── main.py           # Typer CLI
├── config/
│   └── config.json       # target_username и настройки
├── data/
│   ├── export/           # zip-архивы и разархивированные данные
│   ├── snapshots/        # сохраненные снимки
│   └── reports/          # отчеты
├── logs/
├── tests/
├── main.py               # точка входа
└── requirements.txt
```

## Архитектура

- `Repository` — интерфейс хранилища. Сейчас `JsonRepository`, в будущем можно заменить на `SQLiteRepository`.
- `AnalyticsService` не знает про Instagram: ему нужны только `Snapshot` и `User`.
- `OfficialExportClient` читает `followers_*.json` и `following.json` из официального архива.

## Тесты

```bash
pytest tests -v
```

## Ограничение официального архива

Instagram не включает `user_id` в файлы followers/following. Вместо этого используется `username` как ключ. Если человек сменит ник, программа посчитает его новым пользователем. Это ограничение самого Instagram, а не программы.
