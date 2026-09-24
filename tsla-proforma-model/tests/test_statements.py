"""Three-statement integrity and formula tests."""
import numpy as np
import pytest

from tsla_model import config
from tsla_model.checks import run_checks
from tsla_model.statements import opening_balances, run_model

SCEN = config.SCENARIOS


def test_opening_balance_sheet_equals_reported_fy2025(bundle):
    o = opening_balances(bundle)
    assets = sum(o[k] for k in ("cash", "ar", "inventory", "prepaid", "nfa", "rou", "digital", "dta", "other_nca"))
    le = sum(o[k] for k in ("ap", "accrued", "defrev", "debt", "fl", "ol", "revolver")) + o["equity"] + o["nci"]
    assert assets == pytest.approx(bundle.value("total_assets", "FY2025"))
    assert le == pytest.approx(bundle.value("total_le", "FY2025"))


@pytest.mark.parametrize("scenario", SCEN)
def test_balance_sheet_balances_every_year(bundle, aset, scenario):
    r = run_model(bundle, aset, scenario)
    diff = r.balance.loc["TOTAL ASSETS"] - r.balance.loc["TOTAL LIABILITIES & EQUITY"]
    assert np.abs(diff.to_numpy(dtype=float)).max() < 1e-6


@pytest.mark.parametrize("scenario", SCEN)
def test_all_checks_pass_for_default_scenarios(bundle, aset, scenario):
    r = run_model(bundle, aset, scenario)
    chk = run_checks(r, ke=0.10, g=0.03)
    assert chk["Pass"].all(), chk[~chk["Pass"]]


def test_cash_on_balance_sheet_comes_from_cash_flow(bundle, aset):
    r = run_model(bundle, aset)
    L = r.lines
    cash = L["cash_begin"] + L["cfo"] + L["cfi"] + L["cff"]
    assert np.allclose(cash, r.balance.loc["Cash & short-term investments", [f"FY{y}E" for y in config.FORECAST_YEARS]].to_numpy(float))
    assert L["cash_begin"][0] == pytest.approx(opening_balances(bundle)["cash"])
    assert np.allclose(L["cash_begin"][1:], L["cash"][:-1])


def test_revenue_is_driver_based(bundle, aset):
    r = run_model(bundle, aset)
    i = 2
    g = lambda k: aset.get(k)[i]
    auto = g("deliveries_3y") * g("asp_3y") + g("deliveries_other") * g("asp_other")
    assert r.lines["rev_auto_sales"][i] == pytest.approx(auto)
    assert r.lines["rev_energy"][i] == pytest.approx(g("storage_gwh") * g("energy_rev_per_gwh"))
    svc = bundle.value("rev_services", "FY2025") * np.prod(1 + aset.get("services_growth")[: i + 1])
    assert r.lines["rev_services"][i] == pytest.approx(svc)


def test_fcfe_formula(bundle, aset):
    r = run_model(bundle, aset)
    L = r.lines
    fcfe = L["ni_parent"] + L["da"] + L["sbc"] - L["capex"] - L["delta_nwc"] + (L["debt_issued"] - L["debt_repaid"] - L["fl_principal"] + L["revolver_draw"])
    assert np.allclose(fcfe, L["fcfe"])
    # Reconciles to the change in cash
    recon = L["fcfe"] + (L["ni_nci"] - L["nci_dist"]) - L["strategic"] + L["option_proceeds"] - L["buybacks"]
    assert np.allclose(recon, L["net_change_cash"])


def test_non_recurring_items_excluded(bundle, aset):
    r = run_model(bundle, aset)
    assert (r.income.loc["Restructuring & other (non-recurring)", [f"FY{y}E" for y in config.FORECAST_YEARS]] == 0).all()
    assert (r.income.loc["Other income, net (non-recurring)", [f"FY{y}E" for y in config.FORECAST_YEARS]] == 0).all()


def test_balance_sheet_is_not_a_plug(bundle, aset):
    """Raising capex by X lowers ending cash by X less the tax-effected D&A shield - not by an arbitrary plug."""
    base = run_model(bundle, aset)
    a2 = aset.copy()
    a2.drivers["capex"].values["base"][-1] += 1000.0
    r2 = run_model(bundle, a2)
    d_cash = r2.lines["cash"][-1] - base.lines["cash"][-1]
    # final-year capex only affects final-year cash via capex itself (D&A is on beginning assets)
    assert d_cash == pytest.approx(-1000.0)
    assert r2.lines["nfa"][-1] - base.lines["nfa"][-1] == pytest.approx(1000.0)
    assert r2.lines["assets"][-1] - base.lines["assets"][-1] == pytest.approx(0.0, abs=1e-6)


def test_revolver_draws_only_when_needed(bundle, aset):
    base = run_model(bundle, aset)
    assert base.lines["revolver"].max() == 0
    a2 = aset.copy()
    a2.drivers["capex"].values["base"] = [25000, 45000, 20000, 16000, 15000]
    r2 = run_model(bundle, a2)
    assert r2.lines["revolver_draw"][1] > 0
    assert r2.lines["revolver"].max() <= aset.p("revolver_capacity") + 1e-6
    assert run_checks(r2)["Pass"].all() or r2.lines["cash_shortfall"].max() > 0


def test_share_roll_forward(bundle, aset):
    a2 = aset.copy()
    a2.drivers["buybacks"].values["base"] = [0, 5000, 5000, 0, 0]
    r = run_model(bundle, a2)
    L = r.lines
    assert L["shares_begin"][0] == bundle.value("shares_diluted_q2_2026", "H1_2026")
    assert np.allclose(L["shares_end"], L["shares_begin"] + L["shares_issued"] - L["shares_repurchased"])
    assert L["shares_repurchased"][1] == pytest.approx(5000 / bundle.market["price"]["value"])
    assert run_checks(r)["Pass"].all()
