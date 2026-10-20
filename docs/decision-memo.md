# Investment Committee Memo — Tesla, Inc. (TSLA)

**To:** Portfolio Manager and Investment Committee  
**From:** Miles Nine, AI task force analyst  
**Date:** October 19, 2026  
**Valuation date:** September 24, 2026 · **Units:** USD millions except per-share figures  
**Share basis:** 3,540.0M diluted shares (10-Q Q2 2026); excludes 423.7M unearned 2025 CEO award shares

> Educational project for FIN 43900. Not investment advice.

## 1. Recommendation: WATCH / DEFER. Do not initiate at the current price.

This fund does not hold a TSLA position and, based on our model, should not open one now. The five-year pro-forma
model values the equity at **about $27 to $29 per share in the base case** (FCFF $27.22, FCFE $29.05), against a market
price of **$378.25** as of September 24, 2026. The price was $367.81 on October 19, 2026, which does not change the
conclusion: even our best case, the bull case at $87.83, is about 77% below the market price.

With this said, I recommend **watch/defer** rather than "do not initiate," because the gap comes from autonomy, like
robotaxis, and AI value that Tesla does not yet report. The triggers in Section 6 tell us whether or not to reopen the
case and review it again.

## 2. Valuation range (not a point estimate)

| Case | Value / share | What it assumes |
|---|---:|---|
| Bull | $87.83 | 2.2M Model 3/Y cars and $25B robotaxi revenue at a 50% margin by 2030 |
| **Base** | **$27–$29** | 1.9M Model 3/Y cars, $8B robotaxi revenue, capex falling from $25B to $15B |
| Bear | $4.16 | Flat volumes, lower prices and margins, capex cut |
| Recession / downside | $3.02 | About a 15% delivery drop in 2027 and a margin squeeze; draws the revolver |
| FCFF sensitivity: WACC 9–11%, terminal growth 2–4% | $22–$41 | WACC × growth grid |

**Market price: $378.25.** No case in our tested range reaches it.

## 3. Strongest evidence (10-K FY2025 and 10-Q Q2 2026)

- **Revenue has stalled while spending has tripled.** Revenue went from $96.8B (FY2023) to $94.8B (FY2025).
  Management guides 2026 capital spending **above $25B**, against $8.5B in FY2025 (10-Q Q2 2026, p. 35).
- **Free cash flow turns negative.** FCFE is −$9.2B in 2026 and −$5.4B in 2027 before turning positive in 2028, so
  value depends heavily on the terminal value (110% of DCF value).
- **The model is verified.** The balance sheet balances in every year, cash ties to the cash-flow statement, the
  valuation refuses to run when a check fails, all 71 automated tests pass, and 176 stored historical values matched
  SEC XBRL data.

## 4. What the market price requires (reverse DCF)

To justify $378 with everything else unchanged, the market needs **one** of:

- a cost of equity of **3.58%**, below the 5.11% risk-free rate;
- perpetual growth of **9.8%**; or
- **$451B of robotaxi revenue by 2030**, against $8B in our base case.

No change to the existing car or energy businesses gets there: even a much higher car margin tops out at about $180
per share. **The price is a bet on autonomy, not on today's businesses.**

## 5. Why the methods disagree

| Method | Value / share | Why it differs |
|---|---:|---|
| FCFF DCF (WACC 10.33%) | $27.22 | Primary method; the bridge subtracts $10.0B of debt, finance leases and NCI |
| FCFE DCF (cost of equity 10.38%) | $29.05 | Same forecast; debt is handled through the yearly cash flows |
| Peer EV / revenue (2.0×) | $68 | Values Tesla like other manufacturers on sales, ignoring its thinner cash flow |
| Peer P/E (25.6×) | $18 | Tesla's earnings are low relative to its spending |
| **Market** | **$378** | Implies about **524× 2026 earnings** |

We do not average these. The DCFs value cash flows; the multiples value Tesla like other manufacturers. The market
values something neither captures, and that gap is the decision.

## 6. Risks and triggers

**What would move us to INITIATE (buy):**

- Tesla starts **reporting robotaxi revenue separately**, and it is scaling toward billions of dollars from this
  business.
- The **market price falls toward our bull value**, which is about $90.
- Tesla **cuts its spending on factories and AI (capex) back to about $12B a year** after 2027. Spending over $25B in
  2026 is why its cash flow is negative for two years; spending less leaves more cash for shareholders.
- Tesla's **profit on each car stays above 23 cents per dollar of sales** (car cash gross margin above 23%). This is our
  biggest driver: every extra 2 cents per dollar adds about $5 per share in our model.

**What would move us to DO NOT INITIATE:**

- Model 3/Y deliveries fall below **1.5 million** a year.
- Cash falls below the model's **minimum-cash floor of 15% of revenue**, or Tesla draws its revolver.
- Energy gross margins fall below the **25%** mark.

**Biggest model risks:**

- Robotaxi revenue and margins are just our judgment, which Tesla does not disclose.
- Tesla does not disclose prices by vehicle model, so it is sometimes hard to see what drives automotive revenue.
- **Most of the value comes from after 2030** (the terminal value). Because Tesla spends so much in 2026–27, those
  years are worth less than zero, so almost all of the value depends on our guess about 2030 and beyond. If that guess
  is wrong, the whole answer moves.

## 7. Committee ask

Approve **WATCH / DEFER**: no position now, and re-run this model when the next 10-Q is released, or sooner if any
trigger in Section 6 is hit.

---

*AI use: the model, tests and this memo were built with AI assistance (Claude, Codex). The named tools and the checks
performed on their output are in [`docs/validation-and-ai-use.md`](validation-and-ai-use.md). Model output:
[`tsla-proforma-model/output/visible_output.md`](../tsla-proforma-model/output/visible_output.md).*
