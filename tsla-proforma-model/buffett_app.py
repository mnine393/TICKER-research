"""Streamlit viewer for the repo-local investor panel skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "buffett-owner-earnings"
WOOD_SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "wood-disruptive-innovation"
BURRY_SKILL_DIR = PROJECT_ROOT / ".codex" / "skills" / "burry-cash-and-balance-sheet"
for skill_dir in [SKILL_DIR, WOOD_SKILL_DIR, BURRY_SKILL_DIR]:
    if str(skill_dir) not in sys.path:
        sys.path.insert(0, str(skill_dir))

from buffett_facts import normalize_ticker, run  # noqa: E402
from burry_cash_balance import run as run_burry  # noqa: E402
from wood_innovation import run as run_wood  # noqa: E402


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])\$?\(?-?\d[\d,]*(?:\.\d+)?\)?\s*(?:%|million|billion|m|bn)?", re.IGNORECASE)
PANEL_NAMES = ["Buffett", "Wood", "Burry"]


def _numeric_value(text: str) -> float | None:
    cleaned = text.lower().replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    value = float(match.group())
    return value * 1_000 if "billion" in cleaned or re.search(r"\bbn\b", cleaned) else value


def unprinted_memo_numbers(memo: str, analysis: dict) -> list[str]:
    """Return numeric memo tokens that cannot be reconciled to the printed report."""
    printed_tokens = NUMBER_PATTERN.findall(analysis["report"])
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


def _item(row: dict, key: str) -> dict:
    return row.get(key, {"value": None, "tag": "not found", "display": "not found"})


def table_frame(analysis: dict) -> pd.DataFrame:
    rows = []
    metrics = [
        ("revenue", "Revenue"), ("net_income", "Net income"), ("operating_cash_flow", "Operating cash flow"),
        ("capital_spending", "Capital spending"), ("research_and_development", "Research and development"),
        ("equity", "Equity"), ("liabilities", "Liabilities"), ("assets_current", "Current assets"),
        ("liabilities_current", "Current liabilities"),
    ]
    for row in analysis["years"]:
        for key, label in metrics:
            item = _item(row, key)
            rows.append({"Fiscal year end": row["fiscal_year_end"], "Metric": label, "Value": item["display"], "XBRL tag": item["tag"]})
        rows.extend([
            {"Fiscal year end": row["fiscal_year_end"], "Metric": "Return on equity", "Value": _item(row, "roe")["display"], "XBRL tag": "Net income / year-end equity"},
            {"Fiscal year end": row["fiscal_year_end"], "Metric": "Current ratio", "Value": _item(row, "current_ratio")["display"], "XBRL tag": "Current assets / current liabilities"},
            {"Fiscal year end": row["fiscal_year_end"], "Metric": "Liabilities / equity", "Value": _item(row, "liabilities_to_equity")["display"], "XBRL tag": "Liabilities / year-end equity"},
            {"Fiscal year end": row["fiscal_year_end"], "Metric": "Owner earnings", "Value": _item(row, "owner_earnings")["display"], "XBRL tag": "Operating cash flow - capital spending"},
        ])
    return pd.DataFrame(rows)


def metric_change(first: dict, latest: dict, is_percent: bool = False) -> str:
    if first["value"] is None or latest["value"] is None:
        return "not known"
    if is_percent:
        return f"{(latest['value'] - first['value']) * 100:+.1f} percentage points from first year"
    return "$" + f"{(latest['value'] - first['value']) / 1_000_000:+,.1f} million from first year"


def earnings_chart(analysis: dict) -> alt.Chart:
    rows = []
    for row in analysis["years"]:
        for series, key in [("Owner earnings", "owner_earnings"), ("Net income", "net_income")]:
            value = _item(row, key)["value"]
            if value is not None:
                rows.append({"Fiscal year end": row["fiscal_year_end"], "Series": series, "Value ($ millions)": value / 1_000_000})
    return (
        alt.Chart(pd.DataFrame(rows)).mark_line(strokeWidth=4, point=alt.OverlayMarkDef(filled=True, size=90))
        .encode(
            x=alt.X("Fiscal year end:O", title="Fiscal year end", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Value ($ millions):Q", title="$ millions"),
            color=alt.Color("Series:N", title="", scale=alt.Scale(domain=["Owner earnings", "Net income"], range=["#38BDF8", "#A78BFA"])),
            tooltip=["Fiscal year end:O", "Series:N", alt.Tooltip("Value ($ millions):Q", format=",.1f")],
        ).properties(height=360)
    )


def roe_chart(analysis: dict) -> alt.Chart:
    rows = [{"Fiscal year end": row["fiscal_year_end"], "Return on equity (%)": _item(row, "roe")["value"] * 100} for row in analysis["years"] if _item(row, "roe")["value"] is not None]
    base = alt.Chart(pd.DataFrame(rows)).encode(x=alt.X("Fiscal year end:O", title="Fiscal year end", axis=alt.Axis(labelAngle=0)))
    line = base.mark_line(strokeWidth=4, point=alt.OverlayMarkDef(filled=True, size=90), color="#F59E0B").encode(
        y=alt.Y("Return on equity (%):Q", title="Return on equity (%)"),
        tooltip=["Fiscal year end:O", alt.Tooltip("Return on equity (%):Q", format=".1f")],
    )
    threshold = alt.Chart(pd.DataFrame({"Return on equity (%)": [15]})).mark_rule(color="#94A3B8", strokeDash=[7, 5], strokeWidth=2).encode(y="Return on equity (%):Q")
    return (line + threshold).properties(height=360)


def _status_style(result: str) -> str:
    colors = {"pass": ("#14532D", "#DCFCE7"), "fail": ("#7F1D1D", "#FEE2E2"), "not known": ("#374151", "#E5E7EB")}
    background, text = colors.get(result, colors["not known"])
    return f"background-color: {background}; color: {text}; font-weight: 700; white-space: pre-line;"


def memo_banner(memo: str, checks: dict[str, str]) -> str | None:
    match = re.search(r"\*\*Conclusion:\s*([^*]+)\*\*", memo, re.IGNORECASE)
    if not match:
        return None
    if "fail" in checks.values():
        background, text = "#7F1D1D", "#FEE2E2"
    elif "not known" in checks.values():
        background, text = "#713F12", "#FEF3C7"
    else:
        background, text = "#14532D", "#DCFCE7"
    return f"<div class='memo-banner' style='background:{background};color:{text}'>Conclusion: {match.group(1).strip()}</div>"


def check_score(checks: dict[str, str]) -> str:
    return f"{sum(result == 'pass' for result in checks.values())} of {len(checks)}"


def memo_verdict(memo: str) -> str:
    match = re.search(r"\*\*Conclusion:\s*([^*]+)\*\*", memo, re.IGNORECASE)
    return match.group(1).strip() if match else "memo not found"


def panel_grid(analyses: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for investor, investor_analysis in analyses.items():
        checks = list(investor_analysis["checks"].items())
        row = {"Investor": investor}
        for index in range(3):
            if index < len(checks):
                label, result = checks[index]
                row[f"Check {index + 1}"] = f"{label.replace('_', ' ').title()}\n{result.upper()}"
            else:
                row[f"Check {index + 1}"] = "—"
        rows.append(row)
    return pd.DataFrame(rows)


def style_panel_grid(frame: pd.DataFrame) -> pd.io.formats.style.Styler:
    def cell_style(value: object) -> str:
        lowered = str(value).lower()
        if lowered.endswith("pass"):
            return _status_style("pass")
        if lowered.endswith("fail"):
            return _status_style("fail")
        if lowered.endswith("not known"):
            return _status_style("not known")
        return "color: #94A3B8;"
    return frame.style.map(cell_style, subset=["Check 1", "Check 2", "Check 3"])


def style_fact_table(frame: pd.DataFrame) -> pd.io.formats.style.Styler:
    def gap_style(value: object) -> str:
        return "background-color: #374151; color: #D1D5DB; font-weight: 700;" if str(value) == "not found" else ""
    return frame.style.map(gap_style, subset=["Value", "XBRL tag"])


def select_ticker(ticker: str) -> None:
    st.session_state["panel_ticker"] = ticker
    st.session_state["load_requested"] = True


st.set_page_config(page_title="Investor Panel", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px;}
    [data-testid="stSidebar"] {border-right: 1px solid #263244;}
    [data-testid="stMetric"] {background: #172033; border: 1px solid #334155; border-radius: 14px; padding: 18px;}
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {color: #CBD5E1 !important; font-weight: 700;}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {color: #F8FAFC !important; font-weight: 800;}
    .hero {background: linear-gradient(120deg, #0B1220 0%, #172554 55%, #0F766E 130%); border: 1px solid #334155; border-radius: 20px; padding: 30px 34px; margin-bottom: 10px;}
    .hero h1 {margin: 0; color: #F8FAFC; font-size: 2.7rem; letter-spacing: -0.04em;}
    .hero p {margin: 8px 0 0; color: #CBD5E1; font-size: 1.05rem;}
    .memo-banner {border-radius: 12px; padding: 14px 16px; font-size: 1.05rem; font-weight: 800; text-transform: uppercase; margin-bottom: 14px;}
    [data-testid="stTabs"] [data-baseweb="tab-list"] {gap: 10px;}
    [data-testid="stTabs"] button {border-radius: 9px 9px 0 0; font-weight: 700;}
    </style>""",
    unsafe_allow_html=True,
)

analysis = st.session_state.get("buffett_analysis")
with st.sidebar:
    st.title("Investor panel")
    st.caption("Five years of 10-K facts")
    st.text_input("Ticker", value=analysis["ticker"] if analysis else "COST", max_chars=12, key="panel_ticker")
    quick_columns = st.columns(3)
    for column, ticker in zip(quick_columns, ["COST", "NVDA", "JPM"]):
        column.button(ticker, on_click=select_ticker, args=(ticker,), use_container_width=True)
    load_clicked = st.button("Load SEC 10-K facts", type="primary", use_container_width=True)
    st.caption("Quick buttons use the same SEC-only workflow.")

load_requested = load_clicked or st.session_state.pop("load_requested", False)
if load_requested:
    try:
        with st.spinner("Downloading SEC EDGAR Company Facts and applying 10-K rules..."):
            analysis = run(normalize_ticker(st.session_state["panel_ticker"]), PROJECT_ROOT / "output")
        st.session_state["buffett_analysis"] = analysis
        st.rerun()
    except (RuntimeError, ValueError) as error:
        st.error(str(error))

if not analysis:
    st.markdown("""<div class='hero'><h1>Investor panel</h1><p>Load a ticker from the sidebar to compare three rule-based views of the same five-year 10-K record.</p></div>""", unsafe_allow_html=True)
    st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")
    st.stop()

first_year = analysis["years"][0]
latest_year = analysis["years"][-1]
st.markdown(
    f"""<div class='hero'><h1>{analysis['company_name']} <span style='color:#67E8F9'>({analysis['ticker']})</span></h1>
    <p>CIK {analysis['cik']} &nbsp;•&nbsp; Latest fiscal year ended {latest_year['fiscal_year_end']}</p></div>""",
    unsafe_allow_html=True,
)
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

try:
    wood = run_wood(analysis["ticker"], PROJECT_ROOT / "output")
    burry = run_burry(analysis["ticker"], PROJECT_ROOT / "output")
except (OSError, KeyError, ValueError) as error:
    st.error(f"Panel could not read the saved fact record: {error}")
    wood = burry = None

overview_tab, panel_tab, memos_tab, data_tab = st.tabs(["Overview", "Investor panel", "Memos", "10-K data"])

with overview_tab:
    metric_cards = [
        ("Revenue", _item(first_year, "revenue"), _item(latest_year, "revenue"), False),
        ("Net income", _item(first_year, "net_income"), _item(latest_year, "net_income"), False),
        ("Owner earnings", _item(first_year, "owner_earnings"), _item(latest_year, "owner_earnings"), False),
        ("Return on equity", _item(first_year, "roe"), _item(latest_year, "roe"), True),
    ]
    for column, (label, first, latest, is_percent) in zip(st.columns(4), metric_cards):
        with column:
            st.metric(label, latest["display"], metric_change(first, latest, is_percent))
    st.markdown("#### Earnings record")
    st.altair_chart(earnings_chart(analysis), use_container_width=True)
    st.markdown("#### Return on equity")
    st.caption("The dashed line is Buffett's 15% threshold.")
    st.altair_chart(roe_chart(analysis), use_container_width=True)

with panel_tab:
    if wood and burry:
        analyses = {"Buffett": analysis, "Wood": wood, "Burry": burry}
        st.markdown("#### Check grid")
        st.dataframe(style_panel_grid(panel_grid(analyses)), use_container_width=True, hide_index=True, height=240)
        st.markdown("#### Verdicts and scores")
        memo_paths = {investor: PROJECT_ROOT / "memos" / f"{analysis['ticker']}_{investor.lower() if investor != 'Buffett' else 'buffett'}_memo.md" for investor in PANEL_NAMES}
        memos = {investor: path.read_text(encoding="utf-8") if path.exists() else "" for investor, path in memo_paths.items()}
        for column, investor in zip(st.columns(3), PANEL_NAMES):
            with column:
                checks = analyses[investor]["checks"]
                passed, total = sum(result == "pass" for result in checks.values()), len(checks)
                st.markdown(f"### {investor}")
                st.caption(memo_verdict(memos[investor]))
                st.progress(passed / total if total else 0, text=f"{passed} of {total} checks pass")
    else:
        st.info("Load a fact record with the panel inputs to view the investor comparison.")

with memos_tab:
    if wood and burry:
        analyses = {"Buffett": analysis, "Wood": wood, "Burry": burry}
        memo_paths = {investor: PROJECT_ROOT / "memos" / f"{analysis['ticker']}_{investor.lower() if investor != 'Buffett' else 'buffett'}_memo.md" for investor in PANEL_NAMES}
        memos = {investor: path.read_text(encoding="utf-8") if path.exists() else "" for investor, path in memo_paths.items()}
        combined_analysis = dict(analysis)
        combined_analysis["report"] = "\n".join([analysis["report"], wood["report"], burry["report"]])
        flagged_by_memo = {investor: unprinted_memo_numbers(memo, combined_analysis) for investor, memo in memos.items() if memo}
        flags = [f"{investor}: {', '.join(numbers)}" for investor, numbers in flagged_by_memo.items() if numbers]
        if flags:
            st.error("Unprinted-number flags — " + " | ".join(flags))
        else:
            st.success("No memo contains a number absent from the combined printed Buffett, Wood, and Burry reports.")
        for column, investor in zip(st.columns(3), PANEL_NAMES):
            with column:
                with st.container(border=True):
                    st.markdown(f"### {investor}")
                    memo = memos[investor]
                    if memo:
                        banner = memo_banner(memo, analyses[investor]["checks"])
                        if banner:
                            st.markdown(banner, unsafe_allow_html=True)
                        st.markdown(memo.replace("$", r"\$"))
                    else:
                        st.info(f"No {investor} memo found yet.")
    else:
        st.info("Load a fact record with the panel inputs to view the investor memos.")

with data_tab:
    st.markdown("#### Five-year 10-K facts and tags")
    st.caption("Gray cells marked not found are disclosure gaps, not estimates.")
    st.dataframe(style_fact_table(table_frame(analysis)), use_container_width=True, hide_index=True, height=720)
