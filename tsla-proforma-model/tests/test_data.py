"""Seed data integrity, source table and ingestion helpers."""
import numpy as np
import pandas as pd
import pytest

from tsla_model import data_ingestion as di

IS_PERIODS = ["FY2023", "FY2024", "FY2025", "H1_2026"]
BS_PERIODS = ["FY2023", "FY2024", "FY2025", "Q2_2026"]


def test_seed_loads_with_fallback_status(bundle):
    assert bundle.financials["meta"]["ticker"] == "TSLA"
    assert any(s[1] == "fallback" for s in bundle.status)
    assert bundle.market["price"]["value"] > 0


@pytest.mark.parametrize("p", IS_PERIODS)
def test_income_statement_ties(bundle, p):
    v = lambda k: bundle.value(k, p)
    rev = v("rev_auto_sales") + v("rev_reg_credits") + v("rev_auto_leasing") + v("rev_energy") + v("rev_services")
    assert rev == pytest.approx(v("rev_total"))
    cogs = v("cogs_auto_sales") + v("cogs_auto_leasing") + v("cogs_energy") + v("cogs_services")
    assert cogs == pytest.approx(v("cogs_total"))
    assert v("rev_total") - v("cogs_total") == pytest.approx(v("gross_profit"))
    assert v("rd") + v("sga") + v("restructuring") == pytest.approx(v("opex_total"))
    assert v("gross_profit") - v("opex_total") == pytest.approx(v("ebit"))
    assert v("ebit") + v("interest_income") - v("interest_expense") + v("other_income") == pytest.approx(v("pretax"))
    assert v("pretax") - v("tax") == pytest.approx(v("net_income_total"))
    assert v("net_income_total") - v("ni_nci") == pytest.approx(v("ni_parent"))


@pytest.mark.parametrize("p", BS_PERIODS)
def test_balance_sheet_ties(bundle, p):
    v = lambda k: bundle.value(k, p)
    assets = sum(v(k) for k in ["cash", "st_investments", "ar", "inventory", "prepaid", "olv", "energy_systems", "ppe",
                                "rou", "digital_assets", "dta", "other_nca"])
    assert assets == pytest.approx(v("total_assets"))
    liab = sum(v(k) for k in ["ap", "accrued_current", "deferred_rev_current", "debt_fl_current", "debt_fl_noncurrent",
                              "deferred_rev_noncurrent", "other_ltl"])
    assert liab == pytest.approx(v("total_liabilities"))
    assert liab + v("redeemable_nci") + v("equity_parent") + v("nci") == pytest.approx(v("total_le"))
    assert v("total_assets") == pytest.approx(v("total_le"))


def test_delivery_split_reconciles_to_reported_totals(bundle):
    # Totals from the 8-K Ex. 99.1 releases: FY2023 1,808,581; FY2024 1,789,226; FY2025 1,636,129
    tot = {p: bundle.value("deliveries_3y", p) + bundle.value("deliveries_other", p) for p in ["FY2023", "FY2024", "FY2025"]}
    assert tot == {"FY2023": 1808581, "FY2024": 1789226, "FY2025": 1636129}


def test_source_table_covers_every_line_item(bundle):
    src = di.build_source_table(bundle)
    fin = bundle.financials
    n_expected = sum(len(li["values"]) for li in fin["line_items"].values()) + sum(len(li["values"]) for li in fin["operating"].values())
    hist = src[src["Section"].isin(["Income statement", "Balance sheet", "Cash flow", "Segment note", "Operating KPI"])]
    assert len(hist) == n_expected
    for col in ["Filing / document", "Accession", "Page / section", "Source type"]:
        assert hist[col].astype(str).str.len().min() > 0, col
    assert set(["Market data", "Obligations / guidance"]).issubset(set(src["Section"]))


def test_xbrl_value_parser_and_verification(bundle):
    facts = {"facts": {"us-gaap": {
        "Revenues": {"units": {"USD": [
            {"start": "2025-01-01", "end": "2025-12-31", "val": 94_827_000_000},
            {"start": "2025-10-01", "end": "2025-12-31", "val": 24_901_000_000}]}},
        "Assets": {"units": {"USD": [{"end": "2025-12-31", "val": 137_000_000_000}]}},
    }}}
    assert di.xbrl_value(facts, "Revenues", "FY2025", instant=False) == pytest.approx(94827)
    assert di.xbrl_value(facts, "Revenues", "FY2024", instant=False) is None
    b = di.load_seed()
    di.verify_against_xbrl(b, facts)
    assert b.verification[("rev_total", "FY2025")] == "XBRL match"
    assert b.verification[("total_assets", "FY2025")].startswith("XBRL mismatch")


def test_regression_beta_recovers_known_slope():
    rng = np.random.default_rng(0)
    rm = rng.normal(0.01, 0.04, 60)
    rs = 1.5 * rm + rng.normal(0, 1e-6, 60)
    m = pd.Series(np.cumprod(1 + np.r_[0, rm]))
    s = pd.Series(np.cumprod(1 + np.r_[0, rs]))
    beta, n = di.regression_beta(s, m)
    assert n == 60
    assert beta == pytest.approx(1.5, abs=1e-3)


def test_offline_mode_never_touches_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network called")
    monkeypatch.setattr(di, "refresh_sec", boom)
    monkeypatch.setattr(di, "refresh_market", boom)
    b = di.get_data(live=False)
    assert b.value("rev_total", "FY2025") == 94827


def test_live_failure_falls_back_gracefully(monkeypatch):
    class Dead:
        @staticmethod
        def get(*a, **k):
            raise ConnectionError("offline")
    monkeypatch.setattr(di, "requests", Dead)
    monkeypatch.setattr(di.pd, "read_csv", lambda *a, **k: (_ for _ in ()).throw(ConnectionError("offline")))
    b = di.get_data(live=True)
    assert b.market["price"]["value"] == pytest.approx(378.25)
    statuses = {s[0]: s[1] for s in b.status}
    assert statuses["Share price"] == "fallback"
    assert statuses["SEC filings"] == "fallback"
    assert statuses["Risk-free rate"] == "fallback"
