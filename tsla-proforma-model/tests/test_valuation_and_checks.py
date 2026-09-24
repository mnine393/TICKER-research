"""Valuation formulas, failure states and invalid terminal-value inputs."""
import numpy as np
import pytest

from tsla_model.checks import material_failures, run_checks
from tsla_model.statements import run_model
from tsla_model.valuation import capm, cost_of_equity, relever, run_valuation, unlever


def test_capm_and_hamada():
    assert capm(0.05, 1.2, 0.045) == pytest.approx(0.05 + 1.2 * 0.045)
    bu = unlever(1.5, 0.5, 0.21)
    assert bu == pytest.approx(1.5 / (1 + 0.79 * 0.5))
    assert relever(bu, 0.5, 0.21) == pytest.approx(1.5)


def test_bottom_up_beta_uses_peer_average(bundle, aset):
    r = run_model(bundle, aset)
    coe = cost_of_equity(bundle, aset, r, "bottom-up")
    peers = coe["bottom_up"]["peers"]
    auto = peers[~peers["Group"].str.contains("Energy")]["Unlevered beta"].mean()
    energy = peers[peers["Group"].str.contains("Energy")]["Unlevered beta"].mean()
    w = aset.p("peer_weight_auto")
    assert coe["bottom_up"]["weighted_unlevered"] == pytest.approx(w * auto + (1 - w) * energy)
    assert coe["ke"] == pytest.approx(aset.p("risk_free") + coe["beta"] * aset.p("erp"))
    obs = cost_of_equity(bundle, aset, r, "observed")
    assert obs["beta"] == pytest.approx(aset.p("beta_observed"))


def test_valuation_arithmetic(bundle, aset, val_date):
    r = run_model(bundle, aset)
    v = run_valuation(bundle, aset, r, "base", val_date)
    assert v.status == "OK"
    assert v.terminal_value == pytest.approx(v.fcfe_2031 / (v.ke - v.g))
    assert v.pv_fcfe == pytest.approx(v.pv_table["PV"].sum())
    assert v.equity_value == pytest.approx(v.pv_fcfe + v.pv_terminal + v.non_operating)
    assert v.value_per_share == pytest.approx(v.equity_value / v.shares)
    assert v.tv_share_of_dcf == pytest.approx(v.pv_terminal / (v.pv_fcfe + v.pv_terminal))
    # 2031 bridge: every component grows at g from FY2030E, capex = D&A x terminal ratio
    tb = v.terminal_bridge.set_index("Component")
    da31 = tb.loc["+ D&A (grown at g)", "FY2031"]
    assert da31 == pytest.approx(r.lines["da"][-1] * (1 + v.g))
    assert -tb.loc["- Capex (terminal capex/D&A x D&A)", "FY2031"] == pytest.approx(da31 * aset.p("terminal_capex_to_da"))
    assert tb.loc["= Operating FCFE", "FY2031"] == pytest.approx(tb["FY2031"].iloc[:-1].sum())


@pytest.mark.parametrize("g", [0.12, 0.2])
def test_terminal_growth_at_or_above_ke_refuses(bundle, aset, val_date, g):
    r = run_model(bundle, aset)
    v = run_valuation(bundle, aset, r, "base", val_date, g_override=g)
    assert v.status == "FAILED"
    assert v.value_per_share is None
    assert any("Terminal growth" in f for f in v.failures)


def test_terminal_growth_equal_to_ke_refuses(bundle, aset, val_date):
    r = run_model(bundle, aset)
    v = run_valuation(bundle, aset, r, "base", val_date, ke_override=0.08, g_override=0.08)
    assert v.status == "FAILED" and v.value_per_share is None


def test_broken_balance_sheet_blocks_valuation(bundle, aset, val_date):
    r = run_model(bundle, aset, build_frames=False)
    r.lines["cash"][2] += 500.0          # corrupt one year
    chk = run_checks(r, 0.10, 0.03)
    assert not chk["Pass"].all()
    assert any("Assets = liabilities" in f for f in material_failures(chk))
    v = run_valuation(bundle, aset, r, "base", val_date, checks=chk)
    assert v.status == "FAILED"


def test_minimum_cash_breach_blocks_valuation(bundle, aset, val_date):
    a2 = aset.copy()
    a2.params["revolver_capacity"].value = 0.0
    a2.drivers["capex"].values["base"] = [60000, 60000, 60000, 60000, 60000]
    r = run_model(bundle, a2)
    v = run_valuation(bundle, a2, r, "base", val_date)
    assert v.status == "FAILED"
    assert any("minimum" in f for f in v.failures)


def test_toggles_move_value_in_expected_direction(bundle, aset, val_date):
    base = run_valuation(bundle, aset, run_model(bundle, aset), "base", val_date).value_per_share
    a2 = aset.copy(); a2.params["include_ceo_award_shares"].value = True
    assert run_valuation(bundle, a2, run_model(bundle, a2), "base", val_date).value_per_share < base
    a3 = aset.copy(); a3.params["add_back_sbc"].value = False
    assert run_valuation(bundle, a3, run_model(bundle, a3), "base", val_date).value_per_share < base
    a4 = aset.copy(); a4.params["mid_year"].value = True
    assert run_valuation(bundle, a4, run_model(bundle, a4), "base", val_date).value_per_share != pytest.approx(base)


def test_higher_discount_rate_lowers_value(bundle, aset, val_date):
    r = run_model(bundle, aset)
    lo = run_valuation(bundle, aset, r, "base", val_date, ke_override=0.09).value_per_share
    hi = run_valuation(bundle, aset, r, "base", val_date, ke_override=0.12).value_per_share
    assert lo > hi


def test_h1_2026_stub_is_removed_from_fy2026(bundle, aset, val_date):
    r = run_model(bundle, aset)
    v = run_valuation(bundle, aset, r, "base", val_date)
    row = v.pv_table.iloc[0]
    assert "H2" in row["Year"]
    assert row["Operating FCFE valued"] == pytest.approx(r.lines["fcfe_operating"][0] + row["Less H1-2026 actual (already in cash)"])
    assert 0 < row["Discount period (yrs)"] < 0.5
