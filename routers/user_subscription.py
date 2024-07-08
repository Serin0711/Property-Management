from datetime import datetime
from typing import Tuple

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status
from pymongo import errors

from database import UserSubscription, UserSubscriptionPlan, UserSubscriptionHistory
from main import get_current_user_role
from routers.role_checker import jwt_required

router = APIRouter()


@jwt_required
@router.post("/user_subscription")
async def post_user_subscription(subscription_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'customer', 'owner', 'vendor']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_subscription = UserSubscription.find_one({"user_id": user_id})
        if existing_subscription:
            if existing_subscription["subscription_id"] == subscription_id:
                return {"status": "success", "message": "User subscription already exists. Try to upgrade."}

            previous_subscription = existing_subscription.copy()
            previous_subscription["_id"] = ObjectId()
            previous_subscription["updated_on"] = datetime.utcnow()

            try:
                UserSubscriptionHistory.insert_one(previous_subscription)
            except errors.PyMongoError as e:
                raise HTTPException(status_code=500, detail=f"Failed to insert into subscription history: {str(e)}")

            # Update the existing subscription
            try:
                UserSubscription.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "subscription_id": subscription_id,
                        "updated_on": datetime.utcnow()
                    }}
                )
            except errors.PyMongoError as e:
                raise HTTPException(status_code=500, detail=f"Failed to update user subscription: {str(e)}")

            return {"status": "success", "message": "User subscription updated successfully"}

        else:
            new_subscription = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "created_on": datetime.utcnow()
            }

            try:
                UserSubscription.insert_one(new_subscription)
            except errors.PyMongoError as e:
                raise HTTPException(status_code=500, detail=f"Failed to add new user subscription: {str(e)}")

            return {"status": "success", "message": "User subscription added successfully"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Failed to handle user subscription: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@jwt_required
@router.get("/get_user_subscription_plan")
async def get_user_subscription(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'customer', 'owner', 'vendor']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        user_subscription = UserSubscription.find_one({"user_id": user_id})

        if not user_subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")

        subscription_id = user_subscription.get("subscription_id")

        subscription_plan = UserSubscriptionPlan.find_one({"subscription_id": subscription_id}, {"_id": 0})

        if not subscription_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")

        return {
            "status": "success", "subscription_id": subscription_id, "subscription_plan": subscription_plan}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Failed to handle user subscription: {str(e)}")


@jwt_required
@router.delete("/user_subscription")
async def delete_user_subscription(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'customer', 'owner', 'vendor']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        user_subscription = UserSubscription.find_one({"user_id": user_id})

        if not user_subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")

        UserSubscriptionHistory.insert_one({
            "user_id": user_subscription["user_id"],
            "subscription_id": user_subscription["subscription_id"],
            "created_on": user_subscription["created_on"],
            "deleted_on": datetime.utcnow()
        })

        UserSubscription.delete_one({"user_id": user_id})

        return {"status": "success", "message": "User subscription deleted successfully"}

    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Failed to handle user subscription: {str(e)}")
