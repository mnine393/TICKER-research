"""Build a five-year, 10-K-only owner-earnings record from SEC EDGAR facts."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SEC_USER_AGENT = "Miles Nine mnine@purdue.edu"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ANNUAL_DAYS_MIN = 350
ANNUAL_DAYS_MAX = 380

METRICS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_spending": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "research_and_development": ["ResearchAndDevelopmentExpense"],
    "equity": ["StockholdersEquity"],
    "liabilities": ["Liabilities"],
    "assets_current": ["AssetsCurrent"],
    "liabilities_current": ["LiabilitiesCurrent"],
}
INSTANT_METRICS = {"equity", "liabilities", "assets_current", "liabilities_current"}


def fetch_json(url: str) -> dict:
    """Fetch an SEC JSON document with the declared course User-Agent."""
    request = Request(url, headers={"User-Agent": SEC_USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"SEC EDGAR request failed: {error}") from error


def normalize_ticker(value: str) -> str:
    ticker = value.strip().upper()
    if not re.fullmatch(r"[A-Z.\-]{1,12}", ticker):
        raise ValueError("Ticker must contain only letters, periods, or hyphens.")
    return ticker


def cik_for_ticker(ticker: str) -> str:
    records = fetch_json(TICKERS_URL)
    for record in records.values():
        if record.get("ticker", "").upper() == ticker:
            return str(record["cik_str"]).zfill(10)
    raise ValueError(f"Ticker {ticker} was not found in SEC company_tickers.json.")


def _latest_by_end(candidates: list[dict]) -> dict:
    return max(candidates, key=lambda item: (item.get("filed", ""), item.get("accn", "")))


def _annual_values(fact: dict) -> dict[str, dict]:
    """Return one latest-filed 10-K annual duration fact per fiscal-year end."""
    candidates: dict[str, list[dict]] = {}
    for item in fact.get("units", {}).get("USD", []):
        if item.get("form") != "10-K" or not item.get("start") or not item.get("end"):
            continue
        try:
            duration = (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days
        except ValueError:
            continue
        if ANNUAL_DAYS_MIN <= duration <= ANNUAL_DAYS_MAX:
            candidates.setdefault(item["end"], []).append(item)
    return {end: _latest_by_end(items) for end, items in candidates.items()}


def _instant_values(fact: dict) -> dict[str, dict]:
    """Return one latest-filed 10-K instant fact per fiscal-year end."""
    candidates: dict[str, list[dict]] = {}
    for item in fact.get("units", {}).get("USD", []):
        if item.get("form") == "10-K" and item.get("end") and not item.get("start"):
            candidates.setdefault(item["end"], []).append(item)
    return {end: _latest_by_end(items) for end, items in candidates.items()}


def metric_candidates(company_facts: dict, metric: str) -> dict[str, dict]:
    """Select the stated tag priority, with latest filing winning within a period."""
    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})
    selected: dict[str, dict] = {}
    selector = _instant_values if metric in INSTANT_METRICS else _annual_values
    for tag in METRICS[metric]:
        fact = us_gaap.get(tag)
        if not fact:
            continue
        for end, item in selector(fact).items():
            selected.setdefault(end, {"value": item.get("val"), "tag": tag, "filed": item.get("filed")})
    return selected


def _display_millions(value: float | int | None) -> str:
    if value is None:
        return "not found"
    return f"${value / 1_000_000:,.1f} million"


def _record(source: dict | None) -> dict:
    if not source or source.get("value") is None:
        return {"value": None, "tag": "not found", "display": "not found"}
    value = source["value"]
    return {"value": value, "tag": source["tag"], "display": _display_millions(value)}


def _check_all(condition_values: list[bool | None]) -> str:
    if any(value is None for value in condition_values):
        return "not known"
    return "pass" if all(condition_values) else "fail"


def build_analysis(ticker: str) -> dict:
    """Download facts and return a five-year analysis without writing a file."""
    ticker = normalize_ticker(ticker)
    cik = cik_for_ticker(ticker)
    company_facts = fetch_json(FACTS_URL.format(cik=cik))
    sources = {metric: metric_candidates(company_facts, metric) for metric in METRICS}
    fiscal_ends = sorted({end for values in sources.values() for end in values})[-5:]
    if not fiscal_ends:
        raise RuntimeError(f"No 10-K USD facts were available for {ticker}.")

    years = []
    for fiscal_end in fiscal_ends:
        row = {"fiscal_year_end": fiscal_end}
        for metric in METRICS:
            row[metric] = _record(sources[metric].get(fiscal_end))

        net_income = row["net_income"]["value"]
        equity = row["equity"]["value"]
        if net_income is None or equity is None or equity <= 0:
            row["roe"] = {"value": None, "display": "not known"}
        else:
            roe = net_income / equity
            row["roe"] = {"value": roe, "display": f"{roe:.1%}"}

        assets_current = row["assets_current"]["value"]
        liabilities_current = row["liabilities_current"]["value"]
        if assets_current is None or liabilities_current is None or liabilities_current == 0:
            row["current_ratio"] = {"value": None, "display": "not known"}
        else:
            current_ratio = assets_current / liabilities_current
            row["current_ratio"] = {"value": current_ratio, "display": f"{current_ratio:.2f}x"}

        liabilities = row["liabilities"]["value"]
        if liabilities is None or equity is None or equity <= 0:
            row["liabilities_to_equity"] = {"value": None, "display": "not known"}
        else:
            liabilities_to_equity = liabilities / equity
            row["liabilities_to_equity"] = {"value": liabilities_to_equity, "display": f"{liabilities_to_equity:.2f}x"}

        operating_cash_flow = row["operating_cash_flow"]["value"]
        capital_spending = row["capital_spending"]["value"]
        if operating_cash_flow is None or capital_spending is None:
            row["owner_earnings"] = {"value": None, "display": "not found"}
        else:
            owner_earnings = operating_cash_flow - capital_spending
            row["owner_earnings"] = {
                "value": owner_earnings,
                "display": _display_millions(owner_earnings),
            }
        years.append(row)

    roe_check = _check_all([None if row["roe"]["value"] is None else row["roe"]["value"] >= 0.15 for row in years])
    owner_positive = _check_all(
        [None if row["owner_earnings"]["value"] is None else row["owner_earnings"]["value"] > 0 for row in years]
    )
    first_owner = years[0]["owner_earnings"]["value"]
    last_owner = years[-1]["owner_earnings"]["value"]
    owner_growth = "not known" if first_owner is None or last_owner is None else ("pass" if last_owner > first_owner else "fail")

    analysis = {
        "ticker": ticker,
        "cik": cik,
        "company_name": company_facts.get("entityName", "not found"),
        "source": "SEC EDGAR Company Facts; 10-K filings only",
        "years": years,
        "checks": {
            "roe_at_least_15_percent_every_year": roe_check,
            "owner_earnings_positive_every_year": owner_positive,
            "owner_earnings_grew_first_to_last": owner_growth,
        },
    }
    analysis["report"] = format_report(analysis)
    return analysis


def format_report(analysis: dict) -> str:
    lines = [
        f"{analysis['ticker']} owner-earnings facts (SEC EDGAR, 10-K only)",
        f"CIK: {analysis['cik']} | Company: {analysis['company_name']}",
        "All dollar values are $ millions. 'not found' is not an estimate.",
        "",
    ]
    for row in analysis["years"]:
        lines.append(f"Fiscal year ended {row['fiscal_year_end']}")
        for key, label in [
            ("revenue", "Revenue"),
            ("net_income", "Net income"),
            ("operating_cash_flow", "Operating cash flow"),
            ("capital_spending", "Capital spending"),
            ("research_and_development", "Research and development"),
            ("equity", "Equity"),
            ("liabilities", "Liabilities"),
            ("assets_current", "Current assets"),
            ("liabilities_current", "Current liabilities"),
        ]:
            item = row[key]
            lines.append(f"  {label}: {item['display']} | XBRL tag: {item['tag']}")
        lines.append(f"  ROE: {row['roe']['display']} | Net income / year-end equity")
        lines.append(f"  Current ratio: {row['current_ratio']['display']} | Current assets / current liabilities")
        lines.append(f"  Liabilities / equity: {row['liabilities_to_equity']['display']} | Liabilities / year-end equity")
        lines.append(f"  Owner earnings: {row['owner_earnings']['display']} | Operating cash flow - capital spending")
        lines.append("")
    lines.extend(
        [
            "Buffett business checks:",
            f"  ROE at least 15% every year: {analysis['checks']['roe_at_least_15_percent_every_year']}",
            f"  Owner earnings positive every year: {analysis['checks']['owner_earnings_positive_every_year']}",
            f"  Owner earnings grew from first year to last: {analysis['checks']['owner_earnings_grew_first_to_last']}",
        ]
    )
    return "\n".join(lines)


def write_analysis(analysis: dict, output_dir: Path | str = "output") -> Path:
    destination = Path(output_dir) / f"{analysis['ticker']}_facts.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    return destination


def run(ticker: str, output_dir: Path | str = "output") -> dict:
    analysis = build_analysis(ticker)
    write_analysis(analysis, output_dir)
    return analysis


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    if len(arguments) != 1:
        print("Usage: python buffett_facts.py TICKER", file=sys.stderr)
        return 2
    try:
        analysis = run(arguments[0])
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(analysis["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
