from datetime import datetime
from typing import Tuple

import pymongo
import requests
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from pymongo import errors
from starlette import status

from config import settings
from database import Geolocations, Users
from database import PropertyDetail, PropertyAccessLog, UserSubscription, UserSubscriptionPlan
from main import get_current_user_role
from routers.role_checker import jwt_required, format_currency
from schemas.propertySchemas import PropertyDetailsSchema, LocalityDetails, RentalDetails, AmenitiesDetails, \
    GalleryDetails, HomeDetailsSchema, GeoLocation, PropertyUpdateSchema

router = APIRouter()

allowed_roles = ['admin', 'vendor', 'customer', 'owner']


@jwt_required
@router.post("/add_home_detail")
async def add_home_detail(details: HomeDetailsSchema, role_and_id: Tuple[str, str] = Depends(get_current_user_role),
                          property_id: str = None):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            data = details.dict(exclude_unset=True)
            del data["property_id"]
            data["user_id"] = user_id
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "property updated successfully", "property_id": property_id}

        else:
            data = details.dict(exclude_unset=True)
            data["property_id"] = str(ObjectId())
            data["user_id"] = user_id
            data["added_on"] = datetime.now()

            PropertyDetail.insert_one(data)

            return {"status": "success", "property_id": data["property_id"]}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e  # re-raise HTTPException with original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.post("/add_property_detail")
async def add_property_detail_old(details: PropertyDetailsSchema,
                                  role_and_id: Tuple[str, str] = Depends(get_current_user_role),
                                  property_id: str = None):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_property = PropertyDetail.find_one({"property_id": property_id})
        # print(existing_property)
        if existing_property:
            data = details.dict(exclude_unset=True)
            del data["property_id"]
            data["user_id"] = user_id
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "property updated successfully", "property_id": property_id,
                    "ad_category": data['ad_category']}

        else:
            data = details.dict(exclude_unset=True)
            data["property_id"] = str(ObjectId())
            data["user_id"] = user_id
            data["added_on"] = datetime.now()

            # Insert data into MongoDB
            PropertyDetail.insert_one(data)

            return {"status": "success", "property_id": data["property_id"], "ad_category": data['ad_category']}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e  # re-raise HTTPException with original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.post("/add_property_detail_new")
async def add_property_detail(property_id: str, details: PropertyDetailsSchema,
                              role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in ['admin', 'vendor']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            # if "area" in existing_apartment:
            data = details.dict(exclude_unset=True)
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id

            # Insert data into MongoDB
            PropertyDetail.insert_one(data)
            return {"status": "success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.post("/add_locality_detail")
async def add_locality_detail(property_id: str, details: LocalityDetails,
                              role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            # if "area" in existing_apartment:
            data = details.dict(exclude_unset=True)
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id

            # Insert data into MongoDB
            PropertyDetail.insert_one(data)

            return {"status": "success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.post("/add_rental_detail")
async def add_rental_detail(property_id: str, details: RentalDetails,
                            role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            data = details.dict(exclude_unset=True)
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id
            data["expected_rent"] = int(data["expected_rent"])
            data["expected_deposit"] = int(data["expected_deposit"])
            data["maintenance_extra"] = int(data["maintenance_extra"])
            # Insert data into MongoDB
            PropertyDetail.insert_one(data)

            return {"status": "success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @jwt_required
@router.get("/get_property_details")
async def get_property_details(property_id: str):
    try:
        details = PropertyDetail.find_one({"property_id": property_id})

        if details is None:
            raise HTTPException(status_code=404, detail="Property not found")

        formatted_details = {
            k: (format_currency(v) if k in ['expected_deposit', 'expected_lease_amount', 'expected_rent', 'sale_amount',
                                            'current_worth'] else v) for k, v in details.items() if
            k != "_id" and v not in [None, "", [], {}]
        }

        for key in ['lease_negotiable', 'sale_negotiable', 'rent_negotiable']:
            if key in details:
                formatted_details[key] = "negotiable" if details[key] else "non-negotiable"

        return {"status": "success", "data": formatted_details}

    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.get("/get_locality_details")
async def get_locality_details(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = []
        for document in details:
            if 'area' in document:
                formatted_details.append({k: v for k, v in document.items() if k != "_id"})

        return {"status": "success", "data": formatted_details}

    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.get("/get_rental_details")
async def get_rental_details(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = []
        for document in details:
            if 'rental_type' in document:
                formatted_details.append({k: v for k, v in document.items() if k != "_id"})

        return {"status": "success", "data": formatted_details}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.get("/get_all_property_details")
async def get_all_property_details(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    global viewed_count

    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to fetch property details")
    try:
        user_subscription = UserSubscription.find_one({"user_id": user_id})
        if not user_subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")

        subscription_id = user_subscription.get("subscription_id")
        subscription_plan = UserSubscriptionPlan.find_one({"subscription_id": subscription_id})
        if not subscription_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")

        limit = subscription_plan.get("limits")
        if limit is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Subscription plan limit not found")

        property_log = PropertyAccessLog.find_one({"user_id": user_id})
        if not property_log:
            property_log = {
                "property_id": property_id,
                "user_id": user_id,
                "viewed_count": 1,
                "last_viewed": datetime.utcnow(),
            }
            PropertyAccessLog.insert_one(property_log)
        else:
            viewed_count = property_log.get("viewed_count", 0) + 1
            if viewed_count > limit:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Your subscription limit has been exceeded, you can upgrade your plan")

            PropertyAccessLog.update_one(
                {"user_id": user_id},
                {"$inc": {"viewed_count": 1}, "$set": {"last_viewed": datetime.utcnow()}}
            )

        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = [{k: v for k, v in doc.items() if k != "_id"} for doc in details]

        response_data = {
            "user_id": user_id,
            "viewed_count": property_log.get("viewed_count", viewed_count),
            "last_viewed": property_log.get("last_viewed", datetime.utcnow())
        }
        return {"status": "success", "viewed_count": response_data, "data": formatted_details}

    except errors.PyMongoError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch property details")


@jwt_required
@router.post("/add_amenities_detail")
async def add_amenities_detail(property_id: str, details: AmenitiesDetails,
                               role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            data = details.dict(exclude_unset=True)
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id

            PropertyDetail.insert_one(data)

            return {"status": "success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@jwt_required
@router.get("/get_amenities_details")
async def get_amenities_details(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = []
        for document in details:
            formatted_details.append({k: v for k, v in document.items() if k != "_id"})

        return {"status": "success", "data": formatted_details}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.post("/upload_photo")
async def upload_photo(property_id: str, details: GalleryDetails,
                       role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        # Strip the base64 prefix from the images
        details.strip_base64_prefix()

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            data = details.dict(exclude_unset=True)
            data["modified_on"] = datetime.now()
            data["status"] = "finished"
            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "Update success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id
            data["status"] = "finished"
            PropertyDetail.insert_one(data)
            # print(data)
            return {"status": "Upload success"}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException:
        raise  # re-raise HTTPException to keep original status code and detail


@jwt_required
@router.get("/get_gallery_details")
async def get_gallery_details(property_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

        details = PropertyDetail.find({"property_id": property_id})
        formatted_details = []
        for document in details:
            formatted_details.append({k: v for k, v in document.items() if k != "_id"})

        return {"status": "success", "data": formatted_details}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.post("/upload_img")
async def upload_img(property_id: str, del_image: int, details: GalleryDetails,
                     role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to perform this action")

        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            data = details.dict(exclude_unset=True)

            if del_image is not None and 0 <= del_image < len(existing_property.get('upload_images', [])):
                existing_property['upload_images'].pop(del_image)

                PropertyDetail.update_one(
                    {"property_id": property_id},
                    {"$set": {"upload_images": existing_property['upload_images']}}
                )

            PropertyDetail.update_one({"property_id": property_id}, {"$set": data})
            return {"status": "success"}

        else:
            data = details.dict(exclude_unset=True)
            data["added_on"] = datetime.now()
            data["property_id"] = property_id

            PropertyDetail.insert_one(data)

            return {"status": "Upload success"}
    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.get("/get_owned_property_details")
async def get_owned_property_details(role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    try:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have permission to fetch house details")

        details_count = PropertyDetail.count_documents({"user_id": user_id})
        details = PropertyDetail.find({"user_id": user_id})

        formatted_details = []
        if details:
            for document in details:
                formatted_document = {k: v for k, v in document.items() if k != "_id" and v is not None and v != ""}
                formatted_details.append(formatted_document)

            return {"status": "success", "property_count": details_count, "data": formatted_details}
        else:
            raise HTTPException(status_code=403, detail="Detail Not Found")

    except errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch house details")


@jwt_required
@router.delete("/delete_property_detail")
async def delete_property_detail(property_id: str,
                                 role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id
    if role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action")

    try:
        existing_property = PropertyDetail.find_one({"property_id": property_id})
        if existing_property:
            PropertyDetail.delete_one({"property_id": property_id})
            return {"status": "property deleted successfully", "property_id": property_id}
        else:
            # print("else")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Property not found")

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def get_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "bc4f9c0af6dd4e61b1d3f32371ee1eb5"
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        geometry = data['results'][0]['geometry']['location']
        return geometry['lat'], geometry['lng']
    else:
        return None, None


async def get_geolocation_by_address(geo: GeoLocation, api_key: str):
    address = f"{geo.street_name}, {geo.city}, {geo.state}"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or not data['results']:
            raise HTTPException(status_code=404, detail="Address not found")

        result = data['results'][0]['geometry']
        geo.latitude = result['lat']
        geo.longitude = result['lng']
        geo.geo_type = "address"
        geo.user_update = "User_update"
        geo.system_update = 'None'
        return geo
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching geolocation data: {str(e)}")


async def get_geolocation_by_lat_lng(geo: GeoLocation, api_key: str):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={geo.latitude}+{geo.longitude}&key={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or not data['results']:
            raise HTTPException(status_code=404, detail="Coordinates not found")

        result = data['results'][0]['components']
        geo.street_name = result.get('road', '')
        geo.city = result.get('city', result.get('town', result.get('village', '')))
        geo.state = result.get('state', '')
        geo.geo_type = "lat_long"
        geo.system_update = "system_update"
        geo.user_update = 'None'
        return geo
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching geolocation data: {str(e)}")


@router.post("/geolocation/", response_model=GeoLocation)
async def get_geolocation(geo: GeoLocation):
    opencage_api_key = settings.OPENCAGE_API_KEY
    print(opencage_api_key)
    try:
        if geo.street_name and geo.city and geo.state:
            geo = await get_geolocation_by_address(geo, opencage_api_key)
        elif geo.latitude and geo.longitude:
            geo = await get_geolocation_by_lat_lng(geo, opencage_api_key)
        else:
            raise HTTPException(status_code=400,
                                detail="Invalid input. Provide either a complete address or latitude and longitude.")

        try:
            Geolocations.insert_one(geo.dict())
        except pymongo.errors.PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        return geo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/update_property_details")
async def update_house_details(property_id: str, updated_details: PropertyUpdateSchema,
                               role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to update house details")

    existing_details = PropertyDetail.find_one({"property_id": property_id})
    if not existing_details:
        raise HTTPException(status_code=404, detail="Property details not found.")

    data_dict = updated_details.dict(exclude_unset=True)
    data_dict["modified_by"] = user_id
    data_dict["modified_on"] = datetime.utcnow()
    try:
        # Perform the update using update_one
        updated_data = PropertyDetail.update_one({"property_id": property_id}, {"$set": data_dict})
        modified_count = updated_data.modified_count

        return {"status": "success", "message": f"{modified_count} document(s) updated."}
    except pymongo.errors.PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to update property details")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_required
@router.get("/get_owner_details/{owner_id}")
async def get_owner_details(owner_id: str, role_and_id: Tuple[str, str] = Depends(get_current_user_role)):
    role, user_id = role_and_id

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have permission to access owner details")

    try:
        owner = Users.find_one({"_id": ObjectId(owner_id)})
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        if "_id" in owner:
            del owner["_id"]

        return {"status": "success", "data": owner}

    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
