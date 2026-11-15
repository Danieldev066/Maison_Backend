from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import AdminUser, DbSession
from app.models import MenuCategory, MenuItem
from app.schemas import CategoryCreate, CategoryOut, CategoryPatch, MenuItemCreate, MenuItemOut, MenuItemPatch

router = APIRouter(prefix="/menu", tags=["Menu"])


def get_category(db: DbSession, category_id: int) -> MenuCategory:
    category = db.get(MenuCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def get_item(db: DbSession, item_id: int) -> MenuItem:
    item = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: DbSession):
    return db.scalars(select(MenuCategory).where(MenuCategory.is_active.is_(True)).order_by(MenuCategory.position, MenuCategory.id)).all()


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: DbSession, _: AdminUser):
    obj = MenuCategory(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists") from None
    db.refresh(obj)
    return obj


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryPatch, db: DbSession, _: AdminUser):
    obj = get_category(db, category_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        setattr(obj, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists") from None
    db.refresh(obj)
    return obj


@router.get("/items", response_model=list[MenuItemOut])
def list_menu_items(
    db: DbSession,
    category_id: int | None = None,
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    statement = select(MenuItem).join(MenuCategory).where(MenuItem.is_active.is_(True), MenuCategory.is_active.is_(True))
    if category_id is not None:
        statement = statement.where(MenuItem.category_id == category_id)
    if q:
        statement = statement.where(MenuItem.name.ilike(f"%{q}%"))
    return db.scalars(statement.order_by(MenuItem.id).offset(offset).limit(limit)).all()


@router.get("/items/{item_id}", response_model=MenuItemOut)
def menu_item_detail(item_id: int, db: DbSession):
    item = get_item(db, item_id)
    if not item.is_active or not item.category.is_active:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.post("/items", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: MenuItemCreate, db: DbSession, _: AdminUser):
    get_category(db, payload.category_id)
    obj = MenuItem(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/items/{item_id}", response_model=MenuItemOut)
def update_item(item_id: int, payload: MenuItemPatch, db: DbSession, _: AdminUser):
    obj = get_item(db, item_id)
    values = payload.model_dump(exclude_unset=True)
    if "category_id" in values and values["category_id"] is not None:
        get_category(db, values["category_id"])
    for key, value in values.items():
        if value is None and key != "image_url":
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/items/{item_id}", status_code=204)
def archive_item(item_id: int, db: DbSession, _: AdminUser):
    obj = get_item(db, item_id)
    obj.is_active = False
    db.commit()
