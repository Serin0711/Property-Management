from datetime import datetime
from typing import Tuple

import pymongo.errors
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors

from database import Tenants
from main import get_current_user_role
from routers.role_checker import jwt_required
from schemas.tenantSchema import Tenant

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'owner', 'customer']


@jwt_required
@router.get("/get_all_tenant_details")
async def get_all_tenants(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to access tenant details")

    try:
        # Retrieve all tenants from the database
        tenants = Tenants.find()
        details = []

        for document in tenants:
            if 'tenant_id' in document:
                del document["_id"]
                document["tenant_id"] = str(document["tenant_id"])
                details.append(document)

        return {"status": "success", "data": details}
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@jwt_required
@router.post("/add_tenants")
async def add_tenant(tenant: Tenant, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in ['admin', 'owner']:
        raise HTTPException(status_code=403, detail="You don't have permission to add tenant details")

    try:
        existing_tenant = Tenants.find_one({"tenant_id": tenant.tenant_id})
        if existing_tenant:
            for field, value in tenant:
                if field not in ["tenant_id", "owner_id"]:
                    setattr(tenant, field, value)
            tenant_dict = tenant.dict(exclude={"tenant_id", "owner_id"})
            Tenants.update_one(
                {"tenant_id": tenant.tenant_id}, {"$set": {**tenant_dict, "updated_on": datetime.utcnow()}})

            return {"status": "success", "message": "User subscription updated successfully"}

        else:
            tenant_dict = tenant.dict(exclude_unset=True)
            tenant_dict['tenant_id'] = str(ObjectId())
            tenant_dict['owner_id'] = user_id

            Tenants.insert_one(tenant_dict)
            return {"message": "Tenant added successfully", "tenant_id": tenant_dict['tenant_id']}
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@jwt_required
@router.get("/get_tenant_details/{tenant_id}")
async def get_tenant_details(tenant_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to access tenant details")
    try:
        # Find the tenant by tenant_id  
        tenant = Tenants.find_one({"tenant_id": tenant_id}, {"_id": 0})
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {"status": "success", "data": tenant}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@jwt_required
@router.patch("/update_tenant_details/{tenant_id}")
async def update_tenant(tenant_id: str, tenant: Tenant, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to update tenant details")

    try:
        # Convert tenant object to dictionary and exclude unset fields
        updated_details = tenant.dict(exclude_unset=True)

        # Add modified_by and modified_on fields
        updated_details["modified_by"] = user_id
        updated_details["modified_on"] = datetime.now()

        # Update the tenant in the database
        update_result = Tenants.update_one(
            {"tenant_id": tenant_id},
            {"$set": updated_details}
        )

        # Check if the tenant was found and updated
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {"message": "Tenant updated successfully"}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
