from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db


router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)


@router.post('/dish', status_code=status.HTTP_201_CREATED)
def add_dish(
    dish_in: schemas.GlobalDishCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.require_roles(models.UserRole.ADMIN))
):
    dish = db.query(models.GlobalDish).filter(models.GlobalDish.name == dish_in.name).first()
    
    if dish:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dish already exists")

    new_dish = models.GlobalDish(**dish_in.dict())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


@router.post('/restaurant', status_code=status.HTTP_201_CREATED)
def add_restaurant(
    restaurant_in: schemas.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.require_roles(models.UserRole.ADMIN))
):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.name == restaurant_in.name).first()
    
    if restaurant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant already exists")

    # Check owner information from users table
    owner = db.query(models.User).filter(models.User.id == restaurant_in.owner_id).first()
    
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID: '{restaurant_in.owner_id}' not found")

    new_restaurant = models.Restaurant(**restaurant_in.dict())
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    return new_restaurant   

@router.delete('/restaurant/{restaurant_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.require_roles(models.UserRole.ADMIN))
):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restaurant with ID: '{restaurant_id}' not found")
    
    db.delete(restaurant)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) 