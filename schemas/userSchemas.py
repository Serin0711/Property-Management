from pydantic import BaseModel, EmailStr, constr


class UserSchema(BaseModel):
    user_id: str
    role: str
    username: str | None = None
    email: EmailStr
    password: constr(min_length=8)
    passwordConfirm: str


class SocialSignupSchema(BaseModel):
    user_id: str
    user_type: str
    provider: str
    email: EmailStr
    username: str | None = None
    id: str


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
    email: EmailStr
    oldPassword: str
    password: constr(min_length=8)
    passwordConfirm: str


class Settings(BaseModel):
    authjwt_secret_key: str = 'b4bb9013c1c03b29b9311ec0df07f3b0d8fd13edd02d5c45b2fa7b86341fa405'
