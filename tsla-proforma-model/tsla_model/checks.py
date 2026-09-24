"""Validation block. Every check is evaluated for every forecast year.

Checks recompute results from the *presented* line items (not from the same variables the engine
used), so a wiring mistake in any schedule surfaces here.
"""
from __future__ import annotations

import pandas as pd

from . import config
from .statements import ModelResult

TOL = config.CHECK_TOL

CHECK_NAMES = [
    "1. Assets = liabilities + equity",
    "2. Cash-flow ending cash = balance-sheet cash",
    "3. Fixed-asset (PP&E) roll-forward ties",
    "4a. Debt roll-forward ties",
    "4b. Finance & operating lease roll-forwards tie",
    "4c. Revolver roll-forward ties",
    "5. Share-count roll-forward ties",
    "6. Cash >= minimum (after any revolver financing)",
    "7. Terminal growth < cost of equity",
    "Revenue build reconciles to total revenue",
]


def run_checks(res: ModelResult, ke: float | None = None, g: float | None = None) -> pd.DataFrame:
    L = res.lines
    rows = []

    def add(name, year, diff, passed, detail=""):
        rows.append({"Check": name, "Year": year, "Difference": diff, "Pass": bool(passed), "Material": True, "Detail": detail})

    for i, y in enumerate(config.FORECAST_YEARS):
        col = f"FY{y}E"
        bs = res.balance[col] if not res.balance.empty else None
        # 1 balance sheet - re-add every component (never trust stored totals)
        assets = sum(L[k][i] for k in ("cash", "ar", "inventory", "prepaid", "nfa", "rou", "digital", "dta", "other_nca"))
        le = sum(L[k][i] for k in ("ap", "accrued", "defrev", "debt", "fl", "ol", "revolver", "equity", "nci"))
        diff = assets - le
        if bs is not None:
            diff_presented = bs["TOTAL ASSETS"] - bs["TOTAL LIABILITIES & EQUITY"]
            diff = diff if abs(diff) > abs(diff_presented) else diff_presented
        add(CHECK_NAMES[0], y, diff, abs(diff) <= TOL)
        # 2 cash link: beginning cash + sum of every CF line item vs balance-sheet cash
        cf_sum = (L["ni_total"][i] + L["da"][i] + L["sbc"][i] - L["delta_nwc"][i]
                  - L["capex"][i] - L["strategic"][i]
                  + L["debt_issued"][i] - L["debt_repaid"][i] - L["fl_principal"][i] + L["revolver_draw"][i]
                  + L["option_proceeds"][i] - L["buybacks"][i] - L["nci_dist"][i])
        if not res.cashflow.empty:
            c = res.cashflow[col]
            cf_sum = c["Cash from operations"] + c["Cash from investing"] + c["Cash from financing"]
        diff = (L["cash_begin"][i] + cf_sum) - L["cash"][i]
        if bs is not None:
            diff = (L["cash_begin"][i] + cf_sum) - bs["Cash & short-term investments"]
        add(CHECK_NAMES[1], y, diff, abs(diff) <= TOL)
        # 3 PP&E
        diff = L["nfa_begin"][i] + L["capex"][i] + L["fl_additions"][i] - L["da"][i] - L["nfa"][i]
        add(CHECK_NAMES[2], y, diff, abs(diff) <= TOL)
        # 4 debt / leases / revolver
        diff = L["debt_begin"][i] + L["debt_issued"][i] - L["debt_repaid"][i] - L["debt"][i]
        add(CHECK_NAMES[3], y, diff, abs(diff) <= TOL)
        d_fl = L["fl_begin"][i] + L["fl_additions"][i] - L["fl_principal"][i] - L["fl"][i]
        d_ol = L["ol_begin"][i] + L["ol_additions"][i] - L["ol"][i]
        add(CHECK_NAMES[4], y, d_fl + d_ol, abs(d_fl) <= TOL and abs(d_ol) <= TOL)
        diff = L["revolver_begin"][i] + L["revolver_draw"][i] - L["revolver"][i]
        add(CHECK_NAMES[5], y, diff, abs(diff) <= TOL and L["revolver"][i] >= -TOL)
        # 5 shares
        diff = L["shares_begin"][i] + L["shares_issued"][i] - L["shares_repurchased"][i] - L["shares_end"][i]
        prev_end = L["shares_end"][i - 1] if i else L["shares_begin"][0]
        link = L["shares_begin"][i] - prev_end
        add(CHECK_NAMES[6], y, diff + link, abs(diff) <= 1e-6 and abs(link) <= 1e-6)
        # 6 minimum cash
        short = L["cash_shortfall"][i]
        add(CHECK_NAMES[7], y, -short, short <= TOL,
            f"cash {L['cash'][i]:,.0f} vs minimum {L['min_cash'][i]:,.0f}; revolver {L['revolver'][i]:,.0f}")
        # revenue reconciliation
        parts = (L["rev_auto_sales"][i] + L["rev_credits"][i] + L["rev_leasing"][i] + L["rev_services"][i]
                 + L["rev_autonomy"][i] + L["rev_energy"][i])
        add(CHECK_NAMES[9], y, parts - L["rev_total"][i], abs(parts - L["rev_total"][i]) <= TOL)

    if ke is not None and g is not None:
        add(CHECK_NAMES[8], "Terminal", g - ke, g < ke, f"g = {g:.2%}, cost of equity = {ke:.2%}")
    return pd.DataFrame(rows)


def material_failures(checks: pd.DataFrame) -> list[str]:
    bad = checks[(~checks["Pass"]) & checks["Material"]]
    return [f"{r.Check} ({r.Year}): difference {r.Difference:,.2f} {r.Detail}".strip() for r in bad.itertuples()]


def summary(checks: pd.DataFrame) -> pd.DataFrame:
    return (checks.groupby("Check", sort=False)["Pass"].agg(["all", "count"])
            .rename(columns={"all": "All years pass", "count": "Years tested"}).reset_index())
