"""Streamlit viewer for the repo-local Buffett owner-earnings skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "buffett-owner-earnings"
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from buffett_facts import normalize_ticker, run  # noqa: E402


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


st.set_page_config(page_title="Buffett Owner Earnings", layout="wide")
st.title("Buffett Owner Earnings")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

ticker_input = st.text_input("Ticker", value="COST", max_chars=12)
if st.button("Load SEC 10-K facts", type="primary"):
    try:
        with st.spinner("Downloading SEC EDGAR Company Facts and applying 10-K rules..."):
            analysis = run(normalize_ticker(ticker_input), PROJECT_ROOT / "output")
        st.session_state["buffett_analysis"] = analysis
    except (RuntimeError, ValueError) as error:
        st.error(str(error))

analysis = st.session_state.get("buffett_analysis")
if analysis:
    st.subheader(f"{analysis['ticker']} — five fiscal years")
    st.line_chart(chart_frame(analysis))
    st.subheader("10-K table and XBRL tags")
    st.dataframe(table_frame(analysis), use_container_width=True, hide_index=True)
    st.subheader("Buffett business checks")
    checks = analysis["checks"]
    st.write(f"ROE at least 15% every year: **{checks['roe_at_least_15_percent_every_year']}**")
    st.write(f"Owner earnings positive every year: **{checks['owner_earnings_positive_every_year']}**")
    st.write(f"Owner earnings grew from first year to last: **{checks['owner_earnings_grew_first_to_last']}**")

    memo_path = PROJECT_ROOT / "memos" / f"{analysis['ticker']}_buffett_memo.md"
    st.subheader("Owner memo")
    if memo_path.exists():
        memo = memo_path.read_text(encoding="utf-8")
        st.markdown(memo.replace("$", r"\$"))
        flagged = unprinted_memo_numbers(memo, analysis)
        if flagged:
            st.warning("Numbers in the memo that do not match a printed script value: " + ", ".join(flagged))
        else:
            st.success("Every numeric memo reference matches a printed script value (allowing for displayed rounding and percent signs).")
    else:
        st.info(f"No memo found yet. Create {memo_path.relative_to(PROJECT_ROOT)} with the skill after reviewing the printed facts.")
