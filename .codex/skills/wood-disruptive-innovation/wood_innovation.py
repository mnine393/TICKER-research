"""Run reproducible revenue-growth and innovation-spending checks from saved SEC 10-K facts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REVENUE_COMPOUND_ANNUAL_GROWTH_MINIMUM = 0.15
RESEARCH_AND_DEVELOPMENT_AS_REVENUE_MINIMUM = 0.10


def _all_check(values: list[bool | None]) -> str:
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(values) else "fail"


def _score(checks: dict[str, str]) -> str:
    return f"{sum(result == 'pass' for result in checks.values())} of {len(checks)}"


def _percent_record(value: float | None) -> dict:
    return {"value": value, "display": "not known" if value is None else f"{value:.1%}"}


def build_analysis(facts: dict) -> dict:
    years = facts["years"]
    first = years[0]
    latest = years[-1]
    revenues = [row["revenue"]["value"] for row in years]
    first_revenue = revenues[0]
    last_revenue = revenues[-1]
    if first_revenue is None or last_revenue is None or first_revenue <= 0 or len(years) < 2:
        revenue_growth_rate = None
    else:
        revenue_growth_rate = (last_revenue / first_revenue) ** (1 / (len(years) - 1)) - 1
    revenue_grew_every_year = _all_check([
        None if prior is None or current is None else current > prior
        for prior, current in zip(revenues, revenues[1:])
    ])
    latest_research = latest["research_and_development"]["value"]
    if latest_research is None or last_revenue is None or last_revenue == 0:
        research_as_revenue = None
    else:
        research_as_revenue = latest_research / last_revenue
    checks = {
        "revenue_compound_annual_growth_at_least_15_percent": "not known" if revenue_growth_rate is None else ("pass" if revenue_growth_rate >= REVENUE_COMPOUND_ANNUAL_GROWTH_MINIMUM else "fail"),
        "revenue_grew_every_year": revenue_grew_every_year,
        "research_and_development_at_least_10_percent_of_revenue_latest_year": "not known" if research_as_revenue is None else ("pass" if research_as_revenue >= RESEARCH_AND_DEVELOPMENT_AS_REVENUE_MINIMUM else "fail"),
    }
    return {
        "ticker": facts["ticker"],
        "company_name": facts["company_name"],
        "latest_year": latest["fiscal_year_end"],
        "revenue_compound_annual_growth": _percent_record(revenue_growth_rate),
        "research_and_development_as_revenue": _percent_record(research_as_revenue),
        "checks": checks,
        "score": _score(checks),
    }


def format_report(analysis: dict) -> str:
    checks = analysis["checks"]
    return "\n".join([
        f"{analysis['ticker']} Wood disruptive-innovation checks (saved SEC 10-K facts only)",
        f"Latest fiscal year ended {analysis['latest_year']}",
        f"Revenue compound annual growth minimum: {REVENUE_COMPOUND_ANNUAL_GROWTH_MINIMUM:.1%}",
        f"Revenue compound annual growth, first year to last: {analysis['revenue_compound_annual_growth']['display']}",
        f"Research-and-development-as-revenue minimum: {RESEARCH_AND_DEVELOPMENT_AS_REVENUE_MINIMUM:.1%}",
        f"Latest research and development as a share of revenue: {analysis['research_and_development_as_revenue']['display']}",
        "Wood disruptive-innovation checks:",
        f"  Revenue compound annual growth at least {REVENUE_COMPOUND_ANNUAL_GROWTH_MINIMUM:.1%}: {checks['revenue_compound_annual_growth_at_least_15_percent']}",
        f"  Revenue grew every year: {checks['revenue_grew_every_year']}",
        f"  Research and development at least {RESEARCH_AND_DEVELOPMENT_AS_REVENUE_MINIMUM:.1%} of revenue: {checks['research_and_development_at_least_10_percent_of_revenue_latest_year']}",
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
        print("Usage: python wood_innovation.py TICKER", file=sys.stderr)
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
