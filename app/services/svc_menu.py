from sqlalchemy.orm import Session
from app.models import RestaurantMenuItem, GlobalDish, Restaurant
from fastapi import HTTPException, status
from app.schemas import MenuItemCreate

def get_restaurant_by_user_id(db: Session, user_id: int)->Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == user_id).first()
    
    if not restaurant or not restaurant.is_open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Current logged in user with user_id: '{user_id}' is not a restaurant owner")
    
    return restaurant

def check_global_dish_validity(db: Session, dish_name: str)->GlobalDish:
    # First Query the Global Dish table to get the Global Dish ID
    # Only add menu items that are available in the Global Dish table
    # If the dish is not available, raise an exception
    # Later change this logic that if the dish is not available, ask admin to add the receipe to global dish table
    # Also once the item is added, the restaurant admin should receive a notification that the item is added to the menu
    global_dish = db.query(GlobalDish).filter(GlobalDish.name == dish_name).first()
    
    if not global_dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Global dish with name: '{dish_name}' is not available")
    
    return global_dish

def add_item_to_menu(db: Session, user_id: int, item_in: MenuItemCreate)->RestaurantMenuItem:
    
    print(f"add_item_to_menu -> Function starts")
    # Check if restaurant is valid
    restaurant = get_restaurant_by_user_id(db, user_id)

    print(f"add_item_to_menu -> Rstuarant_id: {restaurant.id}")
    
    # Check if global dish is valid
    global_dish = check_global_dish_validity(db, item_in.name)
    print(f"add_item_to_menu -> Global_dish_id: {global_dish.id}")
    
    # Create the link between the Restaurant and the Global Dish
    new_item = RestaurantMenuItem(
        restaurant_id=restaurant.id,
        global_dish_id=global_dish.id,
        price=item_in.price,
        is_available=True
    )   

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

