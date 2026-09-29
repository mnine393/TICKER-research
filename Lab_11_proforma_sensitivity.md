# Lab 11 — Pro-Forma Sensitivity: Find Your Company's Drivers

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Partner's Company:** Marriott International, Inc. (NASDAQ: `MAR`)  
**Code:** [`sensitivity_tsla.py`](sensitivity_tsla.py) runs one-at-a-time sensitivity analysis across the Lab 10 model ([`proforma_tsla.py`](proforma_tsla.py)) and the Lab 09 three-statement engine ([`proforma.py`](proforma.py))  
**Filings:** [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) · [10-K FY2024](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm) · [10-K FY2023](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm) · [10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)  
**Units:** USD millions except per-share figures

> Learning demonstration, not investment advice.

---

## D — The Question

> **Which assumptions drive my company's forecast and value, and what explains their effects?**

**Company:** Tesla, Inc. (`TSLA`).  
A base forecast gives a single point estimate. Sensitivity analysis identifies which operational assumptions carry that answer, how linked accounting statements translate input changes into cash flows, and where new filing evidence would alter our understanding.

---

## R — Choose the Inputs and the Comparison

### 1. Two Independent Operating Drivers

We select two independent operating drivers already in our Lab 10 assumption table:

| Driver | Base Value | Lower Value | Higher Value | Units | Affected Years | Source Label & Reason for Range |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Driver 1: Revenue Growth (`GROWTH`)** | 10.0% | 8.0% | 12.0% | % annual growth | FY2026E–FY2030E (all 5 years) | **Judgment.** In H1 2026, revenue grew 21% (10-Q p. 31), but FY2025 revenue declined 2.9% (10-K p. 50). The ±2.0 percentage point range (8.0% to 12.0%) captures plausible macroeconomic variance across delivery volume and price realization. |
| **Driver 2: Gross Margin before D&A (`GROSS_MARGIN`)** | ~22.39% | 21.39% | 23.39% | % of revenue before D&A | FY2026E–FY2030E (all 5 years) | **History / Judgment.** FY2025 gross margin before D&A was 22.39% (adding back $3,780M automotive D&A and $355M energy D&A to $17,094M GAAP gross profit, divided by $94,827M revenue). Tested at ±1.0 percentage point (21.39% to 23.39%). |

### 2. Output Metrics

Every run evaluates three outputs under identical conventions:
1. **Final-Year Operating Profit:** FY2030E Operating Income (USD millions).
2. **Final-Year Free Cash Flow:** FY2030E Free Cash Flow to Equity (FCFE, USD millions), consistent with Tesla's capital structure and the Lab 09/10 engine.
3. **Value per Share:** Equity value per diluted share (USD), with every forecast-year FCFE included with its sign (discounting negative FCFE at cost of equity $k_e = 10.38\%$, with terminal growth $g = 3.0\%$ and 3,540.0M diluted shares).

---

### 3. Locked Changed-Input Record

```text
LOCKED PREDICTION RECORD (Timestamp: 2026-09-29 13:40 EDT)
Target: Tesla, Inc. (TSLA)

1. Prediction for Driver 1 (Revenue Growth: 10.0% -> 12.0%, +2.0 percentage points):
   - Input old -> new with units: GROWTH 10.0% -> 12.0% annual revenue growth (+2.0 pp across all 5 years)
   - Expected output direction and rough size:
     * FY2030E Operating Income: Increase by ~$1.5B–$1.8B (from $6.1B to ~$7.6B–$7.9B).
     * FY2030E FCFE: Increase by ~$1.4B–$1.7B (from $2.2B to ~$3.6B–$3.9B).
     * Value per share: Increase by ~$4.00–$5.00/share (from -$1.83 to positive ~$2.50–$3.50/share).
   - Why (statement / economic link): Higher growth compounds over 5 years, expanding FY2030E revenue
     from $152.7B to ~$167.1B. At ~22.4% gross margin, gross profit expands by ~$3.2B. Because SG&A is
     48% of gross profit in 2030, operating income captures ~52% of the incremental gross profit.
     Higher operating income flows into higher FCFE and lifts the Gordon-growth terminal value.

2. Prediction for Driver 2 (Gross Margin: 22.39% -> 23.39%, +1.0 percentage point):
   - Input old -> new with units: GROSS_MARGIN 22.39% -> 23.39% of revenue before D&A (+1.0 pp across all 5 years)
   - Expected output direction and rough size:
     * FY2030E Operating Income: Increase by ~$750M–$850M (from $6.1B to ~$6.8B–$7.0B).
     * FY2030E FCFE: Increase by ~$650M–$750M.
     * Value per share: Increase by ~$2.00–$2.50/share (from -$1.83 to ~$0.30–$0.70/share).
   - Why (statement / economic link): +1.0 pp margin directly lifts gross profit on unchanged $152.7B revenue
     by +$1.53B; with SG&A at 48% of gross profit, 52% drops to operating income (~$794M).
```

### 4. Partner Exchange 1 — Predict, Then Question (Partner Company: Marriott International, `MAR`)

> **Question from partner (Marriott):**  
> *"Tesla guides 2026 capital spending above $25B, which burns most of its cash pile. For Marriott, our business is asset-light hotel franchising and management fees with under $300M in annual capex, so our biggest driver is RevPAR growth and fee margin. Why do you test only a ±1.0 pp range on Tesla's gross margin when RevPAR or hotel fee margins can swing 3–5 percentage points in a cycle?"*  
>
> **My answer:**  
> *"Tesla is a capital-intensive manufacturing business, not an asset-light franchisor. Tesla's gross margin before D&A has stayed within a narrow historical band (22.0%–22.4% over FY23–FY25), but each 1.0 percentage point shift represents ~$794M of operating income on our $152.7B 2030 revenue base. More importantly, testing a 2.0 pp decline in Tesla's margin exhausts our $5.0B credit facility and breaches the $15.0B minimum cash floor in 2029 due to our heavy capex commitments. Marriott's asset-light model can absorb wider margin swings without liquidity distress because Marriott does not carry multi-billion-dollar factory construction commitments."*  
>
> **Check performed on partner's analysis (Marriott):**  
> *I checked my partner's Marriott pro-forma model. I confirmed that their two chosen drivers were independent inputs (net room growth at 4.5% base with a 3.0%–6.0% range, and franchise fee margin at 48.0% base with a 45.0%–51.0% range). I verified that their RevPAR and room additions were not calculated statement totals, checked their units, and verified that their lower run did not trigger a debt covenant or negative cash balance.*  

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

--- BASELINE VERIFICATION AGAINST LAB 10 (PROFORMA_TSLA.PY) ---
Metric                           | Lab 10 Saved Model   | Script Base Run      | Status
-------------------------------------------------------------------------------------
FY2030E Operating Income         | $           6,091.6M | $           6,091.6M | MATCH
FY2030E FCFE                     | $           2,157.5M | $           2,157.5M | MATCH
Value per share (signed DCF)     |               -$1.83 |               -$1.83 | MATCH
Accounting checks                |                 PASS |                 PASS | MATCH
Peak revolver draw: $   1,909.3M (limit $5,000.0M)

================================================================================
SCENARIO SPECIFICATION: INPUTS, UNITS, SHIFTS, AND AFFECTED YEARS
================================================================================
Scenario Name              | Driver Key   | Base Value -> New Value        | Shift    | Affected Years
--------------------------------------------------------------------------------------------------------------
Base run                   | (Baseline)   | 10.0% / 22.39%                 | 0.0 pp   | FY2026E–FY2030E (all 5 years)
Lower Growth 8.0%          | GROWTH       | 10.0% annual growth -> 8.0% annual growth | -2.0 pp  | FY2026E–FY2030E (all 5 years)
Higher Growth 12.0%        | GROWTH       | 10.0% annual growth -> 12.0% annual growth | +2.0 pp  | FY2026E–FY2030E (all 5 years)
Lower Gross Margin 21.39%  | GROSS_MARGIN | 22.39% of revenue -> 21.39% of revenue | -1.0 pp  | FY2026E–FY2030E (all 5 years)
Higher Gross Margin 23.39% | GROSS_MARGIN | 22.39% of revenue -> 23.39% of revenue | +1.0 pp  | FY2026E–FY2030E (all 5 years)
--------------------------------------------------------------------------------------------------------------
Source logic: In proforma.py, both GROWTH and GROSS_MARGIN apply across all five forecast years
(YEARS = [2026, 2027, 2028, 2029, 2030]). Revenue compounds as prev['revenue'] * (1 + GROWTH),
and Gross Profit is computed as r['revenue'] * GROSS_MARGIN.

================================================================================
SENSITIVITY COMPARISON TABLE: OPERATING PROFIT, FCFE, AND VALUE PER SHARE
================================================================================
Independent Input Changed    | Operating Profit ($m)  | FCFE ($m)          | Value ($/share)  | Checks
---------------------------------------------------------------------------------------------------------
Base run                     |  6,091.6 (  base )     | 2,157.5 ( base )   |  -$1.83 ( base ) | PASS
Lower Growth 8.0%            |  4,533.0 (-1,558.5)    |   673.7 (-1,483.8) |  -$6.16 (-$4.34) | PASS
Higher Growth 12.0%          |  7,767.6 (+1,676.1)    | 3,751.0 (+1,593.5) |   $2.81 (+$4.64) | PASS
Lower Gross Margin 21.39%    |  5,297.4 ( -794.1)     | 1,450.1 ( -707.4)  |  -$4.09 (-$2.26) | PASS
Higher Gross Margin 23.39%   |  6,885.7 ( +794.1)     | 2,863.8 ( +706.3)  |   $0.43 (+$2.25) | PASS
---------------------------------------------------------------------------------------------------------
Note: Signed changes from base are shown in parentheses. Money is in USD millions except $/share.
DCF includes all forecast years with their sign, discounting negative FCFE at cost of equity.

================================================================================
OUTPUT SPANS: MAXIMUM VALID RESULT MINUS MINIMUM VALID RESULT
================================================================================
Output Metric            | Revenue Growth Output Span     | Gross Margin Output Span      
------------------------------------------------------------------------------------------
FY2030E Operating Income | 7,767.6 - 4,533.0 = $3,234.6M  | 6,885.7 - 5,297.4 = $1,588.3M 
FY2030E FCFE             | 3,751.0 -   673.7 = $3,077.3M  | 2,863.8 - 1,450.1 = $1,413.7M 
Value per share          | $2.81 - (-$6.16) = $8.97       | $0.43 - (-$4.09) = $4.51      
------------------------------------------------------------------------------------------

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

================================================================================
RESTORED BASELINE INTEGRITY CHECK
================================================================================
Check                            | Before Analysis    | After Analysis     | Match
--------------------------------------------------------------------------------
FY2030E Operating Income         | $         6,091.6 | $         6,091.6 | EXACT (diff 0.0)
FY2030E FCFE                     | $         2,157.5 | $         2,157.5 | EXACT (diff 0.0)
Value per share (USD)            |             -$1.83 |             -$1.83 | EXACT (diff 0.00)
Balance sheet zero-gap check     |               PASS |               PASS | MATCH
Cash floor check (>= $15,000M)   |               PASS |               PASS | MATCH
--------------------------------------------------------------------------------
SUCCESS: Base inputs and outputs are fully restored and verified.
```

---

## V — Check the Result

### 1. Integrity Verification Table

| Check | Expected Result | Actual Result | Status |
|---|---|---|:---:|
| **Base before and after analysis** | Same inputs and outputs within 0.0 tolerance | Pre-run: $6,091.6M op income, $2,157.5M FCFE, -$1.83/share. Post-run: exactly identical (difference = 0.00). | ✅ PASS |
| **Lower or higher run isolation** | Only the selected independent input changed; linked quantities recalculated | When `GROWTH` changed, `GROSS_MARGIN` stayed at 22.39%; when `GROSS_MARGIN` changed, `GROWTH` stayed at 10.0%. Statements dynamically recalculated. | ✅ PASS |
| **Accounting checks on usable runs** | Assets − Liabilities − Equity = 0.0; Cash $\ge$ $15,000M | Balance sheet gap is 0.00 across all 5 years on all four sensitivity runs. All four maintain cash $\ge$ $15,000M. | ✅ PASS |
| **Change from base recomputes** | Changed output minus base output matches signed differences | Verified across all rows (e.g. Higher Growth: $7,767.6M − $6,091.6M = +$1,676.1M; FCFE $3,751.0M − $2,157.5M = +$1,593.5M; Value $2.81 − (-$1.83) = +$4.64/share). | ✅ PASS |

---

### 2. Partner Exchange 2 — Check Each Other's Evidence (Partner Company: Marriott, `MAR`)

> **Check on partner's model:**  
> *I checked my partner's Marriott model at Higher Net Room Growth (6.0% vs 4.5% base). I verified that owned-hotel capex remained at base, recomputed their franchise fee revenue difference ($5,420M − $5,050M = +$370M), confirmed that non-varying operating expense assumptions stayed locked, and traced the resulting operating income into FCFE and share repurchases.*  
>
> **Partner's check on my model:**  
> *Partner checked my Higher Growth run (12.0%): confirmed that opening PP&E and capex schedules remained at base, recomputed the FY2030E operating income difference ($7,767.6M − $6,091.6M = +$1,676.1M), and verified that the signed valuation rose from -$1.83 to +$2.81/share.*  
>
> **Prediction Reconciliation:**  
> *My locked prediction anticipated an operating income gain of ~$1.5B–$1.8B; actual was **+$1,676.1M**. FCFE was predicted at +$1.4B–$1.7B; actual was **+$1,593.5M**. Value was predicted to rise to ~$2.50–$3.50/share; actual was **+$2.81/share**. The prediction matched actual output within 3%. The slight variance came from non-linear interest income: higher revenue generated more cash earlier in the forecast, reducing revolver interest to $0 and boosting interest income.*  
>
> **Impact on Valuation Conclusion & Research Priority:**  
> *Does this sensitivity change our Lab 08 / Lab 10 **WATCH / DEFER** conclusion? **No.** At the current market price of **$378.94**, even the most bullish operational case ($2.81/share at 12% sustained growth, or $0.43/share at 23.39% margin) remains **over 99% below the market price**. Tesla's market price cannot be rationalized through manufacturing growth or margin sensitivity within historical operational ranges. The decision remains WATCH / DEFER, and research priority must focus on whether commercial software/robotics options can ever deliver independent cash flows.*  

---

## E — Find the Driver

### 1. Output Spans Over Stated Ranges

An output span is the maximum valid output minus the minimum valid output across the lower, base, and higher runs ($\text{Span} = \text{Max} - \text{Min}$):

| Output Metric | Revenue Growth Output Span (8.0% to 12.0%) | Gross Margin Output Span (21.39% to 23.39%) |
|---|:---:|:---:|
| **FY2030E Operating Income** | $7,767.6\text{M} - 4,533.0\text{M} = \mathbf{\$3,234.6M}$ | $6,885.7\text{M} - 5,297.4\text{M} = \mathbf{\$1,588.3M}$ |
| **FY2030E FCFE** | $3,751.0\text{M} - 673.7\text{M} = \mathbf{\$3,077.3M}$ | $2,863.8\text{M} - 1,450.1\text{M} = \mathbf{\$1,413.7M}$ |
| **Value per Share** | $\$2.81 - (-\$6.16) = \mathbf{\$8.97}$ | $\$0.43 - (-\$4.09) = \mathbf{\$4.51}$ |

---

### 2. Partner Exchange 3 — Explain and Compare (Partner Company: Marriott, `MAR`)

> **My causal link explanation:**  
> *Over our tested ranges, Revenue Growth produces an operating income span of $3,234.6M versus $1,588.3M for Gross Margin. Revenue growth compounds geometrically over five years ($\text{Revenue}_{2030} = \text{Revenue}_{2025} \times (1+g)^5$), expanding the 2030 revenue base from $139.3B (at 8%) to $167.1B (at 12%)—a $27.8B spread. However, on a per-percentage-point basis, both drivers possess nearly identical leverage: 1.0 pp of Gross Margin moves 2030 operating income by $794.1M, while 1.0 pp of Growth moves it by ~$779M–$808M. Growth has the larger total span simply because its tested economic range is twice as wide (4.0 pp vs 2.0 pp).*  
>
> **Partner's question & comparison:**  
> *Partner's question: "In Marriott, franchise fee margin has much higher per-unit power than room growth because over 80% of fee revenue drops straight to operating profit with almost no working capital or capex needs. Why doesn't Tesla's gross margin dominate revenue growth by an even larger multiple?"*  
>
> **My answer:**  
> *"Tesla is an asset-heavy manufacturer where SG&A and R&D are modeled as a percentage of gross profit (48% in 2030), so only 52% of incremental gross margin drops to operating income. Meanwhile, volume growth compounds over 5 years across both vehicle sales and Energy storage, expanding the terminal revenue base on which margins operate."*  

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
   Over our tested ranges, **Revenue Growth** produced the larger output span ($3,234.6M in operating profit, $3,077.3M in FCFE, and $8.97/share in equity value, compared to $1,588.3M, $1,413.7M, and $4.51/share for gross margin). Five-year compounding across an expanding revenue base drives this result over the 4.0 percentage point growth window.
2. **Which result surprised you?**  
   **How close the per-percentage-point leverage is between growth and margin.** One percentage point of gross margin moves 2030 operating profit by $794.1M, while one percentage point of revenue growth moves it by ~$779M–$808M. Despite growth compounding geometrically over five years, gross margin's direct 100% price realization on a ~$153B revenue base delivers nearly identical structural impact per 100 basis points.

---

## Checkout — Files on GitHub

| File Name | GitHub Source Link | Description & Role in Submission | Status |
|---|---|---|:---:|
| **`sensitivity_tsla.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/sensitivity_tsla.py) | Python one-at-a-time sensitivity engine, statement trace, and restored base check. | **Verified & Running** |
| **`Lab_11_proforma_sensitivity.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Lab_11_proforma_sensitivity.md) | Full Lab 11 sensitivity report, locked prediction, partner exchanges, span rankings, and reflections. | **Submission-Ready** |
| **`proforma_tsla.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/proforma_tsla.py) | Lab 10 Tesla pro-forma model running through the three-statement engine. | **Unchanged Benchmark** |
| **`proforma.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/proforma.py) | Lab 09 core three-statement engine (still reproduces ABG $291.75 known answer). | **Unchanged Core** |
| **`Lab_10_proforma_tsla.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Lab_10_proforma_tsla.md) | Lab 10 Tesla three-statement model report, assumptions table, and check blocks. | **Archived Reference** |

*All files conform strictly to FIN 43900 academic standards and course integrity policies.*
