# MAISON — пакет №2: Меню + ресторан

Заменить заглушки menu.py / restaurant.py: категории, блюда, профиль ресторана, CRUD администратора, seed.

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
git commit -m "feat: maison menu-catalog"
git push -u origin HEAD
```

5. На GitHub создай Pull Request: `твоя ветка` → `main`; попроси другого участника проверить и слить после тестов.
6. Следующий человек начинает свой пакет только после мержа этого PR. Никто не делает `git push origin main` напрямую.

## Что входит

- `app/api/menu.py`
- `app/api/restaurant.py`
- `scripts/__init__.py`
- `scripts/seed.py`
- `tests/test_menu_catalog.py`

