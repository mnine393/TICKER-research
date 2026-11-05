"""Run three reproducible Graham-style checks from a saved SEC 10-K fact record."""

from __future__ import annotations

import json
import sys
from pathlib import Path


CURRENT_RATIO_MINIMUM = 2.0


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
    current_ratio = latest["current_ratio"]["value"]
    current_ratio_check = "not known" if current_ratio is None else ("pass" if current_ratio >= CURRENT_RATIO_MINIMUM else "fail")
    earnings_positive = _all_check([None if row["net_income"]["value"] is None else row["net_income"]["value"] > 0 for row in years])
    first_income = years[0]["net_income"]["value"]
    last_income = latest["net_income"]["value"]
    income_growth = "not known" if first_income is None or last_income is None else ("pass" if last_income > first_income else "fail")
    checks = {
        "current_ratio_at_least_2_0_latest_year": current_ratio_check,
        "net_income_positive_every_year": earnings_positive,
        "net_income_grew_first_to_last": income_growth,
    }
    return {"ticker": facts["ticker"], "company_name": facts["company_name"], "checks": checks, "score": _score(checks), "latest_year": latest["fiscal_year_end"], "current_ratio": latest["current_ratio"]}


def format_report(analysis: dict) -> str:
    checks = analysis["checks"]
    return "\n".join([
        f"{analysis['ticker']} Graham defensive checks (saved SEC 10-K facts only)",
        f"Latest fiscal year ended {analysis['latest_year']}",
        f"Current-ratio threshold: {CURRENT_RATIO_MINIMUM:.1f}x",
        f"Latest current ratio: {analysis['current_ratio']['display']}",
        "Graham defensive checks:",
        f"  Current ratio at least {CURRENT_RATIO_MINIMUM:.1f}: {checks['current_ratio_at_least_2_0_latest_year']}",
        f"  Net income positive every year: {checks['net_income_positive_every_year']}",
        f"  Net income grew from first year to last: {checks['net_income_grew_first_to_last']}",
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
        print("Usage: python graham_defensive.py TICKER", file=sys.stderr)
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
