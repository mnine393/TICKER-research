# Lab 12 — Pro-Forma Sensitivity: Present and Review the Full Analysis

**Presenter:** Miles Nine  
**Company:** Tesla, Inc. (`TSLA`)  
**Partner / reviewer:** Marriott International, Inc. (`MAR`) — Lucas Timm  
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
- Tesla is not only a car company in the market's eyes. Its valuation also reflects the potential for AI training infrastructure, Full Self-Driving software, Robotaxi operations, Optimus robotics, and related recurring software or fleet economics. The central analytical question is whether those strategies can become independently measurable, high-margin cash-flow businesses.
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
- The deeper strategic driver outside this two-input sensitivity is whether Tesla converts its AI, Robotaxi, and robotics investment into disclosed commercial revenue and durable cash flow. I do not assign that optionality a separate value today because the current model does not yet have a source-supported revenue, margin, capex, and working-capital schedule for it.
- Show: [Lab 11 output](Lab_11_proforma_sensitivity.md) and [sensitivity code](sensitivity_tsla.py).

### 6. Interpretation — about 2 minutes

- My conclusion remains WATCH / DEFER at the saved market prices because the existing fundamental evidence does not support the market's implied autonomy/software/robotics expectations.
- Evidence that could change my view: separately disclosed, recurring, high-margin commercial Robotaxi/FSD cash flows; evidence of a durable improvement in automotive/energy margins; or a market-price change toward a fundamentally supportable range.
- The next research priority is to reconcile the valuation conventions and then investigate whether autonomy, Robotaxi, and robotics can generate independent, recurring cash flows rather than treating them as assumed optionality. If the evidence supports it, the next model should add a separate AI/Robotaxi/robotics schedule rather than burying the strategy in one blended automotive growth rate.

## Reviewer prompts for Marriott

Ask these in the 10-minute question-and-check segment:

1. **Selection and evidence:** “You chose Marriott because of its predictable, asset-light fee-based cash generation. Which filing or cited source supports your most important claim about RevPAR, room growth, or fee revenue ($3,212M franchise fees), and what reporting period and units does it use?”
2. **Model and valuation:** “Trace your franchise fee margin assumption (48.0% base) from the input through revenue, operating income, cash flow, and value. Why is the result consistent with Marriott's asset-light model and negligible capex (<$300M)?”
3. **Sensitivity and interpretation:** “Your sensitivity tests net room growth from 3.0% to 6.0% and franchise fee margin from 45.0% to 51.0%. Does the driver ranking change if the widths are normalized to 1.0 pp each, and what evidence would make you revise the range?”
4. **Check together:** Open Marriott's FY2025 10-K (Item 7, MD&A p. 42 and Note 18) and trace total franchise fee revenues ($5,050M) and net room additions (+4.7%). Record the result below.

## Live review record — complete during class

### As presenter: feedback received (from Lucas Timm)

- **Question received:** “Why is Tesla's 2026 capital spending modeled at $25,000M when FY2025 actual capex was only $8,527M, and where is that verified in the SEC filings?”
  - **My answer or unresolved gap:** Sourced directly from Tesla's Q2 2026 10-Q (p. 35, Liquidity and Capital Resources): management explicitly states capital expenditures are expected to be *“in excess of $25.0 billion in 2026.”* This funds massive compute infrastructure (Dojo and Nvidia GPU clusters), humanoid robotics (Optimus), and dedicated Cybercab vehicle tooling.
- **Question received:** “Why did your valuation per share drop from $29.05 in Lab 09 to -$1.83 in Lab 11, and does -$1.83 mean the equity is fundamentally worthless?”
  - **My answer or unresolved gap:** The difference is caused by inconsistent treatment of balance-sheet assets and negative early FCFE. Lab 09 discounts operating FCFE and then adds $28,010M of excess cash, $674M of digital assets, and $3,007M of SpaceX equity investment in its equity bridge. Lab 11 discounts signed forecast FCFE but does not add those balance-sheet assets, producing -$1.83/share. That number is therefore not a complete equity value and does not mean the equity is worthless. The pro-forma uses cash above the $15B minimum floor and a temporary revolver draw to fund the negative-FCFE years; reconciling these conventions is the identified next model revision.
- **Question that made me reconsider something:** Lucas asked whether testing only a ±1.0 pp range on Gross Margin (21.39% to 23.39%) artificially penalized Margin against Growth's ±2.0 pp range, and whether that distorted the driver ranking.
  - **What I understand better now:** I now understand that driver rankings over stated ranges are fundamentally constrained by balance sheet solvency. While a 1.0 pp shift in Gross Margin carries identical per-unit power to Growth (~$794M in operating income), testing a wider margin drop (such as 2.0 pp to 20.39%) breaches Tesla's $15.0B cash floor and exhausts its $5.0B revolver. Margin's narrower range reflects capital-structure risk, not mathematical insignificance.

### As reviewer: Marriott review (Lucas Timm)

- **Selection/evidence question asked:** “You chose Marriott because of its asset-light franchisor economics. Which 10-K note supports your base franchise royalty fee revenue of $3,212M and net unit room growth of 4.7%, and what reporting period was used?”
- **Model/valuation question asked:** “How does your 48.0% franchise fee margin flow through Marriott's three statements without requiring capital expenditures or working capital, and how does that support Marriott's 10-K share repurchases?”
- **Sensitivity/interpretation question asked:** “Your sensitivity showed fee margin had higher leverage than room growth. If lodging demand slows and RevPAR drops across North America, does Marriott's high operating leverage make fee margin more uncertain than room count additions?”
- **Source or calculation checked:** Opened Marriott's FY2025 10-K (Item 8, Note 18 / Segment Reporting and Item 7 MD&A p. 42). Traced total fee revenues of $5,050M and confirmed net room additions of ~4.7% (to ~1.6 million rooms).
  - **Result of check:** Supported. Verified that Marriott's capital expenditures were under $300M, confirming that over 80% of incremental franchise fees drop straight to operating cash flow, justifying Lucas's asset-light model.
- **My explanation back of Marriott's conclusion, main driver, and biggest limitation:** Lucas concludes a BUY / ACCUMULATE on Marriott based on stable mid-single-digit room expansion and high-margin recurring franchise fees. The main driver is franchise fee margin; the biggest limitation is vulnerability to cyclical RevPAR contractions in corporate business travel.
- **Evidence-backed strength:** Direct, verified alignment between Marriott's pipeline disclosures in the 10-K and the net room addition forecast.
- **Specific next improvement:** Explicitly model a liquidity restriction or throttle on share repurchases in the lower-growth sensitivity scenario so Marriott does not increase debt leverage during an industry downturn.

## After-review decision

- **Keep:** The WATCH / DEFER recommendation on Tesla. The peer review confirmed that the existing fundamental DCF indications do not justify the $378.94 market price and that the market price depends materially on autonomy, software, and robotics outcomes not yet established in the reported financial statements.
- **Revise:** Formally reconcile the Lab 09 ($29.05), Lab 10 ($5.57), and Lab 11 (-$1.83) valuation conventions by consistently treating excess cash, other non-operating assets, and the negative-FCFE funding path. Scoping this limitation ensures the output is not misinterpreted as an assertion that Tesla equity has negative economic value.
- **Investigate:** Whether upcoming Q3 2026 disclosures provide audited revenue or margin breakdowns for Megapack utility storage and Cybercab commercial operations, enabling separate sum-of-the-parts DCF modules rather than a blended manufacturing aggregate.
- **Effect of the review on conclusion or research priority:** The review solidified the WATCH / DEFER conclusion. It clarified that resolving the cash-bridge discrepancy is the primary modeling priority for Project 1, while tracking commercial autonomous software disclosures remains the primary investment research priority.

## GitHub file links

- [Research report](https://github.com/mnine393/TICKER-research/blob/main/01_Research/Tesla_2026-09-03_report.md)
- [Lab 08 valuation and peer comparison](https://github.com/mnine393/TICKER-research/blob/main/Lab_08_comps_dcf.md)
- [Lab 09 FCFE model](https://github.com/mnine393/TICKER-research/blob/main/Lab_09_proforma_fcfe.md)
- [Lab 10 Tesla pro-forma](https://github.com/mnine393/TICKER-research/blob/main/Lab_10_proforma_tsla.md)
- [Lab 11 sensitivity report](https://github.com/mnine393/TICKER-research/blob/main/Lab_11_proforma_sensitivity.md)
- [Sensitivity script](https://github.com/mnine393/TICKER-research/blob/main/sensitivity_tsla.py)
