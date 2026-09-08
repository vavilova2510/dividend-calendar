"""Точка входа: config.yaml -> MOEX ISS + smart-lab.ru -> docs/index.html + docs/dividends.csv."""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

from src.model import DividendEvent, compute_yield_percent, previous_business_day
from src.moex_api import fetch_security_info
from src.render import write_csv, write_html
from src.smartlab import HISTORY_URL, UPCOMING_URL, RawDividendRow, fetch_dividend_rows

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
DOCS_DIR = ROOT / "docs"


def load_tickers(config_path: Path = CONFIG_PATH) -> list[str]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return [t.upper() for t in data.get("tickers", [])]


def build_events(tickers: list[str]) -> list[DividendEvent]:
    raw_rows: list[RawDividendRow] = fetch_dividend_rows(UPCOMING_URL) + fetch_dividend_rows(HISTORY_URL)
    wanted = set(tickers)
    events: list[DividendEvent] = []

    for row in raw_rows:
        if row.ticker not in wanted:
            continue

        info = fetch_security_info(row.ticker)
        buy_before = previous_business_day(row.cutoff_date)
        events.append(
            DividendEvent(
                ticker=row.ticker,
                name=info.short_name or row.name,
                period=row.period,
                dividend_value=row.dividend_value,
                cutoff_date=row.cutoff_date,
                buy_before_date=buy_before,
                payment_date=row.payment_date,
                current_price=info.last_price,
                yield_percent=compute_yield_percent(row.dividend_value, info.last_price),
            )
        )

    missing = wanted - {e.ticker for e in events}
    if missing:
        logger.warning("Нет данных о дивидендах на smart-lab.ru для тикеров: %s", ", ".join(sorted(missing)))

    return events


def main() -> None:
    tickers = load_tickers()
    logger.info("Тикеров в config.yaml: %d", len(tickers))

    events = build_events(tickers)
    logger.info("Собрано событий: %d", len(events))

    DOCS_DIR.mkdir(exist_ok=True)
    write_csv(events, DOCS_DIR / "dividends.csv")
    write_html(events, DOCS_DIR / "index.html")
    logger.info("Готово: %s", DOCS_DIR)


if __name__ == "__main__":
    main()
