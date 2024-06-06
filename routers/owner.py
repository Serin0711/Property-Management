from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError

from database import Owners
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.ownerSchemas import OwnerSchemas

allowed_roles = ['admin', 'property_manager', 'owner']

router = APIRouter()


@jwt_required
@router.post("/add_owner")
async def add_owner(owner: OwnerSchemas, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to add owner details")

    try:
        existing_owner = Owners.find_one({"email": owner.email})
        if existing_owner:
            raise HTTPException(status_code=400, detail="An owner with the provided email already exists")

        owner_dict = owner.dict(exclude_unset=True)
        owner_dict['owner_id'] = owner.owner_id

        Owners.insert_one(owner_dict)
        return {"message": "Owner added successfully", "owner_id": owner_dict['owner_id']}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@jwt_required
@router.get("/get_owner_details/{owner_id}")
async def get_owner_details(owner_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to access owner details")

    try:
        owner = Owners.find_one({"owner_id": owner_id})
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        if "_id" in owner:
            del owner["_id"]

        return {"status": "success", "data": owner}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@jwt_required
@router.patch("/update_owner/{owner_id}")
async def update_owner(owner_id: str, owner: OwnerSchemas,
                       role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to update owner details")

    try:
        existing_owner = Owners.find_one({"owner_id": owner_id})

        if not existing_owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        owner_dict = owner.dict(exclude_unset=True)

        Owners.update_one({"owner_id": owner_id}, {"$set": owner_dict})
        return {"message": "Owner updated successfully", "owner_id": owner_id}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@jwt_required
@router.delete("/delete_owner/{owner_id}")
async def delete_owner(owner_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to delete owner details")

    try:
        existing_owner = Owners.find_one({"owner_id": owner_id})

        if not existing_owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        Owners.delete_one({"owner_id": owner_id})
        return {"message": "Owner deleted successfully", "owner_id": owner_id}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
