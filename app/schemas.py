from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from app.models import UserRole

# User Schema
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    address: str
    phone_number: str
    role: UserRole = Field(description="Role of the user")

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    created_at: datetime
    updated_at: datetime
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
    address: str | None = None
    phone_number: str | None = None


# Global Dish Schema
class GlobalDishResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str | None
    is_veg: bool

    model_config = ConfigDict(from_attributes=True)


class RestaurantResponse(BaseModel):
    id: int
    name: str
    city: str
    rating: float
    is_open: bool

    model_config = ConfigDict(from_attributes=True)


class MenuItemResponse(BaseModel):
    id: int
    price: Decimal
    is_available: bool
    dish: GlobalDishResponse

    model_config = ConfigDict(from_attributes=True)


class RestaurantWithMenuResponse(RestaurantResponse):
    menu_items: list[MenuItemResponse]


class GlobalDishCreate(BaseModel):
    name: str
    is_veg: Optional[bool] = True
    description: str | None = None
    category: str | None = None


class GlobalDishUpdate(BaseModel):
    is_veg: Optional[bool] = None
    description: str | None = None
    category: str | None = None


class GlobalDishDelete(BaseModel):
    id: int


class MenuItemCreate(BaseModel):
    name: str 
    price: float
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    name: str
    price: float | None = None
    is_available: bool | None = None

class MenuItemDelete(BaseModel):
    id: int


class RestaurantCreate(BaseModel):
    name: str
    address: str
    city: str
    rating: float
    is_open: bool
    owner_id: int

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    restaurant_id: int
    delivery_address: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    price_at_order: Decimal
    menu_item: MenuItemResponse

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    delivery_address: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderSummaryResponse(BaseModel):
    id: int
    total_amount: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None
