"""Lab 10 - Tesla (TSLA) through the Lab 09 engine.

The engine in proforma.py is unchanged (it still reproduces the ABG known answer). This file only
replaces the ABG opening balance sheet and assumptions with Tesla's, taken from the FY2023-FY2025 10-Ks
and the Q2 2026 10-Q. USD millions except per-share figures.

Run:          python proforma_tsla.py
Break test:   python proforma_tsla.py --break-cash   (sets 2026 cash to the opening 44,059; must refuse)
"""
import sys

import proforma as engine

# ------------------------------------------------------------------ Tesla assumption set
# (label in the comment; reasons are in Lab_10_proforma_tsla.md)
engine.GROWTH = 0.10                                         # judgment
engine.GROSS_MARGIN = (17094 + 3780 + 355) / 94827           # history: FY2025 GAAP gross profit + D&A inside cost of revenues
engine.SGA_TO_GP = [0.60, 0.57, 0.54, 0.51, 0.48]            # judgment: (R&D + SG&A, ex-D&A) / gross profit
engine.DEP_RATIO = 6148 / 50159                              # history: FY2025 D&A / year-end net fixed assets
engine.IMPAIRMENT = 0.0                                      # judgment: impairment is inside Tesla's D&A line
engine.CAPEX = [25000.0, 22000.0, 18000.0, 16000.0, 15000.0] # guidance (2026: "in excess of $25B"), judgment after
engine.TAX_RATE = 0.25                                       # judgment
engine.INV_DAYS = 12392 / (94827 - (17094 + 3780 + 355)) * 365   # history: FY2025 inventory / cash cost of revenues
engine.FLOOR_PLAN_RATIO = 0.0                                # none: Tesla has no floor plan
engine.FLOOR_PLAN_RATE = 0.0                                 # none
engine.OTHER_WC = -(13371 + 13279 + 3424 - 4576 - 7615) / 94827  # history: FY2025 net operating working capital / revenue
engine.MIN_CASH = 15000.0                                    # judgment: ~15% of revenue
engine.REVOLVER_LIMIT = 5000.0                               # history: $5.0B unused committed credit (10-Q p.35)
engine.REVOLVER_RATE = 0.06                                  # judgment
engine.REPAYMENT = 0.0                                       # judgment: Tesla refinances maturities (net borrowing ~0)
engine.BUYBACK = 0.0                                         # history: no repurchases FY2023-H1 2026
engine.DEBT_RATE = 338 / ((8213 + 8376) / 2)                 # history: FY2025 interest expense / average debt + leases
engine.INTEREST_INCOME_RATE = (856 * 2) / ((44059 + 43524) / 2)  # history: H1 2026 annualised interest income / average cash
engine.COST_OF_EQUITY = 0.0511 + 1.17 * 0.045                # judgment: CAPM, 10-yr Treasury 5.11% + bottom-up beta 1.17 x ERP 4.5%
engine.TERMINAL_GROWTH = 0.03                                # judgment
engine.SHARES = 3540.0                                       # fact: diluted shares, 10-Q Q2 2026 (millions)

# ------------------------------------------------------------------ opening balance sheet, FY2025 (10-K p.49)
engine.OPENING = {
    "revenue": 94827.0,
    "inventory": 12392.0,
    "ppe": 50159.0,              # PP&E 40,643 + operating lease vehicles 4,912 + energy systems 4,604
    "other_assets": 31196.0,     # total assets 137,806 less inventory, net fixed assets and cash
    "cash": 44059.0,             # cash 16,513 + short-term investments 27,546
    "floor_plan": 0.0,           # none
    "debt": 8376.0,              # debt and finance leases, current 1,640 + non-current 6,736
    "revolver": 0.0,
    "other_liabilities": 46565.0,  # total liabilities 54,941 less debt and finance leases
    "equity": 82865.0,           # stockholders' equity 82,137 + NCI 670 + redeemable NCI 58
}

PRICE, PRICE_TIME = 378.94, "September 24, 2026, 2:01 pm ET (Yahoo Finance)"


def main():
    rows = engine.project(break_cash="--break-cash" in sys.argv)
    engine.print_statements(rows)
    engine.print_checks(rows)
    negative = [f"FY{r['year']}E" for r in rows if r["fcfe"] < 0]
    if negative:
        print(f"{'Negative FCFE in':32}{', '.join(negative)}")
    engine.assert_balanced(rows)
    ke, g = engine.COST_OF_EQUITY, engine.TERMINAL_GROWTH
    # Lab 10 rule: value only what is positive. The negative years are funded by the opening cash pile
    # (44,059), which the engine's formula does not count, so both are left out together.
    pv_positive = sum(r["fcfe"] / (1 + ke) ** (t + 1) for t, r in enumerate(rows) if r["fcfe"] > 0)
    last = rows[-1]
    if last["fcfe"] <= 0:
        raise ValueError("FY2030E FCFE is negative: a terminal value on a negative cash flow is not a number")
    terminal = (last["fcfe"] + last["repayment"]) * (1 + g) / (ke - g)
    pv_terminal = terminal / (1 + ke) ** len(rows)
    equity_value = pv_positive + pv_terminal
    all_years_value, _, all_years_per_share = engine.value_equity(rows)
    print("\nVALUATION (positive FCFE only, per the Lab 10 rule)")
    print(f"{'Cost of equity':32}{ke:>12.2%}")
    print(f"{'Terminal growth':32}{g:>12.2%}")
    print(f"{'PV of positive FCFE (FY2030E)':32}{pv_positive:>12,.2f}")
    print(f"{'Terminal value at end-2030':32}{terminal:>12,.2f}")
    print(f"{'PV of terminal value':32}{pv_terminal:>12,.2f}")
    print(f"{'Equity value (USD millions)':32}{equity_value:>12,.2f}")
    print(f"{'Share of value after 2030':32}{pv_terminal / equity_value:>12.2%}")
    print(f"{'Value per share (USD)':32}{equity_value / engine.SHARES:>12,.2f}")
    print(f"{'Memo: all five years (engine)':32}{all_years_per_share:>12,.2f}   "
          f"(equity {all_years_value:,.0f}; omits the opening cash that funds FY2026-29)")
    print(f"{'Market price (USD)':32}{PRICE:>12,.2f}   {PRICE_TIME}")
    print(f"{'Shares used (millions)':32}{engine.SHARES:>12,.1f}")


if __name__ == "__main__":
    main()
