from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, constr


class HomeDetailsSchema(BaseModel):
    # Home details
    property_id: str
    name: str
    phone_number: constr(min_length=10)
    type_of_property: str  # Residential,Commercial, Land/Plot
    ad_category: str  # Rent, Resale, PG/Hostel, and Flatmates


class PropertyDetailsSchema(BaseModel):
    # property details
    property_id: str
    property_type: str
    type_of_property: str
    ad_category: str  # Rent, Resale, PG/Hostel, and Flatmates
    BHK_type: str
    floor: Optional[str] = ''
    total_floor: Optional[str] = ''
    property_age: str
    facing: str
    total_area: int
    # other Fields in resale
    apartment_name: str
    # ownership_type: str
    # carpet_area: str


class LocalityDetails(BaseModel):
    # locality details
    area: str
    locality: str
    landmark: str


class RentalDetails(BaseModel):
    # rental details
    # rental_type: str
    expected_lease_amount: int = None
    sale_amount: int = None
    expected_rent: int
    lease_negotiable: bool = None
    rent_negotiable: bool = None
    sale_negotiable: bool = None
    year_of_lease: str = None
    expected_deposit: str = None
    current_worth: str = None
    monthly_maintenance: str = None
    maintenance_extra: str = None
    floor_type: Optional[str] = ''
    preferred_tenant: List[str]
    is_furnishing: str = None
    is_parking: str = None
    parking_extra: Optional[str] = ''
    legal: Optional[str] = ''
    available_from: str
    # description: str


class AmenitiesDetails(BaseModel):
    # amenities
    bathroom: int
    balcony: str
    water_supply: str
    water_sources: str
    soil_type: str
    terrain_type: str
    farm: str
    zoning: str
    environmental: str
    previous_crops: str
    current_crops: str
    electricity: str
    showing_agent: str
    gym: str
    gated_security: str
    personal_number: int
    secondary_number: int
    available_amenities: List[str]
    # non_veg_allowed: str


class GalleryDetails(BaseModel):
    # gallery
    upload_images: List[str]

    # upload_videos: List[str] = None
    def strip_base64_prefix(self):
        self.upload_images = [img.split(",")[1] if img.startswith("data:image/jpeg;base64,") else img for img in
                              self.upload_images]


class AdditionalDetails(BaseModel):
    # Additional details
    property_tax_paid: str
    occupancy_certificate: str
    sale_deed_certificate: str
    completion_certificate: str


class ScheduleDetails(BaseModel):
    # Schedule details
    Availability: str
    schedule_time: str


class PropertySchema(BaseModel):
    # Schedule details
    Availability: str
    schedule_time: str


class HouseSchemas(BaseModel):
    # Schedule details
    Availability: str
    schedule_time: str


class LandSchema(BaseModel):
    land_id: str
    property_type: str
    plot_area: float
    length: float
    width: float
    boundary_wall: bool
    floors_allowed: bool

    # locality details
    area: str
    locality: str
    landmark: str
    map_location: str

    # resale
    expected_price: int
    available_from: datetime
    price_negotiable: str = None
    year_of_registration: str
    currently_under_loan: bool
    description: str
    # estimated_EMI: int

    # amenities
    water_supply: bool
    electricity_connection: bool
    sewage_connection: bool
    width_of_facing_road: bool
    gated_security: bool
    showing_agent: str

    # Additional Details
    free_hold: str
    lease_hold: str
    lease_term: datetime
    sale_deed_certificate: bool
    encumbrance_certificate: bool
    conversion_certificate: bool
    RERA_approved: bool

    # gallery
    uploaded_images: List[str]
    uploaded_videos: List[str] = None

    added_on: datetime = datetime.now()
    modified_on: datetime = datetime.now()


class LandDetailsSchema(BaseModel):
    property_id: str
    type_of_property: str
    ad_category: str
    property_type: str
    BHK_type: str
    total_area: float
    length: float
    width: float
    boundary_wall: bool
    floors_allowed: bool


class PropertyUpdateSchema(BaseModel):
    # Property details
    property_id: Optional[str] = None
    property_type: Optional[str] = None
    type_of_property: Optional[str] = None
    ad_category: Optional[str] = None  # Rent, Resale, PG/Hostel, and Flatmates
    BHK_type: Optional[str] = None
    floor: Optional[str] = ''
    total_floor: Optional[str] = ''
    property_age: Optional[str] = None
    facing: Optional[str] = None
    total_area: Optional[int] = None
    apartment_name: Optional[str] = None

    # Locality details
    area: Optional[str] = None
    locality: Optional[str] = None
    landmark: Optional[str] = None

    # Rental details
    expected_lease_amount: Optional[int] = None
    sale_amount: Optional[int] = None
    expected_rent: Optional[int] = None
    lease_negotiable: Optional[bool] = None
    rent_negotiable: Optional[bool] = None
    sale_negotiable: Optional[bool] = None
    year_of_lease: Optional[str] = None
    expected_deposit: Optional[str] = None
    current_worth: Optional[str] = None
    monthly_maintenance: Optional[str] = None
    maintenance_extra: Optional[str] = None
    floor_type: Optional[str] = ''
    preferred_tenant: Optional[List[str]] = None
    is_furnishing: Optional[str] = None
    is_parking: Optional[str] = None
    parking_extra: Optional[str] = ''
    legal: Optional[str] = ''
    available_from: Optional[str] = None

    # Amenities details
    bathroom: Optional[int] = None
    balcony: Optional[str] = None
    water_supply: Optional[str] = None
    water_sources: Optional[str] = None
    soil_type: Optional[str] = None
    terrain_type: Optional[str] = None
    farm: Optional[str] = None
    zoning: Optional[str] = None
    environmental: Optional[str] = None
    previous_crops: Optional[str] = None
    current_crops: Optional[str] = None
    electricity: Optional[str] = None
    showing_agent: Optional[str] = None
    gym: Optional[str] = None
    gated_security: Optional[str] = None
    personal_number: Optional[int] = None
    secondary_number: Optional[int] = None
    available_amenities: Optional[List[str]] = None

    # Gallery details
    upload_images: Optional[List[str]] = None

    def strip_base64_prefix(self):
        if self.upload_images:
            self.upload_images = [
                img.split(",")[1] if img.startswith("data:image/jpeg;base64,") else img for img in self.upload_images
            ]


class GeoLocation(BaseModel):
    property_id: str
    user_id: str
    geo_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_one: Optional[str] = None
    address_two: Optional[str] = None
    street_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: int
    status: str
    system_update: str
    user_update: str
    added_on: datetime = datetime.now()
    updated_on: datetime = datetime.now()
