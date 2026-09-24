"""Plotly figures. Every chart is built directly from model / scenario outputs - no typed-in numbers."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import config

PALETTE = {
    "auto": "#3B6FB6", "credits": "#8FB3E0", "leasing": "#6C8EBF", "services": "#2E9E83",
    "autonomy": "#9B59B6", "energy": "#E0A030", "neg": "#C0504D", "pos": "#2E9E83",
    "market": "#17BECF", "base": "#3B6FB6", "bull": "#2E9E83", "bear": "#E0A030", "recession": "#C0504D",
    "grid": "rgba(128,128,128,0.2)",
}
LAYOUT = dict(template="plotly_white", margin=dict(l=40, r=20, t=60, b=40), font=dict(size=12),
              legend=dict(orientation="h", yanchor="top", y=-0.12, x=0))


def revenue_mix(income: pd.DataFrame) -> go.Figure:
    rows = [("Automotive sales", "auto"), ("Regulatory credits", "credits"), ("Automotive leasing", "leasing"),
            ("Services & other", "services"), ("Robotaxi / autonomy (isolated)", "autonomy"),
            ("Energy generation & storage", "energy")]
    fig = go.Figure()
    for label, key in rows:
        fig.add_bar(x=income.columns, y=income.loc[label] / 1000, name=label, marker_color=PALETTE[key])
    fig.update_layout(barmode="stack", title="Revenue by segment ($B) - reported vs. forecast", yaxis_title="$B", **LAYOUT)
    return fig


def margins(income: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=income.columns, y=income.loc["Memo: GAAP gross margin"], name="GAAP gross margin", mode="lines+markers")
    fig.add_scatter(x=income.columns, y=income.loc["Memo: EBITDA margin"], name="EBITDA margin", mode="lines+markers")
    fig.add_scatter(x=income.columns, y=income.loc["EBIT"] / income.loc["Total revenue"], name="EBIT margin", mode="lines+markers")
    fig.update_layout(title="Margins", yaxis_tickformat=".0%", **LAYOUT)
    return fig


def fcfe_bars(fcfe: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    y = fcfe.loc["Operating FCFE (valued)"] / 1000
    fig.add_bar(x=fcfe.columns, y=y, name="Operating FCFE", marker_color=[PALETTE["pos"] if v >= 0 else PALETTE["neg"] for v in y])
    fig.add_scatter(x=fcfe.columns, y=fcfe.loc["FCFE"] / 1000, name="FCFE incl. interest income", mode="lines+markers")
    fig.update_layout(title="Free cash flow to equity ($B)", yaxis_title="$B", **LAYOUT)
    return fig


def cash_vs_minimum(balance: pd.DataFrame, cashflow: pd.DataFrame) -> go.Figure:
    cols = [c for c in balance.columns if c.endswith("E")]
    fig = go.Figure()
    fig.add_bar(x=balance.columns, y=balance.loc["Cash & short-term investments"] / 1000, name="Cash & ST investments", marker_color=PALETTE["auto"])
    fig.add_scatter(x=cols, y=cashflow.loc["Memo: minimum cash requirement", cols] / 1000, name="Minimum cash rule", mode="lines+markers",
                    line=dict(color=PALETTE["neg"], dash="dash"))
    fig.update_layout(title="Liquidity vs. minimum-cash rule ($B)", yaxis_title="$B", **LAYOUT)
    return fig


def equity_value_waterfall(val) -> go.Figure:
    labels = ["PV of FCFE (H2-26 to 2030)", "PV of terminal value", "Non-operating assets", "Equity value"]
    vals = [val.pv_fcfe / 1000, val.pv_terminal / 1000, val.non_operating / 1000, val.equity_value / 1000]
    fig = go.Figure(go.Waterfall(x=labels, y=vals, measure=["relative", "relative", "relative", "total"],
                                 text=[f"{v:,.1f}" for v in vals], textposition="outside",
                                 increasing=dict(marker_color=PALETTE["pos"]), decreasing=dict(marker_color=PALETTE["neg"]),
                                 totals=dict(marker_color=PALETTE["base"])))
    fig.update_layout(title="Equity value build ($B)", yaxis_title="$B", showlegend=False, **{k: v for k, v in LAYOUT.items() if k != "legend"})
    return fig


def heatmap(df: pd.DataFrame, title: str, price: float | None = None, x_title: str = "", y_title: str = "") -> go.Figure:
    z = df.to_numpy(dtype=float)
    text = [[("n/a" if np.isnan(v) else f"${v:,.0f}") for v in row] for row in z]
    fig = go.Figure(go.Heatmap(z=z, x=list(df.columns), y=list(df.index), text=text, texttemplate="%{text}",
                               colorscale="RdYlGn", colorbar=dict(title="$/share"), hoverongaps=False))
    sub = f" (market price ${price:,.0f})" if price else ""
    fig.update_layout(title=title + sub, xaxis_title=x_title, yaxis_title=y_title, **{k: v for k, v in LAYOUT.items() if k != "legend"})
    fig.update_yaxes(autorange="reversed")
    return fig


def tornado_chart(tor: pd.DataFrame, base_value: float) -> go.Figure:
    t = tor.iloc[::-1]
    fig = go.Figure()
    fig.add_bar(y=t["Driver"] + " (" + t["Shock"] + ")", x=t["Low delta"], orientation="h", name="Adverse / low shock",
                marker_color=PALETTE["neg"], base=base_value)
    fig.add_bar(y=t["Driver"] + " (" + t["Shock"] + ")", x=t["High delta"], orientation="h", name="Favourable / high shock",
                marker_color=PALETTE["pos"], base=base_value)
    fig.add_vline(x=base_value, line_color=PALETTE["market"], line_dash="dot")
    fig.update_layout(barmode="overlay", title=f"Tornado: value per share vs. base ${base_value:,.1f} (full model re-run per bar)",
                      xaxis_title="Implied value per share ($)", height=max(420, 32 * len(t)), **LAYOUT)
    fig.update_layout(margin=dict(l=40, r=20, t=60, b=110), legend=dict(y=-0.1))
    return fig


def one_variable_lines(ov: pd.DataFrame) -> go.Figure:
    steps = [c for c in ov.columns if c.startswith("step")]
    fig = go.Figure()
    for _, r in ov.iterrows():
        fig.add_scatter(x=[int(s.split()[1]) for s in steps], y=[r[s] for s in steps], name=r["Driver"], mode="lines+markers")
    fig.update_layout(title="One-variable sensitivities (x-axis = number of standard shocks)", xaxis_title="Shock steps",
                      yaxis_title="Value per share ($)", height=520, **LAYOUT)
    return fig


def value_bridge_chart(bridge: pd.DataFrame, price: float) -> go.Figure:
    colors = []
    for c, t in zip(bridge["Case"], bridge["Type"]):
        if t == "market":
            colors.append(PALETTE["market"])
        elif t == "discount rate":
            colors.append("#7F7F7F")
        else:
            key = c.split()[0].lower().rstrip("/")
            colors.append(PALETTE.get(key, PALETTE["base"]))
    y = bridge["Value per share ($)"]
    fig = go.Figure(go.Bar(x=bridge["Case"], y=y, marker_color=colors,
                           text=[f"${v:,.0f}" if not np.isnan(v) else "fail" for v in y], textposition="outside"))
    fig.add_hline(y=price, line_dash="dash", line_color=PALETTE["market"], annotation_text=f"Market ${price:,.2f}")
    fig.update_layout(title="Market price vs. implied value per share (scenarios and discount-rate cases)",
                      yaxis_title="$ per share", showlegend=False, **{k: v for k, v in LAYOUT.items() if k != "legend"})
    return fig


def scenario_revenue(evals: dict) -> go.Figure:
    fig = go.Figure()
    for s, e in evals.items():
        fig.add_scatter(x=[f"FY{y}E" for y in config.FORECAST_YEARS], y=e.model.lines["rev_total"] / 1000,
                        name=config.SCENARIO_LABELS[s], mode="lines+markers", line=dict(color=PALETTE[s]))
    fig.update_layout(title="Revenue by scenario ($B)", yaxis_title="$B", **LAYOUT)
    return fig
