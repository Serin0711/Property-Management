from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Tenant(BaseModel):
    tenant_id: str
    owner_id: str
    tenant_name: str
    email: EmailStr
    phone: str
    start_date: str
    end_date: str
    contract_type: str
    is_active: bool = True
    rent_amount: Optional[float] = None
    lease_amount: Optional[float] = None

    previous_address: Optional[str] = None
    previous_landlord: Optional[str] = None
    previous_landlord_contact: Optional[str] = None

    lease_duration: Optional[int] = None
    lease_start_date: Optional[str] = None
    lease_end_date: Optional[str] = None

    pet_friendly: Optional[bool] = None
    smoking_friendly: Optional[bool] = None
    parking_space_needed: Optional[bool] = None

    credit_score: Optional[int] = None
    background_check_completed: Optional[bool] = None

    guarantor_name: Optional[str] = None
    guarantor_contact: Optional[str] = None
    guarantor_relationship: Optional[str] = None

    created_on: datetime = datetime.now()
    modified_on: datetime = datetime.now()


class TenantUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]


class Lease(BaseModel):
    start_date: str
    end_date: str
    rent_amount: float
    is_active: bool = True
