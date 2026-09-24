"""Linked three-statement forecast engine (FY2026E-FY2030E, base = FY2025A balance sheet).

Mechanics (no plugs):
  Income statement  driver-based revenue by segment -> cash gross profit (margins ex-D&A)
                    -> cash opex -> EBITDA -> D&A (from fixed-asset roll-forward) -> EBIT
                    -> interest on *beginning* balances (no circularity) -> tax -> NI
  Balance sheet     every line is either rolled forward from a schedule or driven by a
                    working-capital ratio; cash comes only from the cash-flow statement
  Cash flow         CFO/CFI/CFF built from the IS and balance-sheet changes; a revolver is
                    drawn only if cash would fall below the minimum-cash rule
Non-recurring items (restructuring, FX/digital-asset/SpaceX fair-value gains, valuation-
allowance releases) are excluded from the forecast.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config
from .assumptions import AssumptionSet
from .data_ingestion import DataBundle

YEARS = config.FORECAST_YEARS
FCOLS = [f"FY{y}E" for y in YEARS]
HCOLS = ["FY2023A", "FY2024A", "FY2025A"]


@dataclass
class ModelResult:
    scenario: str
    income: pd.DataFrame
    balance: pd.DataFrame
    cashflow: pd.DataFrame
    schedules: dict
    fcfe: pd.DataFrame
    lines: dict            # raw per-year arrays (forecast only), keyed by line id
    base: dict             # FY2025A opening balances
    h1_actual: dict        # H1 2026 actuals used for the valuation stub
    drivers: dict = field(default_factory=dict)   # driver arrays used for this run
    add_back_sbc: bool = True
    notes: list = field(default_factory=list)


def opening_balances(b: DataBundle, period: str = "FY2025") -> dict:
    v = lambda k: b.value(k, period)
    return {
        "cash": v("cash") + v("st_investments"),
        "ar": v("ar"), "inventory": v("inventory"), "prepaid": v("prepaid"),
        "nfa": v("ppe") + v("olv") + v("energy_systems"),
        "rou": v("rou"), "digital": v("digital_assets"), "dta": v("dta"), "other_nca": v("other_nca"),
        "ap": v("ap"),
        "accrued": v("accrued_current") + v("other_ltl") - v("op_lease_liab"),
        "defrev": v("deferred_rev_current") + v("deferred_rev_noncurrent"),
        "debt": v("debt_fl_current") + v("debt_fl_noncurrent") - v("finance_lease_liab"),
        "fl": v("finance_lease_liab"), "ol": v("op_lease_liab"), "revolver": 0.0,
        "equity": v("equity_parent"), "nci": v("nci") + v("redeemable_nci"),
        "services_rev": b.value("rev_services", "FY2025" if period.startswith("FY") else period),
    }


def _bs_totals(d: dict) -> tuple[float, float, float]:
    assets = sum(d[k] for k in ("cash", "ar", "inventory", "prepaid", "nfa", "rou", "digital", "dta", "other_nca"))
    liab = sum(d[k] for k in ("ap", "accrued", "defrev", "debt", "fl", "ol", "revolver"))
    eq = d["equity"] + d["nci"]
    return assets, liab, eq


def h1_2026_actuals(b: DataBundle) -> dict:
    """H1 2026 reported flows used to strip the already-elapsed half-year from FY2026E."""
    v = lambda k: b.value(k, "H1_2026")
    net_borrow = v("debt_issued") - v("debt_repaid") - v("fl_principal")
    pretax = v("pretax")
    return {
        "cfo": v("cfo"), "capex": v("capex"), "net_borrowing": net_borrow, "ni_nci": v("ni_nci"),
        "sbc": v("sbc"), "interest_income": v("interest_income"), "tax_rate": v("tax") / pretax if pretax else 0.0,
        "ni_parent": v("ni_parent"), "da": v("da_total"),
    }


def run_model(b: DataBundle, a: AssumptionSet, scenario: str = "base", build_frames: bool = True) -> ModelResult:
    g = lambda k: a.get(k, scenario)
    o = opening_balances(b)
    n = len(YEARS)
    L = {k: np.zeros(n) for k in [
        "rev_auto_sales", "rev_credits", "rev_leasing", "rev_services", "rev_autonomy", "rev_energy", "rev_total",
        "cc_auto_sales", "cc_leasing", "cc_services", "cc_autonomy", "cc_energy", "cash_cogs", "cash_gp",
        "rd", "sga", "ebitda", "da", "da_cogs", "gaap_gp", "ebit", "interest_income", "interest_expense", "other_income",
        "pretax", "tax", "ni_total", "ni_nci", "ni_parent", "sbc",
        "cash", "ar", "inventory", "prepaid", "nfa", "rou", "digital", "dta", "other_nca",
        "ap", "accrued", "defrev", "debt", "fl", "ol", "revolver", "equity", "nci",
        "assets", "liabilities", "total_equity", "nwc", "delta_nwc",
        "cfo", "capex", "strategic", "cfi", "debt_issued", "debt_repaid", "fl_principal", "fl_additions",
        "revolver_draw", "option_proceeds", "buybacks", "nci_dist", "cff", "net_change_cash", "min_cash", "cash_shortfall",
        "shares_begin", "shares_issued", "shares_repurchased", "shares_end", "shares_avg", "eps",
        "nfa_begin", "debt_begin", "fl_begin", "ol_begin", "ol_additions", "revolver_begin", "cash_begin",
        "equity_begin", "net_borrowing", "fcfe", "after_tax_interest_income", "fcfe_operating",
    ]}
    prev = dict(o)
    prev_nwc = o["ar"] + o["inventory"] + o["prepaid"] - o["ap"] - o["accrued"] - o["defrev"]
    services_prev = o["services_rev"]
    price = b.market["price"]["value"]
    shares = float(b.value("shares_diluted_q2_2026", "H1_2026"))
    rev_cap = float(a.p("revolver_capacity"))
    rev_rate = float(a.p("revolver_rate"))

    for i in range(n):
        x = {k: g(k)[i] for k in a.drivers}
        # ---------------- revenue build ----------------
        auto_sales = x["deliveries_3y"] * x["asp_3y"] + x["deliveries_other"] * x["asp_other"]   # k units * $k = $M
        services = services_prev * (1 + x["services_growth"])
        energy = x["storage_gwh"] * x["energy_rev_per_gwh"]
        rev = auto_sales + x["reg_credits"] + x["auto_leasing_rev"] + services + x["autonomy_rev"] + energy
        # ---------------- cash cost of revenues (ex-D&A) ----------------
        cc = {
            "cc_auto_sales": auto_sales * (1 - x["gm_auto_sales"]),
            "cc_leasing": x["auto_leasing_rev"] * (1 - x["gm_leasing"]),
            "cc_services": services * (1 - x["gm_services"]),
            "cc_autonomy": x["autonomy_rev"] * (1 - x["gm_autonomy"]),
            "cc_energy": energy * (1 - x["gm_energy"]),
        }   # regulatory credits have negligible cost (10-K Note 2)
        cash_cogs = sum(cc.values())
        cash_gp = rev - cash_cogs
        rd, sga = rev * x["rd_pct"], rev * x["sga_pct"]
        ebitda = cash_gp - rd - sga
        da = x["da_rate"] * prev["nfa"]
        da_cogs = da * x["da_cogs_share"]
        ebit = ebitda - da
        ii = x["interest_yield_cash"] * prev["cash"]
        ie = x["interest_rate_debt"] * (prev["debt"] + prev["fl"]) + rev_rate * prev["revolver"]
        pretax = ebit + ii - ie
        tax = x["tax_rate"] * max(pretax, 0.0)
        ni_total = pretax - tax
        ni_nci = x["nci_income"]
        ni_parent = ni_total - ni_nci
        sbc = rev * x["sbc_pct"]
        gaap_cogs = cash_cogs + da_cogs
        # ---------------- working capital (end of year) ----------------
        ar = rev * x["dso"] / 365
        inv = gaap_cogs * x["dio"] / 365
        ap = gaap_cogs * x["dpo"] / 365
        prepaid = rev * x["prepaid_pct"]
        accrued = rev * x["accrued_pct"]
        defrev = rev * x["deferred_rev_pct"]
        nwc = ar + inv + prepaid - ap - accrued - defrev
        d_nwc = nwc - prev_nwc
        # ---------------- fixed assets, leases, debt ----------------
        capex, fl_add = x["capex"], x["fl_additions"]
        nfa = prev["nfa"] + capex + fl_add - da
        fl_pay = min(x["fl_principal"], prev["fl"] + fl_add)
        fl = prev["fl"] + fl_add - fl_pay
        ol = prev["ol"] * (1 + x["op_lease_growth"])
        rou = prev["rou"] + (ol - prev["ol"])
        repaid = min(x["debt_repaid"], prev["debt"] + x["debt_issued"])
        debt = prev["debt"] + x["debt_issued"] - repaid
        other_nca = prev["other_nca"] + x["strategic_investment"]
        # ---------------- cash flow ----------------
        cfo = ni_total + da + sbc - d_nwc
        cfi = -capex - x["strategic_investment"]
        cff_pre = x["debt_issued"] - repaid - fl_pay + x["option_proceeds"] - x["buybacks"] - x["nci_distributions"]
        cash_pre = prev["cash"] + cfo + cfi + cff_pre
        min_cash = x["min_cash_pct"] * rev
        if cash_pre < min_cash:
            draw = min(min_cash - cash_pre, max(rev_cap - prev["revolver"], 0.0))
        elif prev["revolver"] > 0:
            draw = -min(prev["revolver"], cash_pre - min_cash)
        else:
            draw = 0.0
        cff = cff_pre + draw
        cash = prev["cash"] + cfo + cfi + cff
        revolver = prev["revolver"] + draw
        equity = prev["equity"] + ni_parent + sbc + x["option_proceeds"] - x["buybacks"]
        nci = prev["nci"] + ni_nci - x["nci_distributions"]
        # ---------------- shares (diluted, millions) ----------------
        sh_issued = shares * x["share_issuance_pct"]
        sh_rep = x["buybacks"] / price if price > 0 else 0.0
        sh_end = shares + sh_issued - sh_rep
        # ---------------- FCFE ----------------
        net_borrow = x["debt_issued"] - repaid - fl_pay + draw
        fcfe = ni_parent + da + (sbc if a.p("add_back_sbc") else 0.0) - capex - d_nwc + net_borrow
        at_ii = ii * (1 - x["tax_rate"])

        cur = dict(cash=cash, ar=ar, inventory=inv, prepaid=prepaid, nfa=nfa, rou=rou, digital=prev["digital"],
                   dta=prev["dta"], other_nca=other_nca, ap=ap, accrued=accrued, defrev=defrev, debt=debt, fl=fl,
                   ol=ol, revolver=revolver, equity=equity, nci=nci)
        assets, liab, eq = _bs_totals(cur)
        rec = dict(
            rev_auto_sales=auto_sales, rev_credits=x["reg_credits"], rev_leasing=x["auto_leasing_rev"],
            rev_services=services, rev_autonomy=x["autonomy_rev"], rev_energy=energy, rev_total=rev,
            cash_cogs=cash_cogs, cash_gp=cash_gp, rd=rd, sga=sga, ebitda=ebitda, da=da, da_cogs=da_cogs,
            gaap_gp=cash_gp - da_cogs, ebit=ebit, interest_income=ii, interest_expense=ie, other_income=0.0,
            pretax=pretax, tax=tax, ni_total=ni_total, ni_nci=ni_nci, ni_parent=ni_parent, sbc=sbc,
            assets=assets, liabilities=liab, total_equity=eq, nwc=nwc, delta_nwc=d_nwc,
            cfo=cfo, capex=capex, strategic=x["strategic_investment"], cfi=cfi, debt_issued=x["debt_issued"],
            debt_repaid=repaid, fl_principal=fl_pay, fl_additions=fl_add, revolver_draw=draw,
            option_proceeds=x["option_proceeds"], buybacks=x["buybacks"], nci_dist=x["nci_distributions"], cff=cff,
            net_change_cash=cfo + cfi + cff, min_cash=min_cash, cash_shortfall=max(min_cash - cash, 0.0),
            shares_begin=shares, shares_issued=sh_issued, shares_repurchased=sh_rep, shares_end=sh_end,
            shares_avg=(shares + sh_end) / 2, eps=ni_parent / ((shares + sh_end) / 2),
            nfa_begin=prev["nfa"], debt_begin=prev["debt"], fl_begin=prev["fl"], ol_begin=prev["ol"],
            ol_additions=ol - prev["ol"], revolver_begin=prev["revolver"], cash_begin=prev["cash"],
            equity_begin=prev["equity"], net_borrowing=net_borrow, fcfe=fcfe,
            after_tax_interest_income=at_ii, fcfe_operating=fcfe - at_ii, **cc, **cur,
        )
        for k, v in rec.items():
            L[k][i] = v
        prev = cur
        prev_nwc = nwc
        services_prev = services
        shares = sh_end

    res = ModelResult(scenario=scenario, income=pd.DataFrame(), balance=pd.DataFrame(), cashflow=pd.DataFrame(),
                      schedules={}, fcfe=pd.DataFrame(), lines=L, base=o, h1_actual=h1_2026_actuals(b),
                      drivers={k: g(k) for k in a.drivers}, add_back_sbc=bool(a.p("add_back_sbc")))
    if build_frames:
        _build_frames(res, b)
    return res


# --------------------------------------------------------------------------------------------
# Presentation frames (history + forecast)
# --------------------------------------------------------------------------------------------
def _hist_is(b: DataBundle) -> dict:
    out = {}
    for p, col in zip(["FY2023", "FY2024", "FY2025"], HCOLS):
        v = lambda k: b.value(k, p)
        da_cogs = v("da_cogs_auto") + v("da_cogs_energy")
        da_opex = v("da_total") - da_cogs
        opex = v("rd") + v("sga")
        out[col] = {
            "Automotive sales": v("rev_auto_sales"), "Regulatory credits": v("rev_reg_credits"),
            "Automotive leasing": v("rev_auto_leasing"), "Services & other": v("rev_services"),
            "Robotaxi / autonomy (isolated)": 0.0, "Energy generation & storage": v("rev_energy"),
            "Total revenue": v("rev_total"),
            "Cash cost of revenues (ex-D&A)": v("cogs_total") - da_cogs,
            "Cash gross profit": v("gross_profit") + da_cogs,
            "R&D (ex-D&A)": v("rd") - da_opex * v("rd") / opex,
            "SG&A (ex-D&A)": v("sga") - da_opex * v("sga") / opex,
            "Restructuring & other (non-recurring)": v("restructuring"),
            "EBITDA": v("ebit") + v("da_total"),
            "D&A": v("da_total"),
            "EBIT": v("ebit"),
            "Interest income": v("interest_income"), "Interest expense": -v("interest_expense"),
            "Other income, net (non-recurring)": v("other_income"),
            "Pre-tax income": v("pretax"), "Income tax": -v("tax"), "Net income (incl. NCI)": v("net_income_total"),
            "NCI share": -v("ni_nci"), "Net income to common": v("ni_parent"),
            "Memo: GAAP gross profit": v("gross_profit"), "Memo: GAAP gross margin": v("gross_profit") / v("rev_total"),
            "Memo: EBITDA margin": (v("ebit") + v("da_total")) / v("rev_total"),
            "Memo: SBC (non-cash, inside costs)": v("sbc"),
            "Memo: diluted shares (M)": v("shares_diluted"), "Memo: diluted EPS ($)": v("ni_parent") / v("shares_diluted"),
        }
    return out


def _build_frames(res: ModelResult, b: DataBundle) -> None:
    L = res.lines
    f = {}
    for i, col in enumerate(FCOLS):
        f[col] = {
            "Automotive sales": L["rev_auto_sales"][i], "Regulatory credits": L["rev_credits"][i],
            "Automotive leasing": L["rev_leasing"][i], "Services & other": L["rev_services"][i],
            "Robotaxi / autonomy (isolated)": L["rev_autonomy"][i], "Energy generation & storage": L["rev_energy"][i],
            "Total revenue": L["rev_total"][i],
            "Cash cost of revenues (ex-D&A)": L["cash_cogs"][i], "Cash gross profit": L["cash_gp"][i],
            "R&D (ex-D&A)": L["rd"][i], "SG&A (ex-D&A)": L["sga"][i], "Restructuring & other (non-recurring)": 0.0,
            "EBITDA": L["ebitda"][i], "D&A": L["da"][i], "EBIT": L["ebit"][i],
            "Interest income": L["interest_income"][i], "Interest expense": -L["interest_expense"][i],
            "Other income, net (non-recurring)": 0.0,
            "Pre-tax income": L["pretax"][i], "Income tax": -L["tax"][i], "Net income (incl. NCI)": L["ni_total"][i],
            "NCI share": -L["ni_nci"][i], "Net income to common": L["ni_parent"][i],
            "Memo: GAAP gross profit": L["gaap_gp"][i], "Memo: GAAP gross margin": L["gaap_gp"][i] / L["rev_total"][i],
            "Memo: EBITDA margin": L["ebitda"][i] / L["rev_total"][i],
            "Memo: SBC (non-cash, inside costs)": L["sbc"][i],
            "Memo: diluted shares (M)": L["shares_avg"][i], "Memo: diluted EPS ($)": L["eps"][i],
        }
    res.income = pd.DataFrame({**_hist_is(b), **f})

    # ---------------- balance sheet ----------------
    bs_rows = [("Cash & short-term investments", "cash"), ("Accounts receivable", "ar"), ("Inventory", "inventory"),
               ("Prepaid & other current assets", "prepaid"), ("Net fixed assets (PP&E + lease vehicles + energy systems)", "nfa"),
               ("Operating lease ROU assets", "rou"), ("Digital assets", "digital"), ("Deferred tax assets", "dta"),
               ("Other non-current assets", "other_nca"), ("TOTAL ASSETS", "assets"),
               ("Accounts payable", "ap"), ("Accrued & other liabilities (ex-leases)", "accrued"),
               ("Deferred revenue", "defrev"), ("Debt (ex-finance leases)", "debt"), ("Finance lease liabilities", "fl"),
               ("Operating lease liabilities", "ol"), ("Revolver", "revolver"), ("TOTAL LIABILITIES", "liabilities"),
               ("Stockholders' equity", "equity"), ("Noncontrolling interests (incl. redeemable)", "nci"),
               ("TOTAL EQUITY", "total_equity"), ("TOTAL LIABILITIES & EQUITY", "le")]
    hist = {}
    for p, col in zip(["FY2023", "FY2024", "FY2025"], HCOLS):
        ob = opening_balances(b, p)
        a_, l_, e_ = _bs_totals(ob)
        ob.update(assets=a_, liabilities=l_, total_equity=e_, le=l_ + e_)
        hist[col] = {lab: ob[k] for lab, k in bs_rows}
    fc = {}
    for i, col in enumerate(FCOLS):
        d = {k: L[k][i] for k in L}
        d["le"] = d["liabilities"] + d["total_equity"]
        fc[col] = {lab: d[k] for lab, k in bs_rows}
    res.balance = pd.DataFrame({**hist, **fc})

    # ---------------- cash flow ----------------
    cf_rows = [("Net income (incl. NCI)", lambda i: L["ni_total"][i]), ("D&A", lambda i: L["da"][i]),
               ("Stock-based compensation", lambda i: L["sbc"][i]),
               ("Change in net working capital", lambda i: -L["delta_nwc"][i]),
               ("Cash from operations", lambda i: L["cfo"][i]),
               ("Capital expenditures", lambda i: -L["capex"][i]),
               ("Strategic investments", lambda i: -L["strategic"][i]),
               ("Cash from investing", lambda i: L["cfi"][i]),
               ("Debt issued", lambda i: L["debt_issued"][i]), ("Debt repaid", lambda i: -L["debt_repaid"][i]),
               ("Finance lease principal", lambda i: -L["fl_principal"][i]),
               ("Revolver draw / (repayment)", lambda i: L["revolver_draw"][i]),
               ("Option exercises / ESPP", lambda i: L["option_proceeds"][i]),
               ("Share repurchases", lambda i: -L["buybacks"][i]),
               ("Distributions to NCI", lambda i: -L["nci_dist"][i]),
               ("Cash from financing", lambda i: L["cff"][i]),
               ("Net change in cash", lambda i: L["net_change_cash"][i]),
               ("Beginning cash & ST investments", lambda i: L["cash_begin"][i]),
               ("Ending cash & ST investments", lambda i: L["cash_begin"][i] + L["net_change_cash"][i]),
               ("Memo: minimum cash requirement", lambda i: L["min_cash"][i])]
    hist_cf = {}
    for p, col in zip(["FY2023", "FY2024", "FY2025"], HCOLS):
        v = lambda k: b.value(k, p)
        dnwc = sum(v(k) for k in ("cf_chg_ar", "cf_chg_inventory", "cf_chg_olv", "cf_chg_prepaid", "cf_chg_ap_accr", "cf_chg_defrev"))
        hist_cf[col] = {"Net income (incl. NCI)": v("net_income_total"), "D&A": v("da_total"),
                        "Stock-based compensation": v("sbc"), "Change in net working capital": dnwc,
                        "Cash from operations": v("cfo"), "Capital expenditures": -v("capex"),
                        "Strategic investments": -v("strategic_investment"), "Cash from investing": v("cfi"),
                        "Debt issued": v("debt_issued"), "Debt repaid": -v("debt_repaid"),
                        "Finance lease principal": -v("fl_principal"), "Revolver draw / (repayment)": 0.0,
                        "Option exercises / ESPP": v("option_proceeds"), "Share repurchases": -v("buybacks"),
                        "Distributions to NCI": -v("nci_distributions"), "Cash from financing": v("cff")}
    fcf = {col: {lab: fn(i) for lab, fn in cf_rows} for i, col in enumerate(FCOLS)}
    res.cashflow = pd.DataFrame({**hist_cf, **fcf})
    res.notes.append("Historical CFO includes other non-cash items (FX, deferred tax, write-downs, fair-value gains) not shown line-by-line; "
                     "historical CFI includes net purchases of short-term investments, which the forecast treats as part of cash.")

    # ---------------- schedules ----------------
    def sched(rows):
        return pd.DataFrame({col: {lab: fn(i) for lab, fn in rows} for i, col in enumerate(FCOLS)})

    res.schedules["Revenue build"] = sched([
        ("Model 3/Y deliveries (k)", lambda i: res.drivers["deliveries_3y"][i]),
        ("Other models deliveries (k)", lambda i: res.drivers["deliveries_other"][i]),
        ("Automotive sales ($M)", lambda i: L["rev_auto_sales"][i]),
        ("Regulatory credits ($M)", lambda i: L["rev_credits"][i]),
        ("Automotive leasing ($M)", lambda i: L["rev_leasing"][i]),
        ("Services & other ($M)", lambda i: L["rev_services"][i]),
        ("Robotaxi / autonomy ($M)", lambda i: L["rev_autonomy"][i]),
        ("Storage deployed (GWh)", lambda i: res.drivers["storage_gwh"][i]),
        ("Energy revenue ($M)", lambda i: L["rev_energy"][i]),
        ("Total revenue ($M)", lambda i: L["rev_total"][i]),
        ("Revenue growth (%)", lambda i: L["rev_total"][i] / (L["rev_total"][i - 1] if i else b.value("rev_total", "FY2025")) - 1),
    ])
    res.schedules["Fixed assets roll-forward"] = sched([
        ("Beginning net fixed assets", lambda i: L["nfa_begin"][i]), ("+ Capex", lambda i: L["capex"][i]),
        ("+ New finance leases", lambda i: L["fl_additions"][i]), ("- D&A", lambda i: -L["da"][i]),
        ("Ending net fixed assets", lambda i: L["nfa"][i])])
    res.schedules["Debt & lease roll-forward"] = sched([
        ("Debt: beginning", lambda i: L["debt_begin"][i]), ("Debt: issued", lambda i: L["debt_issued"][i]),
        ("Debt: repaid", lambda i: -L["debt_repaid"][i]), ("Debt: ending", lambda i: L["debt"][i]),
        ("Finance leases: beginning", lambda i: L["fl_begin"][i]), ("Finance leases: additions", lambda i: L["fl_additions"][i]),
        ("Finance leases: principal paid", lambda i: -L["fl_principal"][i]), ("Finance leases: ending", lambda i: L["fl"][i]),
        ("Operating leases: beginning", lambda i: L["ol_begin"][i]), ("Operating leases: net additions", lambda i: L["ol_additions"][i]),
        ("Operating leases: ending", lambda i: L["ol"][i]),
        ("Revolver: beginning", lambda i: L["revolver_begin"][i]), ("Revolver: draw/(repay)", lambda i: L["revolver_draw"][i]),
        ("Revolver: ending", lambda i: L["revolver"][i]),
        ("Interest expense", lambda i: L["interest_expense"][i])])
    res.schedules["Equity & share roll-forward"] = sched([
        ("Equity: beginning", lambda i: L["equity_begin"][i]), ("+ Net income to common", lambda i: L["ni_parent"][i]),
        ("+ SBC", lambda i: L["sbc"][i]), ("+ Option proceeds", lambda i: L["option_proceeds"][i]),
        ("- Buybacks", lambda i: -L["buybacks"][i]), ("Equity: ending", lambda i: L["equity"][i]),
        ("Diluted shares: beginning (M)", lambda i: L["shares_begin"][i]), ("+ Issued (M)", lambda i: L["shares_issued"][i]),
        ("- Repurchased (M)", lambda i: -L["shares_repurchased"][i]), ("Diluted shares: ending (M)", lambda i: L["shares_end"][i])])
    res.schedules["Working capital"] = sched([
        ("Accounts receivable", lambda i: L["ar"][i]), ("Inventory", lambda i: L["inventory"][i]),
        ("Prepaid & other", lambda i: L["prepaid"][i]), ("Accounts payable", lambda i: -L["ap"][i]),
        ("Accrued & other", lambda i: -L["accrued"][i]), ("Deferred revenue", lambda i: -L["defrev"][i]),
        ("Net working capital", lambda i: L["nwc"][i]), ("Increase in NWC (cash outflow)", lambda i: L["delta_nwc"][i])])
    res.fcfe = sched([
        ("Net income to common", lambda i: L["ni_parent"][i]), ("+ D&A", lambda i: L["da"][i]),
        ("+ SBC (if added back)", lambda i: L["sbc"][i] if res.add_back_sbc else 0.0),
        ("- Capex", lambda i: -L["capex"][i]), ("- Increase in NWC", lambda i: -L["delta_nwc"][i]),
        ("+ Net borrowing (debt, leases, revolver)", lambda i: L["net_borrowing"][i]),
        ("FCFE", lambda i: L["fcfe"][i]),
        ("- After-tax interest income (cash valued separately)", lambda i: -L["after_tax_interest_income"][i]),
        ("Operating FCFE (valued)", lambda i: L["fcfe_operating"][i])])
