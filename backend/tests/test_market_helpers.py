from datetime import date, timedelta
from app.services.market import freshness, money
from decimal import Decimal

def test_freshness_bands():
    today = date(2026, 10, 29)
    assert freshness(today, today) == "fresh"
    assert freshness(today - timedelta(days=4), today) == "aging"
    assert freshness(today - timedelta(days=10), today) == "stale"

def test_money_rounds_to_paise():
    assert money(Decimal("12.345")) == Decimal("12.35")
