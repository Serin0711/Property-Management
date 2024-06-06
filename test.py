from datetime import datetime, timedelta
from typing import Optional

import pymongo.errors
from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import BaseModel

import utils
from oauth2 import AuthJWT

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["Tamil_voterlist"]
users_collection = db["employeedetail"]


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    _id: str
    emp_id: str
    email: str
    password: str
    phone_number: str
    created_by: str
    created_at: datetime
    modified_on: str
    role: str
    name: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: Optional[str]):
    user = await users_collection.find_one({"email": email})
    if user and password is not None:  # Ensure password is not None
        if utils.verify_password(password, user["password"]):
            user["emp_id"] = str(user["emp_id"])
            return user
    return None


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

    except Exception as e:
        raise credential_exception

    user = await users_collection.find_one({"email": username})
    if user is None:
        raise credential_exception

    return user


async def get_current_user_role(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    except Exception as e:
        raise credential_exception from e

    user = users_collection.find_one({"email": username})
    if user is None:
        raise credential_exception

    role = user.get("role")
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not defined for the user",
        )

    return role


ACCESS_TOKEN_EXPIRES_IN = 60
REFRESH_TOKEN_EXPIRES_IN = 240


@app.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 Authorize: AuthJWT = Depends()):
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires)
        # Create refresh token
        refresh_token = Authorize.create_refresh_token(
            subject=str(user["_id"]),  # Access _id directly from the User object
            expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
        )

        # Store refresh and access tokens in cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
            expires=ACCESS_TOKEN_EXPIRES_IN * 60,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="none",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_EXPIRES_IN * 60,
            expires=REFRESH_TOKEN_EXPIRES_IN * 60,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="none",
        )

        response.set_cookie(
            key="logged_in",
            value="True",
            max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
            expires=ACCESS_TOKEN_EXPIRES_IN * 60,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="none",
        )

        return {
            "access_token": access_token,
            "name": user.get("name", ""),
            "role": user.get("role", ""),
            "email": user.get("email", ""),
            "id": str(user["_id"]),
            "emp_id": str(user["emp_id"])
        }
    except pymongo.errors.PyMongoError as e:
        return {"status": "failed", "error": str(e)}, 500
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        return {"status": "failed", "error": str(e)}, 500
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    print("current_user", type(current_user), current_user)
    return current_user


@app.get("/users/me/role")
async def read_current_user_role(role: str = Depends(get_current_user_role)):
    return {"role": role}
