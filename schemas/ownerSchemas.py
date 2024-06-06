from datetime import datetime

from pydantic import BaseModel, EmailStr


class OwnerSchemas(BaseModel):
    owner_id: str
    owner_name: str
    email: EmailStr
    phone: str
    ownership_type: str
    is_active: bool = True
    owned_properties: int = None

    address: str = None
    city: str = None
    state: str = None
    zip_code: str = None

    emergency_contact: str = None
    emergency_contact_phone: str = None
    emergency_contact_relation: str = None

    created_on: datetime = datetime.now()
    modified_on: datetime = datetime.now()
