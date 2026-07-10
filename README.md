# Instagram Tracker

Простой трекер подписчиков/подписок Instagram через официальный экспорт данных.

## Как работает

1. Скачиваешь официальный архив данных из Instagram.
2. Копируешь папку `connections` из архива в папку `data/import` проекта.
3. Запускаешь `python main.py sync` — данные записываются в снимок.
4. Через время повторяешь и сравниваешь через `python main.py history`.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

В `config/config.json` укажи `target_username`.

## Скачать архив Instagram

Перейди по ссылке:

```text
https://accountscenter.instagram.com/info_and_permissions/dyi/
```

Выбери:
- свой Instagram-аккаунт,
- формат **JSON**,
- диапазон — "All time".

Архив придет письмом. Скачай и разархивируй.

## Импорт данных

Нужна только папка `connections` из архива. Скопируй её содержимое в `data/import`:

```text
data/import/
  followers_1.json
  following.json
  recently_unfollowed_profiles.json
```

Запускаешь:

```bash
python main.py sync
```

Программа создаст снимок в `data/snapshots/`.

## Команды

```bash
python main.py sync              # импорт из data/import
python main.py status            # последний снимок
python main.py stats             # статистика
python main.py history           # изменения между снимками
python main.py report            # отчет
python main.py export            # экспорт снимка в JSON/CSV
python main.py config            # конфигурация
```

## Пример работы

```bash
python main.py sync
python main.py status
python main.py history
```

## Структура

```
instagram-tracker/
├── app/
│   ├── clients/          # OfficialExportClient + MockClient
│   ├── config/           # Settings + logger
│   ├── models/           # User, Snapshot, Event
│   ├── repositories/     # JsonRepository
│   ├── services/         # Sync, Analytics, Report
│   └── main.py           # CLI
├── config/
│   └── config.json       # target_username
├── data/
│   ├── import/           # сюда копируешь JSON из Instagram
│   ├── snapshots/        # сохраненные снимки
│   └── reports/          # отчеты
├── logs/
├── tests/
├── main.py               # точка входа
└── requirements.txt
```

## Тесты

```bash
pytest tests -v
```

## Ограничение

Instagram не включает `user_id` в файлы `followers_1.json` и `following.json`. Поэтому в качестве ключа используется `username`. Если человек сменит ник, программа посчитает его новым пользователем.
