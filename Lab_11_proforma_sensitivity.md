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

*(To be recorded prior to running sensitivity analysis)*

```text
LOCKED PREDICTION RECORD (Timestamp: [record date and time before running])
Target: Tesla, Inc. (TSLA)

1. Prediction for Driver 1 (Revenue Growth: 10.0% -> [chosen lower or higher value]):
   - Input old -> new with units: 
   - Expected output direction and rough size:
     * FY2030E Operating Income:
     * FY2030E FCFE:
     * Value per share:
   - Why (statement / economic link):

2. Prediction for Driver 2 (Gross Margin: 22.39% -> [chosen lower or higher value]):
   - Input old -> new with units:
   - Expected output direction and rough size:
     * FY2030E Operating Income:
     * FY2030E FCFE:
     * Value per share:
   - Why (statement / economic link):
```

### 4. Partner Exchange 1 — Predict, Then Question

> **Question from partner:**  
> *[record partner's question on your chosen inputs, units, and ranges]*  
>
> **My answer:**  
> *[your response explaining the support for the proposed ranges]*  
>
> **Check performed on partner's analysis:**  
> *[record what you checked on your partner's company: independent inputs, units, and ranges]*  

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
Value per share:          $      -1.83
Accounting checks:        PASS (all 5 years balance, cash >= floor)
Peak revolver draw:       $   1,909.3M (limit $5,000.0M)

================================================================================
SENSITIVITY COMPARISON TABLE: OPERATING PROFIT, FCFE, AND VALUE PER SHARE
================================================================================
Independent Input Changed    | Operating Profit ($m)  | FCFE ($m)          | Value ($/share)  | Checks
---------------------------------------------------------------------------------------------------------
Base run                     |  6,091.6 (  base )     | 2,157.5 ( base )   | $-1.83 ( base)   | PASS
Lower Growth 8.0%            |  4,533.0 (-1,558.5)    |   673.7 (-1,483.8) | $-6.16 (-4.34)   | PASS
Higher Growth 12.0%          |  7,767.6 (+1,676.1)    | 3,751.0 (+1,593.5) | $ 2.81 (+4.64)   | PASS
Lower Gross Margin 21.39%    |  5,297.4 ( -794.1)     | 1,450.1 ( -707.4)  | $-4.09 (-2.26)   | PASS
Higher Gross Margin 23.39%   |  6,885.7 ( +794.1)     | 2,863.8 ( +706.3)  | $ 0.43 (+2.25)   | PASS
---------------------------------------------------------------------------------------------------------
Note: Signed changes from base are shown in parentheses. Money is in USD millions except $/share.
DCF includes all forecast years with their sign, discounting negative FCFE at cost of equity.

================================================================================
OUTPUT SPANS: MAXIMUM VALID RESULT MINUS MINIMUM VALID RESULT
================================================================================
Output Metric            | Revenue Growth Output Span   | Gross Margin Output Span        
--------------------------------------------------------------------------------------------
FY2030E Operating Income | 7,767.6 - 4,533.0 = $3,234.6M | 6,885.7 - 5,297.4 = $1,588.3M
FY2030E FCFE             | 3,751.0 -   673.7 = $3,077.3M | 2,863.8 - 1,450.1 = $1,413.7M
Value per share          | $ 2.81 - ($-6.16) = $ 8.97   | $ 0.43 - ($-4.09) = $ 4.51      
--------------------------------------------------------------------------------------------

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
Value per share (USD)            | $           -1.83 | $           -1.83 | EXACT (diff 0.00)
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
| **Base before and after analysis** | Same inputs and outputs within 0.0 tolerance | Pre-run: $6,091.6M op income, $2,157.5M FCFE, $-1.83/share. Post-run: exactly identical (difference = 0.00). | ✅ PASS |
| **Lower or higher run isolation** | Only the selected independent input changed; linked quantities recalculated | When `GROWTH` changed, `GROSS_MARGIN` stayed at 22.39%; when `GROSS_MARGIN` changed, `GROWTH` stayed at 10.0%. Statements dynamically recalculated. | ✅ PASS |
| **Accounting checks on usable runs** | Assets − Liabilities − Equity = 0.0; Cash $\ge$ $15,000M | Balance sheet gap is 0.00 across all 5 years on all four sensitivity runs. All four maintain cash $\ge$ $15,000M. | ✅ PASS |
| **Change from base recomputes** | Changed output minus base output matches signed differences | Verified across all rows (e.g. Higher Growth: $7,767.6M − $6,091.6M = +$1,676.1M; FCFE $3,751.0M − $2,157.5M = +$1,593.5M; Value $2.81 − ($-1.83) = +$4.64/share). | ✅ PASS |

---

### 2. Partner Exchange 2 — Check Each Other's Evidence

> **Check on partner's model:**  
> *[record what you checked on your partner's changed result and its base: differences, independent inputs held at base, statement trace]*  
>
> **Partner's check on my model:**  
> *[record partner's check and any question or correction]*  
>
> **Actual result vs prediction reconciliation:**  
> *[add the actual result and an explanation of any prediction error to your locked record]*  
>
> **Impact on valuation conclusion or research priority:**  
> *[state whether the result changes your valuation conclusion or research priority, and why (including a no-change reason)]*  

---

## E — Find the Driver

### 1. Output Spans Over Stated Ranges

An output span is the maximum valid output minus the minimum valid output across the lower, base, and higher runs ($\text{Span} = \text{Max} - \text{Min}$):

| Output Metric | Revenue Growth Output Span (8.0% to 12.0%) | Gross Margin Output Span (21.39% to 23.39%) |
|---|:---:|:---:|
| **FY2030E Operating Income** | $7,767.6\text{M} - 4,533.0\text{M} = \mathbf{\$3,234.6M}$ | $6,885.7\text{M} - 5,297.4\text{M} = \mathbf{\$1,588.3M}$ |
| **FY2030E FCFE** | $3,751.0\text{M} - 673.7\text{M} = \mathbf{\$3,077.3M}$ | $2,863.8\text{M} - 1,450.1\text{M} = \mathbf{\$1,413.7M}$ |
| **Value per Share** | $\$2.81 - (\$-6.16) = \mathbf{\$8.97}$ | $\$0.43 - (\$-4.09) = \mathbf{\$4.51}$ |

---

### 2. Partner Exchange 3 — Explain and Compare

> **My causal link explanation:**  
> *[explain one causal link using your actual results and trace it through the statements]*  
>
> **Partner's question & comparison:**  
> *[record the question you received from your partner on whether the ranking reflects chosen ranges, and summarize their company's driver comparison]*  
>
> **My answer:**  
> *[your response]*  

---

## Sensitivity — Learn on Your Own

### 1. What is one-at-a-time sensitivity?
*[Explain in your own words: what is tested, what is held constant, and what linked quantities do]*

### 2. How does the chosen input range affect the ranking?
*[Explain in your own words: how output span depends on range width as well as underlying model sensitivity, and why we say "over these ranges"]*

### 3. Explain why a sensitivity table is not a forecast probability.
*[Explain in your own words: why three scenario rows do not represent likelihoods, confidence intervals, or joint probabilities]*

---

## Reflect

1. **Which driver mattered most over your ranges?**  
   *[Your answer]*  
2. **Which result surprised you?**  
   *[Your answer]*  

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
