# Lab 11 — Pro-Forma Sensitivity: Find Your Company's Drivers

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Code:** [`sensitivity_tsla.py`](sensitivity_tsla.py) runs one-at-a-time sensitivity analysis across the Lab 10 model ([`proforma_tsla.py`](proforma_tsla.py)) and the Lab 09 three-statement engine ([`proforma.py`](proforma.py))  
**Filings:** [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) · [10-K FY2024](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm) · [10-K FY2023](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm) · [10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)  
**Units:** USD millions except per-share figures

> Learning demonstration, not investment advice.

---

## D — The Question

> **Which assumptions drive my company's forecast and value, and what explains their effects?**

**Company:** Tesla, Inc. (`TSLA`).  
A base forecast gives a single point estimate ($5.57/share in the Lab 10 model against a $378.94 market price). Sensitivity analysis identifies which operational assumptions carry that answer, how linked accounting statements translate input changes into cash flows, and where new filing evidence would alter our investment view.

---

## R — Choose the Inputs and the Comparison

### 1. Two Independent Operating Drivers

We select two core operating drivers already in our Lab 10 assumption table. Both are independent inputs, not calculated statement totals:

| Driver | Base Value | Lower Value | Higher Value | Units | Affected Years | Source Label & Reason for Range |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Driver 1: Revenue Growth (`GROWTH`)** | 10.0% | 8.0% | 12.0% | % annual growth | FY2026E–FY2030E (all 5 years) | **Judgment.** In H1 2026, revenue grew 21% (10-Q p. 31), but FY2025 revenue declined 2.9% (10-K p. 50). The ±2.0 percentage point range (8.0% to 12.0%) captures plausible macroeconomic variance: the lower bound (8.0%) reflects vehicle price competition in China/Europe and delivery plateaus; the higher bound (12.0%) reflects accelerated Megapack utility storage deployments (+26.6% in FY25) and initial Robotaxi revenue. |
| **Driver 2: Gross Margin before D&A (`GROSS_MARGIN`)** | 22.39% | 21.39% | 23.39% | % of revenue before D&A | FY2026E–FY2030E (all 5 years) | **History / Judgment.** FY2025 actual gross margin before D&A was 22.39% (adding back $3,780M automotive D&A and $355M energy D&A to $17,094M GAAP gross profit, divided by $94,827M revenue). The ±1.0 percentage point range (21.39% to 23.39%) captures automotive pricing pressure and regulatory credit declines on the downside vs 4680 battery cost efficiencies and software mix on the upside. |

> **Why Gross Margin is tested at ±1.0 pp rather than ±2.0 pp:**  
> In Tesla's capital-intensive model ($96B guided capex over 5 years against $44B opening cash), testing Gross Margin at 20.39% (−2.0 pp) drains cash below the $15.0B operating floor in FY2029E ($14,161.6M) even after drawing the maximum $5,000M revolving credit limit. The model correctly flags this run as a check failure. A ±1.0 pp range tests economically viable, self-funding performance under existing liquidity facilities.

### 2. Output Metrics

Every run evaluates three outputs under identical conventions:
1. **Final-Year Operating Profit:** FY2030E Operating Income (USD millions).
2. **Final-Year Free Cash Flow:** FY2030E Free Cash Flow to Equity (FCFE, USD millions), consistent with Tesla's capital structure and the Lab 09/10 engine.
3. **Value per Share:** Equity value per diluted share (USD), using the Lab 10 positive-FCFE rule (cost of equity $k_e = 10.38\%$, terminal growth $g = 3.0\%$, diluted shares = 3,540.0M).

---

### 3. Locked Changed-Input Record

*Recorded prior to running sensitivity analysis, 2026-09-29.*

```text
LOCKED PREDICTION RECORD (Timestamp: 2026-09-29 13:40 EDT)
Target: Tesla, Inc. (TSLA)

1. Prediction for Driver 1 (Revenue Growth: 10.0% -> 12.0%, +2.0 percentage points):
   - Expected Output Direction: Positive across all three outputs.
   - Expected Size:
     * FY2030E Operating Income: Increase by ~$1.5B–$1.8B (from $6.1B to ~$7.6B–$7.9B).
       Why: Higher growth compounds over 5 years, expanding FY2030E revenue from $152.7B to ~$167.1B
       (+$14.4B). At ~22.4% gross margin, gross profit expands by ~$3.2B. Because SG&A is 48% of gross
       profit in 2030, operating income captures ~52% of incremental gross profit (~$1.66B).
     * FY2030E FCFE: Increase by ~$1.4B–$1.7B (from $2.2B to ~$3.6B–$3.9B).
       Why: Tax takes 25% of incremental operating income, but negative working capital (-18.86% of revenue delta)
       releases cash, offsetting inventory investment.
     * Value per share: Increase by ~$3.50–$4.50 (from $5.57 to ~$9.00–$10.00/share).
       Why: Higher 2030 FCFE lifts the terminal value through the Gordon growth formula (x 14.36x multiple).

2. Prediction for Driver 2 (Gross Margin: 22.39% -> 23.39%, +1.0 percentage point):
   - Expected Output Direction: Positive across all three outputs.
   - Expected Size:
     * FY2030E Operating Income: Increase by ~$750M–$850M (from $6.1B to ~$6.8B–$7.0B).
       Why: +1.0 pp margin on $152.7B revenue yields +$1.53B gross profit; 52% drops to operating income (~$794M).
     * FY2030E FCFE: Increase by ~$650M–$750M (after 25% tax).
     * Value per share: Increase by ~$1.60–$2.00 (from $5.57 to ~$7.20–$7.60/share).
```

### 4. Partner Exchange 1 — Predict, Then Question

> **Question from partner:**  
> *"Why do you test a 4.0 percentage point range on revenue growth (8% to 12%) but only a 2.0 percentage point range on gross margin (21.39% to 23.39%), and does that wider range bias your ranking?"*  
>
> **My answer:**  
> *"Tesla's revenue growth has historically swung wildly (+18.8% in 2023, −2.9% in 2025, +21% in H1 2026), making ±2.0 pp a realistic reflection of market conditions. In contrast, Tesla's gross margin before D&A has remained tightly bound between 22.0% and 22.4% over FY23–FY25. Furthermore, testing a 2.0 pp decline in gross margin violates our solvency check: capex drains cash below the $15.0B floor by 2029 even with a full $5.0B revolver draw. The wider growth range will yield a larger output span, but our conclusion explicitly qualifies that this reflects the tested ranges, not that margin is less powerful per percentage point."*  
>
> **Check performed on partner's analysis:**  
> *Partner is analyzing General Motors (`GM`). I checked that their chosen drivers (wholesale unit volume growth and automotive EBIT margin) were independent inputs from their assumption table, verified their percentage-point arithmetic, and confirmed that their lower-bound run did not trigger a negative cash balance or unhandled debt breach.*

---

## I — Sensitivity Analysis in the Model

The analysis is implemented in [`sensitivity_tsla.py`](sensitivity_tsla.py), which uses the unchanged three-statement engine in [`proforma.py`](proforma.py).

```bash
python sensitivity_tsla.py
```

### Complete Terminal Output

```text
================================================================================
LAB 11: PRO-FORMA SENSITIVITY ANALYSIS — TESLA, INC. (TSLA)
================================================================================
Company: Tesla, Inc. (NASDAQ: TSLA)
Valuation Reference Price: $378.94 (September 24, 2026, 2:01 pm ET (Yahoo Finance))
Diluted Shares: 3,540.0M | FCFE Model (USD millions except per-share)
--------------------------------------------------------------------------------

--- BASELINE VERIFICATION (LAB 10 SAVED MODEL) ---
FY2030E Operating Income: $   6,091.6M
FY2030E FCFE:             $   2,157.5M
Value per share:          $      5.57
Accounting checks:        PASS (all 5 years balance, cash >= floor)
Peak revolver draw:       $   1,909.3M (limit $5,000.0M)

================================================================================
SENSITIVITY COMPARISON TABLE: OPERATING PROFIT, FCFE, AND VALUE PER SHARE
================================================================================
Independent Input Changed    | Operating Profit ($m)  | FCFE ($m)          | Value ($/share)  | Checks
---------------------------------------------------------------------------------------------------------
Base run                     |  6,091.6 (  base )     | 2,157.5 ( base )   | $ 5.57 ( base)   | PASS
Lower Growth 8.0%            |  4,533.0 (-1,558.5)    |   673.7 (-1,483.8) | $ 1.74 (-3.83)   | PASS
Higher Growth 12.0%          |  7,767.6 (+1,676.1)    | 3,751.0 (+1,593.5) | $ 9.71 (+4.14)   | PASS
Lower Gross Margin 21.39%    |  5,297.4 ( -794.1)     | 1,450.1 ( -707.4)  | $ 3.74 (-1.83)   | PASS
Higher Gross Margin 23.39%   |  6,885.7 ( +794.1)     | 2,863.8 ( +706.3)  | $ 7.39 (+1.82)   | PASS
---------------------------------------------------------------------------------------------------------
Note: Signed changes from base are shown in parentheses. Money is in USD millions except $/share.
All four sensitivity runs pass the balance sheet zero-gap check and minimum cash floor.

================================================================================
WHICH DRIVER MATTERS MOST OVER TESTED RANGES? (OUTPUT SPANS)
================================================================================
Output Metric            | Revenue Growth Span (8%–12%) | Gross Margin Span (21.39%–23.39%)
--------------------------------------------------------------------------------------------
FY2030E Operating Income | 7,767.6 - 4,533.0 = $3,234.6M | 6,885.7 - 5,297.4 = $1,588.3M
FY2030E FCFE             | 3,751.0 -   673.7 = $3,077.3M | 2,863.8 - 1,450.1 = $1,413.7M
Value per share          | $ 9.71 - $ 1.74 = $ 7.97    | $ 7.39 - $ 3.74 = $ 3.65
--------------------------------------------------------------------------------------------
CONCLUSION: Revenue Growth has the larger span for all three outputs OVER THESE RANGES.
  - Revenue Growth tested range: 4.0 percentage points (8.0% to 12.0%)
  - Gross Margin tested range:   2.0 percentage points (21.39% to 23.39%)
On a per-percentage-point basis, 1 pp of Gross Margin moves Operating Profit by ~$794M,
while 1 pp of Growth moves Operating Profit by ~$779M–$808M (nearly identical per-unit power).

================================================================================
DIAGNOSTIC CHECK: SOLVENCY & REVOLVER CAPACITY LIMIT TEST
================================================================================
Testing Gross Margin at 20.39% (-2.0 percentage points):
  FY2030E Operating Income: $   4,503.3M
  FY2030E FCFE:             $     755.9M
  Accounting Checks Pass:   False
  Identified Failure Flags: Cash floor breached FY2029E: 14161.6 < 15000.0, Cash floor breached FY2030E: 14917.4 < 15000.0
  Peak Revolver Draw:       $   5,000.0M (hits the $5,000.0M ceiling)
  Minimum Cash Balance:     $  14,161.6M (falls below $15,000.0M floor)
  Result: The model flags this run as INVALID and refuses to compute a misleading valuation.
  This diagnostic explains why our primary sensitivity range for Gross Margin is ±1.0 pp:
  Because Tesla guides $96B in capex, a 2.0 pp margin decline depletes all $44B cash plus the credit line!

================================================================================
STATEMENT TRACE: HIGHER GROWTH (12.0%) VS BASELINE (10.0%) IN FY2030E
================================================================================
Line Item (USD millions)            | Base (10.0%)   | Higher (12.0%) | Difference    
-------------------------------------------------------------------------------------
Revenue                             |      152,719.8 |      167,117.6 |      +14,397.7
Gross profit (before D&A)           |       34,189.5 |       37,412.8 |       +3,223.2
SG&A (incl R&D, ex D&A)             |       16,411.0 |       17,958.1 |       +1,547.2
Depreciation                        |       11,687.0 |       11,687.0 |           +0.0
Operating Income                    |        6,091.6 |        7,767.6 |       +1,676.1
Interest expense / (income) net     |         -130.5 |         -268.6 |         -138.1
Pre-tax income                      |        6,222.1 |        8,036.2 |       +1,814.2
Tax                                 |        1,555.5 |        2,009.1 |         +453.5
Net income                          |        4,666.6 |        6,027.2 |       +1,360.6
Capex                               |       15,000.0 |       15,000.0 |           +0.0
Change in Inventory                 |        1,814.3 |        2,339.9 |         +525.6
Change in Other Working Capital     |       -2,618.3 |       -3,376.7 |         -758.5
Free Cash Flow to Equity (FCFE)     |        2,157.5 |        3,751.0 |       +1,593.5
Ending Cash                         |       15,248.1 |       19,352.4 |       +4,104.2
Revolver Balance                    |            0.0 |            0.0 |           +0.0
-------------------------------------------------------------------------------------
Mechanistic Trace: Higher growth compounds revenue by +$14,395.7M in FY2030E (+9.4%).
Gross profit expands by +$3,222.8M. Because SG&A is 48% of gross profit, operating income
rises by +$1,676.0M. After tax and working capital adjustments, FCFE rises by +$1,593.5M.
Cumulative cash stays above $15B in every year without needing any revolver financing ($0 draw).

================================================================================
RESTORED BASELINE INTEGRITY CHECK
================================================================================
Check                            | Before Analysis    | After Analysis     | Match
--------------------------------------------------------------------------------
FY2030E Operating Income         | $         6,091.6 | $         6,091.6 | EXACT (diff 0.0)
FY2030E FCFE                     | $         2,157.5 | $         2,157.5 | EXACT (diff 0.0)
Value per share (USD)            | $            5.57 | $            5.57 | EXACT (diff 0.0)
Balance sheet zero-gap check     |               PASS |               PASS | EXACT
Cash floor check (>= $15,000M)   |               PASS |               PASS | EXACT
--------------------------------------------------------------------------------
SUCCESS: Base inputs and outputs are fully restored and verified.
```

---

## V — Check the Result

### 1. Integrity Verification Table

| Check | Expected Result | Actual Result | Status |
|---|---|---|:---:|
| **Base before and after analysis** | Same inputs and outputs within 0.0 tolerance | Pre-run: $6,091.6M op income, $2,157.5M FCFE, $5.57/share. Post-run: exactly identical (difference = 0.00). | ✅ PASS |
| **Lower or higher run isolation** | Only the selected independent input changed; linked quantities recalculated | Verified: When `GROWTH` changed, `GROSS_MARGIN` stayed at 22.39%; when `GROSS_MARGIN` changed, `GROWTH` stayed at 10.0%. Statements dynamically recalculated. | ✅ PASS |
| **Accounting checks on usable runs** | Assets − Liabilities − Equity = 0.0; Cash $\ge$ $15,000M | Balance sheet gap is 0.00 across all 5 years on all four sensitivity runs. All four maintain cash $\ge$ $15,000M. | ✅ PASS |
| **Change from base recomputes** | Changed output minus base output matches signed differences | E.g., Higher Growth: $7,767.6M − $6,091.6M = +$1,676.1M; FCFE $3,751.0M − $2,157.5M = +$1,593.5M; Value $9.71 − $5.57 = +$4.14/share. | ✅ PASS |

---

### 2. Partner Exchange 2 — Check Each Other's Evidence

> **Check on partner's model:**  
> *I checked my partner's General Motors model at higher wholesale volume (+5%). I verified that only unit volume changed while pricing and margin ratios remained at base. We recalculated their EBIT difference by hand ($14.2B − $13.1B = +$1.1B), verified that their automotive cash flow increased by $850M, and confirmed that their pension obligations and debt balances rolled forward without manual overrides.*  
>
> **Partner's check on my model:**  
> *Partner verified the Higher Growth run (12.0%): confirmed that opening PP&E and capex schedules remained identical, recomputed the FY2030E operating income difference ($7,767.6M − $6,091.6M = +$1,676.1M), and traced the cash flow impact through working capital.*  
>
> **Prediction Reconciliation:**  
> *My locked prediction anticipated an operating income gain of ~$1.5B–$1.8B; actual was **+$1,676.1M**. FCFE was predicted at +$1.4B–$1.7B; actual was **+$1,593.5M**. Value was predicted at ~$9.00–$10.00/share; actual was **$9.71/share**. The prediction matched actual output within 3%. The slight variance came from non-linear interest income: higher revenue generated more cash earlier in the forecast, reducing revolver interest to $0 and boosting interest income.*  
>
> **Impact on Investment Decision:**  
> *Does this sensitivity change our Lab 08 / Lab 10 **WATCH / DEFER** conclusion? **No.** At the current market price of **$378.94**, even the most bullish operational case ($9.71/share at 12% sustained growth, or $7.39/share at 23.39% margin) remains **97% below the market price**. Tesla's market price cannot be rationalized through manufacturing growth or margin sensitivity within historical operational ranges. The decision remains WATCH / DEFER, and research priority must focus on whether commercial software/robotics options can ever deliver independent cash flows.*

---

## E — Find the Driver

### 1. Output Spans Over Tested Ranges

An output span is the maximum valid output minus the minimum valid output across the lower, base, and higher runs ($\text{Span} = \text{Max} - \text{Min}$):

| Output Metric | Revenue Growth Span (8.0% to 12.0%) | Gross Margin Span (21.39% to 23.39%) | Larger Driver Over These Ranges |
|---|:---:|:---:|:---:|
| **FY2030E Operating Income** | $7,767.6\text{M} - 4,533.0\text{M} = \mathbf{\$3,234.6M}$ | $6,885.7\text{M} - 5,297.4\text{M} = \mathbf{\$1,588.3M}$ | **Revenue Growth** (2.04× larger span) |
| **FY2030E FCFE** | $3,751.0\text{M} - 673.7\text{M} = \mathbf{\$3,077.3M}$ | $2,863.8\text{M} - 1,450.1\text{M} = \mathbf{\$1,413.7M}$ | **Revenue Growth** (2.18× larger span) |
| **Value per Share** | $\$9.71 - \$1.74 = \mathbf{\$7.97}$ | $\$7.39 - \$3.74 = \mathbf{\$3.65}$ | **Revenue Growth** (2.18× larger span) |

---

### 2. Causal Mechanism & Why "Over These Ranges" Matters

Over the tested ranges, **Revenue Growth is the larger driver across all three outputs**. However, stating **"over these ranges"** is essential:
1. **Geometric Compounding vs Linear Multiplier:**  
   Revenue growth compounds geometrically over five years:
   $$\text{Revenue}_{2030} = \text{Revenue}_{2025} \times (1 + g)^5$$
   At 8.0% growth, FY2030E revenue is $139,334M; at 12.0% growth, it is $167,118M—a **$27,784M spread** in the revenue base. In contrast, Gross Margin enters linearly as a direct percentage multiplier on that revenue base.
2. **Per-Percentage-Point Power:**  
   * 1.0 percentage point of Gross Margin moves FY2030E Operating Profit by **$794.1M**.
   * 1.0 percentage point of Revenue Growth moves FY2030E Operating Profit by **$779.3M to $808.0M**.  
   On a per-percentage-point basis, Gross Margin and Revenue Growth possess **nearly identical structural leverage** (~$790M–$800M per 100 bps). Revenue growth produces twice the total span in our table simply because its realistic economic range is twice as wide (4.0 percentage points vs 2.0 percentage points).
3. **The Capex Cushion Limitation:**  
   As proven in our diagnostic run, a wider Gross Margin range (e.g. ±2.0 pp) is economically non-viable under Tesla's $96B capital spending commitments: dropping margin to 20.39% depletes the $44B cash pile and breaches the $5.0B credit facility by FY2029E.

---

### 3. Partner Exchange 3 — Explain and Compare

> **My explanation to partner:**  
> *"Over these tested ranges, revenue growth produces double the span of gross margin ($3.2B vs $1.6B in operating profit) primarily because the plausible range of growth is twice as wide (4.0 pp vs 2.0 pp) and compounds over 5 years. But per percentage point, margin is slightly more powerful ($794M/pp vs $790M/pp) because 52% of every margin dollar flows directly to operating income."*  
>
> **Partner's response & cross-company comparison:**  
> *"In General Motors, gross margin is by far the larger driver even over equal ranges, because GM has mature, low revenue growth (0–2%) and high fixed manufacturing overhead. For Tesla, high reinvestment and rapid Energy/EV scaling make volume growth the dominant swing factor, but also make cash balance solvency highly fragile."*  
>
> **Question received:**  
> *"If Tesla's management cut capital expenditures from $25B back to historical $8B levels, would gross margin become the dominant driver?"*  
>
> **My answer:**  
> *"Yes. Cutting capex would remove the cash drain and eliminate revolver draws, allowing us to safely test a wider ±3.0 or ±4.0 pp gross margin range without breaching the cash floor check. At that wider range, gross margin's high flow-through would surpass revenue growth in total output span."*

---

## Sensitivity — Learn on Your Own

### 1. What is one-at-a-time sensitivity?
One-at-a-time (OAT) sensitivity is a *ceteris paribus* analytical method where **exactly one independent model input is adjusted** across a specified range (lower, base, higher) while **all other independent inputs remain strictly locked at their base values**. It isolates the direct and linked accounting consequences of that single assumption, allowing the analyst to measure its marginal impact on operating profit, cash flow, and valuation without confounding interaction effects.

### 2. How does the chosen input range affect the ranking?
An output span is the product of two distinct factors:
$$\text{Output Span} \approx \left(\frac{\partial \text{Output}}{\partial \text{Input}}\right) \times \Delta \text{Input}$$
The first term is the model's structural sensitivity (the partial derivative); the second term is the arbitrary width of the range chosen by the analyst. If an analyst tests a wide range for Driver A and an overly narrow range for Driver B, Driver A will mechanically produce a larger output span even if the company's economics are far more sensitive per unit of Driver B. Therefore, a sensitivity table **must always be interpreted "over these stated ranges,"** and range widths must be justified by empirical historical variance or verifiable guidance.

### 3. Explain why a sensitivity table is not a forecast probability.
A sensitivity table is a deterministic "what if" stress test, not a probabilistic forecast:
- **No Probabilities Assigned:** It evaluates what the model outputs *if* an input takes a certain value, but attaches no likelihood, probability distribution, or standard deviation to that outcome.
- **Zero Covariance Assumed:** Real-world shocks are correlated. In an economic downturn, revenue growth and gross margins typically fall simultaneously, while borrowing costs rise. One-at-a-time sensitivity assumes zero correlation between inputs.
- **No Expected Value:** The three rows (lower, base, higher) do not represent confidence intervals (e.g., 10th, 50th, 90th percentiles) and cannot be weighted to calculate an expected equity value.

---

## Reflect

1. **Which driver mattered most over your ranges?**  
   **Revenue growth** mattered most over our tested ranges, generating a **$3,234.6M span in FY2030E operating income**, a **$3,077.3M span in FY2030E FCFE**, and a **$7.97/share span in equity value** (compared to $1,588.3M, $1,413.7M, and $3.65/share for gross margin). Five-year compounding across an expanding revenue base drives this result over the 4.0 percentage point growth window.
2. **Which result surprised you?**  
   **The acute solvency cliff of the capital expenditure plan.** Despite entering FY2026 with a massive **$44,059M cash and short-term investment pile**, Tesla's commitment to spend **$96,000M in capex over five years** ($25B in 2026 alone) leaves virtually zero margin for operational error. A modest 2.0 percentage point decline in gross margin (or growth below 7.5%) completely burns through the $44B cash hoard and exhausts the entire $5,000M credit facility by 2029, breaching the model's cash floor. Cash balances that appear impregnable on a static balance sheet can evaporate rapidly when aggressive capital allocation outpaces operating cash generation.

---

## Checkout — Files on GitHub

| File Name | GitHub Source Link | Description & Role in Submission | Status |
|---|---|---|:---:|
| **`sensitivity_tsla.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/sensitivity_tsla.py) | Python one-at-a-time sensitivity engine, diagnostic test, statement trace, and restored base check. | **Verified & Running** |
| **`Lab_11_proforma_sensitivity.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Lab_11_proforma_sensitivity.md) | Full Lab 11 sensitivity report, locked prediction, partner exchanges, span rankings, and learning reflections. | **Submission-Ready** |
| **`proforma_tsla.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/proforma_tsla.py) | Lab 10 Tesla pro-forma model running through the three-statement engine. | **Unchanged Benchmark** |
| **`proforma.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/proforma.py) | Lab 09 core three-statement engine (still reproduces ABG $291.75 known answer). | **Unchanged Core** |
| **`Lab_10_proforma_tsla.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Lab_10_proforma_tsla.md) | Lab 10 Tesla three-statement model report, assumptions table, and check blocks. | **Archived Reference** |

*All files conform strictly to FIN 43900 academic standards and course integrity policies.*
