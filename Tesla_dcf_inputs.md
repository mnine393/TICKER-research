# Tesla, Inc. (TSLA) — Lab 06: Sensitivity, Reverse DCF, and Conditional Recommendation

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Valuation Date:** September 1, 2026, 16:00 EDT (Market Close)  
**Target Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Primary Source:** Tesla, Inc. Form 10-K for the fiscal year ended December 31, 2025 (filed January 29, 2026; accession `0001628280-26-003952`)  

---

## 1. R — Company Input Table & Sourced Rows

Every row identifies the numerical value, unit, as-of date, classification, and exact SEC EDGAR filing locator.

| Row / Parameter | Value | Unit | As-of Date | Status | Exact Filing Locator & Sourcing Defense |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Starting FCFF** | **6,433.27** | USD millions | Dec 31, 2025 | Reported fact | **Tesla 2025 Form 10-K.** Formula: Operating cash flow + after-tax interest paid − capital expenditures. Sourced from: (1) **Item 8, Consolidated Statements of Cash Flows, p. 53** for operating cash flow ($14,747M) and capital expenditures ($8,527M); (2) **Supplemental Disclosures of Cash Flow Information, p. 53** for cash interest paid ($292M); (3) **Consolidated Statements of Operations, p. 50 & Note 14 (Income Taxes), p. 88** for income before taxes ($5,278M) and income-tax provision ($1,423M), yielding effective tax rate = 1,423 / 5,278 = 26.96%. After-tax interest paid = 292 × (1 − 0.2696) = $213.27M. Correct Starting FCFF = 14,747 + 213.27 − 8,527 = **$6,433.27M**. |
| **Growth, Years 1–5** | **8%, 6%, 5%, 4%, 3%** | decimal | Sep 1, 2026 | **Placeholder** | **Item 7, MD&A, pp. 31–37.** Unresolved forecast assumption in filing-only research. Training trajectory kept as an explicit fading placeholder (8% fading to 3%). |
| **WACC** | **10.0% (0.10)** | decimal | Sep 1, 2026 | **Placeholder** | **Unresolved cost of capital.** Brief estimate: 10-year Treasury risk-free rate ~4.2% + beta 1.4 × 5.0% ERP ≈ 11.2% cost of equity; after-tax cost of debt ~4.5%; weighted by market equity yields ~9.5%–10.0%. Training convention of 10.0% kept as placeholder. |
| **Terminal Growth (\(g\))** | **3.0% (0.03)** | decimal | Sep 1, 2026 | **Placeholder** | **Macroeconomic anchor.** Anchored to long-run nominal GDP growth (FRED series `A191RL1Q225SBEA`), strictly less than WACC. |
| **Non-Operating Cash** | **44,059.0** | USD millions | Dec 31, 2025 | Reported fact | **Tesla 2025 Form 10-K, Item 8, Consolidated Balance Sheets, p. 49; Note 4, p. 70.** Cash and cash equivalents of $16,513M + short-term investments of $27,546M = $44,059M total liquid non-operating assets. |
| **Debt** | **8,376.0** | USD millions | Dec 31, 2025 | Reported fact | **Tesla 2025 Form 10-K, Item 8, Consolidated Balance Sheets, p. 49; Note 9 (Debt), pp. 73–74.** Net carrying value of debt and finance leases ($1,640M current + $6,736M long-term). Unpaid principal is $8,177M ($3M recourse, $8,174M non-recourse). |
| **Diluted Shares** | **3,528.0** | millions of shares | Dec 31, 2025 | Reported fact | **Tesla 2025 Form 10-K, Item 8, Note 4—Earnings per Share, p. 61.** FY2025 diluted weighted-average shares: 3,225M basic common shares + 303M dilutive stock-based awards. |
| **Observed Market Price** | **$356.09** | USD per share | Sep 1, 2026 | Market quote | **Nasdaq Global Select Market (`TSLA`) closing price** as of September 1, 2026, 16:00 EDT. Implied market equity cap: $1,256,285.52M ($1.256T); implied enterprise value: $1,220,602.52M ($1.221T). |

*Note on non-common claims: Tesla also reports $58M of redeemable noncontrolling interests and $670M of noncontrolling interests ($728M total, p. 49). If treated as debt-like claims, net cash adjusts from +$35,683M to +$34,955M.*

---

## 2. I — Company Model Execution (`python dcf.py`)

Ran via terminal command `python dcf.py` in `02_Valuation/`:

```text
FCFF Year 1: 6947.9316
FCFF Year 2: 7364.8075
FCFF Year 3: 7733.0479
FCFF Year 4: 8042.3698
FCFF Year 5: 8283.6409
Present value of the explicit FCFF: 28849.4086
Terminal value at Year 5: 121887.8587
Present value of the terminal value: 75682.7705
Enterprise value: 104532.1790
Equity value: 140215.1790
Value per diluted share: 39.7435
Present value of the terminal value as a share of enterprise value: 0.7240
```

---

## 3. V — Reasonableness Check

* **Model Value per Diluted Share:** **$39.74** (up from $38.67 with corrected starting FCFF).
* **Observed Market Price:** **$356.09**
* **Reasonableness Band Evaluation:**  
  The 0.5× to 2.0× reasonableness band corresponds to **$19.87 to $79.49**. Today's observed market price of $356.09 is **9.0× the model value** (previously 9.2×), placing it **far outside the 0.5× to 2.0× reasonableness band**.
* **Input Distrusted Most & Why:**  
  I distrust the **`GROWTH_RATES`** trajectory most (and its static relation to `STARTING_FCFF`).  
  **Reason:** The baseline model applies a fading automotive OEM growth trajectory (8% fading to 3%), generating only $8.28B of FCFF in Year 5. However, the market at $356.09 (~$1.26T market cap) is pricing Tesla not as an auto manufacturer, but as an unproven software platform and autonomous robotics monopoly (Robotaxi, FSD, Optimus). Furthermore, in Item 7 MD&A (p. 32), management guided that **2026 capex will exceed $20 billion** (up from $8.53B in 2025). That massive reinvestment will severely suppress near-term FCFF (likely driving Year 1 cash flow close to zero or negative), requiring an exponential, non-linear explosion in later-year cash flows that standard linear manufacturing growth assumptions fail to capture.

---

## 4. E — Sensitivity Grid and Reverse DCF

### A. Training-Case Pre-Check Verification
Before running the company model, the engine was verified against the training inputs (`STARTING_FCFF = 100`, WACC 10%, g 3%, Cash 50, Debt 300, Shares 50, Target Price $30.00):
* **Training Grid Output:** Matches cell-for-cell:
  * WACC 9%: g 2% = $28.60 | g 3% = $32.94 | g 4% = $39.02
  * WACC 10%: g 2% = $24.36 | g 3% = $27.50 | g 4% = $31.69
  * WACC 11%: g 2% = $21.06 | g 3% = $23.41 | g 4% = $26.44
* **Training Reverse DCF at $30.00:** Solved uniform growth shift = **+1.78 percentage points (+0.0178)** holding WACC (10%), g (3%), cash ($50M), debt ($300M), and shares (50M) fixed.

---

### B. Target Company Sensitivity Grid: Tesla, Inc. (`TSLA`)

```text
--- SENSITIVITY GRID: VALUE PER DILUTED SHARE ($) ---
WACC \ g     |      2.0% |      3.0% |      4.0%
-------------+-----------+-----------+----------
  9.0%       |     40.75 |     44.71 |     50.25
 10.0%       |     36.88 |     39.74 |     43.56
 11.0%       |     33.87 |     36.02 |     38.78
```

* **Center Cell (Base Case):** **$39.74** (WACC 10.0%, terminal growth 3.0%).
* **Monotonicity & Direction:** Holds across all cells — value strictly falls moving down (as WACC increases from 9% to 11%) and strictly rises moving right (as terminal growth increases from 2% to 4%).
* **Range Read from Corners:** **$33.87** (bearish corner: WACC 11%, g 2%) to **$50.25** (bullish corner: WACC 9%, g 4%).

---

### C. Target Company Reverse DCF Analysis

```text
--- REVERSE DCF ---
Target share price: $356.09
Held fixed:
  - Starting FCFF: 6433.27 USD million
  - Baseline growth rates: [0.08, 0.06, 0.05, 0.04, 0.03]
  - WACC: 10.00%
  - Terminal growth: 3.00%
  - Non-operating cash: 44059.00 USD million
  - Debt: 8376.00 USD million
  - Diluted shares: 3528.00 million
Search bracket (uniform shift): [-5.00%, +10.00%]
No solution in that bracket: target price $356.09 cannot be reached inside [-5.00%, +10.00%]. (Bracket yields $34.06 to $54.60).
```

* **Bracket Result:** At the assigned bracket of `[-5.0%, +10.0%]`, the model correctly reports **no solution**, yielding a maximum valuation of only **$54.60** (up from $52.99).
* **Market-Implied Expectation (Expanded Bracket):**  
  Expanding the upper bound demonstrates that to equate model value to the observed market price of **$356.09**, the required uniform growth shift is **+72.77 percentage points (+0.7277)** (moderated from +74.13 percentage points).  
  * **Implied Annual Growth Rates:** **80.77%, 78.77%, 77.77%, 76.77%, 75.77%**
  * **Implied Year 5 FCFF:** **$114,833M (~$114.8B)** (a 17.8x increase from FY2025 cash flow).
  * **Interpretation:** This shift is not proof of mispricing; rather, it quantifies the extraordinary hurdle rate of cash-flow expansion already priced into TSLA common shares.

---

## 5. Conditional Recommendation

> **Recommendation: Watch / Defer.**  
> **Initiate if:** The growth expectations priced into the stock moderate to levels supportable by tangible manufacturing and energy cash flows — specifically, if market price falls into the fundamental range below **$40.00 to $55.00 per share**, OR if Tesla reports verifiable, high-margin software/Robotaxi fleet revenues with operating margins sustained above 30% that justify raising the five-year FCFF growth trajectory by more than 50 percentage points.  
> **Monitor:** **Quarterly automotive gross margin excluding regulatory credits** and **full-year 2026 Capex versus Operating Cash Flow** (to confirm whether the guided $20B+ capex drives free cash flow negative in Year 1).
