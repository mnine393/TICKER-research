"""Headless Streamlit smoke tests (offline data): every page renders, and a failed check blocks valuation."""
import io
from pathlib import Path

import openpyxl
import pytest

from tsla_model import scenarios as S
from tsla_model.data_ingestion import build_source_table, historical_table
from tsla_model.excel_export import build_workbook

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).parent.parent / "app.py")
PAGES = ["summary", "assumptions", "statements", "valuation", "sensitivities", "checks", "sources"]


def _fresh_app():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["live"] = False          # offline seed data; no network in tests
    return at


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_without_exceptions(page):
    at = _fresh_app()
    at.session_state["force_page"] = page
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.title) >= 1


def test_summary_shows_value_and_disclaimer():
    at = _fresh_app()
    at.run()
    labels = [m.label for m in at.metric]
    assert any("Implied value" in l for l in labels)
    assert "not investment advice" in " ".join(w.value for w in at.warning).lower()


def test_failed_check_shows_refusal_state():
    at = _fresh_app()
    at.run()
    aset = at.session_state["aset"]
    aset.params["revolver_capacity"].value = 0.0
    aset.drivers["capex"].values["base"] = [60000.0] * 5
    at.run()
    assert not at.exception
    assert any("Valuation refused" in e.value for e in at.error)
    assert any(m.value == "REFUSED" for m in at.metric)


def test_workbook_exports_even_when_valuation_refused(bundle, aset, val_date):
    aset.params["revolver_capacity"].value = 0.0
    aset.drivers["capex"].values["base"] = [60000.0] * 5
    x = S.full_analysis(bundle, aset, "base", val_date)
    assert x["evals"]["base"].valuation.status == "FAILED"
    data = build_workbook(bundle, aset, "base", x["evals"], x, build_source_table(bundle), historical_table(bundle))
    wb = openpyxl.load_workbook(io.BytesIO(data))
    assert "VALUATION REFUSED" in str(wb["Valuation"]["A1"].value)
