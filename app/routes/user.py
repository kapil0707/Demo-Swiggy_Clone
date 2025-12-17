from fastapi import APIRouter, Depends, HTTPException, status, Response

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

    email_exists = db.query(models.User).filter(models.User.email == user.email).first()
    
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    phone_exists = db.query(models.User).filter(models.User.phone_number == user.phone_number).first()

    if phone_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")

    # hash the password - user.password
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.put('/{user_id}', response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} not found")


    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    if user.name:
        user_to_update.name = user.name

    if user.phone_number:
        user_to_update.phone_number = user.phone_number
    
    if user.password:
        user_to_update.password = utils.get_password_hash(user.password)    
    
    if user.address:
        user_to_update.address = user.address

    db.commit()
    db.refresh(user_to_update)
    return user_to_update



@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} not found")
    
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    db.delete(user_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
