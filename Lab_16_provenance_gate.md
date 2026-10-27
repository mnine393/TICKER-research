# Lab 16: Provenance Gate

## Question

On the day you would have traded, what did this data actually say, and how much of what you see now came later?

## Calculator

Use [the as-of calculator](tsla-proforma-model/asof.py) to reproduce the result.

```powershell
python tsla-proforma-model/asof.py
```

## Row funnel

The decision date is 31 March 2026. The rows were removed in this order:

| Rule | Rows removed |
|---|---|
| No ticker | 11 |
| Exact duplicate | 7 |
| Published after 31 March 2026 | 3, 8, 10 |
| Older vintage replaced by a revision | 2 |

The as-of panel contains rows 1, 4, 5, 6, 9, and 12.

## Signals

| Ticker | As-of signal | Naive signal that ignores publication date |
|---|---|---|
| AAA | +1.98% in February | +5.83% in March |
| BBB | -1.02% in February | -5.15% in March |
| CCC | +0.91% in February | +1.82% in February, revised |

All signals match the known answer.

## Break test

If the decision date is changed to 2026-04-15, the as-of signals equal the naive signals for every ticker. By that date, every later publication and revision used by the naive comparison was available.

## Learn

Look-ahead bias is using data that you couldn't have had on the actual decision date. Every number has a month it measures, a day it was published and sometimes there is a revision. AAA's +5.83% used March data that was published on Apr. 10, that is after my March 31st decision. This makes it look better than anything that I could have known. On march 31st the real signal was +1.98%

## Reflect

Rule 3, which removes rows published after the decision date, removed the rows that were most important: row 3, 8 and 10. Without this rule AAA and BBB would use March data that no one actually had yet, then BBB would show -5.15% instead of -1.02%. A backtest built on the naive column would claim signals that weren't yet knowable when you traded. This would cause the strategy to look better than it really could have been. 