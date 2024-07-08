import inspect
import os
import re
from datetime import timedelta

import pymongo.errors
from fastapi import FastAPI, Depends, HTTPException, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi_jwt_auth import AuthJWT
from starlette import status

import utils
from config import settings
from database import Users
from routers import (apartment, house, filter, land, auth,
                     subscription_plan, tenant, owner, property, user_subscription, admin)
from schemas.userSchemas import Settings

app = FastAPI()

origins = [settings.CLIENT_ORIGIN, "http://localhost:3000", "http://localhost:8081", "http://localhost:3001",
           "http://localhost:3002"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
try:
    app.include_router(property.router, prefix="/api/property", tags=["Property Details"])
    app.include_router(admin.router, prefix="/api/admin_view", tags=["Admin View"])
    app.include_router(house.router, prefix="/api/property_details", tags=["House Details"])
    app.include_router(apartment.router, prefix="/api/apartment_details", tags=["Apartment Details"])
    app.include_router(land.router, prefix="/api/land_details", tags=["Land Details"])
    app.include_router(filter.router, prefix="/api/filter", tags=["Filter Details"])
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
    app.include_router(subscription_plan.router, prefix="/api/subscription_plan", tags=["subscription Plan"])
    app.include_router(user_subscription.router, prefix="/api/user_subscription", tags=["User subscription"])
    app.include_router(tenant.router, prefix="/api/tenant", tags=["Tenants"])
    app.include_router(owner.router, prefix="/api/owner", tags=["Owner"])

except Exception as e:
    print(f"Error while including routers: {e}")


@app.get("/")
async def health_checker():
    return {"status": "success"}


ACCESS_TOKEN_EXPIRES_IN = 120  # in minutes
REFRESH_TOKEN_EXPIRES_IN = 240


@app.post("/login")
async def login_for_access_token(response: Response, username: str = Form(...), password: str = Form(...),
                                 Authorize: AuthJWT = Depends()):
    try:
        db_user = Users.find_one({"email": username})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect Email",
            )

        # Check password length
        if len(password) < 8:
            response.status_code = status.HTTP_200_OK
            return {"detail": "Password must be at least 8 characters long"}

        else:
            if not utils.verify_password(password, db_user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect Password",
                )

        access_token = Authorize.create_access_token(
            subject=str(db_user["email"]),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
        )

        # Create refresh token
        refresh_token = Authorize.create_refresh_token(
            subject=str(db_user["email"]),
            expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
        )

        # Store refresh and access tokens in cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
            expires=ACCESS_TOKEN_EXPIRES_IN * 60,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="none",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_EXPIRES_IN * 60,
            expires=REFRESH_TOKEN_EXPIRES_IN * 60,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="none",
        )

        return {
            "access_token": access_token,
            "name": db_user.get("username", ""),
            "role": db_user.get("role", ""),
            "email": db_user.get("email", ""),
            "id": str(db_user["_id"]),
            "token_type": "bearer",
        }
    except pymongo.errors.PyMongoError as e:
        return {"status": "failed", "error": str(e)}, 500
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        return {"status": "failed", "error": str(e)}, 500


@app.get('/lock')
async def hello(Authorize: AuthJWT = Depends()):
    """
        ## A sample hello world route
        This returns Hello world
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return {"message": "Hello World"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My Auth API",
        version="1.0",
        description="An API with an Authorize Button",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                    re.search("jwt_required", inspect.getsource(endpoint)) or
                    re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                    re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@AuthJWT.load_config
def get_config():
    return Settings()
