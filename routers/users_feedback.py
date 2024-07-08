from typing import Tuple

import pymongo
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from database import UsersFeedback
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.userSchemas import UserFeedbackSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


@jwt_required
@router.post("/add_feedback")
async def add_feedback(details: UserFeedbackSchema, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        feedback_data = UsersFeedback.find_one({"user_id": user_id})
        if feedback_data:
            data = details.dict(exclude_unset=True)
            UsersFeedback.insert_one(data)
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "data": "No feedbacks found"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/feedbacks")
async def get_all_feedbacks(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")
    try:
        feedbacks = list(UsersFeedback.find({}, {"_id": 0}))
        if feedbacks:
            return {"status": "success", "data": feedbacks}
        else:
            return {"status": "error", "data": "No feedbacks found"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
