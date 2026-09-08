"""Запросы к открытому MOEX ISS API: текущая цена и короткое название бумаги."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

BOARD = "TQBR"
MARKETDATA_URL = (
    "https://iss.moex.com/iss/engines/stock/markets/shares/boards/{board}/securities/{secid}.json"
)
REQUEST_TIMEOUT = 10


@dataclass
class SecurityInfo:
    secid: str
    short_name: str | None
    last_price: float | None


def fetch_security_info(secid: str) -> SecurityInfo:
    """Возвращает цену и название бумаги. При любой ошибке — поля None, тикер не теряется."""
    url = MARKETDATA_URL.format(board=BOARD, secid=secid)
    params = {
        "iss.only": "marketdata,securities",
        "iss.meta": "off",
        "marketdata.columns": "SECID,LAST",
        "securities.columns": "SECID,SHORTNAME",
    }
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("MOEX ISS: не удалось получить данные по %s: %s", secid, exc)
        return SecurityInfo(secid=secid, short_name=None, last_price=None)

    short_name = _first_value(payload, "securities", "SHORTNAME")
    last_price = _first_value(payload, "marketdata", "LAST")
    return SecurityInfo(
        secid=secid,
        short_name=short_name,
        last_price=float(last_price) if last_price is not None else None,
    )


def _first_value(payload: dict, block: str, column: str):
    block_data = payload.get(block)
    if not block_data or not block_data.get("data"):
        return None
    columns = block_data["columns"]
    row = block_data["data"][0]
    return row[columns.index(column)]
