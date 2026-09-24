"""Scenarios and sensitivities.

Rule: every number here comes from a *full* re-run of the three-statement model and the
valuation (``evaluate``). Individual sensitivities are never added together.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from . import config
from .assumptions import AssumptionSet
from .data_ingestion import DataBundle
from .statements import ModelResult, run_model
from .valuation import ValuationResult, run_valuation


@dataclass
class Evaluation:
    scenario: str
    model: ModelResult
    valuation: ValuationResult

    @property
    def value(self) -> float:
        v = self.valuation.value_per_share
        return float(v) if (self.valuation.status == "OK" and v is not None) else np.nan


def evaluate(b: DataBundle, a: AssumptionSet, scenario: str = "base", valuation_date: date | None = None,
             ke_override: float | None = None, g_override: float | None = None,
             beta_method: str | None = None, frames: bool = False) -> Evaluation:
    res = run_model(b, a, scenario, build_frames=frames)
    val = run_valuation(b, a, res, scenario, valuation_date, ke_override, g_override, beta_method)
    return Evaluation(scenario, res, val)


def run_all_scenarios(b: DataBundle, a: AssumptionSet, valuation_date: date | None = None) -> dict:
    return {s: evaluate(b, a, s, valuation_date, frames=True) for s in config.SCENARIOS}


def scenario_summary(evals: dict, price: float) -> pd.DataFrame:
    rows = []
    for s, e in evals.items():
        L, v = e.model.lines, e.valuation
        rows.append({
            "Scenario": config.SCENARIO_LABELS[s], "Status": v.status,
            "Implied value / share ($)": e.value, "Market price ($)": price,
            "Upside / (downside)": e.value / price - 1 if price and not np.isnan(e.value) else np.nan,
            "Cost of equity": v.ke, "Terminal growth": v.g,
            "TV % of DCF value": v.tv_share_of_dcf if v.status == "OK" else np.nan,
            "FY2030E revenue ($M)": L["rev_total"][-1], "FY2030E EBITDA margin": L["ebitda"][-1] / L["rev_total"][-1],
            "FY2030E net income ($M)": L["ni_parent"][-1], "FY2030E FCFE ($M)": L["fcfe"][-1],
            "Min. cash & inv. over forecast ($M)": float(np.min(L["cash"])), "Peak revolver ($M)": float(np.max(L["revolver"])),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------
# Discount-rate x terminal-growth heat map
# ---------------------------------------------------------------------------------------------
def ke_g_grid(b, a, scenario="base", valuation_date=None, ke_values=None, g_values=None) -> pd.DataFrame:
    base = evaluate(b, a, scenario, valuation_date)
    ke0, g0 = base.valuation.ke, base.valuation.g
    ke_values = ke_values if ke_values is not None else [round(ke0 + d, 4) for d in (-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03)]
    g_values = g_values if g_values is not None else [round(g0 + d, 4) for d in (-0.02, -0.01, -0.005, 0, 0.005, 0.01, 0.02)]
    out = pd.DataFrame(index=[f"{k:.2%}" for k in ke_values], columns=[f"{g:.2%}" for g in g_values], dtype=float)
    for ke in ke_values:
        for g in g_values:
            e = evaluate(b, a, scenario, valuation_date, ke_override=ke, g_override=g)
            out.loc[f"{ke:.2%}", f"{g:.2%}"] = e.value   # NaN when g >= ke (valuation refuses)
    out.index.name = "Cost of equity \\ terminal growth"
    return out


# ---------------------------------------------------------------------------------------------
# One-variable sensitivities and tornado
# ---------------------------------------------------------------------------------------------
def _shock_label(a: AssumptionSet, item: str, step: float) -> str:
    kind, size = a.drivers[item].shock
    if kind == "rel":
        return f"{step * size:+.0%}"
    unit = a.drivers[item].unit
    return f"{step * size * 100:+.1f} pts" if unit == "pct" else f"{step * size:+.1f} {unit}"


def one_variable(b, a, scenario="base", valuation_date=None, steps=(-2, -1, 0, 1, 2)) -> pd.DataFrame:
    rows = []
    for item in a.core_drivers():
        row = {"Driver": a.drivers[item].label, "ID": item,
               "Shock unit": "relative %" if a.drivers[item].shock[0] == "rel" else "absolute"}
        for s in steps:
            e = evaluate(b, a.shocked(item, scenario, s), scenario, valuation_date)
            row[f"step {s:+d}"] = e.value
            row[f"label {s:+d}"] = _shock_label(a, item, s)
        rows.append(row)
    return pd.DataFrame(rows)


def tornado(b, a, scenario="base", valuation_date=None) -> pd.DataFrame:
    base = evaluate(b, a, scenario, valuation_date).value
    rows = []
    for item in a.core_drivers():
        lo = evaluate(b, a.shocked(item, scenario, -1), scenario, valuation_date).value
        hi = evaluate(b, a.shocked(item, scenario, +1), scenario, valuation_date).value
        rows.append({"Driver": a.drivers[item].label, "ID": item, "Shock": _shock_label(a, item, 1).lstrip("+"),
                     "Low case value": lo, "High case value": hi, "Base value": base,
                     "Low delta": lo - base, "High delta": hi - base, "Range": abs(hi - lo)})
    return pd.DataFrame(rows).sort_values("Range", ascending=False).reset_index(drop=True)


def two_variable(b, a, item_x: str, item_y: str, scenario="base", valuation_date=None,
                 steps=(-2, -1, 0, 1, 2)) -> pd.DataFrame:
    out = pd.DataFrame(index=[_shock_label(a, item_y, s) for s in steps],
                       columns=[_shock_label(a, item_x, s) for s in steps], dtype=float)
    for sy in steps:
        ay = a.shocked(item_y, scenario, sy)
        for sx in steps:
            e = evaluate(b, ay.shocked(item_x, scenario, sx), scenario, valuation_date)
            out.loc[_shock_label(a, item_y, sy), _shock_label(a, item_x, sx)] = e.value
    out.index.name = f"{a.drivers[item_y].label} \\ {a.drivers[item_x].label}"
    return out


# ---------------------------------------------------------------------------------------------
# Price / implied-value bridge
# ---------------------------------------------------------------------------------------------
def value_bridge(b, a, evals: dict, valuation_date=None) -> pd.DataFrame:
    price = b.market["price"]["value"]
    base = evals["base"]
    rows = [{"Case": f"Market price ({b.market['price']['as_of']})", "Value per share ($)": price, "Cost of equity": np.nan, "Type": "market"}]
    for s in ("recession", "bear", "base", "bull"):
        rows.append({"Case": config.SCENARIO_LABELS[s] + " case", "Value per share ($)": evals[s].value,
                     "Cost of equity": evals[s].valuation.ke, "Type": "scenario"})
    obs = evaluate(b, a, "base", valuation_date, beta_method="observed")
    rows.append({"Case": f"Base @ observed beta ({a.p('beta_observed'):.2f})", "Value per share ($)": obs.value,
                 "Cost of equity": obs.valuation.ke, "Type": "discount rate"})
    for d in (-0.01, 0.01):
        e = evaluate(b, a, "base", valuation_date, ke_override=base.valuation.ke + d)
        rows.append({"Case": f"Base @ cost of equity {base.valuation.ke + d:.1%}", "Value per share ($)": e.value,
                     "Cost of equity": base.valuation.ke + d, "Type": "discount rate"})
    df = pd.DataFrame(rows)
    df["vs. market price"] = df["Value per share ($)"] / price - 1
    return df


# ---------------------------------------------------------------------------------------------
# "What would have to be true for today's price to be correct?"
# ---------------------------------------------------------------------------------------------
def _solve(f, lo, hi, target, iters=40):
    """Bisection for f(x) = target; returns (x, bracketed?)."""
    flo, fhi = f(lo), f(hi)
    if np.isnan(flo) or np.isnan(fhi) or (flo - target) * (fhi - target) > 0:
        return None, fhi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if np.isnan(fm):
            hi = mid
            continue
        if (fm - target) * (flo - target) <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if abs(hi - lo) < 1e-6:
            break
    return 0.5 * (lo + hi), None


def what_must_be_true(b, a, scenario="base", valuation_date=None, target: float | None = None) -> pd.DataFrame:
    target = b.market["price"]["value"] if target is None else target
    base = evaluate(b, a, scenario, valuation_date)
    ke0, g0 = base.valuation.ke, base.valuation.g
    last = len(config.FORECAST_YEARS) - 1

    def scale(item):
        return lambda k: evaluate(b, a.scaled(item, scenario, factor=k), scenario, valuation_date).value

    def shift(item):
        return lambda d: evaluate(b, a.scaled(item, scenario, add=d), scenario, valuation_date).value

    def param(pid):
        def f(x):
            a2 = a.copy()
            a2.params[pid].value = x
            return evaluate(b, a2, scenario, valuation_date).value
        return f

    levers = [
        ("Cost of equity", lambda x: evaluate(b, a, scenario, valuation_date, ke_override=x).value, g0 + 0.0025, 0.40,
         ke0, lambda x: f"{x:.2%}", "Discount rate that equates model FCFE with the market price"),
        ("Terminal FCFE growth", lambda x: evaluate(b, a, scenario, valuation_date, g_override=x).value, -0.05, ke0 - 0.0005,
         g0, lambda x: f"{x:.2%}", "Perpetual growth needed (must stay below cost of equity)"),
        ("Robotaxi / autonomy revenue, FY2030E", scale("autonomy_rev"), 1.0, 200.0,
         a.get("autonomy_rev", scenario)[last], lambda k: f"${k * a.get('autonomy_rev', scenario)[last] / 1000:,.0f}B",
         "All years scaled by the same factor; margins unchanged"),
        ("Automotive sales cash gross margin (all years)", shift("gm_auto_sales"), 0.0, 0.60,
         a.get("gm_auto_sales", scenario)[last], lambda d: f"{a.get('gm_auto_sales', scenario)[last] + d:.1%} in FY2030E (+{d * 100:.1f} pts)",
         "Parallel shift in every year"),
        ("Model 3/Y deliveries (all years)", scale("deliveries_3y"), 1.0, 10.0,
         a.get("deliveries_3y", scenario)[last], lambda k: f"{k * a.get('deliveries_3y', scenario)[last] / 1000:,.1f}M units in FY2030E (x{k:.2f})",
         "Scales volumes only; capex held at the scenario path"),
        ("Energy storage deployed (all years)", scale("storage_gwh"), 1.0, 60.0,
         a.get("storage_gwh", scenario)[last], lambda k: f"{k * a.get('storage_gwh', scenario)[last]:,.0f} GWh in FY2030E (x{k:.2f})",
         "Scales GWh; price per GWh and margin unchanged"),
        ("Services & other growth (all years)", shift("services_growth"), 0.0, 1.5,
         a.get("services_growth", scenario)[last], lambda d: f"+{d * 100:.0f} pts per year",
         "Parallel shift in annual growth"),
        ("Capital expenditures (all years)", scale("capex"), 1.0, 0.0,
         a.get("capex", scenario)[last], lambda k: f"{k:.0%} of scenario capex (FY2030E ${k * a.get('capex', scenario)[last] / 1000:,.1f}B)",
         "Lower capex with unchanged growth - an inconsistent, upper-bound test"),
        ("Terminal capex / D&A", param("terminal_capex_to_da"), float(a.p("terminal_capex_to_da")), 0.0,
         float(a.p("terminal_capex_to_da")), lambda x: f"{x:.2f}x", "Below 1.0x means the asset base shrinks in perpetuity"),
    ]
    rows = []
    for name, f, lo, hi, base_val, fmt, note in levers:
        x, v_at_limit = _solve(f, lo, hi, target)
        if x is None:
            req = "Not achievable within tested range"
            detail = f"value at range limit: ${v_at_limit:,.0f}/share" if v_at_limit is not None and not np.isnan(v_at_limit) else "model fails a check at range limit"
        else:
            req, detail = fmt(x), ""
        base_txt = {"Cost of equity": f"{ke0:.2%}", "Terminal FCFE growth": f"{g0:.2%}"}.get(name)
        if base_txt is None:
            if "capex / D&A" in name:
                base_txt = f"{base_val:.2f}x"
            elif "margin" in name:
                base_txt = f"{base_val:.1%} in FY2030E"
            elif "growth" in name:
                base_txt = f"{base_val:.0%} in FY2030E"
            elif "GWh" in name or "Energy" in name:
                base_txt = f"{base_val:,.0f} GWh in FY2030E"
            elif "deliveries" in name:
                base_txt = f"{base_val / 1000:,.2f}M units in FY2030E"
            else:
                base_txt = f"${base_val / 1000:,.1f}B in FY2030E"
        rows.append({"Lever (moved alone, all else at scenario values)": name, "Model assumption": base_txt,
                     f"Required for ${target:,.0f}/share": req, "Comment": note if not detail else f"{note}; {detail}"})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------
# One-call orchestration used by the app, the Excel export and the tests
# ---------------------------------------------------------------------------------------------
def full_analysis(b: DataBundle, a: AssumptionSet, scenario: str = "base", valuation_date: date | None = None) -> dict:
    from .valuation import multiples_crosscheck

    evals = run_all_scenarios(b, a, valuation_date)
    ev = evals[scenario]
    price = b.market["price"]["value"]
    out = {"evals": evals, "summary": scenario_summary(evals, price)}
    out["bridge"] = value_bridge(b, a, evals, valuation_date)
    if ev.valuation.status != "OK":
        return out
    out["multiples"] = multiples_crosscheck(b, a, ev.model, ev.valuation)
    out["ke_g"] = ke_g_grid(b, a, scenario, valuation_date)
    out["tornado"] = tornado(b, a, scenario, valuation_date)
    out["one_var"] = one_variable(b, a, scenario, valuation_date)
    top = out["tornado"]["ID"].tolist()
    out["two_var_ids"] = (top[0], top[1])
    out["two_var"] = two_variable(b, a, top[0], top[1], scenario, valuation_date)
    out["wmbt"] = what_must_be_true(b, a, scenario, valuation_date)
    return out
