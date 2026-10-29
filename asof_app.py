"""A FRED/ALFRED interest-rate viewer with an as-of-data comparison.

Run from this folder: python -m streamlit run asof_app.py
"""
from __future__ import annotations

from datetime import date
from urllib.parse import urlencode

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

    series_ids = selected.copy()
    if added_id and added_id not in series_ids:
        series_ids.append(added_id)
    if not series_ids:
        st.info("Choose at least one series ID to display data.")
        return

    summaries: list[dict[str, object]] = []
    vintage_label = as_of_date.isoformat()
    for series_id in series_ids:
        display_name = SERIES_NAMES.get(series_id, "Additional FRED series")
        try:
            current = download_current(series_id)
            vintage = download_as_known(series_id, vintage_label)
        except Exception as error:  # Keep another series' download from stopping the page.
            st.error(f"{series_id}: Could not download this FRED series ({error}).")
            continue

        current_chart = current[(current["date"] >= pd.Timestamp(start_date)) & current["value"].notna()]
        st.subheader(f"{series_id} — {display_name}")
        if current_chart.empty:
            st.warning(f"{series_id}: No current non-missing observations on or after {start_date}.")
        else:
            st.line_chart(current_chart.set_index("date")["value"], height=300)
        vintage_last = last_observation(vintage)
        if vintage_last is None:
            st.caption(f"Last date in data known on {vintage_label}: no non-missing value.")
        else:
            st.caption(f"Last date in data known on {vintage_label}: "
                       f"{vintage_last['date'].date().isoformat()} ({vintage_last['value']:g}).")
        summaries.append(make_summary(series_id, current, vintage))

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
        st.caption("A revised shared value differs between ALFRED's vintage and today's FRED download.")


if __name__ == "__main__":
    main()
