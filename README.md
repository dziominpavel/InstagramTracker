# Instagram Tracker

Простой трекер подписчиков и подписок Instagram через официальный экспорт данных.

## Что делает программа

1. Читает JSON-файлы из официального архива Instagram.
2. Сохраняет снимок (snapshot) с подписчиками, подписками и другими списками.
3. Сравнивает снимки между собой и показывает изменения: кто подписался, отписался, сменил ник и т.д.
4. Показывает текущие списки: заблокированные, скрытые из историй, недавно отписанные, заявки в подписчики.

## Пошаговая инструкция

### 1. Заказать архив данных Instagram

Открой в браузере:

```text
https://accountscenter.instagram.com/info_and_permissions/dyi/
```

1. Войди в свой аккаунт Instagram.
2. Нажми **"Скачать данные"** или **"Download your information"**.
3. Выбери:
   - **Аккаунты** — свой Instagram.
   - **Диапазон дат** — "Все время" / "All time".
   - **Формат** — **JSON**.
   - **Качество медиа** — можно "Низкое", чтобы архив был меньше.
4. Нажми **"Запросить"**.

Instagram пришлет письмо со ссылкой на скачивание. Обычно это занимает от нескольких минут до суток.

### 2. Разархивировать архив

Скачай zip-архив и разархивируй его в любую папку. Внутри будет примерно такая структура:

```text
instagram-<username>-<date>-<hash>/
├── connections/
│   ├── contacts/
│   ├── followers_and_following/
│   └── ...
├── your_instagram_activity/
├── personal_information/
└── ...
```

### 3. Скопировать нужные файлы

Программе нужна папка:

```text
<архив>/connections/followers_and_following/
```

Скопируй **всё содержимое** этой папки в папку проекта:

```text
data/import/
```

Должно получиться так:

```text
data/import/
  blocked_profiles.json
  followers_1.json
  following.json
  hide_story_from.json
  recent_follow_requests.json
  recently_unfollowed_profiles.json
```

> Важно: не нужно копировать всю папку `connections`, только `followers_and_following`. Остальные файлы из архива программа не использует.

### 4. Запустить импорт

```bash
python main.py sync
```

Программа создаст снимок в `data/snapshots/`.

### 5. Смотреть результаты

```bash
python main.py status       # последний снимок
python main.py stats        # статистика по всем снимкам
python main.py history      # изменения между снимками
python main.py lists        # текущие списки: блокировки, скрытые истории и т.д.
```

## Команды

| Команда | Описание |
|---------|----------|
| `sync` | Импортировать данные из `data/import`. |
| `status` | Последний сохраненный снимок. |
| `stats` | Статистика по всем снимкам. |
| `history` | Изменения между двумя последними снимками. |
| `lists` | Специальные списки: блокировки, скрытые истории, заявки, отписавшиеся. |
| `export` | Экспорт снимка в JSON или CSV. |
| `config` | Текущая конфигурация. |

## Пример рабочего цикла

```bash
# 1. Положить JSON-файлы в data/import
# 2. Импортировать
python main.py sync

# 3. Посмотреть статистику
python main.py status

# 4. Через неделю повторить и сравнить
python main.py sync --date 2026-07-17
python main.py history
```

## Структура

```text
instagram-tracker/
├── app/
│   ├── clients/          # OfficialExportClient
│   ├── config/           # Settings + logger
│   ├── models/           # User, Snapshot, Event
│   ├── repositories/     # JsonRepository
│   ├── services/         # Sync, Analytics
│   └── main.py           # CLI
├── config/
│   └── config.json       # target_username
├── data/
│   ├── import/           # сюда копируешь JSON из Instagram
│   └── snapshots/        # сохраненные снимки
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

Instagram не включает `user_id` в файлы `followers_1.json` и `following.json`. В качестве ключа используется `username`. Если человек сменит ник, программа посчитает его новым пользователем.
