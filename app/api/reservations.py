from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import AwareDatetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.dependencies import AdminUser, CurrentUser, DbSession
from app.models import DiningTable, Reservation
from app.schemas import AvailabilityOut, ReservationCreate, ReservationOut, TableCreate, TableOut

router = APIRouter(tags=["Tables & Reservations"])
RESERVATION_MINUTES = 90
MAX_BOOKING_DAYS = 90


def booking_window(starts_at: datetime) -> tuple[datetime, datetime]:
    start = starts_at.astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    if not (now + timedelta(minutes=5) <= start <= now + timedelta(days=MAX_BOOKING_DAYS)):
        raise HTTPException(status_code=422, detail="Book at least 5 minutes ahead and at most 90 days ahead")
    return start, start + timedelta(minutes=RESERVATION_MINUTES)


def conflicting_reservation_exists(db: Session, table_id: int, start: datetime, end: datetime) -> bool:
    # Overlap condition: previous_start < new_end AND previous_end > new_start.
    query = select(Reservation.id).where(
        Reservation.table_id == table_id,
        Reservation.status == "confirmed",
        Reservation.starts_at < end,
        Reservation.ends_at > start,
    ).limit(1)
    return db.scalar(query) is not None


@router.get("/tables", response_model=list[TableOut])
def list_tables(db: DbSession):
    return db.scalars(select(DiningTable).where(DiningTable.is_active.is_(True)).order_by(DiningTable.seats, DiningTable.id)).all()


@router.post("/tables", response_model=TableOut, status_code=status.HTTP_201_CREATED)
def add_table(payload: TableCreate, db: DbSession, _: AdminUser):
    obj = DiningTable(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table number already exists") from None
    db.refresh(obj)
    return obj


@router.get("/reservations/availability", response_model=AvailabilityOut)
def availability(
    db: DbSession,
    starts_at: AwareDatetime,
    guests: int = Query(ge=1, le=30),
):
    start, end = booking_window(starts_at)
    tables = db.scalars(
        select(DiningTable).where(DiningTable.is_active.is_(True), DiningTable.seats >= guests).order_by(DiningTable.seats, DiningTable.id)
    ).all()
    free = [table for table in tables if not conflicting_reservation_exists(db, table.id, start, end)]
    return AvailabilityOut(starts_at=start, ends_at=end, available_tables=free)


@router.post("/reservations", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: DbSession, user: CurrentUser):
    start, end = booking_window(payload.starts_at)
    if payload.table_id is not None:
        target = db.get(DiningTable, payload.table_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Table not found")
        candidates = [target.id]
    else:
        candidates = list(db.scalars(
            select(DiningTable.id).where(DiningTable.is_active.is_(True), DiningTable.seats >= payload.guests)
            .order_by(DiningTable.seats, DiningTable.id)
        ))

    # PostgreSQL row locks serialize simultaneous reservations of the same table.
    # Every candidate is locked *before* checking overlaps in the same transaction.
    for table_id in candidates:
        table = db.scalar(select(DiningTable).where(DiningTable.id == table_id).with_for_update())
        if table is None or not table.is_active or table.seats < payload.guests:
            continue
        if conflicting_reservation_exists(db, table.id, start, end):
            continue
        item = Reservation(
            user_id=user.id,
            table_id=table.id,
            guests=payload.guests,
            starts_at=start,
            ends_at=end,
            notes=payload.notes,
            status="confirmed",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    raise HTTPException(status_code=409, detail="No available table for this period and party size")


@router.get("/reservations", response_model=list[ReservationOut])
def my_reservations(db: DbSession, user: CurrentUser):
    return db.scalars(select(Reservation).where(Reservation.user_id == user.id).order_by(Reservation.starts_at.desc())).all()


@router.get("/admin/reservations", response_model=list[ReservationOut])
def all_reservations(db: DbSession, _: AdminUser):
    return db.scalars(select(Reservation).order_by(Reservation.starts_at.desc()).limit(200)).all()


@router.get("/reservations/{reservation_id}", response_model=ReservationOut)
def reservation_detail(reservation_id: int, db: DbSession, user: CurrentUser):
    item = db.get(Reservation, reservation_id)
    if item is None or (item.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Reservation not found")
    return item


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(reservation_id: int, db: DbSession, user: CurrentUser):
    item = db.get(Reservation, reservation_id)
    if item is None or (item.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Reservation not found")
    if item.status != "confirmed":
        raise HTTPException(status_code=409, detail="Reservation is not active")
    if item.starts_at <= datetime.now(timezone.utc) and user.role != "admin":
        raise HTTPException(status_code=409, detail="Past reservations cannot be cancelled")
    item.status = "cancelled"
    db.commit()
    db.refresh(item)
    return item
