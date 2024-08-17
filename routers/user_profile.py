from datetime import datetime
from typing import Tuple

import pymongo
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import UsersProfile
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import ProfileSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


@jwt_required
@router.post("/add_profile_detail")
async def add_profile_detail(details: ProfileSchema,
                             role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        print("try")
        existing_user = UsersProfile.find_one({"user_id": details.user_id})
        print("try", existing_user)
        if existing_user:
            data = details.dict(exclude_unset=True)
            # del data["property_id"]
            UsersProfile.update_one({"user_id": details.user_id}, {"$set": data})
            return {"status": "success", "data": {"user_id": user_id, "message": "Profile updated successfully"}}

        else:
            print("else")
            data = details.dict(exclude_unset=True)
            UsersProfile.insert_one(data)
            return {"status": "success", "data": data}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e


@router.get("/get_profile/{userid}")
async def get_user_profile(userid: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        profile = UsersProfile.find_one({"user_id": userid})
        if profile:
            formatted_details = {k: v for k, v in profile.items() if k != "_id"}
            return {"status": "success", "data": formatted_details}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile Not Found")

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.put("/update_profile/{user_id}")
async def update_profile(updated_profile: ProfileSchema,
                         role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        profile = UsersProfile.find_one({"user_id": user_id})
        if profile:
            data = updated_profile.dict(exclude_unset=True)
            data["updated_at"] = datetime.now()
            UsersProfile.update_one({"user_id": user_id}, {"$set": data})
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "data": "Profile not found"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.delete("/profile/{user_id}")
async def delete_profile(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        result = UsersProfile.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            return {"status": "success", "data": "Profile deleted successfully"}
        else:
            return {"status": "error", "data": "Profile not found"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/profiles/")
async def list_profiles(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        profiles = list(UsersProfile.find({}, {"_id": 0}))
        if profiles:
            return {"status": "success", "data": profiles}
        else:
            return {"status": "error", "data": "No profiles found"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))