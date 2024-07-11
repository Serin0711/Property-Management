from datetime import datetime
from typing import Tuple, List

import pymongo
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import UsersFavorites
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import UserFavoritesPropertySchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


@jwt_required
@router.post("/add_favorite_property")
async def add_favorite_property(details: UserFavoritesPropertySchema,
                                role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_favorites = UsersFavorites.find_one({"user_id": user_id})
        data = details.dict(exclude_unset=True)
        if existing_favorites:
            UsersFavorites.update_one(
                {"user_id": user_id},
                {"$addToSet": {"property_id": {"$each": data["property_id"]}}, "$set": {"updated_at": datetime.now()}}
            )
            return {"status": "success", "message": "Favorite properties updated successfully", "user_id": user_id}
        else:
            UsersFavorites.insert_one(data)
            return {"status": "success", "data": data}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/get_favorite_properties")
async def get_favorite_properties(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        favorites = UsersFavorites.find_one({"user_id": user_id}, {"_id": 0})
        if not favorites:
            raise HTTPException(status_code=404, detail="Favorite properties not found")

        return {"status": "success", "data": favorites}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.put("/update_favorite_properties")
async def update_favorite_properties(updated_details: UserFavoritesPropertySchema,
                                     role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        favorites = UsersFavorites.find_one({"user_id": user_id})
        if not favorites:
            raise HTTPException(status_code=404, detail="Favorite properties not found")

        data = updated_details.dict(exclude_unset=True)
        data["updated_at"] = datetime.now()
        UsersFavorites.update_one({"user_id": user_id}, {"$set": data})
        return {"status": "success", "data": data}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.delete("/delete_favorite_property/{property_id}")
async def delete_favorite_property(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        result = UsersFavorites.update_one({"user_id": user_id}, {"$pull": {"property_id": property_id}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Property not found in favorites")
        return {"status": "success", "detail": "Favorite property deleted successfully"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/list_all_favorite_properties")
async def list_all_favorite_properties(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        favorites = list(UsersFavorites.find({"user_id": user_id}, {"_id": 0}))
        return {"status": "success", "data": favorites}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
