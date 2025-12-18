from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from .. import schemas
from .. import oauth2
from .. import utils
from ..database import get_db
from app.services import svc_restaurant, svc_menu
from typing import List
            
router = APIRouter(
    prefix="/restaurants",
    tags=['Restaurants']
)

# Get restuarant dtails
@router.get('/{restaurant_id}', response_model=schemas.RestaurantWithMenuResponse)
def get_restaurant_details(
    restaurant_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.require_roles(models.UserRole.USER, models.UserRole.RESTAURANT_ADMIN))
)-> models.Restaurant:
    
    restaurant = svc_restaurant.get_restaurant_by_id(db, restaurant_id)

    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restaurant with id: {restaurant_id} not found")

    return restaurant


@router.get('/', response_model=List[schemas.RestaurantResponse])
def get_all_restaurants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.require_roles(models.UserRole.USER, models.UserRole.RESTAURANT_ADMIN))
)-> list[models.Restaurant]:

    restaurants = svc_restaurant.get_restaurants(db)

    if not restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Restaurants registered yet")
    return restaurants  


@router.post("/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(
    item_in: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    # Ensure ONLY a Restaurant Admin can call this
    current_user = Depends(oauth2.require_roles(models.UserRole.RESTAURANT_ADMIN))
):
    # Logic: Get the restaurant associated with this admin
    # (Assuming you link User and Restaurant or the Admin manages one)
    return svc_menu.add_item_to_menu(db, user_id=current_user.id, item_in=item_in)


@router.put("/menu/{menu_item_id}", status_code=status.HTTP_201_CREATED)
def update_menu_item(
    menu_item_id: int,
    item_in: schemas.MenuItemUpdate,
    db: Session = Depends(get_db),
    # Ensure ONLY a Restaurant Admin can call this
    current_user = Depends(oauth2.require_roles(models.UserRole.RESTAURANT_ADMIN))
):
    menu_item = db.query(models.RestaurantMenuItem).filter(models.RestaurantMenuItem.id == menu_item_id).first()
    
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Menu item with ID: '{menu_item_id}' not found")

    if item_in.is_veg:
        menu_item.is_veg = item_in.is_veg
    if item_in.description:
        menu_item.description = item_in.description
    if item_in.category:
        menu_item.category = item_in.category
    if item_in.price:
        menu_item.price = item_in.price
    if item_in.is_available:
        menu_item.is_available = item_in.is_available


    db.commit()
    db.refresh(menu_item)
    return menu_item


@router.get('/menu', response_model=List[schemas.MenuItemResponse])
def get_menu_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
)-> list[models.RestaurantMenuItem]:
    
    menu_items = db.query(models.RestaurantMenuItem).all()
    return menu_items


@router.delete('/menu/{menu_item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    # Ensure ONLY a Restaurant Admin can call this
    current_user = Depends(oauth2.require_roles(models.UserRole.RESTAURANT_ADMIN))
):
    menu_item = db.query(models.RestaurantMenuItem).filter(models.RestaurantMenuItem.id == menu_item_id).first()
    
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Menu item with ID: '{menu_item_id}' not found")
    
    db.delete(menu_item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)






