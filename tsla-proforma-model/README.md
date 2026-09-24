# Tesla (TSLA) Pro-forma FCFE Valuation Model

An educational, fully linked three-statement model and five-year **FCFE** discounted-cash-flow valuation of Tesla, Inc.,
with a Streamlit dashboard, scenario and sensitivity analysis, automated tests and a formatted Excel export.

> **Disclaimer.** For education and research only. This is **not investment advice** and not a recommendation to buy,
> sell or hold TSLA or any security. Forecasts are hypothetical and rest on clearly labelled judgment. Verify all figures
> against Tesla's filings before relying on them.

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py               # opens http://localhost:8501
python -m pytest -q                # full test suite (offline; no network needed)
```

Optional: set `SEC_USER_AGENT="Your Name your@email"` so SEC EDGAR requests identify you (SEC fair-access policy).
The sidebar toggle **Live SEC & market data** switches between live retrieval and the bundled seed data.

## Architecture

| File | Responsibility |
|---|---|
| `tsla_model/data/seed_filings.json` | Every historical line item (FY2023-FY2025, H1/Q2 2026) with filing, accession, page/section |
| `tsla_model/data/seed_market.json` | Fallback price, 10-year Treasury, observed beta, peer betas/market caps/debt |
| `tsla_model/data_ingestion.py` | Seed loading; live EDGAR filing discovery and XBRL verification; live price, Treasury yield, regression betas; source table |
| `tsla_model/assumptions.py` | **Central assumption registry**: per-scenario yearly values, `history` / `guidance` / `judgment` label, source, rationale, revision log |
| `tsla_model/statements.py` | Linked income statement, balance sheet, cash flow and schedules (revenue build, PP&E, debt & leases, equity & shares, working capital, FCFE) |
| `tsla_model/checks.py` | Validation block run for every forecast year |
| `tsla_model/valuation.py` | CAPM (observed and bottom-up beta), FCFE DCF, 2031 terminal bridge, Gordon growth, equity bridge, multiples cross-check |
| `tsla_model/scenarios.py` | Scenarios, cost-of-equity x growth grid, one-variable table, tornado, two-variable matrix, value bridge, "what must be true" solver |
| `tsla_model/charts.py` | Plotly charts built only from model outputs |
| `tsla_model/excel_export.py` | Workbook: Cover, Sources, Assumptions, Historical Financials, Forecast, Valuation, Scenarios, Checks |
| `app.py` | Streamlit UI (executive summary, assumptions, statements, valuation, sensitivities, checks, sources) |
| `tests/` | 66 tests: data ties, formulas, balance-sheet checks, invalid terminal inputs, non-additive sensitivities, export, headless app rendering |

### Model mechanics (USD millions except per-share)

- **Revenue (driver-based, reconciled):** Model 3/Y and Other-model deliveries x ASP; regulatory credits; leasing; services
  and other (growth); an isolated robotaxi/autonomy line; energy = GWh deployed x revenue per GWh.
- **Margins** are modelled *before D&A* ("cash" gross margins), so capex and depreciation flow through explicitly.
  GAAP-equivalent gross margin is shown as a memo line.
- **D&A** = rate x beginning net fixed assets (PP&E + lease vehicles + energy systems); **PP&E roll-forward**:
  begin + capex + new finance leases - D&A.
- **Working capital:** DSO, DIO and DPO (days), plus prepaid, accrued and deferred revenue as % of revenue.
- **Financing:** debt issuance/repayment (scheduled maturities), finance and operating lease roll-forwards, option
  proceeds, buybacks (zero by default), NCI. Interest is charged on **beginning** balances (no circularity).
- **Minimum-cash rule + revolver:** the $5.0B committed facility (10-Q) is drawn only if cash would fall below
  15% of revenue, and repaid first when cash recovers.
- **FCFE** = net income + D&A (+ SBC, toggle) - capex - increase in NWC + net borrowing (debt, finance leases, revolver).
- **Valuation:** *operating* FCFE (FCFE minus after-tax interest income) is discounted from the valuation date. FY2026E
  is reduced by the H1 2026 actual FCFE already in the 30-Jun-2026 balance sheet. Terminal value = FCFE 2031 /
  (ke - g), using an explicit 2031 bridge. Excess cash (above the minimum), digital assets and the SpaceX stake are
  added at balance-sheet value. The unearned 2025 CEO award shares are excluded by default (toggle available).
- **Checks (every year):** assets = liabilities + equity (re-summed from components); cash-flow ending cash = balance-sheet
  cash; PP&E, debt, lease and revolver roll-forwards; share roll-forward; cash >= minimum; terminal g < ke; revenue build
  reconciles. **Any failure blocks the valuation** and the UI and workbook show a refusal state.
- **Sensitivities:** every cell, bar and scenario is a full re-run of the statements and the valuation. Nothing is added together.

## Data sources

Annual: 10-K FY2025 (acc. 0001628280-26-003952), 10-K FY2024 (0001628280-25-003063), 10-K FY2023 (0001628280-24-002390).
Quarterly: 10-Q Q2 2026 (0001628280-26-049270). Delivery/deployment releases filed as 8-K Ex. 99.1 (Jan 2024, Jan 2025,
Jan 2026, Apr 2026, Jul 2026). Market: Yahoo Finance chart API (price, 5-year monthly returns), Nasdaq quote API (peer
market caps), U.S. Treasury daily par yield curve (FRED DGS10 fallback). The **Sources** page and sheet list every item
with document, period, page/section, source type, XBRL verification status and notes.

## Limitations caused by Tesla's disclosures

- No revenue or ASP by vehicle model. Only *Model 3/Y* vs *Other models* deliveries are disclosed, so category ASPs
  use a judgment 2x price relationship. The blended ASP is observable.
- D&A is disclosed only at segment level (automotive and energy cost of revenues). Automotive D&A is allocated pro-rata
  across automotive sales, leasing and services to derive cash margins.
- Robotaxi, FSD and Optimus economics are not disclosed. Robotaxi is an explicit judgment line; Optimus is not modelled.
- Tesla states no minimum cash level and gives capex guidance for 2026 only ("in excess of $25 billion").
- Operating-lease vehicle additions run through operating cash flow in Tesla's statements; the model treats all fixed-asset
  additions as capex.
- Peer D/E for GM and Ford uses judgment-based ex-captive-finance debt, because custom XBRL tags prevent automated extraction.

## Updating for new filings

When a new 10-Q or 10-K is filed, the app flags it on the Sources page. To roll the base period forward, add the new
period's values and page references to `tsla_model/data/seed_filings.json`. The XBRL verification then confirms every
tagged value automatically.
