from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import AdminUser, DbSession
from app.models import RestaurantInfo
from app.schemas import RestaurantOut, RestaurantPatch

router = APIRouter(prefix="/restaurant", tags=["Restaurant"])


def get_restaurant_or_404(db: DbSession) -> RestaurantInfo:
    obj = db.scalar(select(RestaurantInfo).order_by(RestaurantInfo.id))
    if obj is None:
        raise HTTPException(status_code=404, detail="Restaurant not initialized; run demo seed")
    return obj


@router.get("", response_model=RestaurantOut)
def restaurant(db: DbSession):
    return get_restaurant_or_404(db)


@router.patch("", response_model=RestaurantOut)
def edit_restaurant(payload: RestaurantPatch, db: DbSession, _: AdminUser):
    item = get_restaurant_or_404(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is None and field != "image_url":
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item
