from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(ReadModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None
    role: str
    created_at: datetime


class ProfilePatch(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RestaurantOut(ReadModel):
    id: int
    name: str
    description: str
    address: str
    phone: str
    opening_hours: str
    image_url: str | None


class RestaurantPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    address: str | None = Field(default=None, max_length=250)
    phone: str | None = Field(default=None, max_length=32)
    opening_hours: str | None = Field(default=None, max_length=200)
    image_url: str | None = Field(default=None, max_length=500)


class CategoryOut(ReadModel):
    id: int
    name: str
    position: int
    is_active: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    position: int = Field(default=0, ge=0)


class CategoryPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class MenuItemOut(ReadModel):
    id: int
    category_id: int
    name: str
    description: str
    price_som: int
    image_url: str | None
    is_available: bool
    is_active: bool


class MenuItemCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=140)
    description: str = Field(default="", max_length=5000)
    price_som: int = Field(ge=0, le=1_000_000)
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool = True


class MenuItemPatch(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=5000)
    price_som: int | None = Field(default=None, ge=0, le=1_000_000)
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool | None = None
    is_active: bool | None = None


class TableOut(ReadModel):
    id: int
    number: str
    seats: int
    is_active: bool


class TableCreate(BaseModel):
    number: str = Field(min_length=1, max_length=24)
    seats: int = Field(ge=1, le=30)


class AvailabilityOut(BaseModel):
    starts_at: datetime
    ends_at: datetime
    available_tables: list[TableOut]


class ReservationCreate(BaseModel):
    starts_at: AwareDatetime
    guests: int = Field(ge=1, le=30)
    table_id: int | None = Field(default=None, ge=1)
    notes: str | None = Field(default=None, max_length=500)


class ReservationOut(ReadModel):
    id: int
    user_id: int
    table_id: int
    guests: int
    starts_at: datetime
    ends_at: datetime
    status: str
    notes: str | None
    created_at: datetime


class OrderLineCreate(BaseModel):
    menu_item_id: int = Field(ge=1)
    quantity: int = Field(ge=1, le=20)


class OrderCreate(BaseModel):
    order_type: Literal["pickup", "dine_in"]
    reservation_id: int | None = None
    notes: str | None = Field(default=None, max_length=500)
    items: list[OrderLineCreate] = Field(min_length=1, max_length=30)


class OrderItemOut(ReadModel):
    id: int
    menu_item_id: int
    name_snapshot: str
    unit_price_som: int
    quantity: int
    line_total_som: int


class OrderOut(ReadModel):
    id: int
    user_id: int
    order_type: str
    reservation_id: int | None
    status: str
    total_som: int
    notes: str | None
    created_at: datetime
    items: list[OrderItemOut]


class OrderStatusPatch(BaseModel):
    status: Literal["new", "preparing", "ready", "completed", "cancelled"]
