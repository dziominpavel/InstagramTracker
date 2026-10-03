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

<!-- versioning:begin -->
## Версии и changelog (обязательно)

- Версия проекта меняется **только в момент релиза**: бамп вне релиза запрещён,
  между релизами номер остаётся номером последнего релиза. У статического трека
  версия заморожена и не меняется вовсе.
- Каждая пользовательская правка сопровождается пунктом в секции `## [Unreleased]`
  файла `CHANGELOG.md` — в момент работы, а не перед релизом. Чистые доки, спеки,
  тесты, CI и внутренний рефактор в changelog не пишутся.
- Релиз (где есть конвейер): `release.ps1 -Prepare` → сборка артефактов в `dist/`
  → `release.ps1`. Порядок не меняется.
- Сверка перед работой и после: `python scripts/check-version.py`
  (exit 0 — версия и changelog согласованы, exit 1 — рассинхрон).
- Полные правила и запреты: `docs/versioning.md`.
<!-- versioning:end -->
