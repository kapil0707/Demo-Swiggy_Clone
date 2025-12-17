from sqlalchemy.orm import Session
from app.models import RestaurantMenuItem, GlobalDish, Restaurant
from fastapi import HTTPException, status

def check_restaurant_validity(db: Session, restaurant_id: int)->Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant or not restaurant.is_open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restaurant with ID: '{restaurant_id}' not found")
    
    return restaurant

def check_global_dish_validity(db: Session, dish_name: str)->GlobalDish:
    # First Query the Global Dish table to get the Global Dish ID
    # Only add menu items that are available in the Global Dish table
    # If the dish is not available, raise an exception
    # Later change this logic that if the dish is not available, ask admin to add the receipe to global dish table
    # Also once the item is added, the restaurant admin should receive a notification that the item is added to the menu
    global_dish = db.query(GlobalDish).filter(GlobalDish.name.lower() == dish_name.lower()).first()
    
    if not global_dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Global dish with name: '{dish_name}' is not available")
    
    return global_dish

def add_item_to_menu(db: Session, restaurant_id: int, dish_name: str, price: float)->RestaurantMenuItem:
    # Check if restaurant is valid
    restaurant = check_restaurant_validity(db, restaurant_id)
    
    # Check if global dish is valid
    global_dish = check_global_dish_validity(db, dish_name)
    
    # Create the link between the Restaurant and the Global Dish
    new_item = RestaurantMenuItem(
        restaurant=restaurant_id,
        global_dish_id=global_dish.id,
        price=price,
        is_available=True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def update_menu_price(db: Session, menu_item_id: int, price: float)->RestaurantMenuItem:
    menu_item = db.query(RestaurantMenuItem).filter(RestaurantMenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Menu item with ID: '{menu_item_id}' not found")
    menu_item.price = price
    db.commit()
    db.refresh(menu_item)
    return menu_item    