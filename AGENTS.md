# Instagram Tracker — руководство для агента

> Quick reference для Cursor и других агентов. Формальные требования — в `openspec/specs/`.

**Instagram Tracker** — локальный инструмент анализа подписчиков/подписок через официальный экспорт Instagram. Генерирует интерактивный HTML-дашборд.

## Стек

- Python (`main.py`, `app/`)
- Дашборд: HTML/CSS/JS, генерируется из `app/dashboard*.py`
- Enrichment аватарок: Playwright (`app/enricher.py`)
- Данные: `data/import/`, `data/snapshots/`, `data/avatars/`, `data/profiles.json`

## Перед изменениями

1. `README.md` — как пользоваться.
2. `openspec/specs/` — формальные требования (если capability уже есть).
3. Активные changes: `openspec/changes/` (не `archive/`).
4. Workflows: `/opsx:propose`, `/opsx:apply`, `/opsx:archive`.

## OpenSpec

- Артефакты на **русском**, normative keywords — **MUST/SHALL/MUST NOT** (не «ДОЛЖЕН»).
- Main specs: `## Purpose` + `## Requirements`; delta: `## ADDED/MODIFIED/REMOVED`.
- Проверка: `openspec validate --all`.
- Capability = подсистема, не мелкая фича.

## Приоритеты (кратко)

- Официальный экспорт JSON — единственный источник связей.
- Дашборд должен открываться офлайн (локальные аватарки).
- Не ломать генерацию снимков и обратную совместимость данных.
- UI: два варианта (V1 классический / V2 новый) допустимы, пока пользователь не выберет один.
