"""Расчёты: дата последней покупки (T-1) и дивидендная доходность."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class DividendEvent:
    ticker: str
    name: str
    period: str
    dividend_value: float
    cutoff_date: date
    buy_before_date: date
    payment_date: date | None
    current_price: float | None
    yield_percent: float | None

    @property
    def is_upcoming(self) -> bool:
        return self.cutoff_date >= date.today()


def previous_business_day(day: date) -> date:
    """Предыдущий будний день (пн-пт).

    Упрощение: не учитывает биржевые праздники МосБиржи, только выходные.
    Для дивидендного календаря T-1 в режиме T+1 это даёт точный результат
    почти всегда, кроме случаев, когда закрытию реестра предшествует
    праздничный будний день.
    """
    previous = day - timedelta(days=1)
    while previous.weekday() >= 5:  # 5 = суббота, 6 = воскресенье
        previous -= timedelta(days=1)
    return previous


def compute_yield_percent(dividend_value: float, current_price: float | None) -> float | None:
    if not current_price or current_price <= 0:
        return None
    return dividend_value / current_price * 100
