from typing import Tuple, Optional

import pymongo.errors
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from database import Users, UserSubscriptionPlan, UserSubscription, PropertyDetail, Tenants
from main import get_current_user_role
from routers.role_checker import jwt_required

router = APIRouter()


@jwt_required
@router.get("/users")
async def get_all_users(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin']:
        raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        projection = {
            "_id": 0,
            "created_at": 0,
            "updated_at": 0,
            "verification_code": 0,
            "password": 0
        }
        users_cursor = Users.find({}, projection)
        users_list = list(users_cursor)

        user_count = Users.count_documents({})

        return {"status": "success", "user_count": user_count, "users": users_list}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/get_subscription_plans")
async def get_all_subscription_plans(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'vendor']:
        raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        subscription_plans = UserSubscriptionPlan.find({}, {"_id": 0, "created_on": 0, "modified_on": 0})
        subscription_plans_list = []

        for plan in subscription_plans:
            user_count = UserSubscription.count_documents({"subscription_id": plan.get("subscription_id")})
            plan["user_count"] = user_count
            subscription_plans_list.append(plan)

        subscription_plan_count = UserSubscriptionPlan.count_documents({})

        return {"status": "success", "count": subscription_plan_count, "subscription_plans": subscription_plans_list}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/properties")
async def get_properties_count(property_type: str, rental_type: Optional[str] = None,
                               role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'vendor']:
        raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        filter_conditions = {"property_type": property_type}

        if rental_type is not None:
            filter_conditions["rental_type"] = rental_type

        property_count = PropertyDetail.count_documents(filter_conditions)
        properties_cursor = list(PropertyDetail.find(filter_conditions, {"_id": 0}))

        return {"count": property_count, "properties": properties_cursor}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/tenants")
async def get_tenants_by_owner(owner_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'Owner']:
        raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        if role == ['admin', 'Owner'] and user_id == owner_id:
            raise HTTPException(status_code=403, detail="You can only access your own tenants")

        filter_conditions = {"owner_id": owner_id}

        tenants_cursor = Tenants.find(filter_conditions, {"_id": 0})
        tenants_list = list(tenants_cursor)

        tenant_count = Tenants.count_documents(filter_conditions)

        return {"status": "success", "tenant_count": tenant_count, "tenants": tenants_list}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
