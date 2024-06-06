from typing import Optional, Tuple

import pymongo.errors
from fastapi import APIRouter, Depends, HTTPException, status

from database import PropertyDetail
from main import get_current_user_role
from routers.role_checker import jwt_required

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'Owner', 'customer']


@jwt_required
@router.get("/fetch_details")
async def get_apartment_details(city: str, property_type: str, rental_type: str, locality: Optional[str] = None,
                                role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in ['admin', 'customer']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        query = {"city": city, "property_type": property_type, "residential_type": rental_type}
        if locality:
            query["locality"] = locality

        cursor = PropertyDetail.find(query)
        details = []

        for document in cursor:
            del document["_id"]
            document["property_id"] = str(document["property_id"])
            if "house_id" in document:
                document["house_id"] = str(document["house_id"])
            if "land_id" in document:
                document["land_id"] = str(document["land_id"])
            if "apartment_id" in document:
                document["apartment_id"] = str(document["apartment_id"])
            details.append(document)

        return {"status": "success", "data": details}
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/filter_details")
async def get_all_details(type_of_property: str, city : str, property_type: Optional[str] = None,
                          ad_category: Optional[str] = None):
    try:
        query = {}

        if city:
            query["area"] = city
        if property_type:
            query["property_type"] = property_type
        if ad_category:
            query["ad_category"] = ad_category
        if type_of_property:
            query["type_of_property"] = type_of_property

        Property_Detail = PropertyDetail.find(query)
        details = []

        for document in Property_Detail:
            document.pop("_id", None)
            details.append(document)

        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for the provided details."
            )

        return {"status": "success", "data": details}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/owned_properties_count")
async def count_user_properties(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$ad_category", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "ad_category": "$_id", "count": 1}}
        ]

        results = list(PropertyDetail.aggregate(pipeline))

        total_count = sum(item["count"] for item in results)
        response = {
            "status": "success",
            "total_count": total_count,
            "data": results
        }

        return response

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
