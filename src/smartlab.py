"""Парсинг таблицы дивидендов с smart-lab.ru.

MOEX ISS не отдаёт размер дивиденда и дату закрытия реестра без платной
подписки (Corporate Information Service), поэтому эти два поля берём из
открытой таблицы на smart-lab.ru. Курс акции и название бумаги по-прежнему
берутся из бесплатного MOEX ISS (см. moex_api.py).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

UPCOMING_URL = "https://smart-lab.ru/dividends/"
HISTORY_URL = "https://smart-lab.ru/dividends/history/"
REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; moex-dividend-calendar/1.0; +https://github.com/)"


@dataclass
class RawDividendRow:
    ticker: str
    name: str
    period: str
    dividend_value: float
    cutoff_date: date
    payment_date: date | None


def fetch_dividend_rows(url: str) -> list[RawDividendRow]:
    """Скачивает и парсит одну из таблиц smart-lab (будущие или прошедшие дивиденды).

    При сетевой ошибке возвращает пустой список и логирует предупреждение —
    вызывающий код должен уметь продолжить работу с тем, что успело собраться.
    """
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("smart-lab.ru: не удалось загрузить %s: %s", url, exc)
        return []

    return parse_dividend_table(response.text)


def parse_dividend_table(html: str) -> list[RawDividendRow]:
    soup = BeautifulSoup(html, "html.parser")
    table = _find_dividends_table(soup)
    if table is None:
        logger.warning("smart-lab.ru: не нашёл таблицу дивидендов на странице")
        return []

    rows: list[RawDividendRow] = []
    body = table.find("tbody")
    if body is None:
        return rows

    for tr in body.find_all("tr", recursive=False):
        cells = tr.find_all("td", recursive=False)
        if len(cells) < 9:
            continue
        try:
            row = _parse_row(cells)
        except (ValueError, IndexError) as exc:
            logger.warning("smart-lab.ru: пропускаю строку, не смог разобрать: %s", exc)
            continue
        if row is not None:
            rows.append(row)
    return rows


def _find_dividends_table(soup: BeautifulSoup):
    for table in soup.find_all("table"):
        header_text = table.get_text(" ", strip=True)
        if "Тикер" in header_text and "Дивиденд" in header_text:
            return table
    return None


def _parse_row(cells) -> RawDividendRow | None:
    name = cells[0].get_text(strip=True)
    ticker = cells[1].get_text(strip=True)
    period = cells[2].get_text(strip=True)
    dividend_text = cells[3].get_text(strip=True)
    cutoff_text = cells[7].get_text(strip=True)
    payment_text = cells[8].get_text(strip=True)

    if not ticker or not dividend_text or not cutoff_text:
        return None

    return RawDividendRow(
        ticker=ticker,
        name=name,
        period=period,
        dividend_value=_parse_number(dividend_text),
        cutoff_date=_parse_date(cutoff_text),
        payment_date=_parse_date(payment_text) if payment_text else None,
    )


def _parse_number(text: str) -> float:
    return float(text.replace("\xa0", "").replace(" ", "").replace(",", "."))


def _parse_date(text: str) -> date:
    day, month, year = text.split(".")
    return date(int(year), int(month), int(day))
