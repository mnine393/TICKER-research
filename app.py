"""Streamlit learning demonstration for the Meridian portfolio allocation exercise.

Run from this folder:  python -m streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from portfolio import (
    MERIDIAN_CORRELATION,
    MERIDIAN_OBJECTIVE_RETURN,
    MERIDIAN_RESERVE_ELIGIBLE_SLEEVES,
    MERIDIAN_SLEEVES,
    estimate_from_csv,
    search_long_only_mix,
)


st.set_page_config(page_title="Meridian portfolio learning tool", layout="wide")


def sleeves_from_estimate(estimate):
    return tuple(zip(estimate["names"], estimate["returns"], estimate["volatilities"]))


def result_table(result, names):
    if result is None:
        st.info("No mix meets the objective")
        return
    rows = pd.DataFrame({"Asset": names, "Weight": result["weights"]})
    st.dataframe(rows.style.format({"Weight": "{:.2%}"}), hide_index=True, width="stretch")
    metrics = st.columns(3)
    metrics[0].metric("Expected return", f"{result['expected_return']:.2%}")
    metrics[1].metric("Volatility", f"{result['volatility']:.2%}")
    metrics[2].metric("Reserve-eligible weight", f"{result['reserve_eligible_weight']:.2%}")


def main():
    st.title("Meridian long-only portfolio search")
    st.caption("Built with AI help, a learning demonstration, not investment advice.")

    with st.sidebar:
        st.header("Portfolio settings")
        objective_percent = st.number_input("Expected-return objective (%)", 0.0, 100.0,
                                            MERIDIAN_OBJECTIVE_RETURN * 100, 0.5, format="%.2f")
        reserve_minimum_percent = st.number_input("Minimum reserve-eligible weight (%)", 0.0, 100.0,
                                                  3.0, 0.5, format="%.2f")
        upload = st.file_uploader("Monthly prices CSV", type="csv",
                                  help="Date first, oldest first, then one positive-price column per ticker.")
        last_36 = st.toggle("Use only the last 36 months", value=False)

    loaded_sleeves = MERIDIAN_SLEEVES
    loaded_correlation = MERIDIAN_CORRELATION
    loaded_label = "Meridian inputs"
    if upload is not None:
        try:
            full_estimate = estimate_from_csv(upload, last_36_months=False)
            upload.seek(0)
            active_estimate = estimate_from_csv(upload, last_36_months=last_36)
        except (ValueError, pd.errors.ParserError) as error:
            st.error(f"Could not use this CSV: {error}")
            return
        loaded_sleeves = sleeves_from_estimate(full_estimate)
        loaded_correlation = full_estimate["correlation"]
        active_sleeves = sleeves_from_estimate(active_estimate)
        active_correlation = active_estimate["correlation"]
        loaded_label = "CSV inputs, all monthly returns"
        st.caption(f"CSV source: {len(full_estimate['monthly_returns'])} monthly returns; "
                   f"current search: {len(active_estimate['monthly_returns'])} monthly returns.")
    else:
        active_sleeves = MERIDIAN_SLEEVES
        active_correlation = MERIDIAN_CORRELATION

    st.subheader("Expected-return inputs")
    edited_returns = []
    for column, sleeve in zip(st.columns(len(active_sleeves)), active_sleeves):
        with column:
            edited_returns.append(st.number_input(f"{sleeve[0]} expected return (%)", -100.0, 100.0,
                                                  float(sleeve[1]) * 100, 0.5,
                                                  format="%.2f", key=f"return_{sleeve[0]}_{'last36' if last_36 else 'all'}"))
    active_sleeves = tuple((name, edited_return / 100, volatility)
                           for (name, _, volatility), edited_return in zip(active_sleeves, edited_returns))

    st.subheader("Reserve eligibility")
    eligible = []
    for column, sleeve in zip(st.columns(len(active_sleeves)), active_sleeves):
        with column:
            if st.checkbox(sleeve[0], value=sleeve[0] in MERIDIAN_RESERVE_ELIGIBLE_SLEEVES,
                           key=f"eligible_{sleeve[0]}"):
                eligible.append(sleeve[0])

    objective = objective_percent / 100
    reserve_minimum = reserve_minimum_percent / 100
    current = search_long_only_mix(active_sleeves, active_correlation, objective, tuple(eligible), reserve_minimum)
    loaded = search_long_only_mix(loaded_sleeves, loaded_correlation, objective, tuple(eligible), reserve_minimum)

    current_column, loaded_column = st.columns(2)
    with current_column:
        st.subheader("Lowest-risk mix")
        result_table(current, [sleeve[0] for sleeve in active_sleeves])
    with loaded_column:
        st.subheader(f"As loaded: {loaded_label}")
        result_table(loaded, [sleeve[0] for sleeve in loaded_sleeves])
        if current is not None and loaded is not None:
            changes = [abs(new - old) for new, old in zip(current["weights"], loaded["weights"])]
            largest = max(changes)
            asset = loaded_sleeves[changes.index(largest)][0]
            st.metric("Largest weight change", f"{largest * 100:.2f} points", help=f"{asset}")
        else:
            st.metric("Largest weight change", "n/a")


if __name__ == "__main__":
    main()
