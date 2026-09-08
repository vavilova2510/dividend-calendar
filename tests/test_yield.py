from datetime import date

from src.model import compute_yield_percent, previous_business_day


def test_previous_business_day_from_monday_is_friday():
    monday = date(2026, 9, 21)
    assert previous_business_day(monday) == date(2026, 9, 18)


def test_previous_business_day_from_tuesday_is_monday():
    tuesday = date(2026, 9, 22)
    assert previous_business_day(tuesday) == date(2026, 9, 21)


def test_previous_business_day_from_sunday_is_friday():
    sunday = date(2026, 9, 20)
    assert previous_business_day(sunday) == date(2026, 9, 18)


def test_compute_yield_percent_basic():
    assert compute_yield_percent(dividend_value=10, current_price=200) == 5.0


def test_compute_yield_percent_none_price():
    assert compute_yield_percent(dividend_value=10, current_price=None) is None


def test_compute_yield_percent_zero_price():
    assert compute_yield_percent(dividend_value=10, current_price=0) is None
