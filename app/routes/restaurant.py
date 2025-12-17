from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from .. import schemas
from .. import oauth2
from .. import utils
from ..database import get_db
from app.services import svc_restaurant
            
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


@router.get('/', response_model=list[schemas.RestaurantResponse])
def get_all_restaurants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.require_roles(models.UserRole.USER, models.UserRole.RESTAURANT_ADMIN))
)-> list[models.Restaurant]:

    restaurants = svc_restaurant.get_restaurants(db)

    if not restaurants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Restaurants registered yet")
    return restaurants  





