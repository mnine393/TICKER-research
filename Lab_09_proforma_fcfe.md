# Lab 09 — Pro-Forma Three-Statement Model and FCFE Valuation: Tesla, Inc. (`TSLA`)

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Tutorial followed:** *Pro-Forma Valuation with AI* — the ABG tutorial, Weeks 5–6 (Part 1: build the base case; Part 2: take it apart and present it)  
**Valuation Date:** September 24, 2026  
**Target Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Market Price Used:** \$378.25 (2026-09-24, seed market file; the app refreshes it live)  
**Primary Sources:** [Form 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) (accession `0001628280-26-003952`), [Form 10-K FY2024](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm), [Form 10-K FY2023](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm), [Form 10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (accession `0001628280-26-049270`), and Tesla's production & delivery releases filed as 8-K Ex. 99.1  
**Model code:** [`tsla-proforma-model/`](tsla-proforma-model/) in this repository (Python + Streamlit; `streamlit run app.py`)  
**Anchor Labs:** Lab 06 (DCF / reverse DCF), Lab 07 (comps), Lab 08 (triangulation)  

> **Learning demonstration — not investment advice.** Tesla is valued here for teaching only, from public filings and prices as of September 2026. Nothing in this lab is a recommendation to buy, sell or hold any security. All figures are USD millions unless stated; per-share figures in USD; shares in millions.

---

## The Check Block (read this first)

Every projected year is tested before any value is produced. The valuation **refuses to run** if any material check fails (Section 4 breaks it on purpose to prove it).

| Check | Years tested | Result |
| --- | :---: | :---: |
| 1. Assets = liabilities + equity | 5 | PASS |
| 2. Cash-flow ending cash = balance-sheet cash | 5 | PASS |
| 3. Fixed-asset (PP&E) roll-forward ties | 5 | PASS |
| 4a. Debt roll-forward ties | 5 | PASS |
| 4b. Finance & operating lease roll-forwards tie | 5 | PASS |
| 4c. Revolver roll-forward ties | 5 | PASS |
| 5. Share-count roll-forward ties | 5 | PASS |
| 6. Cash >= minimum (after any revolver financing) | 5 | PASS |
| Revenue build reconciles to total revenue | 5 | PASS |
| 7. Terminal growth < cost of equity | 1 | PASS |


Base case, by year:

| Year | Total assets | Liabilities + equity | Difference | Cash & ST inv. | Cash floor (15% of rev.) | All checks |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| FY2026E | 150,807 | 150,807 | 0.000000 | 33,693 | 15,514 | PASS |
| FY2027E | 162,884 | 162,884 | 0.000000 | 29,197 | 17,080 | PASS |
| FY2028E | 177,050 | 177,050 | 0.000000 | 31,998 | 19,028 | PASS |
| FY2029E | 190,244 | 190,244 | 0.000000 | 36,688 | 21,087 | PASS |
| FY2030E | 208,134 | 208,134 | 0.000000 | 47,816 | 23,021 | PASS |


Terminal-value check: g = 3.00% < cost of equity = 10.38% → **PASS**. The same checks pass in the bull, bear and recession scenarios.


---

# PART 1 — Build the Base Case

## 1. What the History Does (and Does Not) Tell Us

| Line item | FY2023 | FY2024 | FY2025 | H1 2026 |
| --- | ---: | ---: | ---: | ---: |
| Total revenue | 96,773 | 97,690 | 94,827 | 50,623 |
| Automotive sales | 78,509 | 72,480 | 65,821 | 35,479 |
| Regulatory credits | 1,790 | 2,763 | 1,993 | 526 |
| Services & other | 8,319 | 10,534 | 12,530 | 8,326 |
| Energy generation & storage | 6,035 | 10,086 | 12,771 | 5,547 |
| GAAP gross margin | 18.2% | 17.9% | 18.0% | 18.7% |
| Operating income | 8,891 | 7,076 | 4,355 | 1,339 |
| Net income to common | 14,997 | 7,091 | 3,794 | 1,591 |
| Model 3/Y deliveries (units) | 1,739,707 | 1,704,093 | 1,585,279 | 809,655 |
| Other-model deliveries (units) | 68,874 | 85,133 | 50,850 | 28,494 |
| Storage deployed (GWh) | 14.7 | 31.4 | 46.7 | 22.3 |
| Operating cash flow | 13,256 | 14,923 | 14,747 | 8,634 |
| Capital expenditures | 8,899 | 11,342 | 8,527 | 8,282 |
| CFO − capex | 4,357 | 3,581 | 6,220 | 352 |


*Sources:* income statement and cash flow [10-K FY2025, pp. 50 and 53](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm); H1 2026 from the [10-Q Q2 2026, pp. 5 and 8–9](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm); deliveries from the 8-K Ex. 99.1 releases; GWh from each 10-K's MD&A overview (FY2025: p. 31) and the 10-Q (p. 28). Every one of the 317 historical values is listed with filing, accession and page in the model's *Sources* page and Excel sheet; in a live run, all 176 XBRL-tagged values matched the SEC's XBRL data with zero mismatches.

**What the history tells us**
- Revenue has been flat for three years (≈\$95–98B) while the mix shifted: automotive sales fell from 78,509 to 65,821, energy doubled, and services grew ~50%.
- Earnings fell sharply: FY2023's 14,997 included a one-time ~\$5.9B tax valuation-allowance release; FY2025 net income was 3,794.
- The business self-funded historically (CFO > capex every year), but H1 2026 capex of 8,282 nearly equals CFO, and management guides 2026 capex **in excess of \$25 billion** ([10-Q p. 35](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)).
- H1 2026 shows a rebound: revenue +21% and services +46% year over year ([10-Q p. 31](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)).

**What the history does NOT tell us**
- Revenue or price **by vehicle model** — only *Model 3/Y* vs *Other models* deliveries are disclosed.
- **D&A by revenue line** — only at segment level (automotive vs energy cost of revenues, [10-K Note 16, p. 93](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)).
- **Robotaxi, FSD and Optimus economics** — robotaxi revenue sits inside services & other; nothing is separately reported.
- A **minimum cash level**, and any capex guidance beyond 2026.
- Which items recur: restructuring (\$684M, \$494M), FX / digital-asset / SpaceX fair-value gains, and tax valuation-allowance releases are **excluded** from the forecast as non-recurring.


## 2. The Assumptions — Every One Labelled

Each assumption carries one label saying where it came from: **history** (held at, or derived from, reported data), **guidance** (company-stated), or **judgment** (my estimate, always with a written rationale). The model has 42 operating drivers (18 history, 1 guidance, 23 judgment) and 15 valuation parameters (4 history, 11 judgment). All live in one file ([`assumptions.py`](tsla-proforma-model/tsla_model/assumptions.py)); every edit made in the app is logged in a revision history.

### 2a. Operating drivers (base case)

| Assumption | Label | FY2026E | FY2030E | Anchor / source |
| --- | :---: | ---: | ---: | --- |
| Model 3/Y deliveries (thousand units) | `judgment` | 1,650 | 1,900 | 8-K Ex. 99.1 delivery releases: FY2025 1,585k; H1 2026 810k |
| Other models deliveries incl. Cybercab/Semi (thousand units) | `judgment` | 58.0 | 360.0 | 8-K Ex. 99.1: FY2025 50.9k; H1 2026 28.5k; Cybercab production began H1 2026 (10-Q p.29) |
| Model 3/Y average selling price (\$ thousand) | `judgment` | 40.8 | 39.2 | Derived: automotive sales / (3Y + 2x other deliveries). FY2025 \$39.0k; H1 2026 \$40.9k |
| Other models ASP (\$ thousand) | `judgment` | 80.0 | 47.0 | Derived history = 2x 3/Y ASP (FY2025 \$78k) |
| Regulatory credit revenue (\$M) | `judgment` | 850 | 200 | 10-K FY2025 p.37: \$1,993M (-28%); 10-Q Q2 2026 p.31: H1 \$526M (-49%); OBBBA restricted credit programs |
| Automotive leasing revenue (\$M) | `judgment` | 1,450 | 1,300 | FY2025 \$1,712M; H1 2026 \$745M (10-Q p.31) |
| Services & other revenue growth (%) | `judgment` | 35.0% | 14.0% | FY2025 \$12,530M (+19%); H1 2026 +46% YoY (10-Q p.31) |
| Robotaxi / autonomy network revenue (\$M) | `judgment` | 0 | 8,000 | No separate disclosure. Robotaxi service launched June 2025; Cybercab production began H1 2026 (10-Q p.28-29) |
| Autonomy revenue cash gross margin (%) | `judgment` | 40.0% | 40.0% | No disclosure |
| Energy storage deployed (GWh) | `judgment` | 50.0 | 95.0 | 10-K: 14.7 / 31.4 / 46.7 GWh (FY2023-25); 10-Q p.28: H1 2026 22.3 GWh |
| Energy revenue per GWh deployed (\$M/GWh) | `judgment` | 245.0 | 220.0 | Derived: FY2025 \$273M; H1 2026 \$249M (includes solar & services) |
| Automotive sales cash gross margin, ex-D&A (%) | `judgment` | 21.0% | 22.0% | Derived from 10-K/10-Q with segment D&A (Note 16): FY2025 19.2%; H1 2026 21.2%; GAAP FY2025 14.5% |
| Automotive leasing cash gross margin (%) | `history` | 50.0% | 50.0% | Derived: FY2025 50.4%; H1 2026 51.3% |
| Services & other cash gross margin (%) | `judgment` | 16.0% | 20.0% | Derived: FY2025 12.5%; H1 2026 16.5% |
| Energy cash gross margin, ex-D&A (%) | `judgment` | 29.0% | 30.0% | Derived: FY2025 32.6%; H1 2026 32.2% (GAAP Q2 2026 fell to 20.4% on tariffs, 10-Q p.32) |
| R&D ex-D&A (% of revenue) | `judgment` | 7.4% | 6.6% | Derived: FY2025 5.6%; H1 2026 7.4% |
| SG&A ex-D&A (% of revenue) | `judgment` | 6.4% | 5.6% | Derived: FY2025 5.1%; H1 2026 6.5% (includes 2025 CEO award SBC, 10-Q p.33) |
| Stock-based compensation (% of revenue, non-cash, within costs) | `judgment` | 4.2% | 3.4% | CF statement: FY2025 3.0%; H1 2026 4.3%; \$9.82B unrecognised CEO award cost over 9.2 yrs (10-Q p.21) |
| D&A (% of beginning net fixed assets) | `history` | 13.0% | 13.0% | Derived: FY2024 13.1%; FY2025 13.3%; H1 2026 ann. 12.8% |
| Share of D&A recorded in cost of revenues (%) | `history` | 67.0% | 67.0% | Segment note D&A in COGS / total D&A: FY2025 67%; H1 2026 66% |
| Capital expenditures (\$M) | `guidance` | 25,000 | 15,000 | 10-Q Q2 2026 p.35: 2026 capex 'in excess of \$25 billion'; H1 2026 actual \$8,282M |
| Strategic equity investments (\$M, non-operating) | `history` | 2,002 | 0 | 10-Q CF p.8-9: purchase of SpaceX equity investment \$2,002M in H1 2026 |
| Receivable days (DSO, on revenue) | `history` | 17.6 | 17.6 | Derived: FY2023 13.2; FY2024 16.5; FY2025 17.6 |
| Inventory days (DIO, on cost of revenues) | `history` | 58.2 | 58.2 | Derived: FY2023 62.9; FY2024 54.7; FY2025 58.2 |
| Payable days (DPO, on cost of revenues) | `history` | 62.8 | 62.8 | Derived: FY2023 66.6; FY2024 56.7; FY2025 62.8 |
| Prepaid & other current assets (% revenue) | `history` | 8.0% | 8.0% | Derived: FY2024 5.5%; FY2025 8.0% |
| Accrued & other liabilities ex-leases (% revenue) | `history` | 20.9% | 20.9% | Derived (current accrued + other LT liabilities - operating lease liabilities): FY2024 16.2%; FY2025 20.9% |
| Deferred revenue, current + non-current (% revenue) | `history` | 7.4% | 7.4% | Derived: FY2024 6.6%; FY2025 7.4% |
| New debt issuance (\$M) | `judgment` | 6,000 | 3,000 | CF history: \$3.9B / \$5.7B / \$5.6B (FY2023-25); H1 2026 \$4.7B (10-Q CF) |
| Debt repayments (\$M) | `judgment` | 5,000 | 2,500 | 10-K Note 9 p.75 scheduled maturities: 2026 \$1,576M, 2027 \$1,233M, 2028 \$649M, 2029 \$4,386M, 2030 \$89M, thereafter \$244M; H1 2026 repaid \$3.9B |
| New finance leases (\$M, non-cash) | `judgment` | 140 | 80 | Finance lease liability \$223M (FY2025) -> \$281M (Q2 2026) |
| Finance lease principal payments (\$M) | `history` | 80 | 80 | 10-K Note 10 finance-lease maturity table: 2026 \$80M, 2027 \$72M, 2028 \$27M, 2029 \$22M, 2030 \$22M, thereafter \$23M |
| Operating lease liability growth (%, non-cash) | `judgment` | 8.0% | 8.0% | Operating lease liabilities \$5,410M -> \$6,343M -> \$6,738M (FY2024, FY2025, Q2 2026) |
| Interest rate on debt & finance leases (% of beginning balance) | `history` | 4.1% | 4.1% | FY2025 interest expense \$338M / average debt & finance leases ~\$8.3B = 4.1% |
| Interest yield on cash & investments (% of beginning balance) | `history` | 3.9% | 3.9% | Derived: FY2025 4.17%; H1 2026 ann. 3.91% |
| Proceeds from option exercises / ESPP (\$M) | `history` | 900 | 900 | CF history: \$700M / \$1,241M / \$1,186M (FY2023-25); H1 2026 \$468M |
| Gross share issuance from equity plans (% of beginning diluted shares) | `history` | 0.6% | 0.6% | Diluted weighted shares 3,485M -> 3,498M -> 3,528M -> 3,540M (FY2023 to Q2 2026) |
| Share repurchases (\$M) | `history` | 0 | 0 | No repurchases in FY2023-FY2025 or H1 2026 cash-flow statements |
| Minimum cash & investments (% of revenue) | `judgment` | 15.0% | 15.0% | Tesla does not state a minimum; it held \$43.5B (86% of H1 2026 annualised revenue) at 2026-06-30 |
| Net income attributable to NCI (\$M) | `history` | 60 | 60 | \$62M / \$61M (FY2024-25); H1 2026 \$28M |
| Distributions to NCI (\$M) | `history` | 90 | 90 | \$144M / \$104M / \$78M (FY2023-25); H1 2026 \$91M |
| Effective tax rate (%) | `judgment` | 26.0% | 23.0% | FY2024 20.4%; FY2025 27.0%; H1 2026 22.1% incl. \$274M CA valuation-allowance release (10-Q p.23) |


### 2b. Why each judgment was made

- **Model 3/Y deliveries (thousand units).** FY2026 = H1 2026 actual (~810k) plus an H2 slightly below H2 2025, which was pulled forward by the Sept-2025 U.S. EV tax-credit expiry. Thereafter low-single-digit growth as the refreshed/standard trims and new markets offset an ageing line-up and intensifying Chinese competition.
- **Other models deliveries incl. Cybercab/Semi (thousand units).** S/X/Cybertruck volumes are small and declining; growth comes from Cybercab and Semi, which Tesla began producing in 2026. The ramp is a judgment - Tesla gives no unit guidance.
- **Model 3/Y average selling price (\$ thousand).** Tesla does not disclose revenue by model. History is split assuming other models carry ~2x the 3/Y price (list-price relationship). Forecast holds near the H1 2026 level, drifting down ~1%/yr for price competition and mix toward cheaper trims; FSD revenue recognised in automotive sales supports ASP.
- **Other models ASP (\$ thousand).** Declines as the mix shifts from S/X/Cybertruck (~\$80k+) toward Cybercab, which Tesla has said will be priced far below current models; blended value reaches the high-\$40ks by 2030.
- **Regulatory credit revenue (\$M).** FY2026 ~ H1 run-rate plus a smaller H2; then continued decline as U.S. programs are curtailed (OBBBA) and other OEMs become self-sufficient in credits. High-margin, so the decline hits profit directly.
- **Automotive leasing revenue (\$M).** Only ~1-2% of deliveries are now subject to operating-lease accounting (8-K Ex. 99.1), so the lease book is running off; revenue stabilises around \$1.3B.
- **Services & other revenue growth (%).** Paid Supercharging, insurance, used vehicles, parts and service scale with Tesla's growing installed fleet. FY2026 reflects the +46% H1 run-rate tapering in H2; growth then fades toward mid-teens.
- **Robotaxi / autonomy network revenue (\$M).** Tesla does not report robotaxi revenue; any current amount sits in services & other. This line is an explicit, isolated judgment for incremental ride-hailing revenue so its value contribution is visible. Base assumes a gradual multi-city ramp; bear assumes no material commercial scale by 2030.
- **Autonomy revenue cash gross margin (%).** A company-owned fleet carries vehicle depreciation (captured via capex/D&A), energy, cleaning, insurance and remote-operations costs. A 40% cash gross margin is an assumption, not a Tesla figure.
- **Energy storage deployed (GWh).** Lathrop and Shanghai Megafactories are ramping and a Houston Megafactory is under construction (10-Q p.30). Growth slows from the 2023-25 pace as tariffs weigh on the U.S. business.
- **Energy revenue per GWh deployed (\$M/GWh).** Megapack ASPs are falling (10-K p.38 cites lower Megapack ASP) as cell costs fall and competition rises; the ratio drifts down ~2-3% per year from the H1 2026 level.
- **Automotive sales cash gross margin, ex-D&A (%).** Margins are modelled before D&A so capex and depreciation flow through explicitly. Base holds near the H1 2026 level, with modest improvement from cost-down and own-cell/cathode ramps offset by tariffs.
- **Services & other cash gross margin (%).** Operating leverage in Supercharging and service as the fleet grows; H1 2026 already showed a step-up.
- **Energy cash gross margin, ex-D&A (%).** Below the FY2025 level because the 10-Q flags tariffs weighing more heavily on energy than autos; partially offset by manufacturing credits and Shanghai Megafactory scale.
- **R&D ex-D&A (% of revenue).** AI training, Optimus and Cybercab keep R&D elevated at the H1 2026 intensity, easing slightly as revenue grows. Bear keeps the base ratios (management trims spend as growth stalls); recession shows a temporary spike as revenue falls faster than costs.
- **SG&A ex-D&A (% of revenue).** Held near the H1 2026 ratio, which includes ~\$1.1B/yr of 2025 CEO Performance Award expense; modest leverage thereafter. Bear keeps the base ratios; recession shows a temporary spike as revenue falls faster than costs.
- **Stock-based compensation (% of revenue, non-cash, within costs).** SBC is already inside the cost ratios above; this line only sizes the non-cash add-back and APIC build. Declines as a share of revenue while CEO award expense stays roughly flat in dollars.
- **New debt issuance (\$M).** Tesla's debt is mostly non-recourse auto/energy ABS that is refinanced continuously. FY2026 = H1 actual plus a smaller H2; later years roughly refinance scheduled maturities.
- **Debt repayments (\$M).** FY2026 = H1 actual plus H2 scheduled amortisation; later years = scheduled maturities (incl. the 2029 bullet) plus ABS amortisation of new issuance.
- **New finance leases (\$M, non-cash).** Small; set so the finance-lease balance stays roughly stable.
- **Operating lease liability growth (%, non-cash).** Store, service and Supercharger footprint growth; the ROU asset moves one-for-one, so no cash or equity effect.
- **Minimum cash & investments (% of revenue).** About two months of costs is a prudent operating buffer for a capital-intensive manufacturer. Cash above this level is treated as excess (non-operating) in the valuation.
- **Effective tax rate (%).** Non-deductible 2025 CEO award expense (10-Q p.23) lifts the rate while pre-tax income is small; it converges toward ~23% as profits grow. One-off valuation-allowance releases are excluded.

### 2c. Valuation parameters

| Parameter | Label | Value | Rationale |
| --- | :---: | ---: | --- |
| Risk-free rate (10-year U.S. Treasury) | `history` | 5.11% | Observed market yield matching the long-dated equity cash flows. |
| Equity risk premium | `judgment` | 4.50% | Within the ~4-5% range of implied U.S. ERP estimates (e.g. Damodaran's monthly implied ERP) in 2024-2026. Update to the latest estimate before use. |
| Beta used in CAPM | `judgment` | bottom-up | Bottom-up peer beta is less noisy than a single regression and reflects the business mix; the observed regression beta is shown as an alternative discount-rate case. |
| Observed TSLA beta (5y monthly vs S&P 500) | `history` | 1.76 | OLS slope of 5 years of monthly total returns (adjusted close) vs. S&P 500 (^GSPC), 59 observations |
| Bottom-up beta: weight on auto peers vs energy peers | `judgment` | 85.00% | Weights the unlevered-beta averages of the auto (legacy + EV) and energy peer groups by Tesla's revenue mix. |
| Marginal tax rate for relevering | `history` | 21.00% | Standard Hamada relevering input. |
| Terminal FCFE growth (Gordon) | `judgment` | 3.00% | Below the 5.1% risk-free rate (a proxy for long-run nominal growth); a mature Tesla growing with nominal GDP. |
| Terminal capex / D&A | `judgment` | 1.15 | In steady state capex must exceed depreciation enough to fund growth; 1.15x supports ~3% growth on Tesla's asset base without the 2026-28 AI/capacity build-out. |
| Add back SBC as a non-cash charge in FCFE | `judgment` | True | The requested FCFE definition adds back non-cash charges. Because SBC is a real economic cost, set this to False for a conservative case; share dilution is modelled separately. |
| Include 423.7M unearned 2025 CEO award shares in diluted count | `judgment` | False | Excluded by default, consistent with GAAP diluted EPS (not yet earned). Set to True to value per share as if all market-cap milestones (which imply a far higher price) are achieved. |
| Mid-period discounting convention | `judgment` | False | End-of-period discounting by default (more conservative); mid-period assumes cash arrives evenly. |
| Revolver capacity (\$M) | `history` | 5,000 | Only drawn if cash falls below the minimum. |
| Revolver interest rate | `judgment` | 6.00% | Approximately SOFR plus an investment-grade margin; only matters if the revolver is drawn. |
| Cross-check: forward P/E low | `judgment` | 15.0 | Roughly a large-cap industrial/auto multiple; secondary cross-check only. |
| Cross-check: forward P/E high | `judgment` | 40.0 | Roughly a high-growth large-cap technology multiple; secondary cross-check only. |


## 3. One Year Built Line by Line — FY2026E (cash computed last)

**Revenue build** (driver × driver, never a single growth rate):

| Step | Calculation | FY2026E |
|---|---|---:|
| Automotive sales | 1,650k Model 3/Y × \$40.8k + 58k other × \$80k | 71,960 |
| Regulatory credits | judgment (OBBBA run-off) | 850 |
| Automotive leasing | judgment | 1,450 |
| Services & other | FY2025 12,530 × (1 + 35%) | 16,916 |
| Robotaxi / autonomy | judgment (isolated line) | 0 |
| Energy | 50 GWh × \$245M/GWh | 12,250 |
| **Total revenue** | sum of the lines above (reconciliation check) | **103,426** |

**Income statement:**

| Line | How it is computed | FY2026E |
|---|---|---:|
| Cash cost of revenues | each line × (1 − its cash gross margin, ex-D&A) | (80,480) |
| Cash gross profit | revenue − cash cost of revenues | 22,946 |
| R&D (ex-D&A) | 7.4% of revenue | (7,653) |
| SG&A (ex-D&A) | 6.4% of revenue | (6,619) |
| **EBITDA** | | **8,673** |
| D&A | 13.0% × beginning net fixed assets 50,159 | (6,521) |
| **EBIT** | | **2,152** |
| Interest income | 3.91% × beginning cash & investments 44,059 | 1,723 |
| Interest expense | 4.1% × beginning debt + finance leases 8,376 | (343) |
| Pre-tax income | | 3,531 |
| Income tax | 26% effective rate | (918) |
| Net income (incl. NCI) | | 2,613 |
| **Net income to common** | less 60 to noncontrolling interests | **2,553** |

Interest uses **beginning** balances, so there is no circular reference.

**Balance sheet (everything except cash):**

| Line | Driver | FY2025A | FY2026E |
|---|---|---:|---:|
| Accounts receivable | 17.6 days of revenue | 4,576 | 4,987 |
| Inventory | 58.2 days of cost of revenues | 12,392 | 13,529 |
| Prepaid & other | 8.0% of revenue | 7,615 | 8,305 |
| Net fixed assets | begin + capex 25,000 + new finance leases 140 − D&A 6,521 | 50,159 | 68,778 |
| Accounts payable | 62.8 days of cost of revenues | 13,371 | 14,599 |
| Accrued & other (ex-leases) | 20.9% of revenue | 19,796 | 21,595 |
| Deferred revenue | 7.4% of revenue | 7,055 | 7,695 |
| Debt | begin + issued 6,000 − repaid 5,000 | 8,153 | 9,153 |
| Stockholders' equity | begin + NI 2,553 + SBC 4,344 + options 900 | 82,137 | 89,934 |

**Cash, computed last — from the cash-flow statement only:**

| Line | FY2026E |
|---|---:|
| Net income (incl. NCI) | 2,613 |
| + D&A | 6,521 |
| + Stock-based compensation (non-cash) | 4,344 |
| ± Change in net working capital (a release is a cash inflow) | 1,428 |
| **Cash from operations** | **14,906** |
| − Capex (guidance: >\$25B) | (25,000) |
| − SpaceX equity investment (H1 actual) | (2,002) |
| **Cash from investing** | **(27,002)** |
| Debt issued − repaid − finance-lease principal | 920 |
| Option proceeds − NCI distributions | 810 |
| Revolver draw | 0 |
| **Cash from financing** | **1,730** |
| Beginning cash & ST investments | 44,059 |
| **Ending cash & ST investments** | **33,693** |
| Cash floor (15% of revenue) | 15,514 → floor respected, no revolver draw |

Only then is the balance sheet totalled: assets 150,807 = liabilities 60,175 + equity 90,632 (difference 0.000). No plug exists anywhere; a test raises FY2030 capex by \$1,000M and confirms cash falls by exactly \$1,000M while fixed assets rise by \$1,000M.


## 4. Checks That Fail on Purpose

A check that never fails proves nothing. Three deliberate breaks, each re-run through the full model:

| Deliberate break | Check(s) that caught it | Valuation status |
| --- | --- | --- |
| Add \$500M of cash to the FY2028 balance sheet without a cash-flow entry | 1. Assets = liabilities + equity; 2. Cash-flow ending cash = balance-sheet cash | **FAILED** — no value produced |
| Terminal growth 12% vs cost of equity 10.38% | 7. Terminal growth < cost of equity | **FAILED** — no value produced |
| Capex \$60B a year with no revolver | 6. Cash >= minimum (after any revolver financing) | **FAILED** — no value produced |


In each case the function returns `status = "FAILED"` and **no value per share**; the app shows a red "Valuation refused" banner and the Excel export writes "VALUATION REFUSED" on the Valuation sheet. These cases are permanent automated tests (`tests/test_valuation_and_checks.py`, `tests/test_app.py`).

## 5. Five Years of Statements That Balance

**Income statement (condensed)**

| Line | FY2025A | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Total revenue | 94,827 | 103,426 | 113,867 | 126,856 | 140,579 | 153,475 |
| Cash gross profit | 21,229 | 22,946 | 25,324 | 28,963 | 33,071 | 36,763 |
| EBITDA | 10,503 | 8,673 | 10,066 | 12,472 | 15,359 | 18,039 |
| D&A | 6,148 | 6,521 | 8,941 | 10,649 | 11,615 | 12,196 |
| EBIT | 4,355 | 2,152 | 1,124 | 1,823 | 3,743 | 5,843 |
| Interest income | 1,680 | 1,723 | 1,317 | 1,142 | 1,251 | 1,434 |
| Interest expense | (338) | (343) | (387) | (387) | (407) | (305) |
| Income tax | (1,423) | (918) | (514) | (619) | (1,055) | (1,604) |
| Net income to common | 3,794 | 2,553 | 1,481 | 1,899 | 3,472 | 5,309 |
| Memo: GAAP gross margin | 18.0% | 18.0% | 17.0% | 17.2% | 18.0% | 18.6% |
| Memo: EBITDA margin | 11.1% | 8.4% | 8.8% | 9.8% | 10.9% | 11.8% |
| Memo: diluted EPS (\$) | \$1.08 | \$0.72 | \$0.41 | \$0.53 | \$0.96 | \$1.46 |


**Balance sheet (condensed)**

| Line | FY2025A | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Cash & short-term investments | 44,059 | 33,693 | 29,197 | 31,998 | 36,688 | 47,816 |
| Accounts receivable | 4,576 | 4,987 | 5,491 | 6,117 | 6,779 | 7,400 |
| Inventory | 12,392 | 13,529 | 15,074 | 16,747 | 18,383 | 19,913 |
| Net fixed assets (PP&E + lease vehicles + energy systems) | 50,159 | 68,778 | 81,917 | 89,348 | 93,813 | 96,697 |
| TOTAL ASSETS | 137,806 | 150,807 | 162,884 | 177,050 | 190,244 | 208,134 |
| Accounts payable | 13,371 | 14,599 | 16,265 | 18,071 | 19,836 | 21,487 |
| Accrued & other liabilities (ex-leases) | 19,796 | 21,595 | 23,775 | 26,488 | 29,353 | 32,045 |
| Debt (ex-finance leases) | 8,153 | 9,153 | 9,153 | 9,653 | 7,153 | 7,653 |
| Revolver | 0 | 0 | 0 | 0 | 0 | 0 |
| TOTAL LIABILITIES | 54,941 | 60,175 | 65,346 | 71,923 | 75,714 | 82,207 |
| TOTAL EQUITY | 82,865 | 90,632 | 97,538 | 105,128 | 114,530 | 125,928 |
| TOTAL LIABILITIES & EQUITY | 137,806 | 150,807 | 162,884 | 177,050 | 190,244 | 208,134 |


**Cash flow and FCFE**

| Line | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cash from operations | 14,906 | 16,774 | 19,570 | 22,460 | 24,899 |
| Capital expenditures | (25,000) | (22,000) | (18,000) | (16,000) | (15,000) |
| Cash from investing | (27,002) | (22,000) | (18,000) | (16,000) | (15,000) |
| Cash from financing | 1,730 | 730 | 1,230 | (1,770) | 1,230 |
| Ending cash & ST investments | 33,693 | 29,197 | 31,998 | 36,688 | 47,816 |
| FCFE | (9,234) | (5,366) | 1,930 | 3,820 | 10,259 |
| Operating FCFE (valued) | (10,509) | (6,354) | 1,063 | 2,857 | 9,154 |


FCFE = net income + D&A + SBC (non-cash) − capex − increase in NWC + net borrowing. *Operating* FCFE removes after-tax interest income, because the cash pile is valued separately at its balance-sheet amount (otherwise it would be counted twice).


## 6. One Value per Share

**Cost of equity (CAPM):** k<sub>e</sub> = r<sub>f</sub> + β × ERP = 5.11% + 1.17 × 4.50% = **10.38%**
(r<sub>f</sub> = 10-year U.S. Treasury, 2026-09-23; β = bottom-up peer beta, Section 7).

**Discounting the forecast** (valuation date September 24, 2026; the H1 2026 cash already sits in the 30-Jun-2026 balance sheet, so only H2 2026 onward is valued):

| Year | Operating FCFE valued | Discount period (yrs) | Discount factor | Present value |
| --- | ---: | ---: | ---: | ---: |
| FY2026E (H2 only) | (10,885) | 0.27 | 0.9739 | (10,601) |
| FY2027E | (6,354) | 1.27 | 0.8824 | (5,606) |
| FY2028E | 1,063 | 2.27 | 0.7992 | 849 |
| FY2029E | 2,857 | 3.27 | 0.7241 | 2,069 |
| FY2030E | 9,154 | 4.27 | 0.6561 | 6,006 |
| **Total** |  |  |  | **(7,283)** |


**The 2031 FCFE bridge (terminal year):**

| Component | FY2030E | FY2031 |
| --- | ---: | ---: |
| Net income to common, ex-interest income (FY2030E x (1+g)) | 4,205 | 4,331 |
| + D&A (grown at g) | 12,196 | 12,562 |
| + SBC (if added back) | 5,218 | 5,375 |
| - Capex (terminal capex/D&A x D&A) | (15,000) | (14,446) |
| - Increase in NWC (NWC x g) | 2,116 | 759 |
| + Net borrowing (debt x g, constant leverage) | 420 | 238 |
| = Operating FCFE | 9,154 | 8,819 |


Terminal value (end-2030) = FCFE<sub>2031</sub> / (k<sub>e</sub> − g) = 8,819 / (10.38% − 3.00%) = **119,535**, worth **78,427** today.

**Equity value bridge:**

| Item | Value |
| --- | ---: |
| PV of operating FCFE (H2 2026 - 2030) | (7,283) |
| Terminal value at end-2030 (FCFE 2031 / (ke - g)) | 119,535 |
| PV of terminal value (discounted 4.27 yrs) | 78,427 |
| Cash & ST investments (30-Jun-2026) | 43,524 |
| Less: minimum operating cash | (15,514) |
| Excess cash | 28,010 |
| Digital assets (30-Jun-2026) | 674 |
| SpaceX equity investment (carrying value) | 3,007 |
| Total non-operating assets | 31,691 |
| Total equity value | 102,835 |
| Diluted shares (M) | 3,540 |
| Implied value per share (\$) | \$29.05 |
| Market price (\$, 2026-09-24) | \$378.25 |
| Upside / (downside) | -92.3% |
| Terminal value share of DCF value (PV FCFE + PV TV) | 110.2% |
| Terminal value share of total equity value | 76.3% |


> **Base-case implied value: \$29.05 per share vs. \$378.25 market price (-92.3%).**
> 110% of the DCF value comes from the terminal value (above 100% because the 2026–27 FCFE is negative while Tesla spends heavily on capex); the terminal value is 76% of total equity value.

---

# PART 2 — Take It Apart

## 7. Beta, Measured Two Ways

**Observed beta:** the OLS slope of 60 months of TSLA monthly total returns (adjusted closes, 59 return observations) on the S&P 500 = **1.76**, giving k<sub>e</sub> = 13.03%.

**Bottom-up beta:** unlever each peer's regression beta with Hamada, β<sub>U</sub> = β<sub>L</sub> / (1 + (1 − t) D/E), average by business group, weight by Tesla's revenue mix, then relever at Tesla's forecast D/E.

| Peer | Group | Levered β | D/E | Tax rate | Unlevered β | Debt source |
| --- | --- | ---: | ---: | ---: | ---: | :---: |
| GM | Legacy auto | 1.42 | 0.22 | 21% | 1.21 | judgment |
| F | Legacy auto | 1.89 | 0.40 | 21% | 1.44 | judgment |
| RIVN | EV pure-play | 1.67 | 0.20 | 0% | 1.39 | history |
| LCID | EV pure-play | 0.76 | 2.02 | 0% | 0.25 | history |
| ENPH | Energy/storage | 1.40 | 0.14 | 21% | 1.26 | history |
| FLNC | Energy/storage | 2.74 | 0.29 | 0% | 2.12 | history |


Auto peers average β<sub>U</sub> = 1.07; energy peers = 1.69; weighted 85% / 15% by FY2025 revenue mix = 1.16. Tesla's forecast D/E is only 0.007 (≈\$9B of debt against a ≈\$1.3T market cap), so the relevered beta is **1.17**.

**Choice:** the bottom-up beta (1.17) is used in the base case because a single stock's regression is noisy and Tesla's price is driven by sentiment about autonomy; the observed beta (1.76) is shown as an alternative discount-rate case. *Judgment flags:* GM and Ford debt exclude their captive finance arms (approximations); LCID's low β with very high D/E pulls the auto average down.

## 8. The Same Statements at Seven Discount Rates

The three statements do not change with the discount rate — only the valuation does. At g = 3.0%:

| Cost of equity | 7.38% | 8.38% | 9.38% | 10.38% | 11.38% | 12.38% | 13.38% |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Value per share | \$49.07 | \$39.87 | \$33.59 | \$29.04 | \$25.60 | \$22.91 | \$20.76 |


**Full cost-of-equity × terminal-growth grid** (value per share; every cell is a full re-run):

| k<sub>e</sub> \ g | 1.00% | 2.00% | 2.50% | 3.00% | 3.50% | 4.00% | 5.00% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7.38% | \$33.24 | \$39.68 | \$43.90 | \$49.07 | \$55.57 | \$64.00 | \$91.49 |
| 8.38% | \$28.75 | \$33.44 | \$36.38 | \$39.87 | \$44.07 | \$49.24 | \$64.15 |
| 9.38% | \$25.36 | \$28.91 | \$31.08 | \$33.59 | \$36.52 | \$40.00 | \$49.34 |
| 10.38% | \$22.70 | \$25.49 | \$27.15 | \$29.04 | \$31.20 | \$33.70 | \$40.09 |
| 11.38% | \$20.58 | \$22.82 | \$24.13 | \$25.60 | \$27.25 | \$29.13 | \$33.77 |
| 12.38% | \$18.85 | \$20.68 | \$21.74 | \$22.91 | \$24.22 | \$25.68 | \$29.19 |
| 13.38% | \$17.41 | \$18.94 | \$19.81 | \$20.76 | \$21.82 | \$22.98 | \$25.73 |


Even at a 7.38% cost of equity with 5.00% perpetual growth the model reaches \$91.49 — far below \$378.25. At the observed beta (k<sub>e</sub> 13.03%) the base case is worth \$21.47.

## 9. What the Terminal Value Assumes

- **It carries the valuation:** PV of terminal value = 78,427 vs. PV of forecast FCFE = (7,283). The forecast period alone is worth less than nothing, because 2026–27 capex (\$25B, \$22B) exceeds operating cash flow.
- **Growth:** g = 3.0% forever, below the 5.11% risk-free rate (a proxy for long-run nominal growth). A mature Tesla growing with the economy.
- **Reinvestment:** 2031 capex = 1.15× D&A. Enough to grow the asset base slowly; it assumes the 2026–28 AI and capacity build-out ends. If capex stayed at 2030's level (\$15B against FY2030 D&A of \$12.2B), terminal FCFE would be lower.
- **Leverage and working capital:** debt and net working capital both grow at g, so leverage stays constant.
- **Margins:** FY2030E EBITDA margin of 11.8% continues forever — below FY2023's 14.0%, above H1 2026's ≈9%.
- **What it leaves out:** any Optimus value, and robotaxi scale beyond \$8B of 2030 revenue. Those are exactly what the market price is paying for (Section 11).

## 10. Every Assumption Shocked

**Tornado** — each core driver moved by one standard shock in every forecast year, full model re-run (base = \$29.05):

| Rank | Driver | Shock | Low case | High case | Range |
| :---: | --- | ---: | ---: | ---: | ---: |
| 1 | Automotive sales cash gross margin, ex-D&A (%) | 2.0 pts | \$24.02 | \$34.08 | \$10.06 |
| 2 | SG&A ex-D&A (% of revenue) | 1.0 pts | \$33.19 | \$24.91 | \$8.28 |
| 3 | R&D ex-D&A (% of revenue) | 1.0 pts | \$33.19 | \$24.91 | \$8.28 |
| 4 | Capital expenditures (\$M) | 10% | \$33.18 | \$24.92 | \$8.26 |
| 5 | Model 3/Y average selling price (\$ thousand) | 10% | \$25.98 | \$32.12 | \$6.14 |
| 6 | Model 3/Y deliveries (thousand units) | 10% | \$25.98 | \$32.12 | \$6.14 |
| 7 | Services & other revenue growth (%) | 5.0 pts | \$27.04 | \$31.41 | \$4.36 |
| 8 | Services & other cash gross margin (%) | 2.0 pts | \$27.39 | \$30.71 | \$3.33 |
| 9 | D&A (% of beginning net fixed assets) | 1.0 pts | \$30.40 | \$27.79 | \$2.61 |
| 10 | Energy storage deployed (GWh) | 10% | \$27.76 | \$30.34 | \$2.58 |
| 11 | Energy revenue per GWh deployed (\$M/GWh) | 10% | \$27.76 | \$30.34 | \$2.58 |
| 12 | Energy cash gross margin, ex-D&A (%) | 2.0 pts | \$27.94 | \$30.16 | \$2.22 |
| 13 | Other models deliveries incl. Cybercab/Semi (thousand units) | 10% | \$28.39 | \$29.71 | \$1.33 |
| 14 | Robotaxi / autonomy network revenue (\$M) | 10% | \$28.42 | \$29.68 | \$1.26 |
| 15 | Payable days (DPO, on cost of revenues) | 5.0 days | \$28.48 | \$29.62 | \$1.13 |
| 16 | Inventory days (DIO, on cost of revenues) | 5.0 days | \$29.62 | \$28.48 | \$1.13 |
| 17 | Effective tax rate (%) | 3.0 pts | \$29.56 | \$28.54 | \$1.02 |
| 18 | Receivable days (DSO, on revenue) | 3.0 days | \$29.47 | \$28.63 | \$0.83 |


**One-variable sensitivity** (value per share at −2, −1, 0, +1, +2 shocks):

| Driver | 1 shock = | −2 | −1 | 0 | +1 | +2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Model 3/Y deliveries (thousand units) | +10% | \$22.91 | \$25.98 | \$29.05 | \$32.12 | \$35.19 |
| Other models deliveries incl. Cybercab/Semi (thousand units) | +10% | \$27.72 | \$28.39 | \$29.05 | \$29.71 | \$30.38 |
| Model 3/Y average selling price (\$ thousand) | +10% | \$22.91 | \$25.98 | \$29.05 | \$32.12 | \$35.19 |
| Services & other revenue growth (%) | +5.0 pts | \$25.35 | \$27.04 | \$29.05 | \$31.41 | \$34.16 |
| Robotaxi / autonomy network revenue (\$M) | +10% | \$27.79 | \$28.42 | \$29.05 | \$29.68 | \$30.31 |
| Energy storage deployed (GWh) | +10% | \$26.47 | \$27.76 | \$29.05 | \$30.34 | \$31.63 |
| Energy revenue per GWh deployed (\$M/GWh) | +10% | \$26.47 | \$27.76 | \$29.05 | \$30.34 | \$31.63 |
| Automotive sales cash gross margin, ex-D&A (%) | +2.0 pts | \$18.87 | \$24.02 | \$29.05 | \$34.08 | \$39.11 |
| Services & other cash gross margin (%) | +2.0 pts | \$25.72 | \$27.39 | \$29.05 | \$30.71 | \$32.38 |
| Energy cash gross margin, ex-D&A (%) | +2.0 pts | \$26.83 | \$27.94 | \$29.05 | \$30.16 | \$31.27 |
| R&D ex-D&A (% of revenue) | +1.0 pts | \$37.33 | \$33.19 | \$29.05 | \$24.91 | \$20.75 |
| SG&A ex-D&A (% of revenue) | +1.0 pts | \$37.33 | \$33.19 | \$29.05 | \$24.91 | \$20.75 |
| D&A (% of beginning net fixed assets) | +1.0 pts | \$31.84 | \$30.40 | \$29.05 | \$27.79 | \$26.62 |
| Capital expenditures (\$M) | +10% | \$37.31 | \$33.18 | \$29.05 | \$24.92 | \$20.72 |
| Receivable days (DSO, on revenue) | +3.0 days | \$29.88 | \$29.47 | \$29.05 | \$28.63 | \$28.22 |
| Inventory days (DIO, on cost of revenues) | +5.0 days | \$30.18 | \$29.62 | \$29.05 | \$28.48 | \$27.91 |
| Payable days (DPO, on cost of revenues) | +5.0 days | \$27.91 | \$28.48 | \$29.05 | \$29.62 | \$30.18 |
| Effective tax rate (%) | +3.0 pts | \$30.07 | \$29.56 | \$29.05 | \$28.54 | \$28.03 |


**Two-variable matrix — the two highest-impact assumptions** (rows: SG&A ex-D&A (% of revenue); columns: Automotive sales cash gross margin, ex-D&A (%)):

|  | -4.0 pts | -2.0 pts | +0.0 pts | +2.0 pts | +4.0 pts |
| --- | ---: | ---: | ---: | ---: | ---: |
| -2.0 pts | \$27.27 | \$32.30 | \$37.33 | \$42.36 | \$47.39 |
| -1.0 pts | \$23.13 | \$28.16 | \$33.19 | \$38.22 | \$43.25 |
| +0.0 pts | \$18.87 | \$24.02 | \$29.05 | \$34.08 | \$39.11 |
| +1.0 pts | \$14.52 | \$19.81 | \$24.91 | \$29.94 | \$34.97 |
| +2.0 pts | \$9.58 | \$15.51 | \$20.75 | \$25.80 | \$30.83 |


Every cell is a full re-run: the corner values differ from base + Δx + Δy (a test proves it), because the effects interact through D&A, tax, working capital and cash. No single operating assumption moves the value by more than about \$10 per share.

## 11. What Would the Market Price Require?

| Lever (moved alone) | Model assumption | Required for \$378 | Comment |
| --- | --- | --- | --- |
| Cost of equity | 10.38% | 3.58% | Discount rate that equates model FCFE with the market price |
| Terminal FCFE growth | 3.00% | 9.80% | Perpetual growth needed (must stay below cost of equity) |
| Robotaxi / autonomy revenue, FY2030E | \$8.0B in FY2030E | \$451B | All years scaled by the same factor; margins unchanged |
| Automotive sales cash gross margin (all years) | 22.0% in FY2030E | Not achievable within tested range | Parallel shift in every year; value at range limit: \$180/share |
| Model 3/Y deliveries (all years) | 1.90M units in FY2030E | Not achievable within tested range | Scales volumes only; capex held at the scenario path; value at range limit: \$323/share |
| Energy storage deployed (all years) | 95 GWh in FY2030E | 2,622 GWh in FY2030E (x27.60) | Scales GWh; price per GWh and margin unchanged |
| Services & other growth (all years) | 14% in FY2030E | +126 pts per year | Parallel shift in annual growth |
| Capital expenditures (all years) | \$15.0B in FY2030E | Not achievable within tested range | Lower capex with unchanged growth - an inconsistent, upper-bound test; value at range limit: \$70/share |
| Terminal capex / D&A | 1.15x | Not achievable within tested range | Below 1.0x means the asset base shrinks in perpetuity; value at range limit: \$65/share |


Each lever is moved on its own, with everything else at base values, and the full model is solved by bisection until value = price. The market price requires either a discount rate below the risk-free rate, near-10% perpetual growth, or robotaxi revenue of several hundred billion dollars by 2030. Operating levers in today's businesses (auto margins, volumes, capex) **cannot** reach the price alone. The market is pricing an autonomy/AI business this model does not include.

## 12. Scenarios and the Price / Value Bridge

| Scenario | Value / share | vs. market | FY2030E revenue | FY2030E EBITDA margin | FY2030E FCFE | Checks |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| Base | \$29.05 | -92.3% | 153,475 | 11.8% | 10,259 | PASS |
| Bull | \$87.83 | -76.8% | 224,732 | 18.0% | 31,642 | PASS |
| Bear | \$4.16 | -98.9% | 111,131 | 6.8% | 2,574 | PASS |
| Recession / downside | \$3.02 | -99.2% | 112,638 | 7.7% | 1,493 | PASS |



| Case | Value per share | Cost of equity | vs. market |
| --- | ---: | ---: | ---: |
| Market price (2026-09-24) | \$378.25 | — | 0.0% |
| Recession / downside case | \$3.02 | 10.38% | -99.2% |
| Bear case | \$4.16 | 10.38% | -98.9% |
| Base case | \$29.05 | 10.38% | -92.3% |
| Bull case | \$87.83 | 10.38% | -76.8% |
| Base @ observed beta (1.76) | \$21.47 | 13.03% | -94.3% |
| Base @ cost of equity 9.4% | \$33.60 | 9.38% | -91.1% |
| Base @ cost of equity 11.4% | \$25.61 | 11.38% | -93.2% |


- **Bull:** ~2.2M Model 3/Y units and 750k other models by 2030, \$25B robotaxi revenue at 50% margin, 25% auto margin, 135 GWh.
- **Bear:** flat volumes, lower prices and margins, capex cut to ≈\$10.5B (without the cut, the bear case breaches the cash floor and the model refuses to value it).
- **Recession:** 2027 delivery drop of ~15%, margin compression, inventory build, capex cut; it is the only case that draws the revolver (≈\$0.5B).

## 13. The Pictures

All charts are generated from model outputs (none are typed in) and live in the app (`streamlit run app.py`):

| Chart | App page | What it shows |
|---|---|---|
| Market price vs. implied value (bridge) | Executive summary, Sensitivities | Market price against every scenario and discount-rate case |
| Revenue by segment, reported → forecast | Financial statements → Charts | Mix shift from autos to services, energy and robotaxi |
| Margins (GAAP gross, EBITDA, EBIT) | Financial statements → Charts | Margin trough in 2026–27, recovery by 2030 |
| Liquidity vs. cash floor | Financial statements → Charts | Cash falls from \$44B to \$29B, stays above the floor |
| FCFE by year | Valuation | Negative FCFE during the capex build, positive from 2028 |
| Equity value waterfall | Valuation | PV FCFE + PV terminal value + non-operating assets |
| k<sub>e</sub> × g heat map | Sensitivities | Section 8 grid |
| Tornado | Sensitivities | Section 10 ranking |
| Two-variable matrix | Sensitivities | Section 10 matrix |

The Excel export (sidebar → *Prepare Excel export*) has separate Sources, Assumptions, Historical Financials, Forecast, Valuation, Scenarios and Checks sheets.

## 14. Presenting It — Telling Colleagues, Answering Questions, Defending the Work

**The 30-second version:**
> "Built from Tesla's filings, a five-year three-statement model whose checks pass in every year values the equity at about \$29 a share against a \$378 price. The gap is not a modelling error. Tesla's current businesses, even with a robotaxi line and energy growth, do not generate the cash to support the price. To get there you need a cost of equity near 3.6%, perpetual growth near 10%, or about \$450 billion of robotaxi revenue by 2030. The market is paying for an autonomy and AI outcome that is not in the filings yet."

**Questions I expect, and my answers:**

| Question | Answer |
|---|---|
| "Isn't a DCF the wrong tool for Tesla?" | It is the right tool for asking what the cash flows support. Section 11 turns it around to show what the price assumes. The DCF does not claim the market is wrong; it makes the bet explicit. |
| "Your robotaxi number is made up." | Yes, and it is labelled *judgment*. It sits on its own line so its value is visible, and it is solved for in Section 11. Even 10× the base case (\$80B) does not reach the price. |
| "Why bottom-up beta instead of Tesla's own?" | A single-stock regression is noisy. The observed beta is shown anyway (Section 7); it lowers the value to ≈\$21. |
| "Doesn't adding back SBC overstate FCFE?" | It follows the lab's FCFE definition (non-cash charges added back). The toggle to treat SBC as a cash cost lowers the value further; dilution is modelled separately. |
| "Why is the terminal value over 100% of the DCF?" | Because 2026–27 FCFE is negative during the capex build. That is a real feature of Tesla's plan, not an error, and it is why Section 9 examines the terminal assumptions line by line. |
| "How do I know the statements are right?" | The check block runs every year: the balance sheet re-sums from components, cash ties to the cash-flow statement, all roll-forwards tie. Section 4 breaks it on purpose. 66 automated tests re-run it, and 176 historical values matched the SEC's XBRL data. |

**What would change my mind:** disclosed robotaxi revenue and unit economics (cost per mile, utilisation); capex guidance falling back toward D&A after 2027; auto gross margin (ex-credits) sustainably above 20%.

## 15. Limitations (from Tesla's disclosures and from the model)

- **No revenue or price by vehicle model.** Category ASPs assume other models sell at ≈2× the Model 3/Y price; only the blended ASP is observable.
- **D&A is disclosed by segment only.** Automotive D&A is allocated pro-rata across automotive sales, leasing and services to derive cash margins.
- **Robotaxi, FSD and Optimus are not reported.** Robotaxi is an explicit judgment line; Optimus is excluded from every scenario.
- **No stated minimum cash, and capex guidance for 2026 only.** The 15%-of-revenue floor and 2027–30 capex are judgment.
- **Share count:** the 423.7M unearned 2025 CEO award shares are excluded (consistent with GAAP diluted EPS); including them lowers the value.
- **Lease vehicles:** operating-lease vehicle additions run through operating cash flow in Tesla's statements; the model treats all fixed-asset additions as capex.
- **Peers:** GM and Ford debt uses judgment-based ex-captive-finance approximations, and the ERP (4.5%) is a judgment.

## 16. Reproduce It

```bash
cd tsla-proforma-model
pip install -r requirements.txt
python -m pytest -q      # 66 tests; offline, no network needed
streamlit run app.py     # dashboard; sidebar toggle switches live vs seed data
```

The tables in this lab were generated from the model's seed data (market data as of September 24, 2026), so they are reproducible; a live run refreshes the price, Treasury yield and betas and moves the result by cents.

## 17. How AI Was Used

The model, tests and this write-up were built with an AI coding assistant (Claude). The process followed the tutorial: every historical figure was extracted from the SEC filings with its page; every assumption was labelled; the check block and refusal logic were written before the valuation; and the numbers in this document were generated directly from the model code, not retyped. As the tutorial says, the first build is slow because you are building the process, not the product. That process can now be re-run for the next company.

---

> **Disclaimer.** Educational and research use only. This model is not investment advice and is not a recommendation to buy, sell or hold TSLA or any other security. Forecasts are hypothetical, depend on judgment-based assumptions that are clearly labelled, and may be materially wrong. Historical data are taken from Tesla's SEC filings; verify all figures against the original documents before relying on them. Past performance does not predict future results.
