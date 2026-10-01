# Lab 12 — Pro-Forma Sensitivity: Present and Review the Full Analysis

**Presenter:** [Name]  
**Company:** Tesla, Inc. (`TSLA`)  
**Partner / reviewer:** Marriott International, Inc. (`MAR`) — [partner name]  
**Presentation date:** October 1, 2026  
**Currency / units:** USD millions except per-share figures  

## Current conclusion

**WATCH / DEFER — do not initiate at the saved market price.** Tesla's reported automotive and energy businesses do not support the saved market-price range under my existing DCF, peer-reference, and pro-forma evidence. The central unresolved issue is the value of autonomy, software, and robotics cash flows that are not yet separately established in the historical financial statements.

Do not average the valuation methods. They use different dates, cash-flow definitions, and assumptions:

| Evidence | Saved result | Date / share basis | What it does and does not show |
|---|---:|---|---|
| Lab 08 DCF sensitivity range | $34.06–$54.60 per share | Sep. 1, 2026 | FCFF model using 9.0%–11.0% WACC and 2.0%–4.0% terminal growth. |
| Lab 08 peer P/E reference | $16.44 per share | Sep. 1, 2026 | GM-only automotive reference; not a Tesla target price. |
| Lab 09 full FCFE bridge | $29.05 per share | Sep. 24, 2026; 3,540.0M diluted shares | Includes a bridge for excess cash and other non-operating assets. |
| Lab 10 pro-forma | $5.57 per share | Sep. 24, 2026; 3,540.0M diluted shares | Positive-FCFE-only convention. Negative FY2026E–FY2029E FCFE is funded by opening cash. |
| Lab 11 sensitivity output | -$1.83 base; $2.81 higher-growth case | Sep. 24, 2026; 3,540.0M diluted shares | Signed-FCFE output. It needs reconciliation to the Lab 09 excess-cash bridge before it is used as a standalone target price. |

**Presentation rule:** State the valuation date, cash-flow convention, currency, and share basis beside each value. The method inconsistency is an identified limitation, not a reason to invent a blended value.

## Six-stop presentation route

### 1. Target selection — about 2 minutes

- I selected Tesla because it combines a large, reported automotive and energy business with a market price that appears to embed material autonomy, software, and robotics expectations.
- My initial view was that a fundamental analysis should separate reported operating evidence from optionality that has not yet produced separately disclosed cash flows.
- Show: [research report](01_Research/Tesla_2026-09-03_report.md) and [Lab 08](Lab_08_comps_dcf.md).

### 2. Company and evidence — about 2 minutes

- Tesla earns revenue from automotive sales and leasing, energy generation and storage, and services and other activities. FY2025 revenue was $94,827M and GAAP gross profit was $17,094M.
- The key evidence uses Tesla's FY2023–FY2025 10-Ks and Q2 2026 10-Q. Keep reporting periods distinct from valuation dates.
- The evidence that matters most to this analysis is FY2025's revenue decline, H1 2026 revenue growth, the energy-storage business, the cash/investment balance, and management's 2026 capex guidance above $25B.
- Show: [research report](01_Research/Tesla_2026-09-03_report.md), [Lab 10 history and assumptions](Lab_10_proforma_tsla.md), and the linked SEC filings.

### 3. Pro-forma — about 3 minutes

- The Lab 10 pro-forma starts with the FY2025 balance sheet and applies 10.0% annual revenue growth, 22.39% gross margin before D&A, a declining SG&A-to-gross-profit ratio, and five years of capex.
- Revenue compounds, gross profit equals revenue times gross margin, SG&A and R&D are modeled as a share of gross profit, and the cash-flow statement drives ending cash. The balance-sheet gap is 0.0 in each forecast year and cash stays at or above the $15B floor.
- The important economic constraint is capex: FY2026E–FY2029E FCFE is negative, and the model uses the opening cash balance and then the revolver to preserve the minimum-cash policy.
- Show: [Lab 10](Lab_10_proforma_tsla.md) and [pro-forma code](proforma_tsla.py).

### 4. Valuation — about 3 minutes

- The core discount-rate assumption is a 10.38% cost of equity: 5.11% risk-free rate + 1.17 bottom-up beta × 4.5% equity-risk premium. Terminal growth is 3.0%.
- Lab 08's FCFF DCF and peer P/E reference are separate evidence, not values to average. GM is a limited automotive reference and does not capture Tesla's energy or potential software businesses.
- Reverse-DCF work indicates that the saved market price requires operating outcomes that the reported manufacturing and energy evidence alone does not support.
- The key limitation is valuation consistency: Lab 09 includes the excess-cash/non-operating-asset bridge; Lab 10 and Lab 11 use different FCFE conventions. I will explain that difference rather than claim they are the same valuation.
- Show: [Lab 08 valuation comparison](Lab_08_comps_dcf.md), [Lab 09 FCFE bridge](Lab_09_proforma_fcfe.md), and [Lab 10](Lab_10_proforma_tsla.md).

### 5. Sensitivity and drivers — about 3 minutes

- Lab 11 changes one independent input at a time across FY2026E–FY2030E while holding the other input at its base value.
- Revenue growth is tested at 8.0%, 10.0%, and 12.0%. Gross margin before D&A is tested at 21.39%, 22.39%, and 23.39%.
- Higher growth (12.0% versus 10.0%) raises FY2030E operating income by $1,676.1M and FY2030E FCFE by $1,593.5M. The trace is: growth → FY2030E revenue (+$14,397.7M) → gross profit (+$3,223.2M) → operating income → FCFE.
- Over these stated ranges, growth has the wider result span: $3,234.6M operating income, $3,077.3M FCFE, and $8.97 per share, versus gross margin's $1,588.3M, $1,413.7M, and $4.51 per share.
- The ranking is not a probability statement. Growth has a 4.0-percentage-point tested range versus gross margin's 2.0-point range; per percentage point, their operating-income effects are similar.
- Show: [Lab 11 output](Lab_11_proforma_sensitivity.md) and [sensitivity code](sensitivity_tsla.py).

### 6. Interpretation — about 2 minutes

- My conclusion remains WATCH / DEFER at the saved market prices because the existing fundamental evidence does not support the market's implied autonomy/software/robotics expectations.
- Evidence that could change my view: separately disclosed, recurring, high-margin commercial Robotaxi/FSD cash flows; evidence of a durable improvement in automotive/energy margins; or a market-price change toward a fundamentally supportable range.
- The next research priority is to reconcile the valuation conventions and then investigate whether autonomy and robotics can generate independent, recurring cash flows rather than treating them as assumed optionality.

## Reviewer prompts for Marriott

Ask these in the 10-minute question-and-check segment. Replace bracketed text with the partner's actual evidence.

1. **Selection and evidence:** “You chose Marriott because [reason]. Which filing or cited source supports your most important claim about RevPAR, room growth, or fee revenue, and what reporting period and units does it use?”
2. **Model and valuation:** “Trace your [net room growth / franchise-fee-margin] assumption from the input through revenue, operating income, cash flow, and value. Why is the result consistent with Marriott's asset-light model?”
3. **Sensitivity and interpretation:** “Your sensitivity tests net room growth from 3.0% to 6.0% and franchise fee margin from 45.0% to 51.0%. Does the driver ranking change if the widths are normalized, and what evidence would make you revise the range?”
4. **Check together:** Open [partner source or model location] and trace [specific assumption / calculation]. Record the result below.

## Live review record — complete during class

### As presenter: feedback received

- **Question received:** [ ]
  - **My answer or unresolved gap:** [ ]
- **Question received:** [ ]
  - **My answer or unresolved gap:** [ ]
- **Question that made me reconsider something:** [ ]
  - **What I understand better now:** [ ]

### As reviewer: Marriott review

- **Selection/evidence question asked:** [ ]
- **Model/valuation question asked:** [ ]
- **Sensitivity/interpretation question asked:** [ ]
- **Source or calculation checked:** [ ]
  - **Result of check:** [ ]
- **My explanation back of Marriott's conclusion, main driver, and biggest limitation:** [ ]
- **Evidence-backed strength:** [ ]
- **Specific next improvement:** [ ]

## After-review decision

- **Keep:** The WATCH / DEFER conclusion unless the review identifies an error in the existing evidence or a source that supports material, recurring autonomy/software cash flows.
- **Revise:** Reconcile the Lab 09, Lab 10, and Lab 11 treatment of negative FCFE, opening/excess cash, and the per-share bridge before presenting any single pro-forma sensitivity value as a target price.
- **Investigate:** Whether Tesla's commercial software, Robotaxi, and robotics businesses have separately disclosed revenue, margins, capital needs, and cash flows.
- **Effect of the review on conclusion or research priority:** [Complete after partner feedback.]

## GitHub file links

- [Research report](https://github.com/mnine393/TICKER-research/blob/main/01_Research/Tesla_2026-09-03_report.md)
- [Lab 08 valuation and peer comparison](https://github.com/mnine393/TICKER-research/blob/main/Lab_08_comps_dcf.md)
- [Lab 09 FCFE model](https://github.com/mnine393/TICKER-research/blob/main/Lab_09_proforma_fcfe.md)
- [Lab 10 Tesla pro-forma](https://github.com/mnine393/TICKER-research/blob/main/Lab_10_proforma_tsla.md)
- [Lab 11 sensitivity report](https://github.com/mnine393/TICKER-research/blob/main/Lab_11_proforma_sensitivity.md)
- [Sensitivity script](https://github.com/mnine393/TICKER-research/blob/main/sensitivity_tsla.py)
