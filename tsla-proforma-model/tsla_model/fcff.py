"""Five-year FCFF DCF using the linked operating forecast and a WACC discount rate."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from . import config
from .assumptions import AssumptionSet
from .checks import material_failures, run_checks
from .data_ingestion import DataBundle
from .statements import ModelResult
from .valuation import _periods, cost_of_equity, diluted_shares, non_operating_assets


@dataclass
class FCFFResult:
    status: str
    failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    value_per_share: float | None = None
    enterprise_value: float | None = None
    equity_value: float | None = None
    wacc: float = 0.0
    g: float = 0.0
    coe: dict = field(default_factory=dict)
    debt_cost: float = 0.0
    equity_weight: float = 0.0
    debt_weight: float = 0.0
    pv_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    terminal_bridge: pd.DataFrame = field(default_factory=pd.DataFrame)
    equity_bridge: pd.DataFrame = field(default_factory=pd.DataFrame)
    reconciliation: pd.DataFrame = field(default_factory=pd.DataFrame)
    fcff_2031: float = 0.0
    terminal_value: float = 0.0
    pv_terminal: float = 0.0
    pv_fcff: float = 0.0
    tv_share_of_ev: float = 0.0
    shares: float = 0.0
    checks: pd.DataFrame = field(default_factory=pd.DataFrame)
    valuation_date: str = ""


def fcff_cash_flow(ebit: float, tax_rate: float, da: float, sbc: float, capex: float, delta_nwc: float,
                   add_sbc: bool) -> tuple[float, float]:
    """Return NOPAT and FCFF; tax shields never arise from a negative EBIT forecast."""
    tax_on_ebit = tax_rate * max(ebit, 0.0)
    nopat = ebit - tax_on_ebit
    return nopat, nopat + da + (sbc if add_sbc else 0.0) - capex - delta_nwc


def q2_bridge_balances(b: DataBundle) -> dict:
    """Balance-sheet claims at 30-Jun-2026, matching the cash/assets bridge date."""
    debt_and_finance_leases = b.value("debt_fl_current", "Q2_2026") + b.value("debt_fl_noncurrent", "Q2_2026")
    finance_leases = b.value("finance_lease_liab", "Q2_2026")
    return {
        "Debt (ex-finance leases, 30-Jun-2026)": debt_and_finance_leases - finance_leases,
        "Finance lease liabilities (30-Jun-2026)": finance_leases,
        "Revolver (30-Jun-2026)": 0.0,
        "Noncontrolling interests incl. redeemable NCI (30-Jun-2026)": b.value("nci", "Q2_2026") + b.value("redeemable_nci", "Q2_2026"),
    }


def wacc_components(b: DataBundle, a: AssumptionSet, res: ModelResult, scenario: str, ke_override: float | None = None) -> dict:
    coe = cost_of_equity(b, a, res)
    ke = float(ke_override) if ke_override is not None else coe["ke"]
    bridge = q2_bridge_balances(b)
    debt = bridge["Debt (ex-finance leases, 30-Jun-2026)"] + bridge["Finance lease liabilities (30-Jun-2026)"] + bridge["Revolver (30-Jun-2026)"]
    shares = diluted_shares(b, a)
    equity = float(b.market["price"]["value"]) * shares
    wd = debt / (equity + debt)
    we = 1.0 - wd
    # The model's historical debt/finance-lease rate is the pre-tax debt cost. A drawn revolver
    # uses its separately stated rate, blended only when it has a balance at the valuation date.
    kd = float(a.get("interest_rate_debt", scenario)[0]) if debt else 0.0
    tax = float(a.get("tax_rate", scenario)[0])
    return {"coe": coe, "ke": ke, "kd": kd, "tax": tax, "equity": equity, "debt": debt,
            "equity_weight": we, "debt_weight": wd, "wacc": we * ke + wd * kd * (1 - tax), "bridge": bridge}


def h1_fcff_actual(b: DataBundle, a: AssumptionSet, add_sbc: bool) -> float:
    """Reported H1 2026 operating FCFF removed from FY2026E, because cash is already at Q2."""
    v = lambda k: b.value(k, "H1_2026")
    delta_nwc = -sum(v(k) for k in ("cf_chg_ar", "cf_chg_inventory", "cf_chg_olv", "cf_chg_prepaid", "cf_chg_ap_accr", "cf_chg_defrev"))
    tax_rate = v("tax") / v("pretax") if v("pretax") else 0.0
    return v("ebit") * (1 - tax_rate) + v("da_total") + (v("sbc") if add_sbc else 0.0) - v("capex") - delta_nwc


def run_fcff(b: DataBundle, a: AssumptionSet, res: ModelResult, scenario: str = "base", valuation_date: date | None = None,
             wacc_override: float | None = None, g_override: float | None = None, checks: pd.DataFrame | None = None) -> FCFFResult:
    valuation_date = valuation_date or date.today()
    comp = wacc_components(b, a, res, scenario)
    wacc = float(wacc_override) if wacc_override is not None else comp["wacc"]
    g = float(g_override) if g_override is not None else float(a.p("terminal_growth"))
    out = FCFFResult(status="OK", wacc=wacc, g=g, coe=comp["coe"], debt_cost=comp["kd"], equity_weight=comp["equity_weight"],
                     debt_weight=comp["debt_weight"], valuation_date=valuation_date.isoformat())
    chk = run_checks(res, wacc, g) if checks is None else checks
    if checks is not None and not (chk["Check"] == "7. Terminal growth < cost of equity").any():
        chk = pd.concat([chk, run_checks(res, wacc, g).query("Year == 'Terminal'")], ignore_index=True)
    out.checks = chk
    out.failures = material_failures(chk)
    if out.failures:
        out.status = "FAILED"
        return out

    L, add_sbc = res.lines, bool(a.p("add_back_sbc"))
    h1 = h1_fcff_actual(b, a, add_sbc)
    rows, pv_sum = [], 0.0
    for i, (y, include, t, _) in enumerate(_periods(valuation_date, bool(a.p("mid_year")))):
        tax_on_ebit = float(a.get("tax_rate", scenario)[i]) * max(L["ebit"][i], 0.0)
        nopat, fcff = fcff_cash_flow(L["ebit"][i], float(a.get("tax_rate", scenario)[i]), L["da"][i], L["sbc"][i], L["capex"][i], L["delta_nwc"][i], add_sbc)
        flow = fcff - h1 if y == 2026 else fcff
        df_ = 1 / (1 + wacc) ** t
        pv = flow * df_ if include else 0.0
        pv_sum += pv
        rows.append({"Year": f"FY{y}E" + (" (H2 only)" if y == 2026 else ""), "EBIT": L["ebit"][i],
                     "Tax on EBIT": -tax_on_ebit,
                     "NOPAT": nopat, "D&A": L["da"][i], "SBC added back": L["sbc"][i] if add_sbc else 0.0,
                     "Capex": -L["capex"][i], "Increase in NWC": -L["delta_nwc"][i], "FCFF": fcff,
                     "Less H1-2026 actual (already in cash)": -h1 if y == 2026 else 0.0,
                     "FCFF valued": flow if include else 0.0, "Discount period (yrs)": t, "Discount factor": df_, "PV": pv})
    out.pv_table, out.pv_fcff = pd.DataFrame(rows), pv_sum

    j, tax_last = len(config.FORECAST_YEARS) - 1, float(a.get("tax_rate", scenario)[-1])
    ebit31 = L["ebit"][j] * (1 + g)
    da31 = L["da"][j] * (1 + g)
    sbc31 = L["sbc"][j] * (1 + g) if add_sbc else 0.0
    capex31 = da31 * float(a.p("terminal_capex_to_da"))
    dnwc31 = L["nwc"][j] * g
    nopat31, fcff31 = fcff_cash_flow(ebit31, tax_last, da31, sbc31, capex31, dnwc31, add_sbc)
    tax31 = tax_last * max(ebit31, 0.0)
    out.terminal_bridge = pd.DataFrame([
        {"Component": "EBIT (FY2030E x (1+g))", "FY2030E": L["ebit"][j], "FY2031": ebit31},
        {"Component": "- Tax on EBIT", "FY2030E": -tax_last * max(L["ebit"][j], 0.0), "FY2031": -tax31},
        {"Component": "= NOPAT", "FY2030E": L["ebit"][j] - tax_last * max(L["ebit"][j], 0.0), "FY2031": nopat31},
        {"Component": "+ D&A (grown at g)", "FY2030E": L["da"][j], "FY2031": da31},
        {"Component": "+ SBC (if added back)", "FY2030E": L["sbc"][j] if add_sbc else 0.0, "FY2031": sbc31},
        {"Component": "- Capex (terminal capex/D&A x D&A)", "FY2030E": -L["capex"][j], "FY2031": -capex31},
        {"Component": "- Increase in NWC (NWC x g)", "FY2030E": -L["delta_nwc"][j], "FY2031": -dnwc31},
        {"Component": "= FCFF", "FY2030E": out.pv_table.iloc[j]["FCFF"], "FY2031": fcff31},
    ])
    if not wacc > g:
        out.status, out.failures = "FAILED", ["Terminal growth must be below WACC"]
        return out
    tv = fcff31 / (wacc - g)
    t_tv = _periods(valuation_date, False)[j][3]
    pv_tv = tv / (1 + wacc) ** t_tv
    ev = pv_sum + pv_tv
    nonop, bridge = non_operating_assets(b, a, res, scenario), comp["bridge"]
    equity = ev + nonop["Total non-operating assets"] - sum(bridge.values())
    shares = diluted_shares(b, a)
    out.fcff_2031, out.terminal_value, out.pv_terminal, out.enterprise_value, out.equity_value, out.shares = fcff31, tv, pv_tv, ev, equity, shares
    out.value_per_share, out.tv_share_of_ev = equity / shares, pv_tv / ev if ev else np.nan
    out.equity_bridge = pd.DataFrame([
        {"Item": "PV of FCFF (H2 2026 - 2030)", "USD m": pv_sum}, {"Item": "PV of terminal value", "USD m": pv_tv},
        {"Item": "Enterprise value", "USD m": ev}, *[{"Item": k, "USD m": v} for k, v in nonop.items()],
        *[{"Item": k, "USD m": -v} for k, v in bridge.items()], {"Item": "Equity value", "USD m": equity},
        {"Item": "Diluted shares (M)", "USD m": shares}, {"Item": "Implied value per share ($)", "USD m": out.value_per_share},
    ])
    # This makes financing differences visible without forcing a residual to zero: FCFE uses
    # parent NI and actual financing flows, while FCFF is consolidated operating cash flow.
    rec_rows = []
    for i, y in enumerate(config.FORECAST_YEARS):
        after_tax_ie = L["interest_expense"][i] * (1 - float(a.get("tax_rate", scenario)[i]))
        after_tax_ii = L["interest_income"][i] * (1 - float(a.get("tax_rate", scenario)[i]))
        net_borrow = L["net_borrowing"][i]
        implied_fcfe = out.pv_table.iloc[i]["FCFF"] - after_tax_ie + after_tax_ii + net_borrow
        rec_rows.append({"Year": f"FY{y}E", "FCFF": out.pv_table.iloc[i]["FCFF"], "- After-tax interest expense": -after_tax_ie,
                         "+ After-tax interest income": after_tax_ii, "+ Net borrowing": net_borrow,
                         "Implied FCFE": implied_fcfe, "Model FCFE": L["fcfe"][i], "Residual": L["fcfe"][i] - implied_fcfe})
    out.reconciliation = pd.DataFrame(rec_rows)
    return out


def wacc_g_grid(b, a, res, scenario="base", valuation_date=None) -> pd.DataFrame:
    values_wacc, values_g = [x / 100 for x in range(8, 14)], [x / 100 for x in range(1, 5)]
    out = pd.DataFrame(index=[f"{x:.0%}" for x in values_wacc], columns=[f"{x:.0%}" for x in values_g], dtype=float)
    for wacc in values_wacc:
        for g in values_g:
            v = run_fcff(b, a, res, scenario, valuation_date, wacc_override=wacc, g_override=g)
            out.loc[f"{wacc:.0%}", f"{g:.0%}"] = v.value_per_share if v.status == "OK" else np.nan
    out.index.name = "WACC \\ terminal growth"
    return out


def reverse_wacc(b, a, res, scenario="base", valuation_date=None, target: float | None = None) -> float | None:
    target = float(b.market["price"]["value"] if target is None else target)
    lo, hi = float(a.p("terminal_growth")) + 0.0001, 0.60
    vlo, vhi = run_fcff(b, a, res, scenario, valuation_date, wacc_override=lo).value_per_share, run_fcff(b, a, res, scenario, valuation_date, wacc_override=hi).value_per_share
    if vlo is None or vhi is None or not (vlo >= target >= vhi):
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        vm = run_fcff(b, a, res, scenario, valuation_date, wacc_override=mid).value_per_share
        if vm is None:
            return None
        if vm > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
