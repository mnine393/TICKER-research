"""FCFF DCF: hand-checkable cash flows, guardrails, WACC behavior and EV bridge."""
import pytest

from tsla_model.fcff import fcff_cash_flow, q2_bridge_balances, run_fcff, wacc_g_grid
from tsla_model.statements import run_model


def test_fcff_three_year_known_answer_with_sbc_toggle():
    # A student can check each synthetic year: EBIT x (1-tax) + D&A + SBC - capex - dNWC.
    years = [(100, .20, 30, 10, 40, 5), (120, .25, 32, 12, 45, 6), (-10, .25, 34, 14, 50, -4)]
    actual = [fcff_cash_flow(*row, add_sbc=True) for row in years]
    assert actual == pytest.approx([(80, 75), (90, 83), (-10, -8)])
    assert fcff_cash_flow(*years[0], add_sbc=False) == pytest.approx((80, 65))


def test_fcff_refuses_terminal_growth_at_or_above_wacc(bundle, aset, val_date):
    res = run_model(bundle, aset)
    v = run_fcff(bundle, aset, res, valuation_date=val_date, wacc_override=.08, g_override=.08)
    assert v.status == "FAILED"
    assert any("Terminal growth" in f for f in v.failures)


def test_fcff_wacc_and_growth_monotonicity(bundle, aset, val_date):
    res = run_model(bundle, aset)
    low_wacc = run_fcff(bundle, aset, res, valuation_date=val_date, wacc_override=.09, g_override=.03)
    high_wacc = run_fcff(bundle, aset, res, valuation_date=val_date, wacc_override=.11, g_override=.03)
    low_g = run_fcff(bundle, aset, res, valuation_date=val_date, wacc_override=.10, g_override=.02)
    high_g = run_fcff(bundle, aset, res, valuation_date=val_date, wacc_override=.10, g_override=.04)
    assert low_wacc.value_per_share > high_wacc.value_per_share
    assert high_g.value_per_share > low_g.value_per_share
    grid = wacc_g_grid(bundle, aset, res, valuation_date=val_date)
    assert list(grid.index) == ["8%", "9%", "10%", "11%", "12%", "13%"]
    assert list(grid.columns) == ["1%", "2%", "3%", "4%"]


def test_fcff_q2_bridge_ties_to_equity_value(bundle, aset, val_date):
    res = run_model(bundle, aset)
    v = run_fcff(bundle, aset, res, valuation_date=val_date)
    bridge = q2_bridge_balances(bundle)
    nonop = v.equity_bridge.loc[v.equity_bridge["Item"] == "Total non-operating assets", "USD m"].iloc[0]
    assert v.equity_value == pytest.approx(v.enterprise_value + nonop - sum(bridge.values()))
    assert v.value_per_share == pytest.approx(v.equity_value / 3540.0)
    assert bridge["Revolver (30-Jun-2026)"] == 0.0


def test_broken_balance_sheet_blocks_fcff_valuation(bundle, aset, val_date):
    res = run_model(bundle, aset)
    res.lines["cash"][0] += 100.0
    v = run_fcff(bundle, aset, res, valuation_date=val_date)
    assert v.status == "FAILED"
    assert any("Assets = liabilities + equity" in f for f in v.failures)
