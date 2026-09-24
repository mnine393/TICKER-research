# Lab 09 — Pro-Forma Build: the Engine and the Known Answer (ABG)

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Case:** Asbury Automotive Group (`ABG`), the case from Part 1 of the video  
**Code:** [`proforma.py`](proforma.py) (single file, Python standard library only)  
**Units:** USD millions except per-share figures

> Learning demonstration, not investment advice.

---

## D — The Question

> **What are five years of a company's statements worth, built from assumptions you can defend, and how do you know the statements are right?**

## R — The Assumption Set

| Assumption | ABG value | Label |
|---|---|:---:|
| Organic revenue growth | 1.8% a year | judgment |
| Gross margin | 17.05% | judgment |
| SG&A ÷ gross profit, 2026 → 2030 | 66.5%, 65.5%, 64.5%, 64.5%, 64.5% | judgment |
| Depreciation ÷ opening PP&E | 82.4 ÷ 3,070.4 | history |
| Impairment, non-cash | 120 a year | judgment |
| Capital spending | 250 a year | guidance |
| Tax rate | 25.5% | judgment |
| Inventory days | 2,135.8 ÷ (17,999.0 − 3,071.7) × 365 | history |
| Floor plan ÷ inventory | 2,027.0 ÷ 2,135.8 | history |
| Other working capital | 0.8% of the change in revenue | judgment |
| Minimum cash / revolver limit / revolver rate | 25 / 850 / 6% | history / judgment / judgment |
| Debt repayment / share buyback | 150 / 150 a year | judgment |
| Interest: floor plan / term debt | 4.67% / 5.44% | history |
| Cost of equity / terminal growth | 10% / 2.5% | judgment |
| Shares outstanding | 17.951349 million | fact (10-Q, 30 June 2026) |

**Opening balance sheet, FY2025:** revenue 17,999.0 · inventory 2,135.8 · PP&E 3,070.4 · other assets 6,371.6 · cash 40.4 · floor plan 2,027.0 · term debt 3,572.0 · other liabilities 2,127.5 · equity 3,891.7 (assets 11,618.2 = liabilities 7,726.5 + equity 3,891.7).

**The three judgments that carry the value:** gross margin (17.05%), the SG&A ÷ gross-profit path (66.5% → 64.5%), and the cost of equity / terminal growth pair (10% / 2.5%).

## I — The Engine

[`proforma.py`](proforma.py) was written by AI from the lab's instruction, with the assumption table and opening balance sheet pasted under it. Each year it computes, in order:

1. **Income statement:** revenue → gross profit → SG&A → depreciation (on opening PP&E) → impairment → operating income → interest (on *opening* floor plan, term debt and revolver) → tax → net income.
2. **Balance sheet except cash:** inventory (days of cost of sales), floor plan (× ratio), PP&E (+ capex − depreciation), other assets (+ 0.8% of Δrevenue − impairment), term debt (− repayment), other liabilities (flat), equity (+ net income − buyback).
3. **FCFE** = net income + depreciation + impairment − capex − Δinventory − Δother working capital + Δfloor plan − repayment.
4. **Cash, last** = opening cash + FCFE − buyback. The revolver is drawn only if cash would fall below 25, and repaid first when cash is above it.
5. **Checks every year:** assets − liabilities − equity = 0, and cash ≥ minimum. `assert_balanced()` raises an error naming the year and the gap, and runs **before** the valuation.

Run it:

```bash
python proforma.py
```

## V — Proof on the Known Answer

| Line | FY2026E expected | FY2026E model | FY2030E expected | FY2030E model | Match |
|---|---:|---:|---:|---:|:---:|
| Revenue | 18,323.0 | 18,323.0 | 19,678.3 | 19,678.3 | ✅ |
| Operating income | 844.2 | 844.2 | 971.4 | 971.4 | ✅ |
| Net income | 413.6 | 413.6 | 527.5 | 527.5 | ✅ |
| Free cash flow to equity | 211.4 | 211.4 | 342.3 | 342.3 | ✅ |
| Cash, year end | 101.8 | 101.8 | 719.8 | 719.8 | ✅ |
| Assets − liabilities − equity | 0.0 | 0.0 | 0.0 | 0.0 | ✅ |
| **Value per share** | **\$291.75** | **\$291.75** | | | ✅ |

Share of value after 2030: **79.76%** (expected "about 80%").

**Check block (model output):**

```text
CHECK BLOCK
                                     FY2026E     FY2027E     FY2028E     FY2029E     FY2030E
Assets - liabilities - equity            0.0         0.0         0.0         0.0         0.0
Cash >= minimum (25)                      OK          OK          OK          OK          OK

VALUATION
Equity value (USD millions)         5,237.34
Share of value after 2030             79.76%
Value per share (USD)                 291.75
```

### Swap and break

Setting 2026 cash to the opening 40.4 instead of the computed figure (the file also accepts `python proforma.py --break-cash` to make the same edit):

```text
ValueError: Balance sheet does not balance in FY2026E: assets - liabilities - equity = -61.4
```

The model **refuses to value** the company, naming FY2026E and a gap of −61.4. That is the year's change in cash (101.8 − 40.4 = 61.4) with the sign flipped. Undoing the change restores the balanced result above.

## Floor Plan — Learn on Your Own

1. **What it is:** short-term loans that finance a dealer's vehicle inventory, provided by manufacturers' captive finance arms and banks. Each car on the lot is pledged against its loan.
2. **How it works:** it rises and falls with inventory (here, 2,027.0 ÷ 2,135.8 ≈ 94.9% of inventory). Interest is charged on the opening balance (4.67%). Because it funds day-to-day operations, the change in floor plan sits **inside FCFE as an operating item**, offsetting the inventory build.
3. **Why removing the line sends cash to about −1.1 billion:** with the floor-plan ratio set to zero, the 2,027.0 opening balance must be repaid in FY2026. That shows up as a −2,027.0 change in floor plan inside FCFE. The revolver draws its full 850 limit and still cannot cover it, so FY2026 cash ends at **−1,112.0** (checked by running the engine with the ratio at 0). Floor plan is how a dealer funds its lots; take it away and the inventory has to be paid for with cash the company does not have.

## Reflect

1. **Why the model computes cash last:** every other line is driven by an assumption. Cash is the only line that is the *result* of all of them: net income, working capital, capex, financing and buybacks flowing through the cash-flow statement. Computing it last, from FCFE rather than as a plug, is what lets assets = liabilities + equity act as a real test of the model.
2. **What the −61.4 tells you before opening a cell:** the break is in FY2026E, and its size equals that year's change in cash. So the balance sheet's cash is not the cash-flow result, and the error is in how cash is linked, not in any operating assumption.

## Checkout — Files on GitHub

- [`proforma.py`](proforma.py): the engine
- [`Lab_09_proforma_engine.md`](Lab_09_proforma_engine.md): this write-up
