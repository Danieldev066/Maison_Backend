from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import AdminUser, CurrentUser, DbSession
from app.models import MenuItem, Order, OrderItem, Reservation
from app.schemas import OrderCreate, OrderOut, OrderStatusPatch

router = APIRouter(tags=["Orders"])

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "new": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"completed"},
    "completed": set(),
    "cancelled": set(),
}


def order_detail_query(order_id: int):
    return select(Order).options(selectinload(Order.items)).where(Order.id == order_id)


@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: DbSession, user: CurrentUser):
    if payload.order_type == "dine_in":
        if payload.reservation_id is None:
            raise HTTPException(status_code=422, detail="dine_in requires a reservation_id")
        reservation = db.get(Reservation, payload.reservation_id)
        if reservation is None or reservation.user_id != user.id or reservation.status != "confirmed":
            raise HTTPException(status_code=422, detail="A confirmed reservation belonging to you is required")
    elif payload.reservation_id is not None:
        raise HTTPException(status_code=422, detail="pickup must not have a reservation_id")

    ids = [line.menu_item_id for line in payload.items]
    if len(ids) != len(set(ids)):
        raise HTTPException(status_code=422, detail="Duplicate menu_item_id; combine quantities")
    items = db.scalars(select(MenuItem).where(MenuItem.id.in_(ids))).all()
    by_id = {item.id: item for item in items}
    lines: list[OrderItem] = []
    total = 0
    for line in payload.items:
        menu_item = by_id.get(line.menu_item_id)
        if menu_item is None or not menu_item.is_active or not menu_item.is_available or not menu_item.category.is_active:
            raise HTTPException(status_code=422, detail=f"Menu item {line.menu_item_id} is unavailable")
        line_total = menu_item.price_som * line.quantity
        total += line_total
        lines.append(OrderItem(
            menu_item_id=menu_item.id,
            name_snapshot=menu_item.name,
            unit_price_som=menu_item.price_som,
            quantity=line.quantity,
            line_total_som=line_total,
        ))

    order = Order(
        user_id=user.id,
        reservation_id=payload.reservation_id,
        order_type=payload.order_type,
        status="new",
        notes=payload.notes,
        total_som=total,
        items=lines,
    )
    db.add(order)
    db.commit()
    return db.scalar(order_detail_query(order.id))


@router.get("/orders", response_model=list[OrderOut])
def my_orders(db: DbSession, user: CurrentUser):
    return db.scalars(
        select(Order).options(selectinload(Order.items)).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    ).all()


@router.get("/admin/orders", response_model=list[OrderOut])
def admin_orders(db: DbSession, _: AdminUser):
    return db.scalars(select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).limit(200)).all()


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: DbSession, user: CurrentUser):
    order = db.scalar(order_detail_query(order_id))
    if order is None or (order.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_my_order(order_id: int, db: DbSession, user: CurrentUser):
    order = db.scalar(order_detail_query(order_id))
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "new":
        raise HTTPException(status_code=409, detail="Only new orders may be cancelled")
    order.status = "cancelled"
    db.commit()
    return order


@router.patch("/admin/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, payload: OrderStatusPatch, db: DbSession, _: AdminUser):
    order = db.scalar(order_detail_query(order_id).with_for_update())
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if payload.status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot change status from {order.status} to {payload.status}")
    order.status = payload.status
    db.commit()
    return order
