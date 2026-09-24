"""Lab 09 - Pro-forma three-statement engine, proved on the ABG (Asbury Automotive Group) case.

Standard library only. USD millions except per-share figures.
Run:           python proforma.py
Break test:    python proforma.py --break-cash   (sets 2026 cash to the opening 40.4; the model must refuse)
"""
import sys

YEARS = [2026, 2027, 2028, 2029, 2030]

# ---------------------------------------------------------------- assumptions (label in comment)
GROWTH = 0.018                                    # organic revenue growth - judgment
GROSS_MARGIN = 0.1705                             # judgment
SGA_TO_GP = [0.665, 0.655, 0.645, 0.645, 0.645]   # SG&A / gross profit, 2026-2030 - judgment
DEP_RATIO = 82.4 / 3070.4                         # FY2025 depreciation / year-end PP&E - history
IMPAIRMENT = 120.0                                # non-cash, per year - judgment
CAPEX = 250.0                                     # per year - guidance (a list of 5 values is also accepted)
TAX_RATE = 0.255                                  # judgment
INV_DAYS = 2135.8 / (17999.0 - 3071.7) * 365      # FY2025 inventory / cost of sales - history
FLOOR_PLAN_RATIO = 2027.0 / 2135.8                # FY2025 floor plan / inventory - history
OTHER_WC = 0.008                                  # of the change in revenue - judgment
MIN_CASH = 25.0                                   # history
REVOLVER_LIMIT = 850.0                            # judgment
REVOLVER_RATE = 0.06                              # judgment
REPAYMENT = 150.0                                 # term debt repayment per year - judgment
BUYBACK = 150.0                                   # per year - judgment
FLOOR_PLAN_RATE = 0.0467                          # history
DEBT_RATE = 0.0544                                # history
INTEREST_INCOME_RATE = 0.0                        # yield on opening cash (0 for ABG, which reports none)
COST_OF_EQUITY = 0.10                             # judgment
TERMINAL_GROWTH = 0.025                           # judgment
SHARES = 17.951349                                # millions - fact (10-Q, 30 June 2026)

# ---------------------------------------------------------------- opening balance sheet, FY2025
OPENING = {
    "revenue": 17999.0, "inventory": 2135.8, "ppe": 3070.4, "other_assets": 6371.6, "cash": 40.4,
    "floor_plan": 2027.0, "debt": 3572.0, "revolver": 0.0, "other_liabilities": 2127.5, "equity": 3891.7,
}


def project(break_cash=False):
    """Project five years. Cash is computed last, from free cash flow to equity."""
    rows = []
    prev = dict(OPENING)
    for i, year in enumerate(YEARS):
        r = {"year": year}
        # ---- income statement
        r["revenue"] = prev["revenue"] * (1 + GROWTH)
        r["gross_profit"] = r["revenue"] * GROSS_MARGIN
        r["sga"] = r["gross_profit"] * SGA_TO_GP[i]
        r["depreciation"] = prev["ppe"] * DEP_RATIO
        r["impairment"] = IMPAIRMENT
        r["operating_income"] = r["gross_profit"] - r["sga"] - r["depreciation"] - r["impairment"]
        r["interest"] = (prev["floor_plan"] * FLOOR_PLAN_RATE + prev["debt"] * DEBT_RATE
                         + prev["revolver"] * REVOLVER_RATE - prev["cash"] * INTEREST_INCOME_RATE)
        r["pretax"] = r["operating_income"] - r["interest"]
        r["tax"] = max(0.0, r["pretax"]) * TAX_RATE
        r["net_income"] = r["pretax"] - r["tax"]
        # ---- balance sheet except cash
        r["inventory"] = (r["revenue"] - r["gross_profit"]) * INV_DAYS / 365
        r["floor_plan"] = r["inventory"] * FLOOR_PLAN_RATIO
        capex = CAPEX[i] if isinstance(CAPEX, (list, tuple)) else CAPEX
        r["ppe"] = prev["ppe"] + capex - r["depreciation"]
        change_other_wc = OTHER_WC * (r["revenue"] - prev["revenue"])
        r["other_assets"] = prev["other_assets"] + change_other_wc - r["impairment"]
        r["debt"] = prev["debt"] - REPAYMENT
        r["other_liabilities"] = prev["other_liabilities"]
        r["equity"] = prev["equity"] + r["net_income"] - BUYBACK
        # ---- free cash flow to equity
        r["change_inventory"] = r["inventory"] - prev["inventory"]
        r["change_other_wc"] = change_other_wc
        r["change_floor_plan"] = r["floor_plan"] - prev["floor_plan"]
        r["capex"] = capex
        r["repayment"] = REPAYMENT
        r["fcfe"] = (r["net_income"] + r["depreciation"] + r["impairment"] - capex
                     - r["change_inventory"] - change_other_wc + r["change_floor_plan"] - REPAYMENT)
        # ---- cash, last: revolver only if cash would fall below the minimum
        cash = prev["cash"] + r["fcfe"] - BUYBACK
        if cash < MIN_CASH:
            draw = min(MIN_CASH - cash, REVOLVER_LIMIT - prev["revolver"])
        else:
            draw = -min(prev["revolver"], cash - MIN_CASH)
        r["revolver_draw"] = draw
        r["revolver"] = prev["revolver"] + draw
        r["buyback"] = BUYBACK
        r["cash"] = cash + draw
        if break_cash and year == 2026:
            r["cash"] = OPENING["cash"]          # deliberate break: cash not taken from the cash flow
        # ---- totals and checks
        r["total_assets"] = r["cash"] + r["inventory"] + r["ppe"] + r["other_assets"]
        r["total_liabilities"] = r["floor_plan"] + r["debt"] + r["revolver"] + r["other_liabilities"]
        r["gap"] = r["total_assets"] - r["total_liabilities"] - r["equity"]
        r["cash_ok"] = r["cash"] >= MIN_CASH - 1e-9
        rows.append(r)
        prev = r
    return rows


def print_table(title, rows, lines):
    print(f"\n{title}")
    print(f"{'':32}" + "".join(f"{'FY' + str(r['year']) + 'E':>12}" for r in rows))
    for label, key in lines:
        print(f"{label:32}" + "".join(f"{round(r[key], 1) + 0.0:>12,.1f}" for r in rows))   # + 0.0 avoids "-0.0"


def print_statements(rows):
    print_table("INCOME STATEMENT (USD millions)", rows, [
        ("Revenue", "revenue"), ("Gross profit", "gross_profit"), ("SG&A", "sga"),
        ("Depreciation", "depreciation"), ("Impairment", "impairment"),
        ("Operating income", "operating_income"), ("Interest (net)", "interest"),
        ("Pre-tax income", "pretax"), ("Tax", "tax"), ("Net income", "net_income")])
    print_table("BALANCE SHEET (USD millions)", rows, [
        ("Cash", "cash"), ("Inventory", "inventory"), ("PP&E", "ppe"), ("Other assets", "other_assets"),
        ("Total assets", "total_assets"), ("Floor plan", "floor_plan"), ("Term debt", "debt"),
        ("Revolver", "revolver"), ("Other liabilities", "other_liabilities"),
        ("Total liabilities", "total_liabilities"), ("Equity", "equity")])
    print_table("CASH FLOW / FCFE (USD millions)", rows, [
        ("Net income", "net_income"), ("+ Depreciation", "depreciation"), ("+ Impairment", "impairment"),
        ("- Capex", "capex"), ("- Change in inventory", "change_inventory"),
        ("- Change in other working capital", "change_other_wc"), ("+ Change in floor plan", "change_floor_plan"),
        ("- Debt repayment", "repayment"), ("Free cash flow to equity", "fcfe"),
        ("- Share buyback", "buyback"), ("Revolver draw / (repayment)", "revolver_draw"),
        ("Cash, year end", "cash")])


def print_checks(rows):
    print("\nCHECK BLOCK")
    print(f"{'':32}" + "".join(f"{'FY' + str(r['year']) + 'E':>12}" for r in rows))
    print(f"{'Assets - liabilities - equity':32}" + "".join(f"{round(r['gap'], 1) + 0.0:>12,.1f}" for r in rows))
    print(f"{'Cash >= minimum (' + format(MIN_CASH, '.0f') + ')':32}" + "".join(f"{('OK' if r['cash_ok'] else 'FAIL'):>12}" for r in rows))


def assert_balanced(rows, tol=0.05):
    """Refuse to value the company if any year fails a check."""
    for r in rows:
        if abs(r["gap"]) > tol:
            raise ValueError(f"Balance sheet does not balance in FY{r['year']}E: "
                             f"assets - liabilities - equity = {r['gap']:,.1f}")
        if not r["cash_ok"]:
            raise ValueError(f"Cash below the minimum in FY{r['year']}E: cash {r['cash']:,.1f} < {MIN_CASH:,.1f}")


def value_equity(rows):
    pv_fcfe = sum(r["fcfe"] / (1 + COST_OF_EQUITY) ** (t + 1) for t, r in enumerate(rows))
    last = rows[-1]
    terminal = (last["fcfe"] + last["repayment"]) * (1 + TERMINAL_GROWTH) / (COST_OF_EQUITY - TERMINAL_GROWTH)
    pv_terminal = terminal / (1 + COST_OF_EQUITY) ** len(rows)
    equity_value = pv_fcfe + pv_terminal
    return equity_value, pv_terminal / equity_value, equity_value / SHARES


def main():
    rows = project(break_cash="--break-cash" in sys.argv)
    print_statements(rows)
    print_checks(rows)
    assert_balanced(rows)
    equity_value, share_after_2030, per_share = value_equity(rows)
    print("\nVALUATION")
    print(f"{'Equity value (USD millions)':32}{equity_value:>12,.2f}")
    print(f"{'Share of value after 2030':32}{share_after_2030:>12.2%}")
    print(f"{'Value per share (USD)':32}{per_share:>12,.2f}")


if __name__ == "__main__":
    main()
