"""Streamlit UI for the TSLA pro-forma FCFE valuation model.

Run:  streamlit run app.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from tsla_model import charts, config
from tsla_model.assumptions import YEARS, default_assumptions, historical_drivers
from tsla_model.checks import summary as check_summary
from tsla_model.data_ingestion import build_source_table, get_data, historical_table
from tsla_model.excel_export import build_workbook
from tsla_model.scenarios import full_analysis

st.set_page_config(page_title="TSLA Pro-forma FCFE Model", page_icon="📈", layout="wide")


# =============================================================================================
# State
# =============================================================================================
@st.cache_resource(show_spinner="Loading filings and market data...")
def load_bundle(live: bool, refresh_token: int):
    return get_data(live=live)


def init_state():
    ss = st.session_state
    ss.setdefault("live", True)
    ss.setdefault("refresh", 0)
    ss.setdefault("scenario", "base")
    ss.setdefault("val_date", date.today())
    b = load_bundle(ss.live, ss.refresh)
    key = (ss.live, ss.refresh)
    if ss.get("bundle_key") != key:
        ss.bundle_key = key
        ss.bundle = b
        ss.aset = default_assumptions(b)
        ss.analysis_cache = {}
    return ss.bundle, ss.aset


def fingerprint(aset, scenario, val_date, market) -> str:
    payload = {
        "d": {k: v.values for k, v in aset.drivers.items()},
        "p": {k: (v.value if not isinstance(v.value, (np.floating,)) else float(v.value)) for k, v in aset.params.items()},
        "s": scenario, "t": val_date.isoformat(),
        "peers": [(p["ticker"], p.get("include", True), p["beta"], p["debt"], p["market_cap"]) for p in market["peers"]],
    }
    return hashlib.md5(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def get_analysis(b, aset) -> dict:
    ss = st.session_state
    fp = fingerprint(aset, ss.scenario, ss.val_date, b.market)
    if fp not in ss.analysis_cache:
        with st.spinner("Re-running the full model for every scenario and sensitivity..."):
            ss.analysis_cache = {fp: full_analysis(b, aset, ss.scenario, ss.val_date)}
    return ss.analysis_cache[fp]


# =============================================================================================
# Formatting helpers
# =============================================================================================
PCT_HINTS = ("margin", "growth (%)", "rate", "share of", "upside", "vs. market", "yield")


def _row_is_pct(label: str) -> bool:
    l = str(label).lower()
    return any(h in l for h in PCT_HINTS) and "($" not in l


def fmt_statement(df: pd.DataFrame, decimals: int = 0):
    def f(v, pct):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return ""
        if pct:
            return f"{v:.1%}"
        if abs(v) < 10 and v != 0 and decimals == 0:
            return f"{v:,.2f}"
        return f"({abs(v):,.{decimals}f})" if v < 0 else f"{v:,.{decimals}f}"
    out = df.copy().astype(object)
    for idx in out.index:
        pct = _row_is_pct(idx)
        out.loc[idx] = [f(v, pct) for v in df.loc[idx]]
    return out


def esc(text: str) -> str:
    """Escape dollar signs so Streamlit markdown does not render them as LaTeX."""
    return str(text).replace("$", "\\$")


def money(v, d=2):
    return "n/a" if v is None or (isinstance(v, float) and np.isnan(v)) else f"${v:,.{d}f}"


def failure_banner(val):
    st.error("**Valuation refused - a material model check failed.** Fix the inputs below before relying on any output.\n\n"
             + "\n".join(f"- {f}" for f in val.failures))


# =============================================================================================
# Sidebar
# =============================================================================================
def sidebar(b, aset):
    ss = st.session_state
    with st.sidebar:
        st.markdown("### TSLA pro-forma model")
        st.caption("Educational FCFE valuation. Not investment advice.")
        ss.scenario = st.selectbox("Scenario shown in detail", config.SCENARIOS, index=config.SCENARIOS.index(ss.scenario),
                                   format_func=lambda s: config.SCENARIO_LABELS[s])
        ss.val_date = st.date_input("Valuation date", ss.val_date)
        live = st.toggle("Live SEC & market data", value=ss.live, help="Off = seed data only (offline mode).")
        if live != ss.live:
            ss.live = live
            st.rerun()
        c1, c2 = st.columns(2)
        if c1.button("Refresh data", width="stretch"):
            ss.refresh += 1
            load_bundle.clear()
            st.rerun()
        if c2.button("Reset inputs", width="stretch"):
            ss.aset = default_assumptions(b)
            ss.analysis_cache = {}
            st.rerun()
        st.divider()
        live_n = sum(1 for s in b.status if s[1] == "live")
        fb_n = sum(1 for s in b.status if s[1] == "fallback")
        st.caption(f"Data: {live_n} live source(s), {fb_n} fallback(s). See *Sources & data*.")
        if st.button("Prepare Excel export", width="stretch"):
            x = get_analysis(b, aset)
            ss.xlsx = build_workbook(b, aset, ss.scenario, x["evals"], x, build_source_table(b), historical_table(b))
        if ss.get("xlsx"):
            st.download_button("Download workbook (.xlsx)", ss.xlsx, file_name=f"TSLA_proforma_{ss.scenario}_{date.today()}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        st.divider()
        st.caption(config.DISCLAIMER)


# =============================================================================================
# Pages
# =============================================================================================
CATALYSTS = [
    ("Robotaxi / Cybercab ramp", "Upside", "Robotaxi service launched June 2025; Cybercab production began H1 2026 (10-Q Q2 2026 p.28-29). Isolated as its own revenue line."),
    ("AI & capacity capex > $25B in 2026", "Risk / upside", "Guidance in 10-Q p.35. Depresses near-term FCFE; value depends on returns the model can only assume."),
    ("Energy storage scale-up", "Upside", "Shanghai & Lathrop Megafactories ramping, Houston under construction (10-Q p.30)."),
    ("Tariffs and trade policy", "Risk", "10-Q p.28: tariffs weigh more heavily on energy; Q2 2026 energy GAAP margin fell to 20.4% (p.32)."),
    ("Regulatory-credit run-off", "Risk", "Credits -28% in FY2025 and -49% in H1 2026 after OBBBA (10-K p.37, 10-Q p.31)."),
    ("2025 CEO Performance Award", "Dilution risk", "423.7M restricted shares earn only if market-cap and operating milestones are met (10-Q p.21). Toggle on the Assumptions page."),
    ("Optimus humanoid robot", "Upside (not modelled)", "No revenue is included in any scenario; any value would be additional."),
]


def page_summary():
    b, aset = st.session_state.bundle, st.session_state.aset
    x = get_analysis(b, aset)
    ev = x["evals"][st.session_state.scenario]
    val = ev.valuation
    price = b.market["price"]["value"]
    st.title("Tesla (TSLA) - Executive summary")
    st.caption(f"Five-year FCFE DCF (FY2026E-FY2030E) with Gordon-growth terminal value. Scenario: "
               f"**{config.SCENARIO_LABELS[st.session_state.scenario]}**. USD millions except per-share figures.")
    if val.status != "OK":
        failure_banner(val)
    c = st.columns(3) + st.columns(3)
    c[0].metric(f"Market price ({b.market['price']['as_of']})", money(price))
    c[1].metric("Implied value / share", money(val.value_per_share) if val.status == "OK" else "REFUSED")
    c[2].metric("Upside / (downside)", f"{val.upside:+.1%}" if val.status == "OK" else "n/a")
    c[3].metric("Cost of equity (CAPM)", f"{val.ke:.2%}", help=f"rf {val.coe['rf']:.2%} + beta {val.coe['beta']:.2f} x ERP {val.coe['erp']:.2%}")
    c[4].metric("Terminal value % of DCF value", f"{val.tv_share_of_dcf:.0%}" if val.status == "OK" else "n/a",
                help="PV of terminal value / (PV of forecast FCFE + PV of terminal value). Above 100% means forecast-period FCFE is negative in PV terms.")
    c[5].metric("Terminal value % of equity value", f"{val.tv_share_of_equity:.0%}" if val.status == "OK" else "n/a",
                help="PV of terminal value / total equity value (which also includes excess cash and other non-operating assets).")
    for w in val.warnings:
        st.warning(w)

    st.subheader("Scenarios (each is a full re-run of the model)")
    summ = x["summary"].copy()
    show = summ[["Scenario", "Status", "Implied value / share ($)", "Upside / (downside)", "Cost of equity", "TV % of DCF value",
                 "FY2030E revenue ($M)", "FY2030E EBITDA margin", "FY2030E FCFE ($M)", "Peak revolver ($M)"]]
    st.dataframe(show.style.format({"Implied value / share ($)": "${:,.2f}", "Upside / (downside)": "{:+.1%}", "Cost of equity": "{:.2%}",
                                    "TV % of DCF value": "{:.0%}", "FY2030E revenue ($M)": "{:,.0f}", "FY2030E EBITDA margin": "{:.1%}",
                                    "FY2030E FCFE ($M)": "{:,.0f}", "Peak revolver ($M)": "{:,.0f}"}, na_rep="n/a"),
                 hide_index=True, width="stretch")
    st.plotly_chart(charts.value_bridge_chart(x["bridge"], price), width="stretch")

    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.subheader("Key assumptions")
        sc = st.session_state.scenario
        keys = ["deliveries_3y", "deliveries_other", "asp_3y", "autonomy_rev", "storage_gwh", "gm_auto_sales", "gm_energy",
                "rd_pct", "sga_pct", "capex", "tax_rate"]
        rows = []
        for k in keys:
            a = aset.drivers[k]
            v = aset.get(k, sc)
            f = (lambda z: f"{z:.1%}") if a.unit == "pct" else (lambda z: f"{z:,.1f}" if abs(z) < 1000 else f"{z:,.0f}")
            rows.append({"Assumption": a.label, "FY2026E": f(v[0]), "FY2030E": f(v[-1]), "Type": a.kind})
        rows += [{"Assumption": "Cost of equity", "FY2026E": f"{val.ke:.2%}", "FY2030E": "", "Type": "CAPM"},
                 {"Assumption": "Terminal growth", "FY2026E": f"{val.g:.2%}", "FY2030E": "", "Type": aset.params['terminal_growth'].kind}]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    with col2:
        st.subheader("Catalysts & risks")
        st.dataframe(pd.DataFrame(CATALYSTS, columns=["Catalyst", "Direction", "Evidence / note"]), hide_index=True, width="stretch")

    st.subheader("Model checks")
    cs = check_summary(val.checks)
    ok = bool(cs["All years pass"].all())
    (st.success if ok else st.error)("All integrity checks pass for every forecast year." if ok else "One or more checks FAIL - see the Checks page.")
    st.dataframe(cs, hide_index=True, width="stretch")

    if "wmbt" in x:
        st.subheader(esc(f"What would have to be true for today's price (${price:,.2f}) to be correct?"))
        st.caption("Each lever is moved on its own with every other input at scenario values, and the full model is re-solved "
                   "(bisection) until implied value equals the market price.")
        st.dataframe(x["wmbt"], hide_index=True, width="stretch")
    st.divider()
    st.warning("**Investment-risk disclaimer.** " + config.DISCLAIMER)


def page_assumptions():
    b, aset = st.session_state.bundle, st.session_state.aset
    sc = st.session_state.scenario
    st.title("Assumptions")
    st.caption(f"Single source of truth for every driver. Editing **{config.SCENARIO_LABELS[sc]}** values (change the scenario in the sidebar). "
               "Percent inputs are decimals (0.21 = 21%). Every edit is logged in the revision history below.")
    hist = historical_drivers(b)
    hist_key = {"deliveries_3y": "deliveries_3y", "deliveries_other": "deliveries_other", "asp_3y": "asp_3y", "asp_other": "asp_other",
                "reg_credits": "reg_credits", "auto_leasing_rev": "auto_leasing_rev", "storage_gwh": "storage_gwh",
                "energy_rev_per_gwh": "energy_rev_per_gwh", "gm_auto_sales": "gm_auto_sales", "gm_leasing": "gm_leasing",
                "gm_services": "gm_services", "gm_energy": "gm_energy", "rd_pct": "rd_pct", "sga_pct": "sga_pct", "sbc_pct": "sbc_pct",
                "da_rate": "da_rate", "da_cogs_share": "da_cogs_share", "capex": "capex", "dso": "dso", "dio": "dio", "dpo": "dpo",
                "prepaid_pct": "prepaid_pct", "accrued_pct": "accrued_pct", "deferred_rev_pct": "deferred_rev_pct",
                "interest_yield_cash": "interest_yield", "tax_rate": "tax_rate"}
    note = st.text_input("Note to attach to edits made now (optional)", key="edit_note")
    cats = list(dict.fromkeys(a.category for a in aset.drivers.values()))
    for cat in cats:
        with st.expander(cat, expanded=cat in ("Automotive volume & price", "Margins")):
            items = [a for a in aset.drivers.values() if a.category == cat]
            df = pd.DataFrame([{
                "ID": a.id, "Assumption": a.label, "Type": a.kind,
                "FY2025A": hist["FY2025"].get(hist_key.get(a.id, ""), np.nan),
                "H1 2026A": hist["H1_2026"].get(hist_key.get(a.id, ""), np.nan),
                **{f"FY{y}E": a.values[sc][i] for i, y in enumerate(YEARS)},
                "Same as base": sc != "base" and a.values[sc] == a.values["base"],
            } for a in items])
            edited = st.data_editor(
                df, key=f"ed_{cat}_{sc}", hide_index=True, width="stretch",
                disabled=["ID", "Assumption", "Type", "FY2025A", "H1 2026A", "Same as base"],
                column_config={f"FY{y}E": st.column_config.NumberColumn(format="%.4g") for y in YEARS}
                | {"FY2025A": st.column_config.NumberColumn(format="%.4g"), "H1 2026A": st.column_config.NumberColumn(format="%.4g", help="Annualised where relevant")})
            changed = False
            for _, r in edited.iterrows():
                for i, y in enumerate(YEARS):
                    new = r[f"FY{y}E"]
                    if new is not None and not pd.isna(new) and float(new) != aset.drivers[r["ID"]].values[sc][i]:
                        aset.set_value(r["ID"], sc, i, float(new), note)
                        changed = True
            for a in items:
                st.markdown(f"**{esc(a.label)}** · `{a.kind}` · *Source:* {esc(a.source)}  \n*Rationale:* {esc(a.rationale)}")
            if changed:
                st.rerun()

    st.subheader("Quick adjust (applies to every forecast year of the selected scenario)")
    with st.form("quick"):
        c1, c2, c3 = st.columns([2, 1, 1])
        drv = c1.selectbox("Driver", list(aset.drivers), format_func=lambda k: aset.drivers[k].label)
        factor = c2.slider("Multiply by", 0.0, 3.0, 1.0, 0.01, help="1.10 = +10% in every year")
        add = c3.number_input("Then add", value=0.0, step=0.005, format="%.4f",
                              help="In driver units (0.01 = +1 pt for percentage drivers)")
        if st.form_submit_button("Apply"):
            cur = list(aset.drivers[drv].values[sc])
            for i in range(len(YEARS)):
                aset.set_value(drv, sc, i, cur[i] * factor + add, note or f"quick adjust (x{factor:.2f} {add:+.4f})")
            st.rerun()

    st.subheader("Valuation parameters")
    P = aset.params
    c1, c2, c3 = st.columns(3)
    with c1:
        rf = st.slider("Risk-free rate", 0.0, 0.10, float(P["risk_free"].value), 0.0005, format="%.4f", help=P["risk_free"].source)
        erp = st.slider("Equity risk premium", 0.02, 0.10, float(P["erp"].value), 0.0025, format="%.4f", help=P["erp"].rationale)
        g = st.slider("Terminal FCFE growth", -0.02, 0.08, float(P["terminal_growth"].value), 0.0025, format="%.4f", help=P["terminal_growth"].rationale)
    with c2:
        method = st.selectbox("Beta method", ["bottom-up", "observed", "average"], index=["bottom-up", "observed", "average"].index(P["beta_method"].value))
        wauto = st.slider("Bottom-up beta weight on auto peers", 0.0, 1.0, float(P["peer_weight_auto"].value), 0.05)
        capda = st.slider("Terminal capex / D&A", 0.8, 2.5, float(P["terminal_capex_to_da"].value), 0.05, help=P["terminal_capex_to_da"].rationale)
    with c3:
        sbc = st.checkbox("Add back SBC in FCFE", bool(P["add_back_sbc"].value), help=P["add_back_sbc"].rationale)
        ceo = st.checkbox("Include 423.7M unearned CEO award shares", bool(P["include_ceo_award_shares"].value), help=P["include_ceo_award_shares"].rationale)
        mid = st.checkbox("Mid-period discounting", bool(P["mid_year"].value))
        rcap = st.number_input("Revolver capacity ($M)", 0.0, 50000.0, float(P["revolver_capacity"].value), 500.0)
    for pid, v in [("risk_free", rf), ("erp", erp), ("terminal_growth", g), ("beta_method", method), ("peer_weight_auto", wauto),
                   ("terminal_capex_to_da", capda), ("add_back_sbc", sbc), ("include_ceo_award_shares", ceo), ("mid_year", mid),
                   ("revolver_capacity", rcap)]:
        aset.set_param(pid, v, note)
    if g >= rf:
        st.info("Terminal growth is at or above the risk-free rate - usually a sign the terminal assumption is too aggressive.")

    st.subheader("Bottom-up beta peers")
    peers = b.market["peers"]
    inc = st.multiselect("Peers included", [p["ticker"] for p in peers], default=[p["ticker"] for p in peers if p.get("include", True)])
    for p in peers:
        p["include"] = p["ticker"] in inc
    st.dataframe(pd.DataFrame(peers)[["ticker", "name", "group", "beta", "market_cap", "debt", "debt_type", "tax_rate", "notes"]],
                 hide_index=True, width="stretch")

    st.subheader("All parameters")
    st.dataframe(aset.params_table().astype(str), hide_index=True, width="stretch")
    st.subheader("Revision history")
    rev = aset.revisions_table()
    st.dataframe(rev.astype(str), hide_index=True, width="stretch")
    st.download_button("Download revision history (CSV)", rev.to_csv(index=False), "assumption_revisions.csv", "text/csv")


def page_statements():
    b, aset = st.session_state.bundle, st.session_state.aset
    x = get_analysis(b, aset)
    ev = x["evals"][st.session_state.scenario]
    res = ev.model
    st.title(f"Financial statements - {config.SCENARIO_LABELS[st.session_state.scenario]}")
    st.caption("FY2023A-FY2025A as reported (with derived ex-D&A splits); FY2026E-FY2030E forecast. USD millions.")
    if ev.valuation.status != "OK":
        failure_banner(ev.valuation)
    t = st.tabs(["Income statement", "Balance sheet", "Cash flow", "Schedules", "FCFE", "Charts"])
    with t[0]:
        st.dataframe(fmt_statement(res.income), width="stretch", height=900)
    with t[1]:
        st.dataframe(fmt_statement(res.balance), width="stretch", height=820)
    with t[2]:
        st.dataframe(fmt_statement(res.cashflow), width="stretch", height=740)
        for n in res.notes:
            st.caption(n)
    with t[3]:
        for name, df in res.schedules.items():
            st.markdown(f"**{name}**")
            st.dataframe(fmt_statement(df), width="stretch")
    with t[4]:
        st.dataframe(fmt_statement(res.fcfe), width="stretch")
        st.caption("FCFE = net income + D&A (+ SBC if added back) - capex - increase in NWC + net borrowing (debt, finance leases, revolver).")
    with t[5]:
        st.plotly_chart(charts.revenue_mix(res.income), width="stretch")
        st.plotly_chart(charts.margins(res.income), width="stretch")
        st.plotly_chart(charts.cash_vs_minimum(res.balance, res.cashflow), width="stretch")
        st.plotly_chart(charts.scenario_revenue(x["evals"]), width="stretch")


def page_valuation():
    b, aset = st.session_state.bundle, st.session_state.aset
    x = get_analysis(b, aset)
    ev = x["evals"][st.session_state.scenario]
    val = ev.valuation
    st.title(f"FCFE valuation - {config.SCENARIO_LABELS[st.session_state.scenario]}")
    if val.status != "OK":
        failure_banner(val)
        return
    coe = val.coe
    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.subheader("Cost of equity (CAPM)")
        st.markdown(f"""
| Component | Value |
|---|---|
| Risk-free rate ({b.market['risk_free']['as_of']}) | {coe['rf']:.2%} |
| Equity risk premium (judgment) | {coe['erp']:.2%} |
| Observed beta (5y monthly regression) | {coe['beta_observed']:.2f} |
| Bottom-up beta (relevered) | {coe['beta_bottom_up']:.2f} |
| **Beta used ({coe['method']})** | **{coe['beta']:.2f}** |
| **Cost of equity = rf + beta x ERP** | **{val.ke:.2%}** |
| Cost of equity @ observed beta | {coe['ke_observed']:.2%} |
| Terminal growth | {val.g:.2%} |
""")
    with c2:
        st.subheader("Bottom-up beta")
        bu = coe["bottom_up"]
        st.dataframe(bu["peers"][["Ticker", "Group", "Levered beta", "D/E", "Tax rate", "Unlevered beta", "Debt source"]]
                     .style.format({"Levered beta": "{:.2f}", "D/E": "{:.2f}", "Tax rate": "{:.0%}", "Unlevered beta": "{:.2f}"}),
                     hide_index=True, width="stretch")
        st.caption(f"Unlevered: auto peers avg {bu['auto_unlevered']:.2f}, energy peers avg {bu['energy_unlevered']:.2f}; "
                   f"revenue-weighted {bu['weighted_unlevered']:.2f}. Relevered at Tesla's forecast D/E of {bu['tesla_de']:.3f} "
                   f"(average forecast debt + leases / market cap) = **{bu['relevered']:.2f}**. "
                   "Hamada: beta_U = beta_L / (1 + (1 - t) D/E).")
    st.subheader("Discounted operating FCFE")
    st.dataframe(val.pv_table.style.format({c: "{:,.0f}" for c in val.pv_table.columns if c not in ("Year", "Discount period (yrs)", "Discount factor")}
                                           | {"Discount period (yrs)": "{:.2f}", "Discount factor": "{:.4f}"}),
                 hide_index=True, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"{config.TERMINAL_YEAR} FCFE bridge (terminal year)")
        st.dataframe(val.terminal_bridge.style.format({"FY2030E": "{:,.0f}", f"FY{config.TERMINAL_YEAR}": "{:,.0f}"}),
                     hide_index=True, width="stretch")
        st.caption(f"Terminal value = FCFE {config.TERMINAL_YEAR} / (ke - g) = {val.fcfe_2031:,.0f} / ({val.ke:.2%} - {val.g:.2%}) "
                   f"= {val.terminal_value:,.0f}")
    with c2:
        st.subheader("Equity value bridge")
        eb = val.equity_bridge.copy()
        eb["Value"] = [(f"{v:.1%}" if ("share of" in i.lower() or "upside" in i.lower()) else
                        (f"${v:,.2f}" if ("per share" in i.lower() or "price" in i.lower()) else f"{v:,.0f}"))
                       for i, v in zip(eb["Item"], eb["USD m"])]
        st.dataframe(eb[["Item", "Value"]], hide_index=True, width="stretch")
    st.plotly_chart(charts.equity_value_waterfall(val), width="stretch")
    st.plotly_chart(charts.fcfe_bars(ev.model.fcfe), width="stretch")
    for w in val.warnings:
        st.warning(w)
    st.subheader("Secondary cross-check: trading multiples")
    st.info("Secondary only. Auto and energy peers have very different growth, margin and autonomy profiles, and the market "
            "prices Tesla on expectations far beyond peer multiples. The DCF above is the primary valuation.")
    if "multiples" in x:
        st.dataframe(x["multiples"].style.format({"Multiple": "{:,.1f}x", "Implied value per share": "${:,.2f}"}, na_rep="n/a"),
                     hide_index=True, width="stretch")


def page_sensitivity():
    b, aset = st.session_state.bundle, st.session_state.aset
    x = get_analysis(b, aset)
    val = x["evals"][st.session_state.scenario].valuation
    price = b.market["price"]["value"]
    st.title(f"Sensitivities - {config.SCENARIO_LABELS[st.session_state.scenario]}")
    st.caption("Every cell and bar below is a full re-run of the three statements and the valuation - sensitivities are never added together.")
    if val.status != "OK":
        failure_banner(val)
        return
    st.plotly_chart(charts.heatmap(x["ke_g"], "Implied value per share: cost of equity x terminal growth", price,
                                   "Terminal growth", "Cost of equity"), width="stretch")
    st.caption("Blank cells: terminal growth >= cost of equity, so the Gordon model is undefined and the valuation refuses to run.")
    st.plotly_chart(charts.tornado_chart(x["tornado"], val.value_per_share), width="stretch")
    st.subheader("One-variable sensitivity: every core operating driver")
    ov = x["one_var"]
    steps = [c for c in ov.columns if c.startswith("step")]
    tbl = pd.DataFrame({"Driver": ov["Driver"], "Shock size (1 step)": ov["label +1"]})
    for s_ in steps:
        tbl[s_.replace("step", "Steps")] = ov[s_].map(lambda v: money(v))
    st.dataframe(tbl, hide_index=True, width="stretch")
    st.plotly_chart(charts.one_variable_lines(ov), width="stretch")
    i1, i2 = x["two_var_ids"]
    st.subheader(f"Two-variable matrix: {aset.drivers[i1].label} x {aset.drivers[i2].label}")
    st.caption("The two highest-impact operating assumptions from the tornado, shocked together in every forecast year.")
    st.plotly_chart(charts.heatmap(x["two_var"], "Implied value per share", price, aset.drivers[i1].label, aset.drivers[i2].label),
                    width="stretch")
    st.subheader("Price / implied-value bridge")
    br = x["bridge"]
    st.dataframe(br.style.format({"Value per share ($)": "${:,.2f}", "Cost of equity": "{:.2%}", "vs. market price": "{:+.1%}"}, na_rep=""),
                 hide_index=True, width="stretch")
    st.plotly_chart(charts.value_bridge_chart(br, price), width="stretch")


def page_checks():
    b, aset = st.session_state.bundle, st.session_state.aset
    x = get_analysis(b, aset)
    st.title("Model checks")
    for s, ev in x["evals"].items():
        val = ev.valuation
        cs = check_summary(val.checks)
        ok = bool(cs["All years pass"].all())
        with st.expander(f"{'✅' if ok else '❌'} {config.SCENARIO_LABELS[s]} - {'all checks pass' if ok else 'FAILURES'}", expanded=not ok or s == st.session_state.scenario):
            st.dataframe(cs, hide_index=True, width="stretch")
            det = val.checks.copy()
            st.dataframe(det.style.format({"Difference": "{:,.4f}"}).apply(
                lambda r: ["background-color: #d9f2e6" if r["Pass"] else "background-color: #f8d7da"] * len(r), axis=1),
                hide_index=True, width="stretch")


def page_sources():
    b = st.session_state.bundle
    st.title("Sources & data")
    st.subheader("Data status this session")
    st.dataframe(pd.DataFrame(b.status, columns=["Component", "Status", "Detail"]), hide_index=True, width="stretch")
    st.subheader("Filings used")
    st.dataframe(pd.DataFrame([{"Key": k, **v} for k, v in b.financials["filings"].items()]), hide_index=True, width="stretch",
                 column_config={"url": st.column_config.LinkColumn("URL")})
    if b.latest_filings:
        st.caption("Latest 10-K/10-Q filings found on EDGAR at runtime:")
        st.dataframe(pd.DataFrame(b.latest_filings), hide_index=True, width="stretch", column_config={"url": st.column_config.LinkColumn("URL")})
    st.subheader("Source table")
    src = build_source_table(b)
    sec = st.multiselect("Sections", sorted(src["Section"].unique()), default=sorted(src["Section"].unique()))
    view = src[src["Section"].isin(sec)].copy()
    view["Value"] = view["Value"].astype(str)
    st.dataframe(view, hide_index=True, width="stretch", column_config={"URL": st.column_config.LinkColumn("URL")})
    st.subheader("Historical financials (as reported)")
    h = historical_table(b)
    st.dataframe(h, hide_index=True, width="stretch")
    st.subheader("Disclosure limitations")
    st.markdown("""
- **Revenue by vehicle model is not disclosed.** Deliveries are split only into *Model 3/Y* and *Other models* (8-K Ex. 99.1). Category ASPs are
  derived by assuming other models sell at ~2x the 3/Y price; only the blended ASP is fully observable.
- **D&A by revenue line is not disclosed.** Segment notes give D&A in cost of revenues for automotive and energy only; automotive D&A is
  allocated pro-rata to COGS across automotive sales, leasing and services to derive ex-D&A ("cash") margins.
- **Robotaxi/autonomy revenue is not reported separately** (it sits in services & other). The model isolates future robotaxi revenue as an explicit judgment line.
- **Operating-lease vehicle additions** run through operating cash flow in Tesla's statements; the model treats all fixed-asset additions as capex.
- **Minimum cash** is not stated by Tesla; the 15%-of-revenue rule is a judgment.
- **Peer debt for GM and Ford** excludes captive-finance debt using judgment-based approximations (custom XBRL tags prevent automated extraction).
""")


# =============================================================================================
PAGE_FUNCS = {"summary": page_summary, "assumptions": page_assumptions, "statements": page_statements,
              "valuation": page_valuation, "sensitivities": page_sensitivity, "checks": page_checks, "sources": page_sources}


def main():
    b, aset = init_state()
    sidebar(b, aset)
    forced = st.session_state.get("force_page")   # used only by the headless AppTest suite
    if forced:
        PAGE_FUNCS[forced]()
        return
    pages = [
        st.Page(page_summary, title="Executive summary", icon="📊", default=True, url_path="summary"),
        st.Page(page_assumptions, title="Assumptions", icon="🛠️", url_path="assumptions"),
        st.Page(page_statements, title="Financial statements", icon="📑", url_path="statements"),
        st.Page(page_valuation, title="Valuation", icon="💵", url_path="valuation"),
        st.Page(page_sensitivity, title="Sensitivities", icon="🌡️", url_path="sensitivities"),
        st.Page(page_checks, title="Model checks", icon="✅", url_path="checks"),
        st.Page(page_sources, title="Sources & data", icon="📚", url_path="sources"),
    ]
    st.navigation(pages).run()


main()
