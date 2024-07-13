from typing import Optional

import pymongo.errors
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from starlette import status

from database import Users, UserSubscriptionPlan, UserSubscription, PropertyDetail, Tenants

router = APIRouter()
allowed_roles = ["admin"]


@router.get("/users")
async def get_all_users():
    # role, user_id = role_and_id
    #
    # if role not in ['admin']:
    #     raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

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


@router.get("/get_subscription_plans")
async def get_all_subscription_plans():
    # role, user_id = role_and_id
    #
    # if role not in ['admin', 'vendor']:
    #     raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

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


@router.get("/properties")
async def get_properties_count(property_type: str, rental_type: Optional[str] = None,
                               ):
    # role, user_id = role_and_id
    #
    # if role not in ['admin', 'vendor']:
    #     raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        filter_conditions = {"property_type": property_type}

        if rental_type is not None:
            filter_conditions["rental_type"] = rental_type

        property_count = PropertyDetail.count_documents(filter_conditions)
        properties_cursor = list(PropertyDetail.find(filter_conditions, {"_id": 0}))

        return {"count": property_count, "properties": properties_cursor}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tenants")
async def get_tenants_by_owner(owner_id: str):
    # role, user_id = role_and_id
    #
    # if role not in ['admin', 'Owner']:
    #     raise HTTPException(status_code=403, detail="You don't have permission to access this endpoint")

    try:
        # if role == ['admin', 'Owner'] and user_id == owner_id:
        #     raise HTTPException(status_code=403, detail="You can only access your own tenants")

        filter_conditions = {"owner_id": owner_id}

        tenants_cursor = Tenants.find(filter_conditions, {"_id": 0})
        tenants_list = list(tenants_cursor)

        tenant_count = Tenants.count_documents(filter_conditions)

        return {"status": "success", "tenant_count": tenant_count, "tenants": tenants_list}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.delete("/delete_user")
async def delete_property_detail(user_id: str):
    # role, user_id = role_and_id
    # if role not in ["admin"]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You are not authorized to perform this action")

    try:
        existing_user = Users.find_one({"user_id": user_id})
        if existing_user:
            Users.delete_one({"user_id": user_id})
            return {"status": "User deleted successfully", "user_id": user_id}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e  # re-raise HTTPException with original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get_user_subscription_plans")
def get_user_subscription_plans(user_id: str):
    try:
        existing_subscription_plans = list(UserSubscription.find({"user_id": user_id}, {'_id': 0}))

        if existing_subscription_plans:
            user_subscriptions = []
            for subscription_plan in existing_subscription_plans:
                subscription_id = subscription_plan.get('subscription_id')
                plan_details = UserSubscriptionPlan.find_one({"subscription_id": subscription_id}, {'_id': 0})
                if plan_details:
                    user_subscriptions.append(plan_details)
                else:
                    raise HTTPException(status_code=404,
                                        detail=f"Subscription plan details not found for"
                                               f" subscription_id: {subscription_id}")

            return {"message": "success", "user_subscription": user_subscriptions}
        else:
            raise HTTPException(status_code=404, detail="No subscription plans found for the user")

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/all_user_subscription_plans")
def get_all_user_subscription_plans():
    try:
        existing_subscription_plans = list(UserSubscription.find({}, {'_id': 0}))
        if not existing_subscription_plans:
            return {"message": "No subscription plans found"}

        user_subscriptions_combined = []

        plan_projection = {
            '_id': 0, 'created_on': 0, 'modified_on': 0, 'description': 0,
            'price': 0, 'limits': 0
        }
        user_projection = {
            'user_id': 0, 'updated_at': 0, 'verification_code': 0,
            'password': 0, 'verified': 0, 'role': 0
        }

        for subscription_plan in existing_subscription_plans:
            subscription_id = subscription_plan.get('subscription_id')
            user_id = subscription_plan.get('user_id')
            plan_details = UserSubscriptionPlan.find_one({"subscription_id": subscription_id}, plan_projection)
            user_details = Users.find_one({"_id": ObjectId(user_id)}, user_projection)

            combined_details = {}
            if plan_details:
                combined_details.update(plan_details)
            if user_details:
                user_details["_id"] = str(user_details["_id"])
                combined_details.update(user_details)
            else:
                combined_details.update(subscription_plan)

            user_subscriptions_combined.append(combined_details)

        return {
            "message": "success",
            "user_subscriptions": user_subscriptions_combined
        }

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"MongoDB Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/all_counts_and_subscription_usage")
async def get_counts_and_subscription_usage():
    try:
        subscription_plans = list(UserSubscriptionPlan.find({}))
        subscription_usage_data = []
        pipeline = [
            {"$group": {"_id": "$ad_category", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "ad_category": "$_id", "count": 1}}
        ]
        results = list(PropertyDetail.aggregate(pipeline))
        total_count = sum(item["count"] for item in results)
        response = {
            "total_count": total_count,
            "data": results,
        }
        for subscription_plan in subscription_plans:
            subscription_id = subscription_plan["subscription_id"]
            user_count_for_plan = UserSubscription.count_documents({"subscription_id": subscription_id})

            if user_count_for_plan > 0:
                subscription_usage_data.append({
                    "plan_type": subscription_plan["plan_type"],
                    "user_count": user_count_for_plan
                })

        return {
            "message": "success",
            "data": {"subscription_usage": subscription_usage_data},
            "details": response
        }
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"MongoDB Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @jwt_required
@router.get("/get_all_properties")
async def get_all_properties():
    try:
        details = list(PropertyDetail.find({}, {"_id": 0}))
        rent_details = list(PropertyDetail.find({"ad_category": {"$in": ["Rent"]}}, {"_id": 0}))
        lease_details = list(PropertyDetail.find({"ad_category": {"$in": ["Lease"]}}, {"_id": 0}))
        sale_details = list(PropertyDetail.find({"ad_category": {"$in": ["Sale"]}}, {"_id": 0}))

        return {"status": "success", "total_property_details": details, "rent_details": rent_details,
                "lease_details": lease_details, "sale_details": sale_details}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
