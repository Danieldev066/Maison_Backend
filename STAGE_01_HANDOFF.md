# MAISON — пакет №1: Auth + общая основа

Подготовить зависимости, единую БД, миграцию, JWT, регистрацию и профиль. Пустые модули API уже подключены в app/main.py.

**Важно:** Открой СВОЮ существующую ветку. Новую ветку создавать не нужно. Прежде чем копировать файлы, предыдущий Pull Request должен быть уже слит в `main`.

```powershell
git status --short
git switch ИМЯ_СВОЕЙ_СУЩЕСТВУЮЩЕЙ_ВЕТКИ
git fetch origin
git merge origin/main
```

Если `git status --short` показал файлы до копирования — сначала разберись с ними, иначе можно случайно перезаписать свою работу.

1. Распакуй этот архив во временную папку.
2. Скопируй *содержимое* папки из архива в корень backend-проекта (там где `app/`). Не копируй саму обёртку папки. Если Git предупреждает о различиях с вашим уже написанным кодом, сравните изменения перед заменой.
3. Выполни `python -m pip install -r requirements.txt` (если ещё не устанавливал), `pytest -q`.
4. Если тесты зелёные, сделай коммит и push только в СВОЮ ветку:

```powershell
git status --short
git add -A
git commit -m "feat: maison auth-foundation"
git push -u origin HEAD
```

5. На GitHub создай Pull Request: `твоя ветка` → `main`; попроси другого участника проверить и слить после тестов.
6. Следующий человек начинает свой пакет только после мержа этого PR. Никто не делает `git push origin main` напрямую.

## Что входит

- `.env.example`
- `.gitignore`
- `alembic.ini`
- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/auth.py`
- `app/api/menu.py`
- `app/api/orders.py`
- `app/api/reservations.py`
- `app/api/restaurant.py`
- `app/core/__init__.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/db/__init__.py`
- `app/db/base.py`
- `app/db/session.py`
- `app/dependencies.py`
- `app/main.py`
- `app/models.py`
- `app/schemas.py`
- `migrations/env.py`
- `migrations/versions/0001_initial.py`
- `requirements.txt`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_auth_users.py`

