from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .. import schemas
from .. import oauth2
from .. import utils

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

def verify_order_owner(
    order_id: int,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
)-> models.Order:

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404)

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403)

    return order

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password

    email_exists = db.query(models.User).filter(models.User.email == user.email).first()
    
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    phone_exists = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()

    if phone_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/restaurants/{id}', response_model=schemas.RestaurantWithMenuResponse)
def get_restaurant_details(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
)-> models.Restaurant:
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == id).first()

    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    menu_items = db.query(models.RestaurantMenuItem).filter(models.RestaurantMenuItem.restaurant_id == id).all()
    restaurant.menu_items = menu_items
    
    return restaurant
