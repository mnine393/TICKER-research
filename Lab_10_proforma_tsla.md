# Lab 10 — Pro-Forma: Tesla Through the Engine

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Code:** [`proforma_tsla.py`](proforma_tsla.py) runs Tesla through the unchanged Lab 09 engine [`proforma.py`](proforma.py), which still prints the ABG known answer of \$291.75  
**Filings:** [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) · [10-K FY2024](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm) · [10-K FY2023](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm) · [10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm)  
**Units:** USD millions except per-share figures

> Learning demonstration, not investment advice.

---

## D — The Question

> **What are five years of your company's statements worth, built from assumptions you can defend?**

**Company:** Tesla, Inc. (`TSLA`).

**The line that makes Tesla different:** Tesla has no floor plan. Its defining line is **capital spending**: guided above \$25 billion for 2026, about three times FY2025's \$8.5 billion, for AI compute, Cybercab and factories. It is paid for out of a **\$44 billion cash pile** instead of borrowed inventory money. In the model this turns FCFE negative for four years, drains cash to its floor, and briefly draws the revolver.

---

## R — History (three 10-Ks)

| Line item | FY2023 | FY2024 | FY2025 | Source | Confirmed by hand |
|---|---:|---:|---:|---|:---:|
| Revenue | 96,773 | 97,690 | 94,827 | 10-K FY2025, Consolidated Statements of Operations, p. 50 | ✅ |
| Gross profit | 17,660 | 17,450 | 17,094 | 10-K FY2025, p. 50 | ☐ |
| SG&A | 4,800 | 5,150 | 5,834 | 10-K FY2025, p. 50 | ☐ |
| R&D *(Tesla-specific; carried with SG&A in the engine)* | 3,969 | 4,540 | 6,411 | 10-K FY2025, p. 50 | ☐ |
| Net income to common stockholders | 14,997 | 7,091 | 3,794 | 10-K FY2025, p. 50 | ✅ |
| Inventory | 13,626 | 12,017 | 12,392 | FY2023: 10-K FY2024 Balance Sheet p. 48; FY2024–25: 10-K FY2025 p. 49 | ☐ |
| PP&E, net | 29,725 | 35,836 | 40,643 | same as inventory | ☐ |
| Shareholders' equity | 62,634 | 72,913 | 82,137 | same as inventory | ☐ |

✅ = opened in the 10-K and checked line by line (revenue and net income, p. 50). Every value above also matched the SEC's XBRL data. Unresolved: none.

### Ratios

| Ratio | FY2023 | FY2024 | FY2025 | Note |
|---|---:|---:|---:|---|
| Gross margin (GAAP) | 18.2% | 17.9% | 18.0% | Tesla's cost of revenues includes D&A |
| Gross margin before D&A (engine basis) | 22.2% | 22.0% | 22.4% | adds back D&A in cost of revenues (10-K Note 16, p. 93: 3,450+343 / 3,680+377 / 3,780+355) |
| SG&A ÷ gross profit (GAAP) | 27.2% | 29.5% | 34.1% | |
| (R&D + SG&A) ex-D&A ÷ gross profit before D&A (engine basis) | 36.8% | 39.0% | 48.2% | H1 2026: 60.8% |
| Inventory days (on GAAP cost of revenues) | 62.9 | 54.7 | 58.2 | |
| Depreciation ÷ year-end net fixed assets | 11.4% | 11.6% | 12.3% | D&A and impairment ÷ (PP&E + lease vehicles + energy systems) |
| Capital spending, filing | 8,899 | 11,342 | 8,527 | Cash-flow statement, 10-K FY2025 p. 53 |
| Capital spending, data provider | 8,899 | 11,342 | 8,527 | Yahoo Finance `annualCapitalExpenditure`; matches the filing exactly in all three years |
| Tax rate | −50.1% | 20.4% | 27.0% | FY2023 includes a one-time valuation-allowance release |
| Reported revenue growth | +18.8% | +0.9% | −2.9% | FY2022 revenue 81,462 (10-K FY2024, Consolidated Statements of Operations, p. 49) |
| Organic / same-store growth | not disclosed | not disclosed | not disclosed | Tesla reports no same-store figure; closest: total deliveries +38% / −1.1% / −8.6% (8-K Ex. 99.1) |

### Assumption set

| Assumption | Value | Label | Reason |
|---|---|:---:|---|
| Revenue growth | 10.0% a year | judgment | H1 2026 revenue grew 21% (10-Q p. 31). Building it up from deliveries, energy storage, services and robotaxi gives about 10% a year to 2030. |
| Gross margin | (17,094 + 3,780 + 355) ÷ 94,827 = 22.39% | history | FY2025 gross margin before D&A. The engine subtracts depreciation separately, so using GAAP margin would count D&A twice. |
| (R&D + SG&A) ÷ gross profit | 60%, 57%, 54%, 51%, 48% | judgment | H1 2026 is 60.8% because of AI R&D and the CEO award. I expect it to return to FY2025's 48% as revenue grows faster than costs. |
| Depreciation ÷ opening PP&E | 6,148 ÷ 50,159 | history | FY2025 D&A ÷ year-end net fixed assets, the same convention as ABG. |
| Impairment | 0 | judgment | Tesla's impairments sit inside its D&A line; restructuring is non-recurring. |
| Capital spending | 25,000, 22,000, 18,000, 16,000, 15,000 | guidance / judgment | 2026 is guidance ("in excess of \$25 billion", 10-Q p. 35). After that I assume the AI build-out peaks and spending eases toward 1.3× depreciation. |
| Tax rate | 25% | judgment | FY2025 was 27%, lifted by the non-deductible CEO award; the rate falls as profit grows. |
| Inventory days | 12,392 ÷ (94,827 − 21,229) × 365 = 61.5 | history | FY2025 inventory ÷ cost of revenues before D&A, consistent with the engine. |
| **Floor plan ÷ inventory** | **none (0)** | history | Tesla sells direct and has no floor plan. Its distinctive line is capex, above. |
| Other working capital | −18.86% of the change in revenue | history | FY2025 (AP 13,371 + accrued 13,279 + deferred revenue 3,424 − AR 4,576 − prepaid 7,615) ÷ revenue. Tesla collects before it pays suppliers, so growth releases cash. |
| Minimum cash / revolver limit / revolver rate | 15,000 / 5,000 / 6% | judgment / history / judgment | About two months of costs. The \$5.0B unused credit line is from the 10-Q (p. 35). |
| Debt repayment / share buyback | 0 / 0 | judgment / history | Tesla refinances its asset-backed debt (H1 2026 net issuance was positive). There were no buybacks in FY2023–H1 2026. |
| Interest: debt / interest income on cash | 338 ÷ 8,295 = 4.07% / 3.91% | history | FY2025 interest expense ÷ average debt and leases; H1 2026 interest income, annualised. |
| Cost of equity / terminal growth | 10.38% / 3.0% | judgment | CAPM: 5.11% 10-year Treasury + 1.17 bottom-up peer beta × 4.5% equity risk premium. Growth is below the risk-free rate. |
| Shares | 3,540 million | fact | Diluted, 10-Q Q2 2026 (p. 13); excludes 423.7M unearned CEO award shares. |

**Opening balance sheet, FY2025 (10-K p. 49):** revenue 94,827 · inventory 12,392 · PP&E 50,159 (PP&E 40,643 + lease vehicles 4,912 + energy systems 4,604) · other assets 31,196 · cash 44,059 (cash 16,513 + short-term investments 27,546) · floor plan 0 · debt 8,376 (including finance leases) · other liabilities 46,565 · equity 82,865 (including noncontrolling interests 728). Assets 137,806 = liabilities 54,941 + equity 82,865.

> **Partner attack (revenue growth, judgment):** "Why 10% a year when revenue fell 2.9% in FY2025, and what would change it?"  
> **My answer:** FY2025 was hurt by lower deliveries and prices, but H1 2026 revenue is already up 21% and energy storage and services are growing faster than cars, so 10% is below the current run-rate. It would change if 2026 deliveries fall back below the FY2025 pace or Megapack deployments stall; I would cut growth toward 3–5%, which lowers the value further.

---

## I — Tesla Through the Engine

```bash
python proforma.py        # still prints the ABG answer: 291.75
python proforma_tsla.py   # Tesla
```

The engine logic is the ABG engine, unchanged. Two optional inputs were added for Tesla: capex by year, and interest income on cash. Both are off for ABG, so the known answer still matches.

```text
INCOME STATEMENT (USD millions)
                                     FY2026E     FY2027E     FY2028E     FY2029E     FY2030E
Revenue                            104,309.7   114,740.7   126,214.7   138,836.2   152,719.8
Gross profit                        23,351.9    25,687.1    28,255.8    31,081.4    34,189.5
SG&A                                14,011.1    14,641.6    15,258.1    15,851.5    16,411.0
Depreciation                         6,148.0     8,458.7    10,118.5    11,084.5    11,687.0
Impairment                               0.0         0.0         0.0         0.0         0.0
Operating income                     3,192.8     2,586.8     2,879.2     4,145.4     6,091.6
Interest (net)                      -1,381.1      -799.7      -393.2      -186.7      -130.5
Pre-tax income                       4,573.9     3,386.5     3,272.4     4,332.0     6,222.1
Tax                                  1,143.5       846.6       818.1     1,083.0     1,555.5
Net income                           3,430.4     2,539.8     2,454.3     3,249.0     4,666.6

BALANCE SHEET (USD millions)
                                     FY2026E     FY2027E     FY2028E     FY2029E     FY2030E
Cash                                29,186.5    18,789.1    15,000.0    15,000.0    15,248.1
Inventory                           13,631.2    14,994.3    16,493.8    18,143.1    19,957.4
PP&E                                69,011.0    82,552.3    90,433.9    95,349.4    98,662.4
Other assets                        29,407.7    27,440.6    25,276.7    22,896.5    20,278.2
Total assets                       141,236.4   143,776.3   147,204.3   151,389.0   154,146.2
Floor plan                               0.0         0.0         0.0         0.0         0.0
Term debt                            8,376.0     8,376.0     8,376.0     8,376.0     8,376.0
Revolver                                 0.0         0.0       973.7     1,909.3         0.0
Other liabilities                   46,565.0    46,565.0    46,565.0    46,565.0    46,565.0
Total liabilities                   54,941.0    54,941.0    55,914.7    56,850.3    54,941.0
Equity                              86,295.4    88,835.3    91,289.6    94,538.6    99,205.2

CASH FLOW / FCFE (USD millions)
                                     FY2026E     FY2027E     FY2028E     FY2029E     FY2030E
Net income                           3,430.4     2,539.8     2,454.3     3,249.0     4,666.6
+ Depreciation                       6,148.0     8,458.7    10,118.5    11,084.5    11,687.0
+ Impairment                             0.0         0.0         0.0         0.0         0.0
- Capex                             25,000.0    22,000.0    18,000.0    16,000.0    15,000.0
- Change in inventory                1,239.2     1,363.1     1,499.4     1,649.4     1,814.3
- Change in other working capital    -1,788.3    -1,967.1    -2,163.8    -2,380.2    -2,618.3
+ Change in floor plan                   0.0         0.0         0.0         0.0         0.0
- Debt repayment                         0.0         0.0         0.0         0.0         0.0
Free cash flow to equity           -14,872.5   -10,397.4    -4,762.8      -935.6     2,157.5
- Share buyback                          0.0         0.0         0.0         0.0         0.0
Revolver draw / (repayment)              0.0         0.0       973.7       935.6    -1,909.3
Cash, year end                      29,186.5    18,789.1    15,000.0    15,000.0    15,248.1

CHECK BLOCK
                                     FY2026E     FY2027E     FY2028E     FY2029E     FY2030E
Assets - liabilities - equity            0.0         0.0         0.0         0.0         0.0
Cash >= minimum (15000)                   OK          OK          OK          OK          OK
Negative FCFE in                FY2026E, FY2027E, FY2028E, FY2029E

VALUATION (positive FCFE only, per the Lab 10 rule)
Cost of equity                        10.38%
Terminal growth                        3.00%
PV of positive FCFE (FY2030E)       1,317.03
Terminal value at end-2030         30,131.82
PV of terminal value               18,393.81
Equity value (USD millions)        19,710.85
Share of value after 2030             93.32%
Value per share (USD)                   5.57
Memo: all five years (engine)          -1.83   (equity -6,471; omits the opening cash that funds FY2026-29)
Market price (USD)                    378.94   September 24, 2026, 2:01 pm ET (Yahoo Finance)
Shares used (millions)               3,540.0
```

*In Tesla's run, the engine's "SG&A" row is R&D + SG&A excluding D&A.*

**The model refuses when broken:** setting 2026 cash to the opening 44,059 (`python proforma_tsla.py --break-cash`) prints
`ValueError: Balance sheet does not balance in FY2026E: assets - liabilities - equity = 14,872.5`, which is the year's fall in cash with the sign flipped.

---

## V — The Check Block and the Price

- **Checks:** assets − liabilities − equity is **0.0 in every year**, and cash stays at or above the \$15B floor.
- **Revolver:** it is drawn in FY2028–29 (peak \$1.9B) because capex keeps FCFE negative after cash reaches the \$15B floor; it is repaid in FY2030 when FCFE turns positive.
- **Negative FCFE** in FY2026E, FY2027E, FY2028E and FY2029E. These years are funded by the \$44B opening cash, so only the positive FY2030E FCFE and its terminal value are valued. The engine formula does not count that opening cash, so counting the negative years without it would show a meaningless −\$1.83.
- **Why a terminal value on a negative FCFE is not a number:** it would value a perpetual stream of losses that shareholders would never fund forever, so Gordon growth returns a negative "value" for a claim that cannot be worth less than zero.

> **The model says \$5.57 per share; the market says \$378.94 (September 24, 2026, 2:01 pm ET), on the same 3,540 million diluted shares.** What does the market expect from Tesla's AI spending that five years of these statements do not show?
---

## E — Fresh Eyes

| | |
|---|---|
| **Attack on my table** | Revenue growth, labelled judgment: "Why 10% a year when revenue fell 2.9% in FY2025, and what would change it?" |
| **My answer** | FY2025 was hurt by lower deliveries and prices, but H1 2026 revenue is already up 21% and energy storage and services are growing faster than cars, so 10% is below the current run-rate. It would change if 2026 deliveries fall back below the FY2025 pace or Megapack deployments stall; I would cut growth toward 3–5%. |
| **My attack on my partner's table** | *[partner's company]*: "Your \_\_\_ is labelled judgment at \_\_\_; the last three years in your filing were \_\_\_, so why that number, and what would make you change it?" |
| **Their answer** | *[partner's two sentences]* |

---

## Organic Growth — Learn on Your Own

1. **What it is:** growth from the business you already owned, excluding acquisitions, new locations and currency effects.
2. **How Tesla discloses it:** it doesn't. There is no same-store or organic figure. The MD&A explains revenue changes through deliveries, average selling price, Megapack deployments and services, so deliveries (−8.6% in 2025) are the closest proxy.
3. **Why ABG carries 1.8% when reported growth was 4.7%:** reported growth included acquired dealerships. Only growth from stores already owned repeats without spending more cash on acquisitions.

## Reflect

1. **The label I would defend the longest:** capital spending as *guidance*. The 2026 figure is Tesla's own words in the 10-Q ("in excess of \$25 billion"), not my estimate, and it is the line that drives four years of negative FCFE.
2. **The number in the filing that surprised me:** 2026 capex of more than \$25 billion against \$8.5 billion in FY2025, nearly three times as much, in a year when revenue had just fallen 2.9%.

## Checkout — Files on GitHub

- [`proforma_tsla.py`](proforma_tsla.py): Tesla through the engine
- [`proforma.py`](proforma.py): the engine (ABG known answer)
- [`Lab_10_proforma_tsla.md`](Lab_10_proforma_tsla.md): this write-up
