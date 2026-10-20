# Lab 14: Portfolio Baselines

## Lab question

How do the benchmark, equal-weight, and inverse-volatility allocation rules compare on expected return, volatility, reserve-eligible weight, and the 6.5% return objective when they use the same four sleeves and correlation assumptions?

## Inputs

| Sleeve | Expected return | Volatility |
|---|---:|---:|
| Treasury bills | 3.5% | 0.5% |
| Treasury 10-year note | 4.3% | 7.0% |
| Investment-grade bond fund | 5.0% | 6.0% |
| Global equity index fund | 8.0% | 16.0% |

Objective return: **6.5%**. Reserve-eligible sleeves: **Treasury bills** and **Treasury 10-year note**.

| Correlation | Bills | 10-year | IG bonds | Equity |
|---|---:|---:|---:|---:|
| Bills | 1.00 | 0.10 | 0.05 | 0.00 |
| 10-year | 0.10 | 1.00 | 0.80 | -0.10 |
| IG bonds | 0.05 | 0.80 | 1.00 | 0.25 |
| Equity | 0.00 | -0.10 | 0.25 | 1.00 |

The program creates each covariance as correlation x sleeve volatility x sleeve volatility.

## Baseline output: `python portfolio.py` compared with the known answers

| Portfolio | Value | Known answer | `python portfolio.py` | Match? |
|---|---|---:|---:|---|
| Benchmark | Treasury bills weight | 0.0% | 0.0% | Yes |
| Benchmark | Treasury 10-year note weight | 0.0% | 0.0% | Yes |
| Benchmark | Investment-grade bond fund weight | 40.0% | 40.0% | Yes |
| Benchmark | Global equity index fund weight | 60.0% | 60.0% | Yes |
| Benchmark | Expected return | 6.80% | 6.80% | Yes |
| Benchmark | Volatility | 10.46% | 10.46% | Yes |
| Benchmark | Reserve-eligible weight | 0.0% | 0.0% | Yes |
| Benchmark | Meets 6.5% objective | Yes | Yes | Yes |
| Equal weight | Treasury bills weight | 25.0% | 25.0% | Yes |
| Equal weight | Treasury 10-year note weight | 25.0% | 25.0% | Yes |
| Equal weight | Investment-grade bond fund weight | 25.0% | 25.0% | Yes |
| Equal weight | Global equity index fund weight | 25.0% | 25.0% | Yes |
| Equal weight | Expected return | 5.20% | 5.20% | Yes |
| Equal weight | Volatility | 5.21% | 5.21% | Yes |
| Equal weight | Reserve-eligible weight | 50.0% | 50.0% | Yes |
| Equal weight | Meets 6.5% objective | No | No | Yes |
| Inverse volatility | Treasury bills weight | 84.3% | 84.3% | Yes |
| Inverse volatility | Treasury 10-year note weight | 6.0% | 6.0% | Yes |
| Inverse volatility | Investment-grade bond fund weight | 7.0% | 7.0% | Yes |
| Inverse volatility | Global equity index fund weight | 2.6% | 2.6% | Yes |
| Inverse volatility | Expected return | 3.77% | 3.77% | Yes |
| Inverse volatility | Volatility | 1.05% | 1.05% | Yes |
| Inverse volatility | Reserve-eligible weight | 90.3% | 90.3% | Yes |
| Inverse volatility | Meets 6.5% objective | No | No | Yes |

Every displayed baseline value matches the known-answer table.

## Prove-it test: change IG-equity correlation to 0.50

I changed both matching cells in the correlation table (IG bonds/Equity and Equity/IG bonds) to 0.50, preserving symmetry. The recalculated volatilities were:

| Portfolio | Volatility |
|---|---:|
| Benchmark | 11.00% |
| Equal weight | 5.49% |
| Inverse volatility | 1.09% |

These match the lab's prove-it values.

## Break test: one correlation cell set to 1.3

Changing only the IG bonds/Equity cell to `1.3` makes the table asymmetric. The program refuses to calculate and prints:

```text
Input error: Correlation table is not symmetric at row 3, column 4.
```

## Mandate check: Candidate E

Candidate E is the 40% investment-grade bond fund and 60% global equity index fund benchmark. `python mandate.py` reports:

```text
E:
Weights sum to 100: 100.0 pass
Long-only (lowest weight): 0.0 pass
Reserve-eligible: 0.0 FAIL
Redeemable in 5 days: 100.0 pass
Largest single company: 0.0 pass
Calendar-year loss: requires CIO clarification
fails 1 rule(s)
```

Candidate E fails the reserve rule because its reserve-eligible weight is 0.0%.

## Benchmark volatility hand calculation

The benchmark has a 40% investment-grade bond fund weight and a 60% global equity index fund weight. In percent-squared terms:

```text
Bond variance contribution:   (0.40^2)(6.0^2) = 5.76
Equity variance contribution: (0.60^2)(16.0^2) = 92.16
Covariance contribution:      2(0.40)(0.60)(0.25)(6.0)(16.0) = 11.52

5.76 + 92.16 + 11.52 = 109.44
square root(109.44) = 10.46%
```

## Reflect

**1. Why does inverse volatility pile into bills?**

Inverse volatility gives each fund a weight based on 1 divided by its volatility, so the least volatile fund gets the most weight. Bills have a volatility of 0.5% while equity is 16%, which is about 30 times larger; that's why bills have over 80%. The result is a very safe portfolio, but its return is 3.77%, which is below the 6.5% mark.

**2. Which baseline would I show the CIO first, and why?**

I would show the CIO the benchmark first, because it's the client's own starting point and it's the only baseline that meets the 6.5% return goal, at 6.80%. But it has 0% in bills and the 10-year note, so it fails the reserve rule. That shows the CIO the real problem right away: the client's own benchmark breaks the client's own mandate. Equal weight meets the reserve rule, but only earns 5.20%, and inverse volatility only earns 3.77%. So none of the simple baselines meet both the return goal and the reserve rule, which is why I would start with the benchmark.


## Before Thursday: my funds

