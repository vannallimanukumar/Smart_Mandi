from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import District, Crop, Market, MarketPrice, Truck, Buyer, Booking, FarmerOffer, Profile
from app.schemas import (
    DistrictOut, CropOut, PriceOut, ComparisonRow, TruckOut, BuyerOut,
    BookingCreate, BookingOut, OfferCreate, OfferOut, ProfileOut, AdminStatusUpdate, VerificationUpdate
)
from app.core.security import get_current_user, require_admin
from app.services.market import list_prices, compare_prices, freshness

router = APIRouter(prefix="/api/v1")

@router.get("/districts", response_model=list[DistrictOut])
def districts(db: Session = Depends(get_db)):
    return db.scalars(select(District).order_by(District.name_en)).all()

@router.get("/crops", response_model=list[CropOut])
def crops(q: str | None = None, db: Session = Depends(get_db)):
    rows = db.scalars(select(Crop).order_by(Crop.name_en)).all()
    result = []
    for c in rows:
        aliases = [a for a in c.aliases.split("|") if a]
        if q and q.lower() not in (c.name_en + " " + c.name_te + " " + c.aliases).lower():
            continue
        result.append({"id": c.id, "name_en": c.name_en, "name_te": c.name_te, "category": c.category, "aliases": aliases})
    return result

@router.get("/prices", response_model=list[PriceOut])
def prices(
    crop_id: str, district_id: str | None = None, market_id: str | None = None,
    date_from: date | None = None, date_to: date | None = None,
    source: str = Query(default="all", pattern="^(all|government|demo)$"),
    db: Session = Depends(get_db)
):
    """Return price records from the database filtered by the selected UI controls."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must be on or before date_to")
    rows = list_prices(db, crop_id, district_id, market_id, date_from, date_to)
    if source == "government":
        return [row for row in rows if row["source_type"] == "government" and not row["is_demo"]]
    if source == "demo":
        return [row for row in rows if row["is_demo"]]
    return rows

@router.get("/markets")
def markets(district_id: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Market).where(Market.is_active.is_(True))
    if district_id:
        stmt = stmt.where(Market.district_id == district_id)
    return [{"id": m.id, "name_en": m.name_en, "name_te": m.name_te, "district_id": m.district_id}
            for m in db.scalars(stmt.order_by(Market.name_en)).all()]

@router.get("/price-history")
def price_history(crop_id: str, market_id: str, date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)):
    if db.get(Crop, crop_id) is None or db.get(Market, market_id) is None:
        raise HTTPException(status_code=404, detail="Crop or market not found")
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must be on or before date_to")
    stmt = select(MarketPrice).where(MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id)
    if date_from: stmt = stmt.where(MarketPrice.price_date >= date_from)
    if date_to: stmt = stmt.where(MarketPrice.price_date <= date_to)
    rows = db.scalars(stmt.order_by(MarketPrice.price_date)).all()
    return [{"price_date": r.price_date, "min_price": r.min_price, "modal_price": r.modal_price,
             "max_price": r.max_price, "source_name": r.source_name, "source_type": r.source_type,
             "is_demo": r.is_demo, "freshness": freshness(r.price_date)} for r in rows]

@router.get("/price-analytics")
def price_analytics(crop_id: str, market_id: str, db: Session = Depends(get_db)):
    history = db.scalars(select(MarketPrice).where(
        MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id
    ).order_by(MarketPrice.price_date)).all()
    points = [{"date": r.price_date, "modal_price": float(r.modal_price), "is_demo": r.is_demo} for r in history]
    has_demo = any(r.is_demo for r in history)
    result = {"crop_id": crop_id, "market_id": market_id, "observations": len(points),
              "history": points, "forecast": None, "evaluation": None,
              "data_mode": "demo" if has_demo else "official_or_imported",
              "note": "Synthetic sample data for UI testing only. Forecast and error metrics are illustrative, not real market guidance." if has_demo else "Forecast baseline only; not selling advice. Validate data quality and backtest before operational use."}
    # A transparent naive baseline: chronological holdout, one-step forecast using previous observation.
    if len(points) >= 12:
        split = max(8, int(len(points) * 0.8))
        train, test = points[:split], points[split:]
        errors = [abs(test[i]["modal_price"] - points[split + i - 1]["modal_price"]) for i in range(len(test))]
        mae = sum(errors) / len(errors) if errors else None
        recent = [p["modal_price"] for p in points[-7:]]
        result["evaluation"] = {"method": "chronological 80/20 holdout; naive previous-value baseline",
                                "train_observations": len(train), "test_observations": len(test), "mae": round(mae, 2) if mae is not None else None}
        result["forecast"] = {"method": "7-observation moving average baseline", "next_modal_price": round(sum(recent) / len(recent), 2)}
        result["note"] = "Baseline forecast only; not investment or selling advice. More data and backtesting are required."
    return result

@router.get("/compare", response_model=list[ComparisonRow])
def compare(
    crop_id: str,
    quantity_quintals: Decimal = Query(default=Decimal("10"), gt=0, le=40),
    district_id: str | None = None,
    share: bool = False,
    source: str = Query(default="all", pattern="^(all|government|demo)$"),
    db: Session = Depends(get_db),
):
    if db.get(Crop, crop_id) is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    rows = compare_prices(db, crop_id, district_id, quantity_quintals, share)
    if source == "government":
        return [row for row in rows if row["source_type"] == "government" and not row["is_demo"]]
    if source == "demo":
        return [row for row in rows if row["is_demo"]]
    return rows

@router.get("/trucks", response_model=list[TruckOut])
def trucks(district_id: str | None = None, quantity_quintals: Decimal = Query(default=Decimal("1"), gt=0, le=40), db: Session = Depends(get_db)):
    stmt = select(Truck).where(Truck.is_active.is_(True), Truck.is_verified.is_(True), Truck.capacity_quintals >= quantity_quintals)
    if district_id:
        stmt = stmt.where(Truck.district_id == district_id)
    return db.scalars(stmt.order_by(Truck.base_freight)).all()

@router.get("/buyers", response_model=list[BuyerOut])
def buyers(district_id: str | None = None, crop_id: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Buyer).where(Buyer.is_active.is_(True), Buyer.is_verified.is_(True))
    if district_id:
        stmt = stmt.where(Buyer.district_id == district_id)
    rows = db.scalars(stmt.order_by(Buyer.display_name)).all()
    out = []
    for b in rows:
        accepted = [x for x in b.crops_accepted.split("|") if x]
        if crop_id and crop_id not in accepted:
            continue
        out.append({
            "id": b.id, "display_name": b.display_name, "buyer_type": b.buyer_type,
            "district_id": b.district_id, "crops_accepted": accepted,
            "min_quantity_quintals": b.min_quantity_quintals,
            "offer_price_per_quintal": b.offer_price_per_quintal, "is_verified": b.is_verified
        })
    return out

@router.get("/crop-advice")
def crop_advice(district_id: str | None = None, db: Session = Depends(get_db)):
    crops = db.scalars(select(Crop).order_by(Crop.name_en)).all()
    # Baseline illustration only; not agronomic advice until evidence-backed inputs are connected.
    margin = {"tomato": 78, "groundnut": 70, "banana": 66, "chilli": 73, "paddy": 58}
    stability = {"tomato": 45, "groundnut": 76, "banana": 62, "chilli": 48, "paddy": 80}
    glut = {"tomato": 65, "groundnut": 35, "banana": 42, "chilli": 58, "paddy": 30}
    result = []
    for c in crops:
        m, s, g = margin.get(c.id, 50), stability.get(c.id, 50), glut.get(c.id, 50)
        score = round(0.4*m + 0.3*s + 0.3*(100-g), 1)
        result.append({"crop_id": c.id, "crop_name_en": c.name_en, "crop_name_te": c.name_te,
                       "score": score, "margin_score": m, "price_stability_score": s,
                       "glut_risk": g, "is_demo": True,
                       "explanation": "Illustrative baseline score; not a verified sowing recommendation."})
    return sorted(result, key=lambda x: x["score"], reverse=True)

@router.get("/auth/me", response_model=ProfileOut)
def me(user: Profile = Depends(get_current_user)):
    return user

@router.post("/bookings", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    if db.get(Crop, payload.crop_id) is None or db.get(District, payload.district_id) is None or db.get(Market, payload.market_id) is None:
        raise HTTPException(status_code=400, detail="Invalid crop, district, or market")
    if payload.truck_id is not None:
        truck = db.get(Truck, payload.truck_id)
        if not truck or not truck.is_active or not truck.is_verified:
            raise HTTPException(status_code=400, detail="Truck is unavailable or not verified")
        if truck.capacity_quintals < payload.quantity_quintals:
            raise HTTPException(status_code=400, detail="Truck capacity is too small for this load")
    ref = "SM-" + uuid4().hex[:10].upper()
    booking = Booking(reference=ref, farmer_user_id=user.id, crop_id=payload.crop_id,
                      district_id=payload.district_id, village=payload.village.strip(),
                      quantity_quintals=payload.quantity_quintals, market_id=payload.market_id,
                      truck_id=payload.truck_id, estimated_freight=payload.estimated_freight,
                      farmer_note=payload.farmer_note, status="requested")
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/bookings/mine", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    return db.scalars(select(Booking).where(Booking.farmer_user_id == user.id).order_by(Booking.created_at.desc())).all()

@router.post("/offers", response_model=OfferOut, status_code=201)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    buyer = db.get(Buyer, payload.buyer_id)
    if not buyer or not buyer.is_active or not buyer.is_verified:
        raise HTTPException(status_code=400, detail="Buyer is unavailable or not verified")
    if db.get(Crop, payload.crop_id) is None or db.get(District, payload.district_id) is None:
        raise HTTPException(status_code=400, detail="Invalid crop or district")
    if payload.quantity_quintals < buyer.min_quantity_quintals:
        raise HTTPException(status_code=400, detail="Quantity is below the buyer's minimum")
    offer = FarmerOffer(farmer_user_id=user.id, buyer_id=payload.buyer_id, crop_id=payload.crop_id,
                        district_id=payload.district_id, quantity_quintals=payload.quantity_quintals,
                        expected_price_per_quintal=payload.expected_price_per_quintal,
                        harvest_date=payload.harvest_date, village=payload.village.strip(),
                        message=payload.message, status="submitted")
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer

@router.get("/offers/mine", response_model=list[OfferOut])
def my_offers(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    return db.scalars(select(FarmerOffer).where(FarmerOffer.farmer_user_id == user.id).order_by(FarmerOffer.created_at.desc())).all()

@router.get("/admin/bookings", response_model=list[BookingOut])
def admin_bookings(db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    return db.scalars(select(Booking).order_by(Booking.created_at.desc())).all()

@router.patch("/admin/bookings/{booking_id}", response_model=BookingOut)
def update_booking_status(booking_id: int, payload: AdminStatusUpdate, db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = payload.status
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/admin/trucks")
def admin_trucks(db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    rows = db.scalars(select(Truck).order_by(Truck.id.desc())).all()
    return [{"id": t.id, "display_name": t.display_name, "vehicle_label": t.vehicle_label,
             "capacity_quintals": t.capacity_quintals, "district_id": t.district_id,
             "base_freight": t.base_freight, "is_verified": t.is_verified, "is_active": t.is_active,
             "contact_phone": t.contact_phone} for t in rows]


@router.patch("/admin/trucks/{truck_id}/verification")
def verify_truck(truck_id: int, payload: VerificationUpdate, db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    truck = db.get(Truck, truck_id)
    if not truck: raise HTTPException(status_code=404, detail="Truck not found")
    truck.is_verified = payload.is_verified
    if payload.is_active is not None: truck.is_active = payload.is_active
    db.commit()
    return {"id": truck.id, "is_verified": truck.is_verified, "is_active": truck.is_active}

@router.get("/admin/buyers")
def admin_buyers(db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    rows = db.scalars(select(Buyer).order_by(Buyer.id.desc())).all()
    return [{"id": b.id, "display_name": b.display_name, "buyer_type": b.buyer_type,
             "district_id": b.district_id, "crops_accepted": b.crops_accepted,
             "is_verified": b.is_verified, "is_active": b.is_active, "contact_phone": b.contact_phone}
            for b in rows]

@router.patch("/admin/buyers/{buyer_id}/verification")
def verify_buyer(buyer_id: int, payload: VerificationUpdate, db: Session = Depends(get_db), user: Profile = Depends(require_admin)):
    buyer = db.get(Buyer, buyer_id)
    if not buyer: raise HTTPException(status_code=404, detail="Buyer not found")
    buyer.is_verified = payload.is_verified
    if payload.is_active is not None: buyer.is_active = payload.is_active
    db.commit()
    return {"id": buyer.id, "is_verified": buyer.is_verified, "is_active": buyer.is_active}
