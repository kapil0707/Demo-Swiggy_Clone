from fastapi import Depends, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings
from app.utils import verify_password
from app.database import get_db
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(data: dict, expires_delta: timedelta | None = None)-> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db))-> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("user_id")
        role = payload.get("role")

        if user_id is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user

def require_roles(*allowed_roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return checker


