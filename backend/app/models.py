from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Numeric, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # Supabase auth user UUID
    role: Mapped[str] = mapped_column(String(20), default="farmer", index=True)
    preferred_language: Mapped[str] = mapped_column(String(2), default="en")
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class District(Base):
    __tablename__ = "districts"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_te: Mapped[str] = mapped_column(String(120))

class Crop(Base):
    __tablename__ = "crops"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_te: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(50), default="other")
    aliases: Mapped[str] = mapped_column(Text, default="")

class Market(Base):
    __tablename__ = "markets"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(160))
    name_te: Mapped[str] = mapped_column(String(160))
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), index=True)
    village_or_town: Mapped[str] = mapped_column(String(120), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class MarketPrice(Base):
    __tablename__ = "market_prices"
    __table_args__ = (Index("ix_price_crop_market_date", "crop_id", "market_id", "price_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"), index=True)
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id"), index=True)
    variety: Mapped[str] = mapped_column(String(120), default="Common")
    min_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    modal_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    max_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    unit: Mapped[str] = mapped_column(String(20), default="quintal")
    price_date: Mapped[date] = mapped_column(Date, index=True)
    source_type: Mapped[str] = mapped_column(String(30), default="demo")
    source_name: Mapped[str] = mapped_column(String(160), default="Demo data")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Truck(Base):
    __tablename__ = "trucks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    vehicle_label: Mapped[str] = mapped_column(String(60))
    capacity_quintals: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), index=True)
    base_freight: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Private fields must never be returned by farmer-facing schemas.
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

class Buyer(Base):
    __tablename__ = "buyers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(String(160))
    buyer_type: Mapped[str] = mapped_column(String(40), default="restaurant")
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), index=True)
    crops_accepted: Mapped[str] = mapped_column(Text, default="")
    min_quantity_quintals: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("0.1"))
    offer_price_per_quintal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Private contact details are not included in public response schemas.
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    farmer_user_id: Mapped[str] = mapped_column(String(80), index=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"))
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"))
    village: Mapped[str] = mapped_column(String(120))
    quantity_quintals: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id"))
    truck_id: Mapped[int | None] = mapped_column(ForeignKey("trucks.id"), nullable=True)
    estimated_freight: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(24), default="requested", index=True)
    farmer_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FarmerOffer(Base):
    __tablename__ = "farmer_offers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_user_id: Mapped[str] = mapped_column(String(80), index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"), index=True)
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"))
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"))
    quantity_quintals: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    expected_price_per_quintal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    village: Mapped[str] = mapped_column(String(120))
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="submitted", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
