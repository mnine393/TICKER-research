# Validation and AI Use: Tesla (TSLA), Project 1

> Final record for submission (October 19, 2026). The Brightspace PDF `Validation-and-AI-Use.pdf` is a copy of this file.

## Decision, version, and as-of boundary

- **Decision and user:** buy-side PM committee. Should the fund initiate a TSLA position, put it on watch/defer, or not initiate?
- **Project of record:** `tsla-proforma-model/` (Streamlit app plus the `tsla_model` engine)
- **Repository commit at freeze:** `3ddeee6` (2026-10-19; content frozen for submission)
- **Valuation date:** 2026-09-24. **Price:** $378.25 (Yahoo/Nasdaq, as of 2026-09-24). **Risk-free rate:** 5.11% (Treasury 10y CMT, 2026-09-23)
- **Filing cutoff:** 10-K FY2023–FY2025 and 10-Q Q2 2026 (acc. 0001628280-26-049270)
- **Environment:** Python 3.10+, `tsla-proforma-model/requirements.txt`, offline seed data

## Data and convention ledger

| Material input | Source | As-of | Definition/units | Treatment | Risk |
|---|---|---|---|---|---|
| Historical statements | 10-Ks FY23–25, 10-Q Q2 2026 (`seed_filings.json`, page refs) | Filing dates | USD M, GAAP | 176 tagged values XBRL-verified in live mode | Low |
| Share price | Yahoo / Nasdaq | 2026-09-24 | USD/share | Fixed in seed for reproducibility | Moves daily; the value range does not depend on it |
| Diluted shares | 10-Q Q2 2026 | 2026-06-30 | 3,540.0M | Unearned 2025 CEO award (423.7M) excluded by default (toggle) | Medium: including them lowers value/share |
| Cost of equity | CAPM: 5.11% + 1.17 bottom-up beta × 4.5% ERP | 2026-09-24 | % | Bottom-up beta from 6 peers; observed beta 1.76 shown as an alternative | High: ke is the strongest value driver |
| Capex | 10-Q guidance "in excess of $25B" for 2026 | 2026 | USD M | Later years are judgment | High: drives negative FCFE in 2026–27 |
| Robotaxi revenue | None disclosed | n/a | USD M | Explicit judgment line: $8B by FY2030 in base | High: this is where the market's value sits |
| Model ASPs | Only Model 3/Y vs Other disclosed | FY2025 | USD/vehicle | Other models assumed at 2× Model 3/Y price | Medium |

## Validation register

| Claim/output | Failure mode | Test and expected result | Actual | Disposition | Evidence |
|---|---|---|---|---|---|
| Engine math is right | Formula error | **Known answer:** `proforma.py` reproduces the ABG training case of $291.75/share | $291.75 | Pass | `Lab_09_proforma_engine.md`, `python proforma.py` |
| Statements articulate | BS doesn't balance; cash doesn't tie | A = L + E, CF cash = BS cash, PP&E/debt/lease/share roll-forwards, every year | All pass in all 4 scenarios | Pass | `tsla_model/checks.py`, `output/visible_output.md` |
| Checks fail loudly | Broken input still produces a value | Break the BS or breach min cash → valuation must refuse | Refuses | Pass | `tests/test_valuation_and_checks.py::test_broken_balance_sheet_blocks_valuation`, `::test_minimum_cash_breach_blocks_valuation` |
| DCF boundary | g ≥ ke gives nonsense | Terminal g at or above ke → refuse | Refuses | Pass | `::test_terminal_growth_at_or_above_ke_refuses` |
| DCF monotonicity | Value moves the wrong way | Higher discount rate → lower value | Lower | Pass | `::test_higher_discount_rate_lowers_value` |
| Source check on load-bearing input | Wrong number copied from filing | XBRL cross-check of stored historicals | 176/176 match | Pass | `data_ingestion.verify_against_xbrl`, MODEL_SUMMARY |
| Independent source check | n/a |  Checked 2026 capex guidance in the 10-Q Q2 on page 30: " We are focused on long-term growth opportunities through critical, high-value investments. We currently expect our capital expenditures to be in excess of $25 billion in 2026, driven by our AI initiatives, including investments in compute infrastructure and data centers, the expansion and ramp of our manufacturing and R&D production lines and facilities, and growth in our fleet of company-operated AI-enabled assets and our retail, service and charging footprint." The model uses $25,000 million (25 billion)which is a match to Tesla's statement | Match: model 2026 capex = $25,000M | Pass | 10-Q Q2 2026 p. 30; tsla_model/assumptions.py (capex) |
| Peer-policy consistency | Peers defined after seeing results; mixed multiple definitions | Peer policy stated before selection; EV and equity multiples on same basis | Policy written in Lab 08 before multiples were computed, carried into `docs/peer-policy.md`. Check on 2026-10-19 found the document defined EV = market cap + debt − cash, but the code (`valuation.py` `multiples_crosscheck`) uses market cap + debt; the document was corrected to match the code and the missing cash deduction is stated as a limitation | Pass after correction | `docs/peer-policy.md`; `tsla_model/valuation.py` |
| Cold run | README doesn't work for a stranger | Fresh clone from GitHub into a new folder, new virtual environment, install requirements, run tests and export | 2026-10-19, own run, 21:39–21:45 EDT (6 minutes): clone, install, **71 passed**, export printed FCFE 29.05 / FCFF 27.22, status OK/OK. First issues: (1) `cd $HOME\Desktop` failed (OneDrive Desktop) — used Downloads; (2) the pushed README still said "66 passed" and plain `streamlit run`, which is not recognized on this PC — fixed to `python -m streamlit run` (README update committed after the run) | Pass | Terminal output from the run; `README.md` |
| Highest-risk claim | The model's value is far below the price mainly because of the capex plan and operating drivers, not an error | Locked Changed-Input Record (Model 3/Y deliveries −10%, prediction committed first) plus FCFF/FCFE cross-check and reverse DCF | Value fell 10.6% as predicted (~10%); decision unchanged; FCFF $27.22 vs FCFE $29.05 reconcile (gap = debt and NCI in the bridge); reverse DCF needs ~$451B robotaxi revenue by 2030 | Pass | Locked record below; `output/visible_output.md` |

**Known oddity to explain:** terminal value is **110%** of DCF value in base (and negative in bear and recession).
This happens because FY2026–27 FCFE is negative, so the PV of the forecast years is below zero. Explain it in Video 2
rather than hiding it.

**Requirement gap resolved (2026-10-19):** Project 1 requirement 4 asks for a **FCFF DCF with WACC and an
enterprise-to-equity bridge** driven by the pro-forma. Codex added `tsla_model/fcff.py`: FCFF from the pro-forma's
EBIT, D&A, capex and working capital, discounted at a WACC of 10.33%, with a 30-Jun-2026 enterprise-to-equity bridge
(FCFF $27.22/share vs. FCFE $29.05/share). New validation rows:

| Claim/output | Failure mode | Test and expected result | Actual | Disposition | Evidence |
|---|---|---|---|---|---|
| FCFF known answer | Formula error | Three-year synthetic case with round numbers, checkable by hand | Matches | Pass | `tests/test_fcff.py::test_fcff_three_year_known_answer_with_sbc_toggle` |
| FCFF boundary | g ≥ WACC gives nonsense | Terminal growth at or above WACC → refuse | Refuses | Pass | `::test_fcff_refuses_terminal_growth_at_or_above_wacc` |
| FCFF monotonicity | Value moves the wrong way | Higher WACC → lower value; higher growth → higher value | As expected | Pass | `::test_fcff_wacc_and_growth_monotonicity` |
| Enterprise-to-equity bridge | Bridge lines don't add up | Bridge lines sum to equity value and per-share value | Ties | Pass | `::test_fcff_q2_bridge_ties_to_equity_value` |
| FCFF refuses when broken | Broken statements still valued | A broken balance sheet blocks the FCFF valuation | Refuses | Pass | `::test_broken_balance_sheet_blocks_fcff_valuation` |
| FCFF vs FCFE reconciliation | Hidden convention mismatch | FCFE = FCFF − after-tax interest + after-tax interest income + net borrowing, residual shown not forced | Residual −$60M/yr = NCI share of income | Pass, explained | `output/visible_output.md` (FCFF-to-FCFE reconciliation) |

## Locked Changed-Input Record (human prediction first, AI closed)

> The Lab 11 record (`Lab_11_proforma_sensitivity.md`, locked 2026-09-29 13:40) was run on the simplified Lab 10
> model, not on the app of record. Its first commit (`241f8b1`, 13:49) already contained both the prediction and
> the results, so there is **no commit of the prediction made before the run**. Use it as supporting evidence, and
> do a fresh record on the app:
>
> 1. With AI closed, write your prediction in the table below (input, old → new, expected direction, rough size, decision effect).
> 2. **Commit and push it.** That commit hash is your proof that the prediction came before the run.
> 3. Make the change in the app, record before/after, then fill in the second table.

### Precommit


Commit: 3bbe9b5 (pushed 10:41 AM)

10/19/2026 10:34 am Model 3/Y deliveries, all forecast years, Tesla sells 1,650k–1,900k cars per year I want to lower this by 10% every year, my expected direction is that Tesla's value per share goes down by about 10% because their sales decrease by 10%, if fewer cars are sold that leads to less revenue which leads to less profit, less cash and a lower value. I still think that my decision will be to defer Tesla if they're selling 10% less cars a year.

### Result

Before I made the change the value was $29.48 per share, after dropping the amount of cars sold by Tesla in a year, the value went down to $26.36 per share. This model ran on live data from today's Tesla market price of $367.81. Overall, the value drop was 10.6% decrease which is really close to my prediction, and my choice to defer stays the same. Tesla's revenue only dropped by 4.9% since they generate revenue from other products and services, but the value dropped by 10.6% because of Tesla's fixed costs such as the factory spending and depreciation that happen even if their sales decreases.


## Named AI-use register

| Tool/model | Date | Task | Output used | Independent check | Disposition | Effect |
|---|---|---|---|---|---|---|
| ChatGPT / Codex | 2026-09-03 | Helped draft the Sept 3 research report (my Edition A) | Report text | Sources checked against the 10-K | Accepted; disclosed as AI-assisted Edition A (`docs/research-evolution.md`) | Baseline position |
| Claude Code, `claude-opus-5-5` | 2026-09-24 | Built the original `tsla-proforma-model/` (statements, checks, FCFE valuation, app, 66 tests) and Lab 09/10 files | Model of record | Tests; ABG known answer $291.75; 176 XBRL matches | Accepted after tests | Core model |
| Codex, GPT-5 | 2026-10-08 | Requirement review, AGENTS.md, README decision frame, peer policy, normalization and challenge records | Docs | Read against Lab 08 and filings | See `docs/ai-use-log.md` | Documentation |
| Codex, GPT-5 | 2026-10-19 | Built FCFF/WACC module and bridge; README and peer-policy fixes | `fcff.py`, `test_fcff.py`, docs | Tests run independently: 11 failed, then 71 passed after fix | Corrected, then accepted (see next row) | FCFF $27.22 |
| Claude Code, `claude-opus-5-5` | 2026-10-19 | Planning, review of Codex output, drafts of the decision memo, Edition B and video scripts | Drafts | Every number checked against `visible_output.md`; I rewrote the memo's recommendation and triggers and Edition B's conclusion | Modified | Written deliverables |
| Claude (Cowork), model id `claude-opus-5-5` | 2026-10-06 | Read the course repo and this repo; listed the Project 1 gaps; ran the cold-run tests; wrote `export_visible_output.py`, the root README project map, and this draft record | Visible output files, README, draft tables | Tests rerun (66 pass); base value $29.05 matches MODEL_SUMMARY ($29.03 at a slightly different price); ABG known answer rerun ($291.75) | Accepted, then modified on 2026-10-19 (README cold-run commands updated; this record completed) | Packaging only; no change to valuation |
| **Corrected AI output:** Codex FCFF build | 2026-10-19 | Codex's first FCFF build read the cost of debt as a single parameter (`a.p("interest_rate_debt")`) instead of the yearly driver | Rejected first version | Ran the tests independently: 11 of 71 failed and the export crashed with `KeyError: 'interest_rate_debt'`; after Codex's fix, Codex said it could not run tests, so I re-ran them: 71 passed, export FCFF $27.22 | **Corrected**, then accepted | Shown in Video 1 |

## Limitations, monitoring, and reversal triggers

My model's biggest limitation is that robotaxi revenue is my own guess, because Tesla doesn't yet report it, and the
stock price really depends almost entirely on it. Also, most of my value comes from after 2030, which is a long time in
the future, because Tesla's heavy spending makes the next two years negative. So small changes in my long-term guesses
move the answer a lot. Tesla also doesn't report prices for each car model, so I had to use an estimate for those.

I'll watch for three things: Tesla reporting robotaxi revenue on its own line, Tesla cutting its spending plans, and car
sales dropping below 1.5 million a year. Any of those could make me rerun the model and could change my recommendation.

Supporting numbers: the market price needs about **$451B of robotaxi revenue by FY2030** (vs. $8B in the base case), or
a cost of equity of about **3.6%**, or perpetual growth of about **9.8%** (`tsla-proforma-model/output/visible_output.md`).
