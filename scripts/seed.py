"""Idempotent demo fixtures. Run: python -m scripts.seed"""
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import DiningTable, MenuCategory, MenuItem, RestaurantInfo, User


def seed():
    settings = get_settings()
    with SessionLocal() as db:
        if db.scalar(select(RestaurantInfo)) is None:
            db.add(RestaurantInfo(
                name="MAISON Restaurant",
                description="Демонстрационное описание ресторана. Замените его в админке.",
                address="Укажите адрес ресторана",
                phone="",
                opening_hours="Укажите часы работы",
            ))
        for category_name, position, dishes in [
            ("Основные блюда", 1, [("Паста с грибами", 480), ("Курица с овощами", 560)]),
            ("Закуски", 2, [("Овощной салат", 290), ("Сырная тарелка", 490)]),
            ("Напитки", 3, [("Лимонад", 180), ("Чай", 120)]),
        ]:
            category = db.scalar(select(MenuCategory).where(MenuCategory.name == category_name))
            if category is None:
                category = MenuCategory(name=category_name, position=position)
                db.add(category)
                db.flush()
            for name, price in dishes:
                exists = db.scalar(select(MenuItem.id).where(MenuItem.category_id == category.id, MenuItem.name == name))
                if not exists:
                    db.add(MenuItem(category_id=category.id, name=name, price_som=price, description="Демонстрационное блюдо"))
        for table_number, seats in [("A1", 2), ("A2", 2), ("B1", 4), ("B2", 4), ("C1", 6)]:
            if db.scalar(select(DiningTable.id).where(DiningTable.number == table_number)) is None:
                db.add(DiningTable(number=table_number, seats=seats))
        if settings.SEED_ADMIN_EMAIL and settings.SEED_ADMIN_PASSWORD:
            if len(settings.SEED_ADMIN_PASSWORD) < 12:
                raise ValueError("SEED_ADMIN_PASSWORD must be at least 12 characters")
            email = settings.SEED_ADMIN_EMAIL.strip().lower()
            if db.scalar(select(User.id).where(User.email == email)) is None:
                db.add(User(email=email, full_name="MAISON Administrator", role="admin", password_hash=hash_password(settings.SEED_ADMIN_PASSWORD)))
        db.commit()
    print("Demo data seeded (existing records preserved).")


if __name__ == "__main__":
    seed()
