from datetime import datetime, timedelta
from typing import Optional, Tuple

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

import utils
from database import Users

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    _id: ObjectId()
    email: str
    role: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXPIRES_IN = 60
REFRESH_TOKEN_EXPIRES_IN = 240


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Set default expiration time (e.g., 30 days)
        expire = datetime.utcnow() + timedelta(days=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: str, password: Optional[str]):
    user = Users.find_one({"email": email})
    if user and password is not None:  # Ensure password is not None
        if utils.verify_password(password, user["password"]):
            return user
    return None


async def get_current_user(Authorize: AuthJWT = Depends()):
    # Define the HTTPException for authorization errors
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        # Require a valid JWT token
        Authorize.jwt_required()
        # Get the subject (user identity) from the token
        username = Authorize.get_jwt_subject()
        if not username:
            raise credential_exception

        user = Users.find_one({"email": username})
        if not user:
            raise credential_exception
        return user
    except JWTError:
        raise credential_exception
    # Handle other unexpected errors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def get_current_user_role(Authorize: AuthJWT = Depends()) -> Tuple[str, str]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        Authorize.jwt_required()  # Ensure JWT token is present and valid
        username = Authorize.get_jwt_subject()
        if not username:
            raise credential_exception
    except Exception as e:
        raise credential_exception from e

    user = Users.find_one({"email": username})
    if not user:
        raise credential_exception
    role = user.get("role")
    user_id = str(user.get("_id"))  # Convert user ID to a string
    print("user role :", role)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not defined for the user",
        )

    return role, user_id
