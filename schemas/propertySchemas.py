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
    floor: str
    total_floor: str
    property_age: str
    facing: str
    total_area: Optional[str] = None
    # other Fields in resale
    apartment_name: str
    ownership_type: str
    # carpet_area: str
    floor_type: str


class LocalityDetails(BaseModel):
    # locality details
    area: str
    locality: str
    landmark: str


class RentalDetails(BaseModel):
    # rental details
    rental_type: str
    expected_rent: str
    expected_deposit: str = None
    expected_lease_amount: int = None
    rent_negotiable: bool = None
    lease_negotiable: bool = None
    year_of_lease: str = None
    monthly_maintenance: str = None
    maintenance_extra: str = None
    available_from: str
    preferred_tenant: List[str]
    is_furnishing: str = None
    is_parking: str = None
    # description: str

    # other fields resale
    expected_price: str
    price_negotiable: bool = None
    under_loan: bool = None
    # kitchen_type: str


class AmenitiesDetails(BaseModel):
    # amenities
    bathroom: int
    balcony: str
    water_supply: str
    gym: str
    # non_veg_allowed: str
    gated_security: str
    showing_agent: str
    secondary_number: int
    available_amenities: List[str]


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
    total_area: float
    length: float
    width: float
    boundary_wall: bool
    floors_allowed: bool
