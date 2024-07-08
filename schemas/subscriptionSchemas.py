from datetime import datetime

from pydantic import BaseModel


class SubscriptionPlan(BaseModel):
    subscription_id: str
    price: int
    limits: int
    plan_type: str
    description: str


class SubscriptionRequest(BaseModel):
    subscription_id: str
    user_id: str
    subscription: bool = True
    viewed_count: int
    expired_date: datetime
    created_on: datetime = datetime.now()
    modified_on: datetime = datetime.now()
