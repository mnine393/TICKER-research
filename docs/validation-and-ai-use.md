# Validation and AI Use: Tesla (TSLA), Project 1

> **WORKING DRAFT.** Lines marked **TODO (Miles)** need your own action or your own words. Rows that are already
> filled in cite evidence that is already in this repo. Check each one before you freeze this file as
> `Validation-and-AI-Use.pdf`.

## Decision, version, and as-of boundary

- **Decision and user:** buy-side PM committee. Should the fund initiate a TSLA position, put it on watch/defer, or not initiate?
- **Project of record:** `tsla-proforma-model/` (Streamlit app plus the `tsla_model` engine)
- **Repository commit at freeze:** TODO (Miles): paste the final commit hash
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
| Independent source check | n/a | TODO (Miles): pick ONE load-bearing input (e.g. FY2025 capex or diluted shares). Open the 10-K/10-Q yourself, record the page and the number, and compare | | | |
| Peer-policy consistency | Peers defined after seeing results; mixed multiple definitions | Peer policy stated before selection; EV and equity multiples on same basis | TODO (Miles): point to where your peer policy is written (Lab 08 / multiples cross-check) | | |
| Cold run | README doesn't work for a stranger | Fresh venv, README only, record first failure and time | Claude's run 2026-10-06: 66 passed. TODO (Miles): a **partner** run, with first failure and minutes | | |
| Highest-risk claim | TODO (Miles): one sentence, e.g. "the market price requires ~$451B robotaxi revenue by 2030" | TODO | | | |

**Known oddity to explain:** terminal value is **110%** of DCF value in base (and negative in bear and recession).
This happens because FY2026–27 FCFE is negative, so the PV of the forecast years is below zero. Explain it in Video 2
rather than hiding it.

**Requirement gap to resolve:** Project 1 requirement 4 asks for a **FCFF DCF with WACC and an enterprise-to-equity
bridge** driven by the pro-forma. The app uses **FCFE at the cost of equity**. The Lab 06 FCFF model (`dcf.py`) is
not driven by the pro-forma. TODO: ask in Week 7 studio whether FCFE is acceptable, or add an FCFF view.

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

| Precommit timestamp | Commit | Material input | Old → new (units) | Expected direction | Expected decision effect |
|---|---|---|---|---|---|
| TODO | TODO | TODO (e.g. cost of equity, or Model 3/Y deliveries) | TODO | TODO | TODO |

### Result

| Before/after output | Actual decision effect | Prediction reconciliation | Diagnosis / why no change | Evidence |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |

## Named AI-use register

| Tool/model | Date | Task | Output used | Independent check | Disposition | Effect |
|---|---|---|---|---|---|---|
| TODO (Miles): list the AI tools you used to build the app and labs (e.g. Codex, ChatGPT, Claude), with dates | | | | | | |
| Claude (Cowork), model id `claude-opus-5-5` | 2026-10-06 | Read the course repo and this repo; listed the Project 1 gaps; ran the cold-run tests; wrote `export_visible_output.py`, the root README project map, and this draft record | Visible output files, README, draft tables | Tests rerun (66 pass); base value $29.05 matches MODEL_SUMMARY ($29.03 at a slightly different price); ABG known answer rerun ($291.75) | TODO (Miles): accept, modify, or reject each | Packaging only; no change to valuation |
| TODO: at least ONE AI output you **corrected or rejected**, with the evidence (e.g. the Lab 08 citation corrections, commits on 2026-09-17) | | | | | | |

## Limitations, monitoring, and reversal triggers

TODO (Miles), in your own words. Starting points from the model's "what must be true" table:

- The market price needs ~**$451B robotaxi revenue by FY2030** (vs. $8B base), OR ke ≈ **3.6%**, OR perpetual growth ≈ **9.8%**.
- Candidate monitoring triggers: robotaxi revenue disclosed as a separate line; autonomy margins in a 10-Q; capex guidance cut; energy deployments far above trend.
- Disclosure limits: no model-level ASPs, segment-only D&A, no robotaxi economics (see `tsla-proforma-model/README.md`).
