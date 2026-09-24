"""Assumption registry: labelling, rationale, editing and revision history."""
import pytest

from tsla_model import config
from tsla_model.assumptions import KINDS, Assumption, historical_drivers


def test_every_driver_is_labelled_and_sourced(aset):
    for a in aset.drivers.values():
        assert a.kind in KINDS
        assert a.source.strip(), a.id
        if a.kind == "judgment":
            assert len(a.rationale) > 30, a.id
        for s in config.SCENARIOS:
            assert len(a.values[s]) == len(config.FORECAST_YEARS)
    for p in aset.params.values():
        assert p.kind in KINDS
        if p.kind == "judgment":
            assert p.rationale.strip(), p.id


def test_judgment_without_rationale_is_rejected():
    with pytest.raises(ValueError):
        Assumption(id="x", label="x", category="c", unit="pct", kind="judgment", source="s", rationale=" ", values={"base": [0.1] * 5})
    with pytest.raises(ValueError):
        Assumption(id="x", label="x", category="c", unit="pct", kind="guess", source="s", rationale="r", values={"base": [0.1] * 5})


def test_capex_2026_ties_to_guidance(bundle, aset):
    assert aset.get("capex", "base")[0] == bundle.obligation("capex_guidance_2026") == 25000
    assert aset.drivers["capex"].kind == "guidance"


def test_edits_are_logged(aset):
    old = aset.get("gm_auto_sales", "bull")[2]
    aset.set_value("gm_auto_sales", "bull", 2, 0.30, "test edit")
    aset.set_param("erp", 0.05, "test")
    rev = aset.revisions_table()
    assert len(rev) == 2
    assert rev.iloc[0]["old"] == pytest.approx(old) and rev.iloc[0]["new"] == pytest.approx(0.30)
    assert rev.iloc[0]["year"] == "2028" and rev.iloc[0]["note"] == "test edit"
    aset.set_value("gm_auto_sales", "bull", 2, 0.30)   # no-op edits are not logged
    assert len(aset.revisions) == 2


def test_shocked_returns_copy(aset):
    before = list(aset.drivers["capex"].values["base"])
    s = aset.shocked("capex", "base", +1)
    assert s.get("capex", "base")[1] == pytest.approx(before[1] * 1.1)
    assert aset.drivers["capex"].values["base"] == before


def test_historical_asp_split_reconciles_to_automotive_sales(bundle):
    h = historical_drivers(bundle)
    for p in ["FY2023", "FY2024", "FY2025", "H1_2026"]:
        d = h[p]
        rebuilt = d["deliveries_3y"] * d["asp_3y"] + d["deliveries_other"] * d["asp_other"]
        assert rebuilt == pytest.approx(bundle.value("rev_auto_sales", p))


def test_historical_cash_margin_bridge(bundle):
    """Ex-D&A gross profit - segment D&A = reported gross profit (FY2025)."""
    h = historical_drivers(bundle)["FY2025"]
    v = lambda k: bundle.value(k, "FY2025")
    cash_gp = (v("rev_auto_sales") * h["gm_auto_sales"] + v("rev_auto_leasing") * h["gm_leasing"]
               + v("rev_services") * h["gm_services"] + v("rev_energy") * h["gm_energy"] + v("rev_reg_credits"))
    assert cash_gp - v("da_cogs_auto") - v("da_cogs_energy") == pytest.approx(v("gross_profit"), abs=1)
