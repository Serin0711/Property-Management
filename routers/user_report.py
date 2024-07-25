from typing import Tuple

import pymongo.errors
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends

from database import PropertyReports
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import PropertyMisuseReport

router = APIRouter()

allowed_roles = ['customer', 'owner']


@jwt_required
@router.post("/property_reports")
async def create_property_report(report: PropertyMisuseReport,
                                 role_and_id: Tuple[str, str] = Depends(get_current_user_role), ):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        report_dict = report.dict(exclude_unset=True)
        PropertyReports.insert_one(report_dict)
        return {
            "message": "Property report created successfully"
        }

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e  # re-raise HTTPException with original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/property_reports/{report_id}")
async def get_property_report(report_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        report = PropertyReports.find_one({"_id": ObjectId(report_id)})
        if report is None:
            raise HTTPException(status_code=404, detail="Property report not found")
        if report:
            return {
                "message": "Property report retrieved successfully",
                "data": report
            }

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.delete("/property_reports/{report_id}")
async def delete_property_report(report_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        result = PropertyReports.delete_one({"_id": ObjectId(report_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Property report not found")

        return {
            "message": "Property report deleted successfully"
        }
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"MongoDB Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/property_reports")
async def get_property_report(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        report = PropertyReports.find_one({}, {"_id": 0})
        if report is None:
            raise HTTPException(status_code=404, detail="Property report not found")
        return {
            "message": "Property report retrieved successfully",
            "data": report
        }

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
