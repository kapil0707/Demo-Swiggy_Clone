# This file contains Pydantic models for data validation and serialization

from pydantic import BaseModel, EmailStr, ConfigDict, computed_field
from typing import Optional
from datetime import datetime
# import phonenumbers


class UserBase(BaseModel):
    name            : str
    email           : EmailStr
    phone_number    : Optional[str] = None


class UserCreate(UserBase):
    password        : str

    # @field_validator('phone_number')
    # def validate_phone(cls, v):
    #     try:
    #         parsed_num = phonenumbers.parse(v, "IN")
    #         if not phonenumbers.is_valid_number(parsed_num):
    #             raise ValueError('Invalid phone number')
    #         return phonenumbers.format_number(
    #             parsed_num, phonenumbers.PhoneNumberFormat.E164
    #         )
    #     except phonenumbers.NumberParseException:
    #         raise ValueError('Invalid phone number format')


class UserResponse(BaseModel):
    id              : int
    name            : str
    created_at      : datetime
    updated_at      : datetime
    # email           : EmailStr
    # phone_number    : Optional[str] = None

    # class Config:
    #   orm_mode = True
    # below is the new way to do it
    model_config = ConfigDict(from_attributes=True)
    
    # Adding custom information to the response
    @computed_field
    def welcome_message(self) -> str:
        return f"Welcome to ZomatoClone, {self.name}!!. Enjoy your meal!"

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


"""
# --- 2. Browsing (Get Menu / Restaurant Details) ---

# Global Dish info (The "What")
class GlobalDishResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    is_veg: bool
    model_config = ConfigDict(from_attributes=True)

# Specific Restaurant Listing (The "How Much")
class MenuItemResponse(BaseModel):
    id: int
    price: float
    is_available: bool
    # Nest the global dish details inside
    dish: GlobalDishResponse
    
    model_config = ConfigDict(from_attributes=True)

class RestaurantBase(BaseModel):
    name: str
    address: str
    city: str

class RestaurantResponse(RestaurantBase):
    id: int
    rating: float
    is_open: bool
    # Return the menu inside the restaurant details
    menu_items: List[MenuItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- 3. Ordering Food ---

# Input: Single item in the cart
class OrderItemCreate(BaseModel):
    restaurant_menu_item_id: int
    quantity: int

# Input: The full order
class OrderCreate(BaseModel):
    restaurant_id: int
    delivery_address: str
    items: List[OrderItemCreate]

# Output: Showing what was ordered
class OrderItemResponse(BaseModel):
    menu_item_name: str # Flattened for easier frontend display
    quantity: int
    price_at_order: float
    
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    restaurant_name: str # Helper field
    status: OrderStatus
    total_amount: float
    delivery_address: str
    created_at: datetime
    items: List[OrderItemResponse]
    
    model_config = ConfigDict(from_attributes=True)


# --- 4. Reviews ---

class ReviewCreate(BaseModel):
    restaurant_id: int
    rating: int # 1 to 5
    comment: Optional[str] = None

    @field_validator('rating')
    def check_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

"""
