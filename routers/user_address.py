from typing import Tuple

import pymongo
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import UsersAddress
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import UserAddressSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


@jwt_required
@router.post("/add_address")
async def add_address(details: UserAddressSchema, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_address = UsersAddress.find_one({"user_id": user_id})
        data = details.dict(exclude_unset=True)
        if existing_address:
            UsersAddress.update_one({"user_id": user_id}, {"$set": data})
            return {"status": "success", "message": "Address updated successfully", "user_id": user_id}
        else:
            UsersAddress.insert_one(data)
            return {"status": "success", "data": data}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/get_address/{address_id}")
async def get_address(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        address = UsersAddress.find_one({"user_id": user_id})
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        address.pop("_id", None)
        return {"status": "success", "data": address}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/list_addresses")
async def list_addresses(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        addresses = list(UsersAddress.find({"user_id": user_id}, {"_id": 0}))
        return {"status": "success", "data": addresses}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
