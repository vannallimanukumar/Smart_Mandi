from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Market, MarketPrice, Truck

def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def list_prices(db: Session, crop_id: str, district_id: str | None = None, market_id: str | None = None, date_from: date | None = None, date_to: date | None = None):
    stmt = select(MarketPrice, Market).join(Market, Market.id == MarketPrice.market_id).where(MarketPrice.crop_id == crop_id)
    if district_id:
        stmt = stmt.where(Market.district_id == district_id)
    if market_id:
        stmt = stmt.where(MarketPrice.market_id == market_id)
    if date_from:
        stmt = stmt.where(MarketPrice.price_date >= date_from)
    if date_to:
        stmt = stmt.where(MarketPrice.price_date <= date_to)
    rows = db.execute(stmt.order_by(MarketPrice.price_date.desc(), Market.name_en)).all()
    return [{
        "crop_id": p.crop_id, "market_id": p.market_id,
        "market_name_en": m.name_en, "market_name_te": m.name_te,
        "district_id": m.district_id, "min_price": p.min_price,
        "modal_price": p.modal_price, "max_price": p.max_price,
        "unit": p.unit, "price_date": p.price_date,
        "source_type": p.source_type, "source_name": p.source_name,
        "is_verified": p.is_verified, "is_demo": p.is_demo,
        "freshness": freshness(p.price_date)
    } for p, m in rows]

def freshness(price_date: date, today: date | None = None) -> str:
    age = ((today or date.today()) - price_date).days
    if age <= 2: return "fresh"
    if age <= 7: return "aging"
    return "stale"

def compare_prices(db: Session, crop_id: str, district_id: str | None, quantity: Decimal, share: bool):
    rows = list_prices(db, crop_id, district_id)
    # Compare only each market's latest available record; history remains available separately.
    latest = {}
    for item in rows:
        if item["market_id"] not in latest:
            latest[item["market_id"]] = item
    out = []
    for row in latest.values():
        gross = money(Decimal(row["modal_price"]) * quantity)
        # Use an actual listed quote from an active, verified truck able to carry this load.
        quotes = db.scalars(select(Truck.base_freight).where(
            Truck.is_active.is_(True), Truck.is_verified.is_(True),
            Truck.capacity_quintals >= quantity, Truck.district_id == row["district_id"]
        ).order_by(Truck.base_freight)).all()
        if quotes:
            freight = money(Decimal(quotes[0]) / 2 if share else Decimal(quotes[0]))
            freight_method = "verified_truck_quote_shared" if share else "verified_truck_quote"
            net = money(gross - freight)
        else:
            freight = None
            net = None
            freight_method = "quote_unavailable"
        out.append({
            "market_id": row["market_id"], "market_name_en": row["market_name_en"],
            "market_name_te": row["market_name_te"], "district_id": row["district_id"],
            "modal_price_per_quintal": row["modal_price"], "gross_value": gross,
            "estimated_freight": freight, "estimated_net": net, "freight_method": freight_method,
            "price_date": row["price_date"], "source_type": row["source_type"],
            "source_name": row["source_name"], "is_demo": row["is_demo"]
        })
    # Ranks with a known quote above rows where a net estimate cannot responsibly be calculated.
    return sorted(out, key=lambda x: (x["estimated_net"] is not None, x["estimated_net"] or Decimal("-1")), reverse=True)
