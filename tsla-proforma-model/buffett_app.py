"""Streamlit viewer for the repo-local Buffett owner-earnings skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "buffett-owner-earnings"
GRAHAM_SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "graham-defensive-investor"
BURRY_SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "burry-cash-and-balance-sheet"
for skill_dir in [SKILL_DIR, GRAHAM_SKILL_DIR, BURRY_SKILL_DIR]:
    if str(skill_dir) not in sys.path:
        sys.path.insert(0, str(skill_dir))

from buffett_facts import normalize_ticker, run  # noqa: E402
from burry_cash_balance import run as run_burry  # noqa: E402
from graham_defensive import run as run_graham  # noqa: E402


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])\$?\(?-?\d[\d,]*(?:\.\d+)?\)?\s*(?:%|million|billion|m|bn)?", re.IGNORECASE)


def _numeric_value(text: str) -> float | None:
    cleaned = text.lower().replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    value = float(match.group())
    if "billion" in cleaned or re.search(r"\bbn\b", cleaned):
        return value * 1_000
    return value


def unprinted_memo_numbers(memo: str, analysis: dict) -> list[str]:
    """Return numeric memo tokens that cannot be reconciled to the printed report."""
    report = analysis["report"]
    printed_tokens = NUMBER_PATTERN.findall(report)
    printed_percentages = [_numeric_value(token) for token in printed_tokens if "%" in token]
    printed_money = [_numeric_value(token) for token in printed_tokens if "$" in token or "million" in token.lower()]
    printed_plain = {_numeric_value(token) for token in printed_tokens if "$" not in token and "%" not in token and "million" not in token.lower()}
    flagged = []
    for token in NUMBER_PATTERN.findall(memo):
        value = _numeric_value(token)
        if value is None:
            continue
        if "%" in token:
            valid = any(candidate is not None and abs(value - candidate) <= 0.15 for candidate in printed_percentages)
        elif "$" in token or "million" in token.lower() or re.search(r"\b(m|bn)\b", token.lower()):
            valid = any(candidate is not None and abs(value - candidate) <= 0.15 for candidate in printed_money)
        else:
            valid = value in printed_plain
        if not valid and token.strip() not in flagged:
            flagged.append(token.strip())
    return flagged


def chart_frame(analysis: dict) -> pd.DataFrame:
    rows = []
    for row in analysis["years"]:
        rows.append(
            {
                "Fiscal year end": row["fiscal_year_end"],
                "Owner earnings ($ millions)": None if row["owner_earnings"]["value"] is None else row["owner_earnings"]["value"] / 1_000_000,
                "Net income ($ millions)": None if row["net_income"]["value"] is None else row["net_income"]["value"] / 1_000_000,
            }
        )
    return pd.DataFrame(rows).set_index("Fiscal year end")


def table_frame(analysis: dict) -> pd.DataFrame:
    rows = []
    for row in analysis["years"]:
        for key, label in [
            ("revenue", "Revenue"),
            ("net_income", "Net income"),
            ("operating_cash_flow", "Operating cash flow"),
            ("capital_spending", "Capital spending"),
            ("equity", "Equity"),
        ]:
            rows.append({"Fiscal year end": row["fiscal_year_end"], "Metric": label, "Value ($ millions)": row[key]["display"], "XBRL tag": row[key]["tag"]})
        rows.append({"Fiscal year end": row["fiscal_year_end"], "Metric": "ROE", "Value ($ millions)": row["roe"]["display"], "XBRL tag": "Net income / year-end equity"})
        rows.append({"Fiscal year end": row["fiscal_year_end"], "Metric": "Owner earnings", "Value ($ millions)": row["owner_earnings"]["display"], "XBRL tag": "Operating cash flow - capital spending"})
    return pd.DataFrame(rows)


def metric_change(first: dict, latest: dict, is_percent: bool = False) -> str:
    """Format the latest-minus-first change without changing the displayed facts."""
    if first["value"] is None or latest["value"] is None:
        return "not known"
    if is_percent:
        change = (latest["value"] - first["value"]) * 100
        return f"{change:+.1f} percentage points from first year"
    change = (latest["value"] - first["value"]) / 1_000_000
    return f"${change:+,.1f} million from first year"


def bold_chart(analysis: dict) -> alt.Chart:
    rows = []
    for row in analysis["years"]:
        for series, key in [("Owner earnings", "owner_earnings"), ("Net income", "net_income")]:
            value = row[key]["value"]
            if value is not None:
                rows.append({"Fiscal year end": row["fiscal_year_end"], "Series": series, "Value ($ millions)": value / 1_000_000})
    return (
        alt.Chart(pd.DataFrame(rows))
        .mark_line(strokeWidth=4, point=alt.OverlayMarkDef(filled=True, size=85))
        .encode(
            x=alt.X("Fiscal year end:O", title="Fiscal year end", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Value ($ millions):Q", title="$ millions"),
            color=alt.Color(
                "Series:N",
                title="",
                scale=alt.Scale(domain=["Owner earnings", "Net income"], range=["#0F766E", "#2563EB"]),
                legend=alt.Legend(orient="top"),
            ),
            tooltip=["Fiscal year end:O", "Series:N", alt.Tooltip("Value ($ millions):Q", format=",.1f")],
        )
        .properties(height=390)
        .configure_axis(labelFontSize=13, titleFontSize=15, titleFontWeight="bold")
        .configure_legend(labelFontSize=14, symbolStrokeWidth=4)
    )


def badge(label: str, result: str) -> str:
    colors = {"pass": ("#DCFCE7", "#166534"), "fail": ("#FEE2E2", "#991B1B"), "not known": ("#E5E7EB", "#374151")}
    background, text = colors.get(result, colors["not known"])
    return (
        f"<div style='background:{background};color:{text};border-radius:10px;padding:16px;"
        f"min-height:82px;font-weight:700;font-size:17px;line-height:1.35'>{label}<br>"
        f"<span style='font-size:24px;text-transform:uppercase'>{result}</span></div>"
    )


def memo_banner(memo: str) -> str | None:
    match = re.search(r"\*\*Conclusion:\s*([^*]+)\*\*", memo, re.IGNORECASE)
    if not match:
        return None
    conclusion = match.group(1).strip()
    lowered = conclusion.lower()
    if "own" in lowered:
        background, text = "#DCFCE7", "#166534"
    elif "pass" in lowered:
        background, text = "#FEE2E2", "#991B1B"
    else:
        background, text = "#FEF3C7", "#92400E"
    return (
        f"<div style='background:{background};color:{text};border-radius:12px;padding:20px 24px;"
        f"font-size:28px;font-weight:800;text-transform:uppercase'>Conclusion: {conclusion}</div>"
    )


def check_score(checks: dict[str, str]) -> str:
    return f"{sum(result == 'pass' for result in checks.values())} of {len(checks)}"


def memo_verdict(memo: str) -> str:
    match = re.search(r"\*\*Conclusion:\s*([^*]+)\*\*", memo, re.IGNORECASE)
    return match.group(1).strip() if match else "memo not found"


def panel_checks(buffett: dict, graham: dict, burry: dict) -> pd.DataFrame:
    investors = [
        ("Buffett", buffett["checks"]),
        ("Graham", graham["checks"]),
        ("Burry", burry["checks"]),
    ]
    rows = []
    for investor, checks in investors:
        for check, result in checks.items():
            rows.append({"Investor": investor, "Check": check.replace("_", " "), "Result": result})
    return pd.DataFrame(rows)


st.set_page_config(page_title="Buffett Owner Earnings", layout="wide")
st.markdown(
    """<style>
    [data-testid="stMetric"] {background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px;}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {color: #0F172A !important; font-size: 1.8rem; font-weight: 800;}
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {color: #334155 !important; font-size: 1rem; font-weight: 700;}
    [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * {color: #475569 !important;}
    </style>""",
    unsafe_allow_html=True,
)
analysis = st.session_state.get("buffett_analysis")
if analysis:
    st.title(f"{analysis['company_name']} ({analysis['ticker']})")
else:
    st.title("Buffett Owner Earnings")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

ticker_input = st.text_input("Ticker", value=analysis["ticker"] if analysis else "COST", max_chars=12)
if st.button("Load SEC 10-K facts", type="primary"):
    try:
        with st.spinner("Downloading SEC EDGAR Company Facts and applying 10-K rules..."):
            analysis = run(normalize_ticker(ticker_input), PROJECT_ROOT / "output")
        st.session_state["buffett_analysis"] = analysis
        st.rerun()
    except (RuntimeError, ValueError) as error:
        st.error(str(error))

if analysis:
    st.subheader(f"{analysis['ticker']} — five fiscal years")
    first_year = analysis["years"][0]
    latest_year = analysis["years"][-1]
    st.subheader(f"Latest fiscal year ended {latest_year['fiscal_year_end']}")
    metric_cards = [
        ("Revenue", first_year["revenue"], latest_year["revenue"], False),
        ("Net income", first_year["net_income"], latest_year["net_income"], False),
        ("Owner earnings", first_year["owner_earnings"], latest_year["owner_earnings"], False),
        ("Return on equity", first_year["roe"], latest_year["roe"], True),
    ]
    for column, (label, first, latest, is_percent) in zip(st.columns(4), metric_cards):
        with column:
            st.metric(label, latest["display"], metric_change(first, latest, is_percent))

    st.subheader("Owner earnings and net income")
    st.altair_chart(bold_chart(analysis), use_container_width=True)
    st.subheader("10-K table and XBRL tags")
    st.dataframe(table_frame(analysis), use_container_width=True, hide_index=True)
    st.subheader("Buffett business checks")
    checks = analysis["checks"]
    check_cards = [
        ("Return on equity at least 15% every year", checks["roe_at_least_15_percent_every_year"]),
        ("Owner earnings positive every year", checks["owner_earnings_positive_every_year"]),
        ("Owner earnings grew from first year to last", checks["owner_earnings_grew_first_to_last"]),
    ]
    for column, (label, result) in zip(st.columns(3), check_cards):
        with column:
            st.markdown(badge(label, result), unsafe_allow_html=True)

    try:
        graham = run_graham(analysis["ticker"], PROJECT_ROOT / "output")
        burry = run_burry(analysis["ticker"], PROJECT_ROOT / "output")
    except (OSError, KeyError, ValueError) as error:
        st.error(f"Panel could not read the saved fact record: {error}")
        graham = burry = None

    if graham and burry:
        memo_paths = {
            "Buffett": PROJECT_ROOT / "memos" / f"{analysis['ticker']}_buffett_memo.md",
            "Graham": PROJECT_ROOT / "memos" / f"{analysis['ticker']}_graham_memo.md",
            "Burry": PROJECT_ROOT / "memos" / f"{analysis['ticker']}_burry_memo.md",
        }
        memos = {investor: path.read_text(encoding="utf-8") if path.exists() else "" for investor, path in memo_paths.items()}
        st.subheader("Three-investor panel")
        st.dataframe(panel_checks(analysis, graham, burry), use_container_width=True, hide_index=True)
        verdict_rows = []
        for investor, investor_analysis in [("Buffett", analysis), ("Graham", graham), ("Burry", burry)]:
            verdict_rows.append({"Investor": investor, "Verdict": memo_verdict(memos[investor]), "Score": check_score(investor_analysis["checks"])})
        st.dataframe(pd.DataFrame(verdict_rows), use_container_width=True, hide_index=True)

        st.subheader("Investor memos")
        for column, investor in zip(st.columns(3), ["Buffett", "Graham", "Burry"]):
            with column:
                st.markdown(f"### {investor}")
                memo = memos[investor]
                if memo:
                    banner = memo_banner(memo)
                    if banner:
                        st.markdown(banner, unsafe_allow_html=True)
                    st.markdown(memo.replace("$", r"\$"))
                else:
                    st.info(f"No {investor} memo found yet.")

        combined_analysis = dict(analysis)
        combined_analysis["report"] = "\n".join([analysis["report"], graham["report"], burry["report"]])
        flagged_by_memo = {investor: unprinted_memo_numbers(memo, combined_analysis) for investor, memo in memos.items() if memo}
        flags = [f"{investor}: {', '.join(numbers)}" for investor, numbers in flagged_by_memo.items() if numbers]
        if flags:
            st.error("Unprinted-number flags — " + " | ".join(flags))
        else:
            st.success("No memo contains a number absent from the combined printed Buffett, Graham, and Burry reports.")
