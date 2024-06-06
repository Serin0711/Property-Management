from typing import Tuple

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from jose import JWTError
from pymongo.errors import PyMongoError

from database import UserSubscriptionPlan
from routers.role_checker import get_current_user_role
from routers.role_checker import jwt_required
from schemas.subscriptionSchemas import SubscriptionPlan

router = APIRouter()


@jwt_required
@router.post("/add_subscription_plan")
def subscribe(payload: SubscriptionPlan, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role != 'admin':
        raise HTTPException(status_code=403, detail="You don't have permission to add subscriptions")

    try:
        existing_subscription = UserSubscriptionPlan.find_one({"subscription_id": payload.subscription_id})

        if existing_subscription:
            raise HTTPException(status_code=400, detail="Subscription already exists")

        data = payload.dict(exclude_unset=True)
        data['subscription_id'] = str(ObjectId())
        UserSubscriptionPlan.insert_one(data)
        return {"message": "Subscription added successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@jwt_required
@router.post("/remove_subscription_plan")
def unsubscribe(subscription_id: str, Authorize: AuthJWT = Depends(),
                role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        Authorize.jwt_required()
    except JWTError:
        raise HTTPException(status_code=401, detail="JWT token is missing or invalid")

    if role != 'admin':
        raise HTTPException(status_code=403, detail="You don't have permission to unsubscribe")

    try:
        existing_subscription = UserSubscriptionPlan.find_one({"subscription_id": subscription_id})
        if not existing_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        UserSubscriptionPlan.delete_one({"subscription_id": subscription_id})

        return {"message": "Unsubscribed successfully"}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@jwt_required
@router.patch("/update_subscription_plan")
def update_subscription(payload: SubscriptionPlan, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role != 'admin':
        raise HTTPException(status_code=403, detail="You don't have permission to update subscriptions")

    try:
        existing_subscription = UserSubscriptionPlan.find_one({"subscription_id": payload.subscription_id})

        if not existing_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        UserSubscriptionPlan.update_one({"subscription_id": payload.subscription_id}, payload.dict(exclude_unset=True))

        return {"message": "Subscription details updated successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@jwt_required
@router.get("/all_subscription_plans")
def get_subscription_plans(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'vendor', 'property_manager', 'owner', 'customer']:
        raise HTTPException(status_code=403, detail="You don't have permission to view subscription plans")

    try:
        subscription_plans = list(UserSubscriptionPlan.find({}, {'_id': 0}))
        return {"message": "success", "subscription_plans": subscription_plans}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
