from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from app.db import Base, engine, SessionLocal
from app.models import District, Crop, Market, MarketPrice, Truck, Buyer

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # All 26 Andhra Pradesh districts. Keep the original pilot IDs unchanged
        # so existing markets, prices, bookings, and buyer records remain linked.
        districts = [
            District(id="alluri-sitharama-raju", name_en="Alluri Sitharama Raju", name_te="అల్లూరి సీతారామరాజు"),
            District(id="anakapalli", name_en="Anakapalli", name_te="అనకాపల్లి"),
            District(id="ananthapuram", name_en="Ananthapuramu", name_te="అనంతపురం"),
            District(id="annamayya", name_en="Annamayya", name_te="అన్నమయ్య"),
            District(id="bapatla", name_en="Bapatla", name_te="బాపట్ల"),
            District(id="chittoor", name_en="Chittoor", name_te="చిత్తూరు"),
            District(id="konaseema", name_en="Dr. B. R. Ambedkar Konaseema", name_te="డా. బి.ఆర్. అంబేద్కర్ కోనసీమ"),
            District(id="east-godavari", name_en="East Godavari", name_te="తూర్పు గోదావరి"),
            District(id="eluru", name_en="Eluru", name_te="ఏలూరు"),
            District(id="guntur", name_en="Guntur", name_te="గుంటూరు"),
            District(id="kakinada", name_en="Kakinada", name_te="కాకినాడ"),
            District(id="krishna", name_en="Krishna", name_te="కృష్ణా"),
            District(id="kurnool", name_en="Kurnool", name_te="కర్నూలు"),
            District(id="nandyal", name_en="Nandyal", name_te="నంద్యాల"),
            District(id="ntr", name_en="NTR", name_te="ఎన్‌టీఆర్"),
            District(id="palnadu", name_en="Palnadu", name_te="పల్నాడు"),
            District(id="parvathipuram-manyam", name_en="Parvathipuram Manyam", name_te="పార్వతీపురం మన్యం"),
            District(id="prakasam", name_en="Prakasam", name_te="ప్రకాశం"),
            District(id="spsr-nellore", name_en="Sri Potti Sriramulu Nellore", name_te="శ్రీ పొట్టి శ్రీరాములు నెల్లూరు"),
            District(id="sri-sathya-sai", name_en="Sri Sathya Sai", name_te="శ్రీ సత్యసాయి"),
            District(id="srikakulam", name_en="Srikakulam", name_te="శ్రీకాకుళం"),
            District(id="tirupati", name_en="Tirupati", name_te="తిరుపతి"),
            District(id="visakhapatnam", name_en="Visakhapatnam", name_te="విశాఖపట్నం"),
            District(id="vizianagaram", name_en="Vizianagaram", name_te="విజయనగరం"),
            District(id="west-godavari", name_en="West Godavari", name_te="పశ్చిమ గోదావరి"),
            District(id="ysr-kadapa", name_en="YSR Kadapa", name_te="వైఎస్ఆర్ కడప"),
        ]
        for x in districts:
            if not db.get(District, x.id): db.add(x)
        crops = [
            Crop(id="tomato", name_en="Tomato", name_te="టమాటా", category="vegetable", aliases="tamata|tamatar|tomatoes"),
            Crop(id="groundnut", name_en="Groundnut", name_te="వేరుశనగ", category="oilseed", aliases="peanut|palli|verusenaga"),
            Crop(id="banana", name_en="Banana", name_te="అరటి", category="fruit", aliases="arati"),
            Crop(id="chilli", name_en="Chilli", name_te="మిర్చి", category="spice", aliases="mirchi|chili"),
            Crop(id="paddy", name_en="Paddy", name_te="వరి", category="grain", aliases="rice|vari"),
            Crop(id="maize", name_en="Maize", name_te="మొక్కజొన్న", category="grain", aliases="corn|mokkajonna"),
            Crop(id="onion", name_en="Onion", name_te="ఉల్లిపాయ", category="vegetable", aliases="ullipaya"),
        ]
        for x in crops:
            if not db.get(Crop, x.id): db.add(x)
        db.flush()
        markets = [
            Market(id="madanapalle", name_en="Madanapalle", name_te="మదనపల్లె", district_id="annamayya", village_or_town="Madanapalle"),
            Market(id="ananthapur", name_en="Anantapur", name_te="అనంతపురం", district_id="ananthapuram", village_or_town="Anantapur"),
            Market(id="hindupur", name_en="Hindupur", name_te="హిందూపురం", district_id="sri-sathya-sai", village_or_town="Hindupur"),
            Market(id="local-yard", name_en="Local yard (illustrative)", name_te="స్థానిక యార్డు (నమూనా)", district_id="annamayya", village_or_town="Local"),
        ]
        for x in markets:
            if not db.get(Market, x.id): db.add(x)
        db.flush()
        # Clearly synthetic daily history for local development until the official API key is available.
        # These values are NOT official mandi prices and must never be presented as live data.
        sample_prices = {
            "tomato": [1850, 1700, 1550, 1250],
            "groundnut": [6400, 6700, 6550, 5900],
            "banana": [2400, 2250, 2150, 1700],
            "chilli": [11800, 11200, 10900, 9800],
            "paddy": [2250, 2180, 2200, 2050],
            "maize": [2200, 2100, 2150, 1950],
            "onion": [1800, 1650, 1720, 1400],
        }
        market_ids = ["madanapalle", "ananthapur", "hindupur", "local-yard"]
        today = date.today()
        for crop_id, values in sample_prices.items():
            for market_id, base_modal in zip(market_ids, values):
                for days_ago in range(29, -1, -1):
                    observation_date = today - timedelta(days=days_ago)
                    exists = db.scalar(select(MarketPrice.id).where(
                        MarketPrice.crop_id == crop_id,
                        MarketPrice.market_id == market_id,
                        MarketPrice.price_date == observation_date,
                        MarketPrice.is_demo.is_(True)
                    ).limit(1))
                    if exists:
                        continue
                    # Deterministic, modest variation so charts are repeatable across runs.
                    variation_steps = (((days_ago * 7 + len(crop_id) * 3 + len(market_id)) % 9) - 4)
                    modal = max(1, round(base_modal * (1 + variation_steps * 0.012)))
                    db.add(MarketPrice(
                        crop_id=crop_id, market_id=market_id, variety="Common",
                        min_price=Decimal(str(round(modal * 0.9, 2))),
                        modal_price=Decimal(str(modal)),
                        max_price=Decimal(str(round(modal * 1.1, 2))),
                        unit="quintal", price_date=observation_date,
                        source_type="demo", source_name="Synthetic sample history — not official or live",
                        is_verified=False, is_demo=True
                    ))
        if db.query(Truck).count() == 0:
            db.add_all([
                Truck(display_name="Demo truck A", vehicle_label="Small goods vehicle", capacity_quintals=Decimal("15"), district_id="annamayya", base_freight=Decimal("1600"), is_verified=False, is_active=True, contact_phone=None),
                Truck(display_name="Demo truck B", vehicle_label="Medium goods vehicle", capacity_quintals=Decimal("40"), district_id="ananthapuram", base_freight=Decimal("2800"), is_verified=False, is_active=True, contact_phone=None),
            ])
        if db.query(Buyer).count() == 0:
            db.add_all([
                Buyer(display_name="Demo restaurant buyer", buyer_type="restaurant", district_id="annamayya", crops_accepted="tomato|onion|banana", min_quantity_quintals=Decimal("0.5"), offer_price_per_quintal=Decimal("1700"), is_verified=False, is_active=True),
                Buyer(display_name="Demo housing community", buyer_type="housing", district_id="ananthapuram", crops_accepted="tomato|banana|onion", min_quantity_quintals=Decimal("0.1"), offer_price_per_quintal=Decimal("1600"), is_verified=False, is_active=True),
            ])
        db.commit()
        print("Seed complete. Synthetic 30-day sample history is for development only; not official/live prices.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
