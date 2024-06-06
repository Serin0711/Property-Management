from datetime import datetime
from typing import Tuple

import pymongo
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import InvalidHeaderError
from pymongo import errors
from starlette import status

from database import PropertyDetail
from main import get_current_user_role
from schemas.propertySchemas import HouseSchemas

router = APIRouter()


@router.post("/add")
async def add_house_details(details: HouseSchemas, Authorize: AuthJWT = Depends(),
                            role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if role not in ['admin', 'vendor', 'property_manager', 'owner']:
        raise HTTPException(status_code=403, detail="You don't have permission to add house details")

    existing_house = PropertyDetail.find_one({"property_id": details.property_id})
    if existing_house:
        raise HTTPException(status_code=400, detail="Property already exists")

    data = details.dict(exclude_unset=True)
    data["added_on"] = datetime.utcnow()
    data["property_id"] = str(ObjectId())

    try:
        PropertyDetail.insert_one(data)
        return {"status": "success"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to add property details") from e


@router.get("/get_all_house_details")
async def get_all_house_details(Authorize: AuthJWT = Depends(),
                                role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if role not in ['admin', 'customer', 'vendor']:
        raise HTTPException(status_code=403, detail="You don't have permission to access house details")

    try:
        cursor = PropertyDetail.find({})
        details = [
            {k: v for k, v in document.items() if k != '_id'}
            for document in cursor
            if 'house_id' in document
        ]
        return {"status": "success", "data": details}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch property details")


@router.get("/fetch_house_details")
async def fetch_house_details(property_id: str, Authorize: AuthJWT = Depends(),
                              role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if role not in ['admin', 'vendor', 'customer']:
        raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

    try:
        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = [
            {k: v for k, v in document.items() if k != '_id'}  # Remove _id from the document
            for document in details
        ]
        return {"status": "success", "data": formatted_details}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update_details")
async def update_house_details(property_id: str, updated_details: HouseSchemas, Authorize: AuthJWT = Depends(),
                               role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if role not in ['admin', 'vendor']:
        raise HTTPException(status_code=403, detail="You don't have permission to update house details")

    existing_details = PropertyDetail.find_one({"property_id": property_id})
    if not existing_details:
        raise HTTPException(status_code=404, detail="Property details not found.")

    # Extract only the fields that need to be updated
    data_dict = updated_details.dict(exclude_unset=True)
    data_dict["modified_by"] = user_id
    data_dict["modified_on"] = datetime.utcnow()

    # Use the filter query to identify the document to be updated
    filter_query = {"property_id": property_id}

    try:
        # Perform the update using update_one
        updated_data = PropertyDetail.update_one(filter_query, {"$set": data_dict})
        modified_count = updated_data.modified_count

        return {"status": "success", "message": f"{modified_count} document(s) updated."}
    except pymongo.errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to update property details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
