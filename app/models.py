# This file contains SQLAlchemy models for the database
from sqlalchemy.sql._elements_constructors import null
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum
import enum

from datetime import datetime
from sqlalchemy.sql import text
from .database import Base

class OrderStatus(enum.Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

# Enum for authorization
class UserRole(str, Enum):
    USER = "USER"
    RESTAURANT_ADMIN = "RESTAURANT_ADMIN"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number    = Column(String, unique=True, nullable=False)
    address         = Column(String, nullable=False)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())
    updated_at      = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    role            = Column(Enum(UserRole), nullable=False, default=UserRole.USER, nullable=False)
    orders          = relationship("Order", back_populates="user")


class Restaurant(Base):
    __tablename__   = "restaurants"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String, nullable=False)
    address         = Column(String, nullable=False)
    city            = Column(String, index=True)
    rating          = Column(Float, default=0.0)
    is_open         = Column(Boolean, default=True)
    role            = Column(Enum(UserRole), nullable=False, default=UserRole.RESTAURANT_ADMIN, nullable=False)
    # Relationship: One restaurant can sell many dishes
    menu_items      = relationship("RestaurantMenuItem", back_populates="restaurant")
    orders          = relationship("Order", back_populates="restaurant")


class GlobalDish(Base):
    __tablename__   = "global_dishes"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, index=True, nullable=False) # Index for fast search
    description     = Column(String)
    category        = Column(String) # e.g., Starters, Indian, Chinese
    is_veg          = Column(Boolean, default=True)
    
    # menu_listings will return list of RestaurantMenuItem objects that have this dish
    # It is a Python-only convenience tool. It does not change your database schema, 
    # but it makes writing your API code much faster.
    # Relationship: One dish can be sold by many restaurants
    restaurant_listings   = relationship("RestaurantMenuItem", back_populates="dish") 
    

class RestaurantMenuItem(Base):
    __tablename__   = "restaurant_menu_items"

    id              = Column(Integer, primary_key=True, index=True)
    restaurant_id   = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    global_dish_id  = Column(Integer, ForeignKey("global_dishes.id"), nullable=False)
    
    # Think of applying discounts too
    price           = Column(Float, nullable=False)
    is_available    = Column(Boolean, default=True)
    
    # Relationships
    restaurant      = relationship("Restaurant", back_populates="menu_items")
    dish            = relationship("GlobalDish", back_populates="restaurant_listings")
    order_items     = relationship("OrderItem", back_populates="menu_item")


class Order(Base):
    __tablename__   = "orders"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id   = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    total_amount    = Column(Float, nullable=False)
    status          = Column(Enum(OrderStatus), default=OrderStatus.PLACED)
    delivery_address= Column(String, nullable=False)
    created_at      = Column(DateTime, nullable=False, server_default=DateTime.now())
    items           = relationship("OrderItem", back_populates="order") 
    user            = relationship("User", back_populates="orders")
    restaurant      = relationship("Restaurant", back_populates="orders")

class OrderItem(Base):
    __tablename__   = "order_items"

    id              = Column(Integer, primary_key=True, index=True)
    order_id        = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id    = Column(Integer, ForeignKey("restaurant_menu_items.id"), nullable=False)
    quantity        = Column(Integer, nullable=False)
    price_at_order  = Column(Float, nullable=False)
    
    # Relationships
    menu_item       = relationship("RestaurantMenuItem", back_populates="order_items")
    order           = relationship("Order", back_populates="items")

"""
Notes Section:
1. PHONE NUMBER VALIDATION:
    SQLAlchemy > @validates, CheckConstraint [at database level]
    Pydantic > field_validator [at application level]
    Can also use phonenumber library to validate phone number
    The recommended way to validate phone_number is at application level
          - Database level will return 500 Internal Server Error
          - Application level will return 422 Unprocessable Entity

2. DIFFERENCE BETWEEN DEFAULT AND SERVER_DEFAULT:
    default (Client-Side Default)
    Execution: SQLAlchemy executes the default logic in Python when a new object is created 
    and no value is provided for the column, inserting the generated value into the INSERT statement.

    server_default (Server-Side Default)
    Execution: The default logic is executed by the database server when a new row is inserted, 
    and the generated value is inserted into the INSERT statement.

3. ONUPDATE:
    onupdate=func.now(): This is the crucial part for the updated_at column. 
    It tells SQLAlchemy to execute the func.now() function (get the current time) every time the row is updated 
    and before the SQL UPDATE statement is issued to the database. 

4. WHY WE NEED RELATIONSHIP:
    menu_listings   = relationship("RestaurantMenuItem", back_populates="dish")    
    
    Without that line, if you wanted to find all restaurants selling a "Veg Burger", 
    you would have to write a complex query manually:

    Without relationship (Hard way):

    Python

    # specific query required every time
    listings = db.query(RestaurantMenuItem).filter(RestaurantMenuItem.global_dish_id == burger.id).all()
    
    With relationship (Easy way):

    Python

    # SQLAlchemy writes the query for you in the background
    listings = burger.menu_listings

    # Here we need to assign RestaurantMenuItem.dish variable to GlobalDish object

        # 1. Create a Global Dish (The definition)
        burger = GlobalDish(name="Veg Burger")
        db.add(burger)
        db.commit()

        # At this point:
        # burger.menu_listings is an empty list []

        # 2. Restaurant A adds this burger to their menu
        item1 = RestaurantMenuItem(restaurant_id=1, price=150.0)

        # HERE IS THE MAGIC:
        # We link them using the relationship
        item1.dish = burger 

        # SQLAlchemy automatically updates the OTHER side in memory!
        print(burger.menu_listings) 
        # Output: [<RestaurantMenuItem id=1 price=150.0>]
    
    Summary: It is a Python-only convenience tool. It does not change your database schema, 
    but it makes writing your API code much faster.

    
5. ADDING CUSTOM FIELDS TO USER_RESPONSE PYDANTIC MODEL:
    You can add fields to your Pydantic UserResponse model that do not exist in your database. 
    These are often called computed fields or virtual fields.

    Since you are likely using Pydantic v2 (indicated by your use of ConfigDict), 
    the best way to do this is using the @computed_field decorator. 
    This allows you to generate a message dynamically based on the user's data (like their username).

6. How access token are stored in headers:
    Initially client send username and password as form data (OAuth2PasswordRequestForm) to the server
    Server validates the credentials and returns access token in response
    Then (OAuth2PasswordBearer) expect this access token to be included in header section in format in the format Bearer <token>  

7. READ ABOUT SCOPES IN ADVANCED SECURITY SECTION (FASTAPI DOCUMENTATION):
"""
    
