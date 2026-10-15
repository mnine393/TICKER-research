# Lab 13 — Portfolio Mandate Defense

## 1. S1–S10 sorted: type + one-line reason [STUDENT]

- **S1 — Objective** — Can't be tested pass or fail on a portfolio; it sets the time frame the return goal will be judged over.
- **S2 — Objective** — A return goal (inflation + 4%) that can only be judged after five years of results, not checked on today's portfolio.
- **S3 — Hard constraint** — 4 × $0.75M = $3M, so at least 3% must be in cash or Treasuries; B holds only 1% and fails.
- **S4 — Preference** — The 60/40 benchmark is a reference point to compare against, not a limit; C at 70% stocks differs from it but breaks no rule.
- **S5 — Hard constraint** — The checker tests the lowest weight; below zero fails, as the probe with A's cash at −2 showed.
- **S6 — Hard constraint** — A yes/no check on any portfolio; B fails at 9% because Acme's bonds and stock count together.
- **S7 — Hard constraint** — A clear limit (25%) with a breach rule (committee approval); it's measured over a year of trades, so mandate.py can't test it on one snapshot.
- **S8 — Hard constraint** — A set number (90%) the checker tests; B fails at 85% because of the private real estate fund.
- **S9 — Unverifiable promise** — Sounds like a rule but has no measure or breach rule, and no one can know next year's loss today, so the checker prints "requires CIO clarification" instead of testing it.
- **S10 — Missing** — The CIO never said what the portfolio should optimize (return, safety, liquidity), so there's no goal to build toward yet.

## 2. Checker results [CODEX]

`output.txt`

```
Reserve minimum: 3.0%
A:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 14.0 pass
Redeemable in 5 days: 100.0 pass
Largest single company: 0.0 pass
Calendar-year loss: requires CIO clarification
passes every checkable rule
B:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 1.0 FAIL
Redeemable in 5 days: 85.0 FAIL
Largest single company: 9.0 FAIL
Calendar-year loss: requires CIO clarification
fails 3 rule(s)
C:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 2.0 FAIL
Redeemable in 5 days: 100.0 pass
Largest single company: 8.0 pass
Calendar-year loss: requires CIO clarification
fails 1 rule(s)
D:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 100.0 pass
Redeemable in 5 days: 100.0 pass
Largest single company: 0.0 pass
Calendar-year loss: requires CIO clarification
passes every checkable rule
```

`probe_output.txt`

```
Reserve minimum: 3.0%
A:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): -2.0 FAIL
Reserve-eligible: 10.0 pass
Redeemable in 5 days: 100.0 pass
Largest single company: 0.0 pass
Calendar-year loss: requires CIO clarification
fails 1 rule(s)
B:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 1.0 FAIL
Redeemable in 5 days: 85.0 FAIL
Largest single company: 9.0 FAIL
Calendar-year loss: requires CIO clarification
fails 3 rule(s)
C:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 2.0 FAIL
Redeemable in 5 days: 100.0 pass
Largest single company: 8.0 pass
Calendar-year loss: requires CIO clarification
fails 1 rule(s)
D:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 100.0 pass
Redeemable in 5 days: 100.0 pass
Largest single company: 0.0 pass
Calendar-year loss: requires CIO clarification
passes every checkable rule
```

## 3. Candidate D: the weights and the AI's stated objection, labeled as AI-proposed [CODEX]

AI-proposed D: Cash 0%; Treasury bills 0%; Treasury 10-year note 100%; Global equity index fund 0%; Investment-grade bond fund 0%; Private real estate fund 0%; Acme Corp bonds 0%; Acme Corp stock 0%.

AI objection: D passes every checkable rule but could reasonably be rejected because it exposes S10: no one has said what the pilot should optimize. A Treasury-only portfolio also bears little resemblance to the 60/40 benchmark in S4 and may not be designed to pursue S2's CPI + 4% objective.

## 4. My judgment of D (two sentences) and the statement I'd cite against my partner's D [STUDENT]

The objection holds: an all-Treasury portfolio passes every checkable rule, but it's so safe that it's unlikely to beat inflation by 4% a year, so it fails the goal in S2. D shows the checker only tests limits, not whether a portfolio actually serves the client's goal.

Against my partner's D, I would cite **S4**: the benchmark expects about 60% stocks, so a portfolio that drifts far from it needs a reason the CIO has not given.

## 5. My question for the CIO and the answer that would change the portfolio [STUDENT]

**Question:** If reaching inflation + 4% (S2) means accepting some chance of losing more than 10% in a year (S9), which matters more: the return goal or avoiding that loss?

**How the answer changes the portfolio:**

- **Return matters more:** keep around 60% or more in stocks, close to the benchmark (like A or C).
- **Avoiding losses matters more:** shift toward bonds and Treasuries, which probably means lowering the return goal too.

## 6. Investment policy statement: what it is, objectives vs constraints, S1–S10 mapped [STUDENT]

An investment policy statement is a written rulebook between a client and whoever manages their money. It states what the client wants (the objectives) and what the manager can and can't do to get there (the constraints). A client writes one so everyone agrees before anyone picks investments, which prevents disputes later.

**Objectives** are desired outcomes, like the CPI + 4% return. **Constraints** are limits, like liquidity, reserve coverage, long-only, and issuer limits.

**Meridian's S1–S10 mapped:**

- **Objectives:** S1 (seven-year horizon), S2 (inflation + 4%)
- **Hard constraints:** S3 (3% reserve), S5 (long-only), S6 (8% issuer limit), S7 (25% turnover), S8 (90% liquid in 5 days)
- **Preference:** S4 (60/40 benchmark)
- **Unverifiable promise:** S9 (10% loss limit)
- **Missing:** S10 (what to optimize)

## 7. Reflection: why passing every checkable rule can still be wrong; the type I was least sure of [STUDENT]

**1. Why a portfolio can pass every check and still be wrong:** A portfolio can pass every check and still be wrong because the checker only tests the rules we give it, not whether the portfolio does what the client actually wants. D passes every check, but it's too safe to beat inflation by 4% (S2), so it doesn't fit what the CIO wants.

**2. The type I was least sure of:** I was least sure about S1. I thought the 10-year note might break the seven-year horizon, but it can be sold in one business day, so holding it doesn't break anything. S1 sets the time frame for the goal; it isn't a pass/fail rule.
