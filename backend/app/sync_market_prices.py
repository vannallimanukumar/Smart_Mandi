"""Import supported official AGMARKNET prices for all Andhra Pradesh districts.

Run from backend/: python -m app.sync_market_prices
The importer fetches pages from data.gov.in, validates state/district/crop/date/prices,
and never converts synthetic demo rows into government records.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from app.core.config import settings
from app.db import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.models import Crop, District, Market, MarketPrice

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

# Provider district names -> stable district IDs in the application database.
DISTRICT_ALIASES = {
    "alluri sitharama raju": "alluri-sitharama-raju",
    "anakapalli": "anakapalli",
    "ananthapuramu": "ananthapuram", "ananthapuram": "ananthapuram", "anantapur": "ananthapuram",
    "annamayya": "annamayya",
    "bapatla": "bapatla", "chittoor": "chittoor",
    "dr b r ambedkar konaseema": "konaseema", "konaseema": "konaseema",
    "east godavari": "east-godavari", "eluru": "eluru", "guntur": "guntur",
    "kakinada": "kakinada", "krishna": "krishna", "kurnool": "kurnool",
    "nandyal": "nandyal", "ntr": "ntr", "palnadu": "palnadu",
    "parvathipuram manyam": "parvathipuram-manyam", "prakasam": "prakasam",
    "sri potti sriramulu nellore": "spsr-nellore", "nellore": "spsr-nellore",
    "sri sathya sai": "sri-sathya-sai", "sri sathya sai district": "sri-sathya-sai",
    "srikakulam": "srikakulam", "tirupati": "tirupati",
    "visakhapatnam": "visakhapatnam", "vizianagaram": "vizianagaram",
    "west godavari": "west-godavari", "ysr kadapa": "ysr-kadapa", "kadapa": "ysr-kadapa",
}

CROP_ALIASES = {
    "paddy common": "paddy", "paddy fine": "paddy", "rice": "paddy",
    "ground nut seed": "groundnut", "groundnut seed": "groundnut",
    "tomato hybrid": "tomato", "green chilli": "chilli", "dry chilli": "chilli",
    "maize yellow": "maize", "sweet orange": "orange",
}

def norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()

def parse_date(value: object):
    raw = str(value or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None

def as_price(value: object):
    try:
        result = Decimal(str(value).replace(",", "").strip())
        return result if result > 0 else None
    except (InvalidOperation, ValueError, AttributeError):
        return None

def _curl_config_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

def fetch_records() -> list[dict]:
    api_key = settings.data_gov_in_api_key.strip()
    if not api_key:
        raise SystemExit("DATA_GOV_IN_API_KEY is empty. Add it to backend/.env; no demo-to-live fallback is performed.")

    # Use provider's maximum page size and paginate; locally validate state because
    # the provider's state filter was inconsistent in testing.
    page_size = 1000
    max_pages = 5
    all_records: list[dict] = []
    for page in range(max_pages):
        offset = page * page_size
        config_lines = [
            "silent", "show-error", "fail", 'connect-timeout = "10"', 'max-time = "60"', "get",
            f'url = "{_curl_config_value(settings.data_gov_in_api_url)}"',
            f'data-urlencode = "{_curl_config_value("api-key=" + api_key)}"',
            'data-urlencode = "format=json"', f'data-urlencode = "limit={page_size}"',
            f'data-urlencode = "offset={offset}"',
            'data-urlencode = "filters[state]=Andhra Pradesh"',
        ]
        try:
            result = subprocess.run(["curl.exe", "--config", "-"], input="\n".join(config_lines) + "\n",
                                    capture_output=True, text=True, timeout=65, check=False)
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise SystemExit(f"Government API request failed on page {page + 1}: {exc}. Database was not changed.") from exc
        if result.returncode != 0:
            raise SystemExit(f"Government API request failed on page {page + 1} (curl exit {result.returncode}). Database was not changed.")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Government API returned invalid JSON on page {page + 1}. Database was not changed.") from exc
        records = payload.get("records") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise SystemExit(f"Government API response has no records list on page {page + 1}. Database was not changed.")
        all_records.extend(row for row in records if isinstance(row, dict) and norm(row.get("state")) in {"andhra pradesh", "andhra pradesh state"})
        print(f"Fetched page {page + 1}: {len(records)} provider records; {len(all_records)} Andhra Pradesh records retained so far.")
        if len(records) < page_size:
            break
    return all_records

def main() -> None:
    records = fetch_records()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    imported = updated = skipped = 0
    try:
        districts = {norm(d.name_en): d for d in db.scalars(select(District)).all()}
        crops = db.scalars(select(Crop)).all()
        crop_by_name = {}
        for crop in crops:
            for alias in [crop.name_en, crop.id, *crop.aliases.split("|")]:
                crop_by_name[norm(alias)] = crop
        for row in records:
            district_name = norm(row.get("district"))
            district_id = DISTRICT_ALIASES.get(district_name)
            district = db.get(District, district_id) if district_id else districts.get(district_name)
            commodity = norm(row.get("commodity"))
            crop_id = CROP_ALIASES.get(commodity)
            crop = db.get(Crop, crop_id) if crop_id else crop_by_name.get(commodity)
            arrival_date = parse_date(row.get("arrival_date"))
            minimum, modal, maximum = (as_price(row.get(k)) for k in ("min_price", "modal_price", "max_price"))
            market_name = str(row.get("market") or "").strip()
            if not district or not crop or not arrival_date or not market_name or not all((minimum, modal, maximum)) or not (minimum <= modal <= maximum):
                skipped += 1
                continue
            market_slug = re.sub(r"[^a-z0-9]+", "-", norm(market_name)).strip("-")[:35]
            market_id = f"agmarknet-{district.id}-{market_slug}"
            market = db.get(Market, market_id)
            if market is None:
                market = Market(id=market_id, name_en=market_name, name_te=market_name, district_id=district.id, village_or_town=market_name, is_active=True)
                db.add(market)
                db.flush()
            variety = str(row.get("variety") or "Common")[:120]
            existing = db.scalar(select(MarketPrice).where(MarketPrice.crop_id == crop.id, MarketPrice.market_id == market.id, MarketPrice.price_date == arrival_date, MarketPrice.variety == variety, MarketPrice.source_type == "government").limit(1))
            values = dict(min_price=minimum, modal_price=modal, max_price=maximum, unit="quintal", source_type="government", source_name="data.gov.in / AGMARKNET", is_verified=True, is_demo=False)
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                db.add(MarketPrice(crop_id=crop.id, market_id=market.id, variety=variety, price_date=arrival_date, **values))
                imported += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"AGMARKNET import finished. New rows: {imported}; updated rows: {updated}; skipped rows: {skipped}; Andhra Pradesh provider rows: {len(records)}.")
    print("Prices retain the reported arrival_date; daily feed is not guaranteed real-time data.")

if __name__ == "__main__":
    main()
