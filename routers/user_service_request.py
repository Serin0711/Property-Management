from datetime import datetime
from typing import Tuple

import pymongo
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import ServiceRequest
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import ServiceRequestSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


# Create Service Request
@jwt_required
@router.post("/request_service")
async def add_service_request(details: ServiceRequestSchema,
                              role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_user = ServiceRequest.find_one({"user_id": user_id})
        if existing_user:
            data = details.dict(exclude_unset=True)
            ServiceRequest.insert_one(data)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "data": "No user found"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Get Service Request
@jwt_required
@router.get("/get_service_request/{request_id}")
async def get_service_request(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        service_request = ServiceRequest.find_one({"user_id": user_id})
        if not service_request:
            raise HTTPException(status_code=404, detail="Service request not found")

        return {"status": "success", "data": service_request}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Update Service Request
@jwt_required
@router.put("/service_request/{request_id}")
async def update_service_request(request_id: str, updated_request: ServiceRequestSchema,
                                 role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        service_request = ServiceRequest.find_one({"_id": request_id})
        if not service_request:
            raise HTTPException(status_code=404, detail="Service request not found")
        data = updated_request.dict(exclude_unset=True)
        data["updated_at"] = datetime.now()
        ServiceRequest.update_one({"_id": request_id}, {"$set": data})
        return {"status": "success", "data": data}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Delete Service Request
@jwt_required
@router.delete("/service_request/{request_id}")
async def delete_service_request(request_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        result = ServiceRequest.delete_one({"_id": request_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Service request not found")
        return {"status": "success", "message": "Service request deleted successfully"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
