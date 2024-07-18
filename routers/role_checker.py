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
        await Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token is missing or invalid")


def format_currency(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    if value >= 10 ** 7:
        return f"{value / 10 ** 7:.1f}Cr" if value % 10 ** 7 != 0 else f"{value // 10 ** 7}Cr"
    elif value >= 10 ** 5:
        return f"{value / 10 ** 5:.1f}Lac" if value % 10 ** 5 != 0 else f"{value // 10 ** 5}Lac"
    elif value >= 10 ** 3:
        return f"{value / 10 ** 3:.1f}k" if value % 10 ** 3 != 0 else f"{value // 10 ** 3}k"
    else:
        return str(value)
