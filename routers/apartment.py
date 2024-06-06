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
from schemas.propertySchemas import PropertySchema

router = APIRouter()


@router.post("/add")
async def add_apartment_details(details: PropertySchema, Authorize: AuthJWT = Depends(),
                                role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()  # Ensure JWT token is present and valid
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if role not in ['admin', 'vendor']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        existing_apartment = PropertyDetail.find_one({"property_id": details.property_id})
        if existing_apartment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Property already exists")

        data = details.dict(exclude_unset=True)
        data["added_on"] = datetime.now()
        data["property_id"] = str(ObjectId())
        data["apartment_id"] = str(ObjectId())

        # Insert data into MongoDB
        PropertyDetail.insert_one(data)

        return {"status": "success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get_all_apartment_details")
async def get_all_apartment_details(Authorize: AuthJWT = Depends(),
                                    role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    # Unpack user role and ID from the dependency
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Check user permissions
    if role not in ["admin", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this endpoint",
        )
    try:
        # Fetch all apartment details from the database
        cursor = PropertyDetail.find({})
        details = [
            {"property_id": str(document["property_id"]), "apartment_id": str(document["apartment_id"]), **document, }
            for document in cursor]

        # Return success response with data
        return {"status": "success", "data": details}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch property details: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))


@router.get("/fetch_apartment_details")
async def fetch_apartment_details(property_id: str, Authorize: AuthJWT = Depends(),
                                  role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    role, user_id = role_and_id

    # Verify JWT token
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Verify user role
    if role not in ['admin', 'customer']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to access this endpoint.")

    # Fetch apartment details
    try:
        cursor = PropertyDetail.find({"property_id": property_id})

        # Format the data using list comprehension
        formatted_data = [
            {**document, "property_id": str(document["property_id"]), "apartment_id": str(document["apartment_id"])}
            for document in cursor
        ]

        return {"status": "success", "data": formatted_data}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))


@router.patch("/update_details")
async def update_apartment_details(property_id: str, updated_details: PropertySchema,
                                   Authorize: AuthJWT = Depends(),
                                   role_and_id: Tuple[str, str] = Depends(get_current_user_role)) -> dict:
    role, user_id = role_and_id

    # Verify JWT token
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Verify user role
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action.")

    # Find the existing apartment details
    try:
        existing_details = PropertyDetail.find_one({"property_id": property_id})
        if not existing_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

        # Prepare data dictionary with updates
        data_dict = updated_details.dict(exclude_unset=True)
        data_dict["modified_by"] = user_id
        data_dict["modified_on"] = datetime.now()

        # Perform the update
        update_result = PropertyDetail.update_one({"property_id": property_id}, {"$set": data_dict})

        if update_result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents were updated.")

        return {"status": "success", "message": f"{update_result.modified_count} document(s) updated."}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error: " + str(e))
