from datetime import datetime
from typing import Tuple

import pymongo
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import PropertyDetail
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.propertySchemas import LandDetailsSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'Owner']


@jwt_required
@router.post("/add_land_detail")
async def add_land_detail(details: LandDetailsSchema, role_and_id: Tuple[str, str] = Depends(get_current_user_role),
                          property_id: str = None):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_property = PropertyDetail.find_one({"property_id": property_id})
        # print(existing_property)
        if existing_property:
            data = details.dict(exclude_unset=True)
            del data["property_id"]
            data["user_id"] = user_id
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "property updated successfully", "property_id": property_id}

        else:
            data = details.dict(exclude_unset=True)
            data["property_id"] = str(ObjectId())
            data["property_type"] = "Land"
            data["user_id"] = user_id
            data["added_on"] = datetime.now()

            # Insert data into MongoDB
            PropertyDetail.insert_one(data)

            return {"status": "success", "property_id": data["property_id"]}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e  # re-raise HTTPException with original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/get_all_land_details")
async def get_land_details(role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    role, user_id = role_and_id

    if role not in ['admin', 'customer', 'vendor', 'property_manager', 'owner']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to access land details")
    try:
        cursor = PropertyDetail.find({})
        details = [
            {
                "land_id": str(document["land_id"]),
                "property_id": str(document["property_id"]),
                **document
            }
            for document in cursor
        ]
        return {"status": "success", "data": details}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))


@jwt_required
@router.get("/fetch_land_details")
async def fetch_land_details(land_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    role, user_id = role_and_id
    if role not in ['admin', 'customer', 'vendor', 'property_manager', 'owner']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to fetch land details")
    try:
        cursor = PropertyDetail.find({"land_id": ObjectId(land_id)})
        details = [
            {
                "land_id": str(document["land_id"]),
                **document
            }
            for document in cursor
        ]
        return {"status": "success", "data": details}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))


@jwt_required
@router.patch("/update_land_details")
async def update_land_details(land_id: str, updated_details: LandDetailsSchema,
                              role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    role, user_id = role_and_id
    if role not in ['admin', 'vendor', 'property_manager', 'owner']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to update land details")
    try:
        existing_details = PropertyDetail.find_one({"land_id": ObjectId(land_id)})
        if not existing_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land details not found.")

        # Prepare data dictionary with updates
        data_dict = updated_details.dict(exclude_unset=True)
        data_dict["updated_by"] = user_id
        data_dict["updated_at"] = datetime.now()

        update_result = PropertyDetail.update_one({"land_id": land_id}, {"$set": data_dict})

        if update_result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents were updated.")

        return {"status": "success", "message": f"{update_result.modified_count} document(s) updated."}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))
