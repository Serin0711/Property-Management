from enum import Enum
from typing import List

from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import InvalidHeaderError
from jose import JWTError
from starlette import status

from main import get_current_user_role


class UserRole(str, Enum):
    admin = "admin"
    vendor = "vendor"
    tenant = "tenant"
    owner = "owner"
    property_manager = "property_manager"
    customer = "customer"


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user_role: str = Depends(get_current_user_role)):
        print("current user role : ", current_user_role)
        if current_user_role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True


async def jwt_required(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token is missing or invalid")
