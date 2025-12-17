from sqlalchemy.orm import Session
from app.models import Restaurant, RestaurantMenuItem
from typing import List

def get_restaurants(db: Session, skip: int = 0, limit: int = 100) -> List[Restaurant]:
    return db.query(Restaurant).offset(skip).limit(limit).all()

def get_restaurant_by_id(db: Session, restaurant_id: int) -> Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    # Get menu items for the restaurant only when restaurant is valid object
    if restaurant:
        menu_items = db.query(RestaurantMenuItem).filter(RestaurantMenuItem.restaurant_id == restaurant_id).all()
        restaurant.menu_items = menu_items
    
    return restaurant