"""A FRED/ALFRED interest-rate viewer with an as-of-data comparison.

Run from this folder: python -m streamlit run asof_app.py
"""
from __future__ import annotations

from datetime import date
from urllib.parse import urlencode

import altair as alt
import pandas as pd
import streamlit as st


SERIES_NAMES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}
DEFAULT_SERIES = list(SERIES_NAMES)
FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_GRAPH_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
PERIOD_FREQUENCIES = {"Month": "M", "Quarter": "Q", "Year": "Y"}


def series_url(series_id: str) -> str:
    """Return the public FRED page for a series."""
    return f"https://fred.stlouisfed.org/series/{series_id}"


def clean_download(frame: pd.DataFrame, series_id: str) -> pd.DataFrame:
    """Standardize FRED's CSV into date/value columns and turn '.' into missing."""
    if frame.shape[1] < 2:
        raise ValueError("The download did not contain a value column.")
    value_column = series_id if series_id in frame.columns else frame.columns[-1]
    cleaned = frame.iloc[:, [0, frame.columns.get_loc(value_column)]].copy()
    cleaned.columns = ["date", "value"]
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"].replace(".", pd.NA), errors="coerce")
    return cleaned.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def download_current(series_id: str) -> pd.DataFrame:
    """Download one series' currently published FRED observations (one request)."""
    url = f"{FRED_GRAPH_URL}?{urlencode({'id': series_id})}"
    return clean_download(pd.read_csv(url), series_id)


@st.cache_data(ttl=3600, show_spinner=False)
def download_as_known(series_id: str, vintage_date: str) -> pd.DataFrame:
    """Download one series as ALFRED showed it on a vintage date (one request)."""
    query = urlencode({"id": series_id, "vintage_date": vintage_date})
    return clean_download(pd.read_csv(f"{ALFRED_GRAPH_URL}?{query}"), series_id)


def last_observation(frame: pd.DataFrame) -> pd.Series | None:
    """Return the most recent non-missing observation, if there is one."""
    usable = frame.dropna(subset=["value"])
    return None if usable.empty else usable.iloc[-1]


def make_candles(current_by_series: dict[str, pd.DataFrame], start_date: date,
                 period_name: str) -> pd.DataFrame:
    """Turn current non-missing values into one open-high-low-close candle per period."""
    frames = []
    for series_id, current in current_by_series.items():
        visible = current[(current["date"] >= pd.Timestamp(start_date)) & current["value"].notna()].copy()
        if visible.empty:
            continue
        visible["series"] = series_id
        visible["period"] = visible["date"].dt.to_period(PERIOD_FREQUENCIES[period_name]).dt.start_time
        frames.append(visible)
    if not frames:
        return pd.DataFrame(columns=["series", "period", "open", "high", "low", "close"])

    observations = pd.concat(frames).sort_values(["series", "period", "date"])
    return observations.groupby(["series", "period"], as_index=False).agg(
        open=("value", "first"),
        high=("value", "max"),
        low=("value", "min"),
        close=("value", "last"),
    )


def combined_line_chart(current_by_series: dict[str, pd.DataFrame], start_date: date) -> alt.Chart | None:
    """Create one current-value line chart with one colored line per series."""
    frames = []
    for series_id, current in current_by_series.items():
        visible = current[(current["date"] >= pd.Timestamp(start_date)) & current["value"].notna()].copy()
        if not visible.empty:
            visible["series"] = series_id
            frames.append(visible)
    if not frames:
        return None
    lines = pd.concat(frames)
    line = alt.Chart(lines).mark_line().encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color("series:N", title="Series"),
        tooltip=[alt.Tooltip("series:N", title="Series"),
                 alt.Tooltip("date:T", title="Date", format="%Y-%m-%d"),
                 alt.Tooltip("value:Q", title="Value", format=".4f")],
    ).properties(height=350)
    return line


def as_of_rule(as_of_date: date) -> alt.Chart:
    """Return a vertical marker for the date used to retrieve the vintage data."""
    return alt.Chart(pd.DataFrame({"as_of_date": [pd.Timestamp(as_of_date)]})).mark_rule(
        color="#666666", strokeDash=[6, 4]
    ).encode(x="as_of_date:T")


def individual_series_chart(current: pd.DataFrame, vintage: pd.DataFrame, start_date: date,
                            as_of_date: date) -> alt.Chart | None:
    """Overlay today's solid values and the selected vintage's dashed values."""
    frames = []
    for label, frame in (("Today", current), ("As known then", vintage)):
        visible = frame[(frame["date"] >= pd.Timestamp(start_date)) & frame["value"].notna()].copy()
        if not visible.empty:
            visible["source"] = label
            frames.append(visible)
    if not frames:
        return None
    lines = pd.concat(frames)
    chart = alt.Chart(lines).mark_line().encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color("source:N", title="Values", scale=alt.Scale(
            domain=["Today", "As known then"], range=["#1f77b4", "#d62728"])),
        strokeDash=alt.StrokeDash("source:N", scale=alt.Scale(
            domain=["Today", "As known then"], range=[[1, 0], [6, 4]])),
        tooltip=[alt.Tooltip("source:N", title="Values"),
                 alt.Tooltip("date:T", title="Date", format="%Y-%m-%d"),
                 alt.Tooltip("value:Q", title="Value", format=".4f")],
    ).properties(height=300)
    return alt.layer(chart, as_of_rule(as_of_date)).interactive()


def monthly_spread(current_by_series: dict[str, pd.DataFrame], left_id: str,
                   right_id: str, start_date: date) -> pd.DataFrame | None:
    """Match two current series by month, averaging all observations within a month."""
    if left_id not in current_by_series or right_id not in current_by_series:
        return None
    monthly = []
    for series_id in (left_id, right_id):
        values = current_by_series[series_id]
        values = values[(values["date"] >= pd.Timestamp(start_date)) & values["value"].notna()].copy()
        if values.empty:
            return None
        values = values.set_index("date")["value"].resample("MS").mean().rename(series_id)
        monthly.append(values)
    matched = pd.concat(monthly, axis=1, join="inner").dropna()
    if matched.empty:
        return None
    return (matched[left_id] - matched[right_id]).rename("spread").reset_index()


def spread_chart(spread: pd.DataFrame, title: str, as_of_date: date) -> alt.Chart:
    """Draw one monthly current-data spread with the selected as-of date marked."""
    chart = alt.Chart(spread).mark_line(color="#1f77b4").encode(
        x=alt.X("date:T", title="Month"),
        y=alt.Y("spread:Q", title="Percentage-point difference"),
        tooltip=[alt.Tooltip("date:T", title="Month", format="%Y-%m-%d"),
                 alt.Tooltip("spread:Q", title="Spread", format=".4f")],
    ).properties(title=title, height=280)
    return alt.layer(chart, as_of_rule(as_of_date)).interactive()


def candlestick_chart(candles: pd.DataFrame) -> alt.Chart:
    """Create one colored, hoverable candlestick chart for all selected series."""
    color = alt.Color("series:N", title="Series")
    x = alt.X("period:T", title="Period")
    offset = alt.XOffset("series:N")
    tooltip = [
        alt.Tooltip("series:N", title="Series"),
        alt.Tooltip("period:T", title="Period", format="%Y-%m-%d"),
        alt.Tooltip("open:Q", title="Open", format=".4f"),
        alt.Tooltip("high:Q", title="High", format=".4f"),
        alt.Tooltip("low:Q", title="Low", format=".4f"),
        alt.Tooltip("close:Q", title="Close", format=".4f"),
    ]
    wicks = alt.Chart(candles).mark_rule().encode(
        x=x, xOffset=offset, y=alt.Y("low:Q", title="Value"), y2="high:Q", color=color, tooltip=tooltip
    )
    bodies = alt.Chart(candles).mark_bar(size=10).encode(
        x=x, xOffset=offset, y="open:Q", y2="close:Q", color=color, tooltip=tooltip
    )
    return alt.layer(wicks, bodies).properties(height=450).interactive()


def make_summary(series_id: str, current: pd.DataFrame, vintage: pd.DataFrame) -> dict[str, object]:
    """Calculate the full-download comparison between vintage and current data."""
    current_last = last_observation(current)
    vintage_last = last_observation(vintage)

    if vintage_last is None:
        new_values = 0
        revised_values = 0
        vintage_date_text = "No value"
        vintage_value = None
    else:
        vintage_end = vintage_last["date"]
        new_values = int(current.loc[current["date"] > vintage_end, "value"].notna().sum())
        shared = current.merge(vintage, on="date", suffixes=("_today", "_then"))
        comparable = shared[(shared["date"] <= vintage_end)
                            & shared["value_today"].notna() & shared["value_then"].notna()]
        revised_values = int((comparable["value_today"] != comparable["value_then"]).sum())
        vintage_date_text = vintage_last["date"].date().isoformat()
        vintage_value = float(vintage_last["value"])

    return {
        "Series": series_id,
        "Last date known then": vintage_date_text,
        "Value known then": vintage_value,
        "Last date today": "No value" if current_last is None else current_last["date"].date().isoformat(),
        "Value today": None if current_last is None else float(current_last["value"]),
        "New values since then": new_values,
        "Revised shared values": revised_values,
    }


def main() -> None:
    st.set_page_config(page_title="FRED as-of interest rates", layout="wide")
    st.title("Interest rates: current data versus data known then")
    st.caption("Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today; "
               "built with AI help, a learning demonstration, not investment advice.")

    with st.sidebar:
        st.header("Data settings")
        selected = st.multiselect(
            "Series",
            options=DEFAULT_SERIES,
            default=DEFAULT_SERIES,
            format_func=lambda item: f"{item} — {SERIES_NAMES[item]}",
        )
        added_id = st.text_input("Add another FRED series ID").strip().upper()
        start_date = st.date_input("Start date", value=date(2020, 1, 1))
        as_of_date = st.date_input("As known on", value=date.today(), max_value=date.today())
        period_name = st.selectbox("Candle period", options=list(PERIOD_FREQUENCIES), index=1)

    series_ids = selected.copy()
    if added_id and added_id not in series_ids:
        series_ids.append(added_id)
    if not series_ids:
        st.info("Choose at least one series ID to display data.")
        return

    summaries: list[dict[str, object]] = []
    current_by_series: dict[str, pd.DataFrame] = {}
    vintage_label = as_of_date.isoformat()
    for series_id in series_ids:
        display_name = SERIES_NAMES.get(series_id, "Additional FRED series")
        try:
            current = download_current(series_id)
            vintage = download_as_known(series_id, vintage_label)
        except Exception as error:  # Keep another series' download from stopping the page.
            st.error(f"{series_id}: Could not download this FRED series ({error}).")
            continue

        current_by_series[series_id] = current
        current_chart = current[(current["date"] >= pd.Timestamp(start_date)) & current["value"].notna()]
        st.subheader(f"{series_id} — {display_name}")
        if current_chart.empty:
            st.warning(f"{series_id}: No current non-missing observations on or after {start_date}.")
        else:
            chart = individual_series_chart(current, vintage, start_date, as_of_date)
            if chart is not None:
                st.altair_chart(chart, width="stretch")
        vintage_last = last_observation(vintage)
        if vintage_last is None:
            st.caption(f"Last date in data known on {vintage_label}: no non-missing value.")
        else:
            st.caption(f"Last date in data known on {vintage_label}: "
                       f"{vintage_last['date'].date().isoformat()} ({vintage_last['value']:g}).")
        summaries.append(make_summary(series_id, current, vintage))

    line_chart = combined_line_chart(current_by_series, start_date)
    st.subheader("Combined current values")
    if line_chart is None:
        st.info("No current non-missing observations are available for the selected start date.")
    else:
        st.altair_chart(alt.layer(line_chart, as_of_rule(as_of_date)).interactive(), width="stretch")

    candles = make_candles(current_by_series, start_date, period_name)
    st.subheader(f"Current values by {period_name.lower()}")
    if candles.empty:
        st.info("No current non-missing observations are available for the selected start date.")
    else:
        st.altair_chart(candlestick_chart(candles), width="stretch")

    st.subheader("Spreads")
    credit_spread = monthly_spread(current_by_series, "BAA", "DGS10", start_date)
    if credit_spread is None:
        st.info("Credit spread needs BAA and DGS10 to be selected and to have current values.")
    else:
        st.altair_chart(spread_chart(credit_spread, "BAA minus DGS10: credit spread", as_of_date), width="stretch")
    rate_spread = monthly_spread(current_by_series, "DGS10", "FEDFUNDS", start_date)
    if rate_spread is None:
        st.info("10-year Treasury minus federal funds rate needs DGS10 and FEDFUNDS to be selected and to have current values.")
    else:
        st.altair_chart(spread_chart(rate_spread, "DGS10 minus FEDFUNDS", as_of_date), width="stretch")

    if summaries:
        st.subheader("As-of comparison")
        table = pd.DataFrame(summaries)
        table["Series"] = table["Series"].map(series_url)
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={"Series": st.column_config.LinkColumn("Series ID", display_text=r".*/([^/]+)$")},
        )
        st.download_button(
            "Download as-of comparison table as CSV",
            data=table.to_csv(index=False).encode("utf-8"),
            file_name="as_of_comparison.csv",
            mime="text/csv",
        )
        st.caption("A revised shared value differs between ALFRED's vintage and today's FRED download.")


if __name__ == "__main__":
    main()
