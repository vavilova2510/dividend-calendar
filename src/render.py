"""Сборка docs/dividends.csv и docs/index.html из списка DividendEvent."""
from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from src.model import DividendEvent

CSV_HEADER = [
    "ticker",
    "name",
    "dividend_value",
    "cutoff_date",
    "buy_before_date",
    "payment_date",
    "current_price",
    "yield_percent",
]


def write_csv(events: list[DividendEvent], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for e in events:
            writer.writerow(
                [
                    e.ticker,
                    e.name,
                    f"{e.dividend_value:.4f}",
                    e.cutoff_date.isoformat(),
                    e.buy_before_date.isoformat(),
                    e.payment_date.isoformat() if e.payment_date else "",
                    f"{e.current_price:.2f}" if e.current_price is not None else "",
                    f"{e.yield_percent:.2f}" if e.yield_percent is not None else "",
                ]
            )


def write_html(events: list[DividendEvent], path: Path) -> None:
    upcoming = sorted((e for e in events if e.is_upcoming), key=lambda e: e.cutoff_date)
    past = sorted((e for e in events if not e.is_upcoming), key=lambda e: e.cutoff_date, reverse=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Календарь дивидендов российских акций</title>
<style>
{_CSS}
</style>
</head>
<body>
<main>
  <h1>Календарь дивидендов российских акций</h1>
  <p class="meta">Обновлено: {generated_at} · Источники данных: MOEX ISS (цена, название), smart-lab.ru (размер дивиденда, даты)</p>

  <h2>Ближайшие выплаты</h2>
  {_render_table(upcoming)}

  <h2>Прошедшие выплаты</h2>
  {_render_table(past)}
</main>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _render_table(events: list[DividendEvent]) -> str:
    if not events:
        return "<p class=\"empty\">Нет данных.</p>"

    rows = "\n".join(_render_row(e) for e in events)
    return f"""<table>
  <thead>
    <tr>
      <th>Тикер</th>
      <th>Название</th>
      <th>Дивиденд, ₽</th>
      <th>Закрытие реестра</th>
      <th>Купить до (T-1)</th>
      <th>Доходность</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>"""


def _render_row(e: DividendEvent) -> str:
    price_cell = f"{e.current_price:.2f} ₽" if e.current_price is not None else "н/д"
    yield_cell = f"{e.yield_percent:.2f}%" if e.yield_percent is not None else "н/д"
    return f"""<tr>
      <td>{e.ticker}</td>
      <td>{e.name or ""}</td>
      <td>{e.dividend_value:.2f}</td>
      <td>{_fmt(e.cutoff_date)}</td>
      <td>{_fmt(e.buy_before_date)}</td>
      <td title="Цена: {price_cell}">{yield_cell}</td>
    </tr>"""


def _fmt(d: date) -> str:
    return d.strftime("%d.%m.%Y")


_CSS = """
body { font-family: -apple-system, Arial, sans-serif; margin: 0; padding: 2rem; background: #fafafa; color: #1a1a1a; }
main { max-width: 900px; margin: 0 auto; }
h1 { font-size: 1.5rem; }
h2 { font-size: 1.1rem; margin-top: 2rem; border-bottom: 2px solid #ddd; padding-bottom: .3rem; }
.meta { color: #666; font-size: .85rem; }
table { width: 100%; border-collapse: collapse; margin-top: .5rem; }
th, td { text-align: left; padding: .5rem .6rem; border-bottom: 1px solid #eee; font-size: .9rem; }
th { color: #666; font-weight: 600; }
.empty { color: #888; font-style: italic; }
"""
