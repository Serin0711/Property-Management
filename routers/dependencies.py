import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

from config import settings
from database import Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    return username


def get_current_active_user(current_user: str = Depends(get_current_user)):
    user = Users.get(current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_user_role(current_user: str = Depends(get_current_user)):
    user = Users.get(current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user["role"]
