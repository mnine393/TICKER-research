"""Run cash-conversion and balance-sheet checks from a saved SEC 10-K fact record."""

from __future__ import annotations

import json
import sys
from pathlib import Path


LIABILITIES_TO_EQUITY_MAXIMUM = 2.0


def _all_check(values: list[bool | None]) -> str:
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(values) else "fail"


def _score(checks: dict[str, str]) -> str:
    known = [result for result in checks.values() if result != "not known"]
    return f"{sum(result == 'pass' for result in known)} of {len(checks)}"


def build_analysis(facts: dict) -> dict:
    years = facts["years"]
    latest = years[-1]
    cash_covers_income = _all_check([
        None if row["operating_cash_flow"]["value"] is None or row["net_income"]["value"] is None else row["operating_cash_flow"]["value"] >= row["net_income"]["value"]
        for row in years
    ])
    liabilities_to_equity = latest["liabilities_to_equity"]["value"]
    leverage_check = "not known" if liabilities_to_equity is None else ("pass" if liabilities_to_equity <= LIABILITIES_TO_EQUITY_MAXIMUM else "fail")
    checks = {
        "operating_cash_flow_at_least_net_income_every_year": cash_covers_income,
        "liabilities_no_more_than_twice_equity_latest_year": leverage_check,
    }
    return {"ticker": facts["ticker"], "company_name": facts["company_name"], "checks": checks, "score": _score(checks), "latest_year": latest["fiscal_year_end"], "liabilities_to_equity": latest["liabilities_to_equity"]}


def format_report(analysis: dict) -> str:
    checks = analysis["checks"]
    return "\n".join([
        f"{analysis['ticker']} Burry cash-and-balance-sheet checks (saved SEC 10-K facts only)",
        f"Latest fiscal year ended {analysis['latest_year']}",
        f"Liabilities-to-equity maximum: {LIABILITIES_TO_EQUITY_MAXIMUM:.1f}x",
        f"Latest liabilities / equity: {analysis['liabilities_to_equity']['display']}",
        "Burry cash-and-balance-sheet checks:",
        f"  Operating cash flow at least net income every year: {checks['operating_cash_flow_at_least_net_income_every_year']}",
        f"  Liabilities no more than twice equity: {checks['liabilities_no_more_than_twice_equity_latest_year']}",
        f"Score: {analysis['score']}",
    ])


def run(ticker: str, output_dir: Path | str = "output") -> dict:
    facts_path = Path(output_dir) / f"{ticker.upper()}_facts.json"
    facts = json.loads(facts_path.read_text(encoding="utf-8"))
    analysis = build_analysis(facts)
    analysis["report"] = format_report(analysis)
    return analysis


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    if len(arguments) != 1:
        print("Usage: python burry_cash_balance.py TICKER", file=sys.stderr)
        return 2
    try:
        analysis = run(arguments[0])
    except (OSError, KeyError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(analysis["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
