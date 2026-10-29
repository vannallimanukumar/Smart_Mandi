from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class DistrictOut(BaseModel):
    id: str
    name_en: str
    name_te: str
    model_config = ConfigDict(from_attributes=True)

class CropOut(BaseModel):
    id: str
    name_en: str
    name_te: str
    category: str
    aliases: list[str] = []
    model_config = ConfigDict(from_attributes=True)

class PriceOut(BaseModel):
    crop_id: str
    market_id: str
    market_name_en: str
    market_name_te: str
    district_id: str
    min_price: Decimal
    modal_price: Decimal
    max_price: Decimal
    unit: str
    price_date: date
    source_type: str
    source_name: str
    is_verified: bool
    is_demo: bool
    freshness: str = "stale"

class ComparisonRow(BaseModel):
    market_id: str
    market_name_en: str
    market_name_te: str
    district_id: str
    modal_price_per_quintal: Decimal
    gross_value: Decimal
    estimated_freight: Decimal | None
    estimated_net: Decimal | None
    freight_method: str
    price_date: date
    source_type: str
    source_name: str
    is_demo: bool

class TruckOut(BaseModel):
    id: int
    display_name: str
    vehicle_label: str
    capacity_quintals: Decimal
    district_id: str
    base_freight: Decimal
    is_verified: bool
    # Intentionally no contact_phone field.
    model_config = ConfigDict(from_attributes=True)

class BuyerOut(BaseModel):
    id: int
    display_name: str
    buyer_type: str
    district_id: str
    crops_accepted: list[str]
    min_quantity_quintals: Decimal
    offer_price_per_quintal: Decimal | None
    is_verified: bool

class BookingCreate(BaseModel):
    crop_id: str
    district_id: str
    village: str = Field(min_length=2, max_length=120)
    quantity_quintals: Decimal = Field(gt=0, le=40)
    market_id: str
    truck_id: int | None = None
    estimated_freight: Decimal = Field(ge=0, le=1000000)
    farmer_note: str | None = Field(default=None, max_length=500)

class BookingOut(BaseModel):
    id: int
    reference: str
    crop_id: str
    district_id: str
    village: str
    quantity_quintals: Decimal
    market_id: str
    truck_id: int | None
    estimated_freight: Decimal
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OfferCreate(BaseModel):
    buyer_id: int
    crop_id: str
    district_id: str
    quantity_quintals: Decimal = Field(gt=0, le=40)
    expected_price_per_quintal: Decimal | None = Field(default=None, gt=0, le=10000000)
    harvest_date: date | None = None
    village: str = Field(min_length=2, max_length=120)
    message: str | None = Field(default=None, max_length=500)

class OfferOut(BaseModel):
    id: int
    buyer_id: int
    crop_id: str
    district_id: str
    quantity_quintals: Decimal
    expected_price_per_quintal: Decimal | None
    harvest_date: date | None
    village: str
    message: str | None
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProfileOut(BaseModel):
    id: str
    role: str
    preferred_language: str
    display_name: str | None
    model_config = ConfigDict(from_attributes=True)

class AdminStatusUpdate(BaseModel):
    status: str = Field(pattern="^(requested|confirmed|completed|cancelled|rejected)$")


class VerificationUpdate(BaseModel):
    is_verified: bool
    is_active: bool | None = None

class AdminBuyerOut(BaseModel):
    id: int
    display_name: str
    buyer_type: str
    district_id: str
    crops_accepted: str
    is_verified: bool
    is_active: bool
    contact_phone: str | None

class AdminTruckOut(BaseModel):
    id: int
    display_name: str
    vehicle_label: str
    capacity_quintals: Decimal
    district_id: str
    base_freight: Decimal
    is_verified: bool
    is_active: bool
    contact_phone: str | None
