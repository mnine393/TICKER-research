# TSLA Pro-forma FCFE Model: Summary

*Valuation date: 24 September 2026. USD millions except per-share figures.*

> **Disclaimer.** For education and research only. This is not investment advice and not a recommendation to buy,
> sell or hold TSLA or any other security.

## Headline result

In the base case, Tesla is worth about **$29 per share against a market price of $378.12 (−92%)**.

| Case | Value per share |
|---|---|
| Market price (24 Sep 2026) | $378.12 |
| Bull | ~$88 |
| **Base** | **$29.03** |
| Bear | ~$4 |
| Recession / downside | ~$3 |

- **Cost of equity:** 10.38% = 5.11% (10-year Treasury) + 1.17 (bottom-up beta) × 4.5% (equity risk premium).
  Tesla's observed beta of 1.75 would give 13.0%.
- **Terminal value:** 110% of the discounted cash-flow value, because free cash flow to equity (FCFE) is negative in
  2026–27 while Tesla spends more than $25B a year on capex.
- **What the market price implies:** for $378 to be correct, one of these would have to hold on its own:
  - cost of equity of about 3.6%
  - perpetual growth of about 9.8%
  - about $451B of robotaxi revenue by 2030

## Verification

- All 66 automated tests pass.
- The Streamlit app runs on live data with no errors on any page.
- In live mode, 176 stored historical values were checked against the SEC's XBRL data, and all matched.

## Architecture

The code is split into separate modules:

| Module | Role |
|---|---|
| `data_ingestion.py` | Loads the stored filing data; pulls live SEC and market data |
| `assumptions.py` | Central registry of every forecast assumption |
| `statements.py` | Income statement, balance sheet and cash flow statement |
| `checks.py` | Integrity checks for every forecast year |
| `valuation.py` | Cost of equity, FCFE discounting, terminal value |
| `scenarios.py` | Scenarios and sensitivities |
| `charts.py` | Charts |
| `excel_export.py` | Excel workbook |
| `app.py` | Streamlit app (seven pages) |

- **Assumptions:** every driver sits in one registry, labelled `history`, `guidance` or `judgment`, with its source,
  a rationale and per-scenario values. Every edit is logged in a revision history.
- **Balance sheet:** built from the forecast, with no plug. Balance-sheet cash comes only from the cash-flow statement.
  A $5B credit facility is drawn only if cash falls below a minimum of 15% of revenue.
- **Checks:** assets = liabilities + equity, cash ties between statements, roll-forwards for fixed assets, debt, leases
  and shares, the minimum-cash rule, and terminal growth below the cost of equity. A failed check blocks the valuation
  in both the app and the workbook.
- **Sensitivities:** every scenario, heat-map cell and tornado bar is a full re-run of the model; nothing is added together.
- **Excel export:** separate sheets for Sources, Assumptions, Historical Financials, Forecast, Valuation, Scenarios and
  Checks, plus a cover sheet with the disclaimer.

## Data sources

- **Filings:** 10-Ks for FY2023, FY2024 and FY2025, the Q2 2026 10-Q, and Tesla's delivery releases filed as 8-K
  exhibits. Every line item carries its accession number and page.
- **Market data:** share price, 10-year Treasury yield, and regression betas for Tesla and six peers (GM, Ford, Rivian,
  Lucid, Enphase, Fluence). All refresh live.
- **Fallback:** with the network off, the app runs on the bundled seed data, and the tests run offline.

## Judgment calls worth reviewing

- **Robotaxi revenue:** a separate, explicit line: $8B by 2030 in the base case. Optimus is not modelled.
- **Stock-based compensation** is added back in FCFE, following the requested formula. Turning that off lowers the value.
- **Bear and recession cases** assume Tesla cuts capex. Without that, the bear case breaks the minimum-cash rule even with
  the credit facility fully drawn, and the model refuses to value it.
- **Other judgments:** the 4.5% equity risk premium, the 15% minimum cash level, and GM and Ford debt figures that exclude
  their finance arms.

## Limits from Tesla's disclosures

- **Selling price by model:** Tesla gives no revenue or price by model, only "Model 3/Y" vs "Other models" deliveries.
  The model assumes other models sell at about 2x the Model 3/Y price.
- **Depreciation:** reported only by segment, so it is allocated across revenue lines to derive margins before depreciation.
- **Unreported items:** Tesla reports no robotaxi revenue and no minimum cash level, and gives capex guidance for 2026 only.
- **CEO award shares:** the 423.7M unearned 2025 CEO award shares are excluded from the share count by default; a toggle
  adds them.

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
python -m pytest -q
```
