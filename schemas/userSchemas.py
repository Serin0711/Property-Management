from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr


class UserSchema(BaseModel):
    user_id: str
    role: str
    username: str | None = None
    email: EmailStr
    password: constr(min_length=8)
    passwordConfirm: str
    # phone_number: int
    # mobile: int
    added_by: Optional[str]
    updated_by: Optional[str]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class ProfileSchema(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    # phone_number: str
    nationality: str
    profile_picture: str
    gender: str
    date_of_birth: Optional[str]
    age: Optional[int]
    status: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UserAddressSchema(BaseModel):
    user_id: str
    address_1: str
    address_2: str
    city: str
    state: str
    postal_code: int
    country: str
    status: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UserFeedbackSchema(BaseModel):
    email_id: str
    feedback_type: str
    message: str
    status: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class ServiceRequestSchema(BaseModel):
    user_id: str
    request_id: str
    status: str
    issue_type: str
    description: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UserFavoritesPropertySchema(BaseModel):
    user_id: str
    property_id: List[str]
    status: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class SocialSignupSchema(BaseModel):
    user_id: str
    user_type: str
    provider: str
    email: EmailStr
    username: str | None = None
    id: str


class PropertyMisuseReport(BaseModel):
    property_id: str
    user_id: str
    report_reason: str
    description: Optional[str] = None
    report_date: datetime = datetime.now()


class UserSigninSchema(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class VerifyOTPSchema(BaseModel):
    email: str
    otp: str


class ResetPasswordSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    passwordConfirm: str


class UpdatePasswordSchema(BaseModel):
    user_id: str
    old_password: str
    new_password: constr(min_length=8)
    password_confirm: str


class Settings(BaseModel):
    authjwt_secret_key: str = 'b4bb9013c1c03b29b9311ec0df07f3b0d8fd13edd02d5c45b2fa7b86341fa405'
