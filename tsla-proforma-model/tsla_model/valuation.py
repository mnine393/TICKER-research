"""Five-year FCFE DCF with a Gordon-growth terminal value.

Value per share = [ PV(operating FCFE, H2-2026 to 2030) + PV(terminal value at end-2030)
                    + excess cash & investments + other non-operating assets ] / diluted shares

* Operating FCFE = FCFE - after-tax interest income. Interest earned on the cash pile is removed
  because cash is added separately at its balance-sheet value (avoids double counting).
* FY2026E FCFE is reduced by the H1 2026 actual FCFE already reflected in the 30-Jun-2026 balance sheet.
* Terminal value uses an explicit 2031 FCFE bridge (each component grown / normalised).
* The valuation refuses to produce a value if any material integrity check fails.
"""
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


class ValuationError(ValueError):
    pass


# ---------------------------------------------------------------------------------------------
# Cost of equity
# ---------------------------------------------------------------------------------------------
def capm(rf: float, beta: float, erp: float) -> float:
    return rf + beta * erp


def unlever(beta_l: float, de: float, tax: float) -> float:
    return beta_l / (1 + (1 - tax) * de)


def relever(beta_u: float, de: float, tax: float) -> float:
    return beta_u * (1 + (1 - tax) * de)


def tesla_de_ratio(res: ModelResult, price: float, shares: float) -> float:
    """Average forecast (debt + finance leases + revolver) / current market value of equity."""
    L = res.lines
    debt = np.mean(L["debt"] + L["fl"] + L["revolver"])
    return float(debt / (price * shares))


def bottom_up_beta(peers: list[dict], tesla_de: float, tax_m: float, weight_auto: float) -> dict:
    rows = []
    for p in peers:
        if not p.get("include", True):
            continue
        de = p["debt"] / p["market_cap"]
        rows.append({"Ticker": p["ticker"], "Name": p["name"], "Group": p["group"], "Levered beta": p["beta"],
                     "Debt ($M)": p["debt"], "Market cap ($M)": p["market_cap"], "D/E": de,
                     "Tax rate": p["tax_rate"], "Unlevered beta": unlever(p["beta"], de, p["tax_rate"]),
                     "Debt source": p["debt_type"], "Notes": p["notes"]})
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValuationError("No peers selected for bottom-up beta")
    is_energy = df["Group"].str.contains("Energy")
    auto_bu = df.loc[~is_energy, "Unlevered beta"].mean()
    energy_bu = df.loc[is_energy, "Unlevered beta"].mean()
    if np.isnan(energy_bu):
        energy_bu, weight_auto = auto_bu, 1.0
    if np.isnan(auto_bu):
        auto_bu, weight_auto = energy_bu, 0.0
    bu = weight_auto * auto_bu + (1 - weight_auto) * energy_bu
    return {"peers": df, "auto_unlevered": auto_bu, "energy_unlevered": energy_bu,
            "simple_average_unlevered": df["Unlevered beta"].mean(), "weighted_unlevered": bu,
            "tesla_de": tesla_de, "relevered": relever(bu, tesla_de, tax_m)}


def cost_of_equity(b: DataBundle, a: AssumptionSet, res: ModelResult, method: str | None = None) -> dict:
    rf, erp = float(a.p("risk_free")), float(a.p("erp"))
    price = b.market["price"]["value"]
    shares = diluted_shares(b, a)
    de = tesla_de_ratio(res, price, shares)
    bu = bottom_up_beta(b.market["peers"], de, float(a.p("tax_rate_beta")), float(a.p("peer_weight_auto")))
    obs = float(a.p("beta_observed"))
    method = method or a.p("beta_method")
    beta = {"bottom-up": bu["relevered"], "observed": obs, "average": 0.5 * (bu["relevered"] + obs)}[method]
    return {"rf": rf, "erp": erp, "beta": beta, "method": method, "beta_observed": obs,
            "beta_bottom_up": bu["relevered"], "bottom_up": bu, "ke": capm(rf, beta, erp),
            "ke_observed": capm(rf, obs, erp), "ke_bottom_up": capm(rf, bu["relevered"], erp)}


def diluted_shares(b: DataBundle, a: AssumptionSet) -> float:
    s = float(b.value("shares_diluted_q2_2026", "H1_2026"))
    if a.p("include_ceo_award_shares"):
        s += float(b.obligation("ceo_2025_award_unearned_shares"))
    return s


# ---------------------------------------------------------------------------------------------
# DCF
# ---------------------------------------------------------------------------------------------
@dataclass
class ValuationResult:
    status: str                         # "OK" or "FAILED"
    failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    value_per_share: float | None = None
    equity_value: float | None = None
    price: float = 0.0
    price_date: str = ""
    upside: float | None = None
    ke: float = 0.0
    g: float = 0.0
    coe: dict = field(default_factory=dict)
    pv_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    terminal_bridge: pd.DataFrame = field(default_factory=pd.DataFrame)
    equity_bridge: pd.DataFrame = field(default_factory=pd.DataFrame)
    fcfe_2031: float = 0.0
    terminal_value: float = 0.0
    pv_terminal: float = 0.0
    pv_fcfe: float = 0.0
    non_operating: float = 0.0
    shares: float = 0.0
    tv_share_of_dcf: float = 0.0
    tv_share_of_equity: float = 0.0
    checks: pd.DataFrame = field(default_factory=pd.DataFrame)
    valuation_date: str = ""


def _periods(valuation_date: date, mid_year: bool):
    """Discount time (years) for each forecast-year cash flow and the terminal value."""
    out = []
    for y in config.FORECAST_YEARS:
        start = date(y, 7, 1) if y == 2026 else date(y, 1, 1)   # H1 2026 is already in the Q2 balance sheet
        end = date(y, 12, 31)
        include = end > valuation_date
        start = max(start, valuation_date)
        t_end = max((end - valuation_date).days / 365.25, 0.0)
        t_mid = max(((start - valuation_date).days + (end - start).days / 2) / 365.25, 0.0)
        out.append((y, include, t_mid if mid_year else t_end, t_end))
    return out


def non_operating_assets(b: DataBundle, a: AssumptionSet, res: ModelResult, scenario: str) -> dict:
    cash_q2 = b.value("cash", "Q2_2026") + b.value("st_investments", "Q2_2026")
    min_cash = float(a.get("min_cash_pct", scenario)[0]) * res.lines["rev_total"][0]
    excess = max(cash_q2 - min_cash, 0.0)
    digital = b.value("digital_assets", "Q2_2026")
    spacex = float(b.obligation("spacex_investment_carrying"))
    return {"Cash & ST investments (30-Jun-2026)": cash_q2, "Less: minimum operating cash": -min(min_cash, cash_q2),
            "Excess cash": excess, "Digital assets (30-Jun-2026)": digital,
            "SpaceX equity investment (carrying value)": spacex, "Total non-operating assets": excess + digital + spacex}


def run_valuation(b: DataBundle, a: AssumptionSet, res: ModelResult, scenario: str = "base",
                  valuation_date: date | None = None, ke_override: float | None = None,
                  g_override: float | None = None, beta_method: str | None = None,
                  checks: pd.DataFrame | None = None) -> ValuationResult:
    valuation_date = valuation_date or date.today()
    coe = cost_of_equity(b, a, res, beta_method)
    ke = float(ke_override) if ke_override is not None else coe["ke"]
    g = float(g_override) if g_override is not None else float(a.p("terminal_growth"))
    price = float(b.market["price"]["value"])
    out = ValuationResult(status="OK", ke=ke, g=g, coe=coe, price=price, price_date=b.market["price"]["as_of"],
                          valuation_date=valuation_date.isoformat())

    chk = run_checks(res, ke, g) if checks is None else checks
    if checks is not None and not (chk["Check"] == "7. Terminal growth < cost of equity").any():
        chk = pd.concat([chk, run_checks(res, ke, g).query("Year == 'Terminal'")], ignore_index=True)
    out.checks = chk
    fails = material_failures(chk)
    if fails:
        out.status, out.failures = "FAILED", fails
        return out

    L = res.lines
    add_sbc = bool(a.p("add_back_sbc"))
    h1 = res.h1_actual
    # H1 2026 actual FCFE on the same definition (CFO already includes NCI income and all non-cash items)
    h1_fcfe = h1["cfo"] - h1["ni_nci"] - (0.0 if add_sbc else h1["sbc"]) - h1["capex"] + h1["net_borrowing"]
    h1_op = h1_fcfe - h1["interest_income"] * (1 - h1["tax_rate"])

    rows, pv_sum = [], 0.0
    for i, (y, include, t, t_end) in enumerate(_periods(valuation_date, bool(a.p("mid_year")))):
        fc = L["fcfe_operating"][i]
        flow = fc - h1_op if y == 2026 else fc
        df_ = 1 / (1 + ke) ** t
        pv = flow * df_ if include else 0.0
        pv_sum += pv
        rows.append({"Year": f"FY{y}E" + (" (H2 only)" if y == 2026 else ""), "FCFE": L["fcfe"][i],
                     "Less after-tax interest income": -L["after_tax_interest_income"][i],
                     "Less H1-2026 actual (already in cash)": -h1_op if y == 2026 else 0.0,
                     "Operating FCFE valued": flow if include else 0.0, "Discount period (yrs)": t,
                     "Discount factor": df_, "PV": pv})
    out.pv_table = pd.DataFrame(rows)
    out.pv_fcfe = pv_sum

    # ---------------- 2031 terminal FCFE bridge ----------------
    j = len(config.FORECAST_YEARS) - 1
    tax_last = float(a.get("tax_rate", scenario)[j])
    ni_op = L["ni_parent"][j] - L["interest_income"][j] * (1 - tax_last)
    ni31 = ni_op * (1 + g)
    da31 = L["da"][j] * (1 + g)
    sbc31 = L["sbc"][j] * (1 + g) if add_sbc else 0.0
    capex31 = da31 * float(a.p("terminal_capex_to_da"))
    dnwc31 = L["nwc"][j] * g
    nb31 = (L["debt"][j] + L["fl"][j] + L["revolver"][j]) * g
    fcfe31 = ni31 + da31 + sbc31 - capex31 - dnwc31 + nb31
    out.terminal_bridge = pd.DataFrame([
        {"Component": "Net income to common, ex-interest income (FY2030E x (1+g))", "FY2030E": ni_op, f"FY{config.TERMINAL_YEAR}": ni31},
        {"Component": "+ D&A (grown at g)", "FY2030E": L["da"][j], f"FY{config.TERMINAL_YEAR}": da31},
        {"Component": "+ SBC (if added back)", "FY2030E": L["sbc"][j] if add_sbc else 0.0, f"FY{config.TERMINAL_YEAR}": sbc31},
        {"Component": "- Capex (terminal capex/D&A x D&A)", "FY2030E": -L["capex"][j], f"FY{config.TERMINAL_YEAR}": -capex31},
        {"Component": "- Increase in NWC (NWC x g)", "FY2030E": -L["delta_nwc"][j], f"FY{config.TERMINAL_YEAR}": -dnwc31},
        {"Component": "+ Net borrowing (debt x g, constant leverage)", "FY2030E": L["net_borrowing"][j], f"FY{config.TERMINAL_YEAR}": nb31},
        {"Component": "= Operating FCFE", "FY2030E": L["fcfe_operating"][j], f"FY{config.TERMINAL_YEAR}": fcfe31},
    ])
    if not ke > g:  # pragma: no cover - guarded by check 7
        raise ValuationError("Terminal growth must be below the cost of equity")
    tv = fcfe31 / (ke - g)
    t_tv = _periods(valuation_date, False)[j][3]
    pv_tv = tv / (1 + ke) ** t_tv
    nonop = non_operating_assets(b, a, res, scenario)
    shares = diluted_shares(b, a)
    equity = pv_sum + pv_tv + nonop["Total non-operating assets"]
    out.fcfe_2031, out.terminal_value, out.pv_terminal = fcfe31, tv, pv_tv
    out.non_operating, out.shares, out.equity_value = nonop["Total non-operating assets"], shares, equity
    out.value_per_share = equity / shares
    if fcfe31 <= 0:
        out.warnings.append(f"Terminal-year (2031) FCFE is negative ({fcfe31:,.0f}); the terminal value subtracts value.")
    if equity <= 0:
        out.warnings.append("Total equity value is negative. Shareholders' limited liability (a floor at zero) is not modelled.")
    out.upside = out.value_per_share / price - 1 if price else None
    dcf_total = pv_sum + pv_tv
    out.tv_share_of_dcf = pv_tv / dcf_total if dcf_total else np.nan
    out.tv_share_of_equity = pv_tv / equity if equity else np.nan
    out.equity_bridge = pd.DataFrame([
        {"Item": "PV of operating FCFE (H2 2026 - 2030)", "USD m": pv_sum},
        {"Item": f"Terminal value at end-2030 (FCFE {config.TERMINAL_YEAR} / (ke - g))", "USD m": tv},
        {"Item": f"PV of terminal value (discounted {t_tv:.2f} yrs)", "USD m": pv_tv},
        *[{"Item": k, "USD m": v} for k, v in nonop.items()],
        {"Item": "Total equity value", "USD m": equity},
        {"Item": "Diluted shares (M)", "USD m": shares},
        {"Item": "Implied value per share ($)", "USD m": out.value_per_share},
        {"Item": f"Market price ($, {out.price_date})", "USD m": price},
        {"Item": "Upside / (downside)", "USD m": out.upside},
        {"Item": "Terminal value share of DCF value (PV FCFE + PV TV)", "USD m": out.tv_share_of_dcf},
        {"Item": "Terminal value share of total equity value", "USD m": out.tv_share_of_equity},
    ])
    return out


# ---------------------------------------------------------------------------------------------
# Secondary cross-check: trading multiples
# ---------------------------------------------------------------------------------------------
def multiples_crosscheck(b: DataBundle, a: AssumptionSet, res: ModelResult, val: ValuationResult) -> pd.DataFrame:
    """SECONDARY cross-check only. Peers trade on very different growth/margin profiles."""
    L = res.lines
    shares = val.shares or diluted_shares(b, a)
    price = b.market["price"]["value"]
    net_debt = (b.value("debt_fl_current", "Q2_2026") + b.value("debt_fl_noncurrent", "Q2_2026")
                - b.value("cash", "Q2_2026") - b.value("st_investments", "Q2_2026"))
    peers = pd.DataFrame(b.market["peers"])
    peers["EV"] = peers["market_cap"] + peers["debt"]
    peers["EV/Revenue"] = peers["EV"] / peers["revenue_lfy"]
    pe = peers["market_cap"] / peers["net_income_lfy"]
    peers["P/E"] = pe.where(peers["net_income_lfy"].fillna(0) > 0)
    ev_rev = float(peers["EV/Revenue"].median())
    pe_med = float(peers["P/E"].dropna().median()) if peers["P/E"].notna().any() else np.nan
    rev26, ni26, ni27 = L["rev_total"][0], L["ni_parent"][0], L["ni_parent"][1]
    eps27 = L["eps"][1]
    rows = [
        {"Method": "Peer median EV / revenue (LFY) x FY2026E revenue", "Multiple": ev_rev,
         "Implied value per share": (ev_rev * rev26 - net_debt) / shares},
        {"Method": "Peer median P/E (profitable peers) x FY2026E net income", "Multiple": pe_med,
         "Implied value per share": pe_med * ni26 / shares if not np.isnan(pe_med) else np.nan},
        {"Method": f"Forward P/E {a.p('pe_multiple_low'):.0f}x (judgment) x FY2027E EPS", "Multiple": a.p("pe_multiple_low"),
         "Implied value per share": a.p("pe_multiple_low") * eps27},
        {"Method": f"Forward P/E {a.p('pe_multiple_high'):.0f}x (judgment) x FY2027E EPS", "Multiple": a.p("pe_multiple_high"),
         "Implied value per share": a.p("pe_multiple_high") * eps27},
        {"Method": "Market-implied P/E on FY2026E net income (price x shares / NI)", "Multiple": price * shares / ni26 if ni26 > 0 else np.nan,
         "Implied value per share": price},
        {"Method": "Market-implied P/E on FY2027E net income", "Multiple": price * shares / ni27 if ni27 > 0 else np.nan,
         "Implied value per share": price},
        {"Method": "Market-implied EV / FY2026E revenue", "Multiple": (price * shares + net_debt) / rev26,
         "Implied value per share": price},
    ]
    return pd.DataFrame(rows)
