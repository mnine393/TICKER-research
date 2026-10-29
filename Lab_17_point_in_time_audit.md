# Lab 17: Point-in-time data audit

## The question

Was each number in your series knowable on the day you would have traded on it, and may Project 2 use it?

Use [asof_app.py](asof_app.py) to repeat the check:

```powershell
python -m streamlit run asof_app.py
```

## Known answer

As known on 5 October 2026, all of these values match.

| Series | Latest measurement then | Value |
|---|---|---:|
| BAA | September 2026 | 6.47 |
| FEDFUNDS | September 2026 | 3.75 |
| DGS10 | 2 October 2026 | 5.28 |
| MORTGAGE30US | 1 October 2026 | 7.28 |

## Employment series probe

For PAYEMS, as known on 15 January 2025, December 2024 was 159,536. Today, December 2024 is 158,316, which is lower. The application shows 381 revised values.

## My series: CPIAUCSL

As known on 30 September 2026, the latest month was August 2026, with a value of 334.131. As known on 29 October 2026, the latest month is September 2026, with a value of 336.298. As known on 31 January 2026, the application shows 59 revised values.

## Data card

| Item | Plain-language record |
|---|---|
| Source | FRED and ALFRED, Federal Reserve Bank of St. Louis, [CPIAUCSL series page](https://fred.stlouisfed.org/series/CPIAUCSL) |
| Measures | Consumer Price Index for All Urban Consumers, all items, United States city average: prices people pay for goods and services. |
| Units | Index, 1982 through 1984 equals 100, adjusted for predictable seasonal patterns, monthly. |
| Publication lag | About two weeks after month end. August 2026 was published 11 September 2026; September 2026 was published 14 October 2026. |
| Revised | Yes. Each February, the seasonal adjustment revises about the last five years. There were 59 values revised since 31 January 2026. |
| Download date | 29 October 2026. |
| Three values checked by hand on the FRED page | July 2026: 332.813; August 2026: 334.131; September 2026: 336.298. |

## Partner attack and my answer

Attack: my partner trusts the “Revised” field least, because the app showed 0 revised values between 30 September and today.

My answer: 0 only means nothing was revised in that one month. When I set “As known on” to 31 January 2026, the app shows 59 revised values, from the February update to the seasonal adjustment, so CPI is revised.

## My call

Quarantine. CPI is published about two weeks after the month ends (September 2026 came out on 14 October) and is revised every February. I’ll admit it to Project 2 only as it was known on each decision date, using ALFRED, and never today’s values with a fixed lag, because a fixed lag would still use the revised numbers.

## Learn

A data card records where a series comes from, what it measures, its units, how late it’s published, whether it’s revised, and when I downloaded it. The publication lag and revision fields stop a leak before it starts, because they tell you not to use a number before the day it was released. “Cleaned the data” isn’t a data card: it doesn’t say what was changed, when the numbers were known, or how to check them.

## Reflect

CPI comes out about two weeks after the month ends. When I set the app to 30 September, September’s number disappeared, because it wasn’t published until 14 October.
A backtest on today’s values would act as if I knew each month’s inflation two weeks early, and it would use revised numbers that didn’t exist yet. Both would make the strategy look better than it really was.