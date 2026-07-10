# Instagram Tracker

Простой инструмент для анализа подписчиков и подписок Instagram через официальный экспорт данных. Генерирует красивый HTML-дашборд.

## Как работает

1. Скачиваешь официальный архив данных Instagram.
2. Копируешь JSON-файлы из папки `connections/followers_and_following/` в `data/import`.
3. Запускаешь `python main.py generate` — получаешь `index.html` с дашбордом.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

В `config/config.json` укажи свой `target_username`.

## Скачать архив Instagram

1. Открой в браузере:
   ```text
   https://accountscenter.instagram.com/info_and_permissions/dyi/
   ```
2. Войди в аккаунт и нажми **"Скачать данные"**.
3. Выбери:
   - **Some of your information** (не All).
   - **Connections → Followers and following**.
   - Формат: **JSON**.
   - Диапазон: **All time**.
4. Дождись письма со ссылкой и скачай архив.

## Подготовить файлы

Разархивируй архив. Найди папку:

```text
<архив>/connections/followers_and_following/
```

Скопируй **все** файлы из неё в папку проекта:

```text
data/import/
  blocked_profiles.json
  followers_1.json
  following.json
  hide_story_from.json
  recent_follow_requests.json
  recently_unfollowed_profiles.json
```

## Сгенерировать дашборд

```bash
python main.py generate
```

Открой `index.html` в браузере.

## Команды

| Команда | Описание |
|---------|----------|
| `generate` | Создать HTML-дашборд из `data/import`. |
| `history` | Показать сохраненные снимки. |
| `config` | Показать конфигурацию. |

## Дашборд

HTML-страница показывает:
- количество подписчиков, подписок, заблокированных, скрытых из историй, отписанных и заявок;
- изменения по сравнению с предыдущим снимком;
- таблицы со всеми списками и ссылками на профили Instagram.

## Структура

```text
instagram-tracker/
├── app/
│   ├── config/         # config.json loader
│   ├── dashboard.py      # HTML generator
│   ├── main.py         # CLI
│   ├── models.py       # User + Snapshot
│   ├── parser.py       # Instagram export JSON parser
│   └── storage.py      # snapshots storage
├── config/
│   └── config.json     # target_username
├── data/
│   ├── import/         # JSON files from Instagram export
│   └── snapshots/      # saved snapshots for history
├── main.py             # entry point
├── index.html          # generated dashboard
└── requirements.txt
```

## Ограничение

Instagram не включает `user_id` в экспорт. Ключом является `username`. Если человек сменит ник, программа посчитает его новым пользователем.
