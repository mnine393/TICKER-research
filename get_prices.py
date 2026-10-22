"""Download five completed years of monthly Yahoo Finance adjusted-close prices.

Run from this folder with: python get_prices.py
"""
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


TICKERS = ("SGOV", "IEF", "USIG", "VT")
OUTPUT_FILE = Path(__file__).with_name("prices.csv")


def first_day_months_before(reference, months):
    """Return the first day of the month a whole number of months before reference."""
    month_number = reference.year * 12 + reference.month - 1 - months
    return date(month_number // 12, month_number % 12 + 1, 1)


def yahoo_adjusted_close(ticker, start, end):
    """Return monthly adjusted closes from Yahoo Finance's chart endpoint."""
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(ticker)}"
        f"?period1={int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())}"
        f"&period2={int(datetime.combine(end, datetime.min.time(), tzinfo=timezone.utc).timestamp())}"
        "&interval=1mo&events=history&includeAdjustedClose=true"
    )
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    result = payload["chart"]["result"]
    if not result:
        raise ValueError(f"Yahoo Finance returned no price data for {ticker}.")
    series = result[0]
    adjusted = series["indicators"]["adjclose"][0]["adjclose"]
    rows = {}
    for timestamp, value in zip(series["timestamp"], adjusted):
        if value is not None:
            month = datetime.fromtimestamp(timestamp, tz=timezone.utc).date().replace(day=1)
            if start <= month < end:
                rows[month] = float(value)
    return rows


def main():
    # The first day of this month is excluded, ensuring the partial current month is never used.
    end = date.today().replace(day=1)
    start = first_day_months_before(end, 60)
    prices = {ticker: yahoo_adjusted_close(ticker, start, end) for ticker in TICKERS}
    common_months = sorted(set.intersection(*(set(series) for series in prices.values())))
    if len(common_months) != 60:
        raise ValueError(f"Expected 60 complete monthly rows from {start} through {end}; received {len(common_months)}.")
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("Date", *TICKERS))
        for month in common_months:
            writer.writerow((month.isoformat(), *(f"{prices[ticker][month]:.6f}" for ticker in TICKERS)))
    print(f"Wrote {OUTPUT_FILE.name}: {common_months[0].isoformat()} through {common_months[-1].isoformat()} ({len(common_months)} rows).")


if __name__ == "__main__":
    main()
