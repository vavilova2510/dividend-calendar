from datetime import date

from src.smartlab import parse_dividend_table

SAMPLE_HTML = """
<html><body>
<table class="table1 fixtable">
  <thead>
    <tr>
      <th>Название</th><th>Тикер</th><th>Период</th>
      <th>Дивиденд, руб</th><th>Див. Дох.</th><th>СД</th>
      <th>Купить До</th><th>Дата закрытия реестра</th>
      <th>Выплата До</th><th>Цена акции</th><th></th>
    </tr>
  </thead>
  <tbody>
    <tr class="dividend_approved">
      <td><a href="/q/SBER/dividend/">Сбербанк</a></td>
      <td>SBER</td>
      <td>2кв 2026</td>
      <td><strong>18,5</strong></td>
      <td><strong>6,7%</strong></td>
      <td></td>
      <td>10.10.2026</td>
      <td>12.10.2026</td>
      <td>22.10.2026</td>
      <td>276,1</td>
      <td><a class="charticon3" href="/forum/SBER"></a></td>
    </tr>
    <tr>
      <td><a href="/q/GMKN/dividend/">Норникель</a></td>
      <td>GMKN</td>
      <td>1кв 2026</td>
      <td><strong>1,85</strong></td>
      <td><strong>1,4%</strong></td>
      <td></td>
      <td>09.10.2026</td>
      <td>12.10.2026</td>
      <td>22.10.2026</td>
      <td>132,48</td>
      <td><a class="charticon3" href="/forum/GMKN"></a></td>
    </tr>
  </tbody>
</table>
</body></html>
"""


def test_parses_all_rows():
    rows = parse_dividend_table(SAMPLE_HTML)
    assert len(rows) == 2


def test_parses_sber_row_fields():
    rows = parse_dividend_table(SAMPLE_HTML)
    sber = next(r for r in rows if r.ticker == "SBER")

    assert sber.name == "Сбербанк"
    assert sber.dividend_value == 18.5
    assert sber.cutoff_date == date(2026, 10, 12)
    assert sber.payment_date == date(2026, 10, 22)


def test_ignores_tables_without_ticker_header():
    html = "<table><tr><td>ничего интересного</td></tr></table>"
    assert parse_dividend_table(html) == []


def test_skips_row_missing_required_fields():
    html = """
    <table>
      <thead><tr><th>Тикер</th><th>Дивиденд</th></tr></thead>
      <tbody>
        <tr>
          <td>Без тикера</td><td></td><td></td><td></td>
          <td></td><td></td><td></td><td></td><td></td>
        </tr>
      </tbody>
    </table>
    """
    assert parse_dividend_table(html) == []
