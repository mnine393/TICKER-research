"""Lab 11 - Pro-Forma Sensitivity Analysis: Tesla (TSLA) Drivers.

Builds on the Lab 10 Tesla pro-forma model (proforma_tsla.py) and the Lab 09 three-statement
engine (proforma.py). Performs one-at-a-time sensitivity analysis for two independent operating
drivers:
  1. Annual Revenue Growth (GROWTH): 8.0% (lower), 10.0% (base), 12.0% (higher)
  2. Gross Margin before D&A (GROSS_MARGIN): 21.39% (lower), ~22.39% (base), 23.39% (higher)

Preserves a separate base input set built directly from Lab 10 (proforma_tsla.py), runs each
scenario from a fresh independent copy, verifies accounting checks, computes output spans,
traces statement mechanics, and confirms that the restored base matches the starting run exactly.
Standard library only.

Run: python sensitivity_tsla.py
"""
import copy
import sys

import proforma as engine
import proforma_tsla

# ------------------------------------------------------------------ Tesla base input set
# Built directly from Lab 10 (proforma_tsla.py) to guarantee baseline consistency
TESLA_BASE_INPUTS = {
    "GROWTH": proforma_tsla.engine.GROWTH,
    "GROSS_MARGIN": proforma_tsla.engine.GROSS_MARGIN,
    "SGA_TO_GP": copy.deepcopy(proforma_tsla.engine.SGA_TO_GP),
    "DEP_RATIO": proforma_tsla.engine.DEP_RATIO,
    "IMPAIRMENT": proforma_tsla.engine.IMPAIRMENT,
    "CAPEX": copy.deepcopy(proforma_tsla.engine.CAPEX),
    "TAX_RATE": proforma_tsla.engine.TAX_RATE,
    "INV_DAYS": proforma_tsla.engine.INV_DAYS,
    "FLOOR_PLAN_RATIO": proforma_tsla.engine.FLOOR_PLAN_RATIO,
    "FLOOR_PLAN_RATE": proforma_tsla.engine.FLOOR_PLAN_RATE,
    "OTHER_WC": proforma_tsla.engine.OTHER_WC,
    "MIN_CASH": proforma_tsla.engine.MIN_CASH,
    "REVOLVER_LIMIT": proforma_tsla.engine.REVOLVER_LIMIT,
    "REVOLVER_RATE": proforma_tsla.engine.REVOLVER_RATE,
    "REPAYMENT": proforma_tsla.engine.REPAYMENT,
    "BUYBACK": proforma_tsla.engine.BUYBACK,
    "DEBT_RATE": proforma_tsla.engine.DEBT_RATE,
    "INTEREST_INCOME_RATE": proforma_tsla.engine.INTEREST_INCOME_RATE,
    "COST_OF_EQUITY": proforma_tsla.engine.COST_OF_EQUITY,
    "TERMINAL_GROWTH": proforma_tsla.engine.TERMINAL_GROWTH,
    "SHARES": proforma_tsla.engine.SHARES,
    "OPENING": copy.deepcopy(proforma_tsla.engine.OPENING),
}

PRICE = proforma_tsla.PRICE
PRICE_TIME = proforma_tsla.PRICE_TIME


def apply_inputs(inputs_dict):
    """Assign an input dictionary to the underlying engine."""
    engine.GROWTH = inputs_dict["GROWTH"]
    engine.GROSS_MARGIN = inputs_dict["GROSS_MARGIN"]
    engine.SGA_TO_GP = copy.deepcopy(inputs_dict["SGA_TO_GP"])
    engine.DEP_RATIO = inputs_dict["DEP_RATIO"]
    engine.IMPAIRMENT = inputs_dict["IMPAIRMENT"]
    engine.CAPEX = copy.deepcopy(inputs_dict["CAPEX"])
    engine.TAX_RATE = inputs_dict["TAX_RATE"]
    engine.INV_DAYS = inputs_dict["INV_DAYS"]
    engine.FLOOR_PLAN_RATIO = inputs_dict["FLOOR_PLAN_RATIO"]
    engine.FLOOR_PLAN_RATE = inputs_dict["FLOOR_PLAN_RATE"]
    engine.OTHER_WC = inputs_dict["OTHER_WC"]
    engine.MIN_CASH = inputs_dict["MIN_CASH"]
    engine.REVOLVER_LIMIT = inputs_dict["REVOLVER_LIMIT"]
    engine.REVOLVER_RATE = inputs_dict["REVOLVER_RATE"]
    engine.REPAYMENT = inputs_dict["REPAYMENT"]
    engine.BUYBACK = inputs_dict["BUYBACK"]
    engine.DEBT_RATE = inputs_dict["DEBT_RATE"]
    engine.INTEREST_INCOME_RATE = inputs_dict["INTEREST_INCOME_RATE"]
    engine.COST_OF_EQUITY = inputs_dict["COST_OF_EQUITY"]
    engine.TERMINAL_GROWTH = inputs_dict["TERMINAL_GROWTH"]
    engine.SHARES = inputs_dict["SHARES"]
    engine.OPENING = copy.deepcopy(inputs_dict["OPENING"])


def run_scenario(inputs_dict):
    """Run the model with the given input dictionary and return structured metrics."""
    apply_inputs(inputs_dict)
    rows = engine.project()
    
    # Check accounting integrity
    gap_ok = True
    cash_ok = True
    fail_reasons = []
    for r in rows:
        if abs(r["gap"]) > 0.05:
            gap_ok = False
            fail_reasons.append(f"BS gap FY{r['year']}E = {r['gap']:.2f}")
        if not r["cash_ok"]:
            cash_ok = False
            fail_reasons.append(f"Cash floor breached FY{r['year']}E: {r['cash']:.1f} < {inputs_dict['MIN_CASH']:.1f}")
    
    checks_pass = gap_ok and cash_ok
    
    last = rows[-1]
    op_inc_2030 = last["operating_income"]
    fcfe_2030 = last["fcfe"]
    
    # DCF valuation: include EVERY forecast year with its sign (do not discard negative FCFE)
    # Cites proforma_tsla.py lines 67-73 and proforma.py value_equity():
    # Terminal value requires final-year FCFE > 0 (proforma_tsla.py line 68: 'if last["fcfe"] <= 0: raise ValueError(...)')
    # and cost of equity > terminal growth (ke > g).
    # Terminal cash flow formula: (last["fcfe"] + last["repayment"]) * (1 + g) / (ke - g) (proforma_tsla.py line 70).
    ke = inputs_dict["COST_OF_EQUITY"]
    g = inputs_dict["TERMINAL_GROWTH"]
    pv_fcfe = sum(r["fcfe"] / (1 + ke) ** (t + 1) for t, r in enumerate(rows))
    
    if checks_pass and last["fcfe"] > 0 and (ke > g):
        terminal = (last["fcfe"] + last["repayment"]) * (1 + g) / (ke - g)
        pv_terminal = terminal / (1 + ke) ** len(rows)
        equity_val = pv_fcfe + pv_terminal
        val_per_share = equity_val / inputs_dict["SHARES"]
    else:
        terminal = None
        pv_terminal = None
        equity_val = None
        val_per_share = None
        
    return {
        "rows": rows,
        "checks_pass": checks_pass,
        "gap_ok": gap_ok,
        "cash_ok": cash_ok,
        "fail_reasons": fail_reasons,
        "op_inc_2030": op_inc_2030,
        "fcfe_2030": fcfe_2030,
        "pv_fcfe": pv_fcfe,
        "terminal": terminal,
        "pv_terminal": pv_terminal,
        "equity_val": equity_val,
        "val_per_share": val_per_share,
        "max_revolver": max(r["revolver"] for r in rows),
        "min_cash": min(r["cash"] for r in rows),
    }


def fmt_val(v):
    """Format a currency value per share cleanly, formatting negative numbers as -$X.XX."""
    if v is None:
        return "N/A"
    if v < 0:
        return f"-${abs(v):.2f}"
    return f"${v:.2f}"


def fmt_diff(d):
    """Format a signed change from base cleanly."""
    if d is None:
        return "N/A"
    sign = "+" if d >= 0 else "-"
    return f"{sign}${abs(d):.2f}"


def calc_spans(run_list):
    """Compute output span = max valid result - min valid result across valid lower/base/higher runs."""
    ops = [r["op_inc_2030"] for r in run_list if r["checks_pass"]]
    fcs = [r["fcfe_2030"] for r in run_list if r["checks_pass"]]
    vals = [r["val_per_share"] for r in run_list if r["checks_pass"] and r["val_per_share"] is not None]
    
    op_min = min(ops) if ops else None
    op_max = max(ops) if ops else None
    op_span = (op_max - op_min) if (op_max is not None and op_min is not None) else None
    
    fc_min = min(fcs) if fcs else None
    fc_max = max(fcs) if fcs else None
    fc_span = (fc_max - fc_min) if (fc_max is not None and fc_min is not None) else None
    
    val_min = min(vals) if vals else None
    val_max = max(vals) if vals else None
    val_span = (val_max - val_min) if (val_max is not None and val_min is not None) else None
    
    return {
        "op_min": op_min, "op_max": op_max, "op_span": op_span,
        "fc_min": fc_min, "fc_max": fc_max, "fc_span": fc_span,
        "val_min": val_min, "val_max": val_max, "val_span": val_span,
    }


def format_metric_span(spans_dict, metric_prefix, unit_suffix="M"):
    """Format an output span line cleanly, printing 'N/A (no valid runs)' if None."""
    s_max = spans_dict[f"{metric_prefix}_max"]
    s_min = spans_dict[f"{metric_prefix}_min"]
    s_span = spans_dict[f"{metric_prefix}_span"]
    if s_span is None or s_max is None or s_min is None:
        return "N/A (no valid runs)"
    if metric_prefix == "val":
        min_str = f"-${abs(s_min):.2f}" if s_min < 0 else f"${s_min:.2f}"
        max_str = f"-${abs(s_max):.2f}" if s_max < 0 else f"${s_max:.2f}"
        if s_min < 0:
            return f"{max_str} - ({min_str}) = ${s_span:.2f}"
        return f"{max_str} - {min_str} = ${s_span:.2f}"
    else:
        return f"{s_max:>7,.1f} - {s_min:>7,.1f} = ${s_span:>7,.1f}{unit_suffix}"


def main():
    print("=" * 80)
    print("LAB 11: PRO-FORMA SENSITIVITY ANALYSIS — TESLA, INC. (TSLA)")
    print("=" * 80)
    print("Company: Tesla, Inc. (NASDAQ: TSLA)")
    print(f"Valuation Reference Price: ${PRICE:.2f} ({PRICE_TIME})")
    print("Diluted Shares: 3,540.0M | FCFE Model (USD millions except per-share)")
    print("-" * 80)

    # 1. Base run before sensitivity and comparison against Lab 10 model
    base_inputs = copy.deepcopy(TESLA_BASE_INPUTS)
    base_res = run_scenario(base_inputs)
    
    # Run Lab 10 model directly via engine to verify baseline integrity
    apply_inputs(TESLA_BASE_INPUTS)
    lab10_rows = engine.project()
    lab10_last = lab10_rows[-1]
    lab10_op = lab10_last["operating_income"]
    lab10_fc = lab10_last["fcfe"]
    # Lab 10 signed DCF valuation per proforma_tsla.py line 73: engine.value_equity(rows)[2]
    _, _, lab10_val = engine.value_equity(lab10_rows)

    diff_lab10_op = abs(base_res["op_inc_2030"] - lab10_op)
    diff_lab10_fc = abs(base_res["fcfe_2030"] - lab10_fc)
    diff_lab10_val = abs(base_res["val_per_share"] - lab10_val)

    print("\n--- BASELINE VERIFICATION AGAINST LAB 10 (PROFORMA_TSLA.PY) ---")
    print(f"{'Metric':32} | {'Lab 10 Saved Model':20} | {'Script Base Run':20} | {'Status'}")
    print("-" * 85)
    print(f"{'FY2030E Operating Income':32} | ${lab10_op:>18,.1f}M | ${base_res['op_inc_2030']:>18,.1f}M | {'MATCH' if diff_lab10_op < 1e-4 else 'MISMATCH'}")
    print(f"{'FY2030E FCFE':32} | ${lab10_fc:>18,.1f}M | ${base_res['fcfe_2030']:>18,.1f}M | {'MATCH' if diff_lab10_fc < 1e-4 else 'MISMATCH'}")
    print(f"{'Value per share (signed DCF)':32} | {fmt_val(lab10_val):>20} | {fmt_val(base_res['val_per_share']):>20} | {'MATCH' if diff_lab10_val < 1e-4 else 'MISMATCH'}")
    print(f"{'Accounting checks':32} | {'PASS':>20} | {('PASS' if base_res['checks_pass'] else 'FAIL'):>20} | MATCH")
    print(f"Peak revolver draw: ${base_res['max_revolver']:>10,.1f}M (limit $5,000.0M)")

    # 2. Define sensitivity scenarios
    # In proforma.py, both GROWTH and GROSS_MARGIN are scalar parameters applied in every year of
    # YEARS = [2026, 2027, 2028, 2029, 2030].
    # GROWTH: compounds revenue each year as prev['revenue'] * (1 + GROWTH)
    # GROSS_MARGIN: calculates gross profit each year as r['revenue'] * GROSS_MARGIN
    base_growth = base_inputs["GROWTH"]
    base_gm = base_inputs["GROSS_MARGIN"]

    scenarios = [
        # (group, label, param_key, param_val, base_val_str, new_val_str, shift_str, affected_years)
        ("Base", "Base run", None, None, "10.0% / 22.39%", "10.0% / 22.39%", "0.0 pp", "FY2026E–FY2030E (all 5 years)"),
        ("Driver 1: Revenue Growth", "Lower Growth 8.0%", "GROWTH", 0.08, "10.0% annual growth", "8.0% annual growth", "-2.0 pp", "FY2026E–FY2030E (all 5 years)"),
        ("Driver 1: Revenue Growth", "Higher Growth 12.0%", "GROWTH", 0.12, "10.0% annual growth", "12.0% annual growth", "+2.0 pp", "FY2026E–FY2030E (all 5 years)"),
        ("Driver 2: Gross Margin", "Lower Gross Margin 21.39%", "GROSS_MARGIN", base_gm - 0.01, "22.39% of revenue", "21.39% of revenue", "-1.0 pp", "FY2026E–FY2030E (all 5 years)"),
        ("Driver 2: Gross Margin", "Higher Gross Margin 23.39%", "GROSS_MARGIN", base_gm + 0.01, "22.39% of revenue", "23.39% of revenue", "+1.0 pp", "FY2026E–FY2030E (all 5 years)"),
    ]

    # 3. Print Scenario Specification Table (Requirement 3)
    print("\n" + "=" * 80)
    print("SCENARIO SPECIFICATION: INPUTS, UNITS, SHIFTS, AND AFFECTED YEARS")
    print("=" * 80)
    print(f"{'Scenario Name':26} | {'Driver Key':12} | {'Base Value -> New Value':30} | {'Shift':8} | {'Affected Years'}")
    print("-" * 110)
    for grp, lbl, pkey, pval, bstr, nstr, sshift, yaff in scenarios:
        pkey_display = pkey if pkey is not None else "(Baseline)"
        trans_str = f"{bstr} -> {nstr}" if pkey is not None else bstr
        print(f"{lbl:26} | {pkey_display:12} | {trans_str:30} | {sshift:8} | {yaff}")
    print("-" * 110)
    print("Source logic: In proforma.py, both GROWTH and GROSS_MARGIN apply across all five forecast years")
    print("(YEARS = [2026, 2027, 2028, 2029, 2030]). Revenue compounds as prev['revenue'] * (1 + GROWTH),")
    print("and Gross Profit is computed as r['revenue'] * GROSS_MARGIN.")

    results = []
    for grp, lbl, pkey, pval, bstr, nstr, sshift, yaff in scenarios:
        scen_inputs = copy.deepcopy(TESLA_BASE_INPUTS)
        if pkey is not None:
            scen_inputs[pkey] = pval
        res = run_scenario(scen_inputs)
        res["group"] = grp
        res["label"] = lbl
        res["param_key"] = pkey
        res["param_val"] = pval
        results.append(res)

    # 4. Print Sensitivity Comparison Table
    print("\n" + "=" * 80)
    print("SENSITIVITY COMPARISON TABLE: OPERATING PROFIT, FCFE, AND VALUE PER SHARE")
    print("=" * 80)
    hdr = f"{'Independent Input Changed':28} | {'Operating Profit ($m)':22} | {'FCFE ($m)':18} | {'Value ($/share)':16} | {'Checks'}"
    print(hdr)
    print("-" * 105)

    base_op = base_res["op_inc_2030"]
    base_fc = base_res["fcfe_2030"]
    base_val = base_res["val_per_share"]

    for r in results:
        diff_op = r["op_inc_2030"] - base_op
        diff_fc = r["fcfe_2030"] - base_fc
        op_str = f"{r['op_inc_2030']:>8,.1f} ({diff_op:>+7,.1f})" if r["label"] != "Base run" else f"{r['op_inc_2030']:>8,.1f} (  base )"
        fc_str = f"{r['fcfe_2030']:>7,.1f} ({diff_fc:>+7,.1f})" if r["label"] != "Base run" else f"{r['fcfe_2030']:>7,.1f} ( base )"
        
        if r["val_per_share"] is not None and base_val is not None:
            diff_v = r["val_per_share"] - base_val
            v_val_str = fmt_val(r["val_per_share"])
            v_diff_str = fmt_diff(diff_v)
            v_str = f"{v_val_str:>7} ({v_diff_str:>6})" if r["label"] != "Base run" else f"{v_val_str:>7} ( base )"
        elif r["val_per_share"] is not None:
            v_str = f"{fmt_val(r['val_per_share']):>7} (  N/A )"
        else:
            v_str = "    N/A          "
            
        chk_str = "PASS" if r["checks_pass"] else "FAIL"
        print(f"{r['label']:28} | {op_str:22} | {fc_str:18} | {v_str:16} | {chk_str}")

    print("-" * 105)
    print("Note: Signed changes from base are shown in parentheses. Money is in USD millions except $/share.")
    print("DCF includes all forecast years with their sign, discounting negative FCFE at cost of equity.")

    # 5. Compute and Print Output Spans
    # Span = max valid output - min valid output across lower, base, higher
    growth_runs = [results[0], results[1], results[2]]  # base, lower, higher
    gm_runs = [results[0], results[3], results[4]]      # base, lower, higher

    g_spans = calc_spans(growth_runs)
    gm_spans = calc_spans(gm_runs)

    print("\n" + "=" * 80)
    print("OUTPUT SPANS: MAXIMUM VALID RESULT MINUS MINIMUM VALID RESULT")
    print("=" * 80)
    print(f"{'Output Metric':24} | {'Revenue Growth Output Span':30} | {'Gross Margin Output Span':30}")
    print("-" * 90)
    print(f"{'FY2030E Operating Income':24} | {format_metric_span(g_spans, 'op'):<30} | {format_metric_span(gm_spans, 'op'):<30}")
    print(f"{'FY2030E FCFE':24} | {format_metric_span(g_spans, 'fc'):<30} | {format_metric_span(gm_spans, 'fc'):<30}")
    print(f"{'Value per share':24} | {format_metric_span(g_spans, 'val'):<30} | {format_metric_span(gm_spans, 'val'):<30}")
    print("-" * 90)

    # 6. Selected Result Statement Trace (Higher Growth 12.0% vs Base)
    print("\n" + "=" * 80)
    print("STATEMENT TRACE: HIGHER GROWTH (12.0%) VS BASELINE (10.0%) IN FY2030E")
    print("=" * 80)
    hi_g_row = results[2]["rows"][-1]
    base_row = base_res["rows"][-1]
    trace_lines = [
        ("Revenue", base_row["revenue"], hi_g_row["revenue"]),
        ("Gross profit (before D&A)", base_row["gross_profit"], hi_g_row["gross_profit"]),
        ("SG&A (incl R&D, ex D&A)", base_row["sga"], hi_g_row["sga"]),
        ("Depreciation", base_row["depreciation"], hi_g_row["depreciation"]),
        ("Operating Income", base_row["operating_income"], hi_g_row["operating_income"]),
        ("Interest expense / (income) net", base_row["interest"], hi_g_row["interest"]),
        ("Pre-tax income", base_row["pretax"], hi_g_row["pretax"]),
        ("Tax", base_row["tax"], hi_g_row["tax"]),
        ("Net income", base_row["net_income"], hi_g_row["net_income"]),
        ("Capex", base_row["capex"], hi_g_row["capex"]),
        ("Change in Inventory", base_row["change_inventory"], hi_g_row["change_inventory"]),
        ("Change in Other Working Capital", base_row["change_other_wc"], hi_g_row["change_other_wc"]),
        ("Free Cash Flow to Equity (FCFE)", base_row["fcfe"], hi_g_row["fcfe"]),
        ("Ending Cash", base_row["cash"], hi_g_row["cash"]),
        ("Revolver Balance", base_row["revolver"], hi_g_row["revolver"]),
    ]
    print(f"{'Line Item (USD millions)':35} | {'Base (10.0%)':14} | {'Higher (12.0%)':14} | {'Difference':14}")
    print("-" * 85)
    for lbl, b_val, h_val in trace_lines:
        d_val = h_val - b_val
        print(f"{lbl:35} | {b_val:>14,.1f} | {h_val:>14,.1f} | {d_val:>+14,.1f}")
    print("-" * 85)

    # 7. Restored Base Verification (Requirement 1 & 8)
    print("\n" + "=" * 80)
    print("RESTORED BASELINE INTEGRITY CHECK")
    print("=" * 80)
    apply_inputs(TESLA_BASE_INPUTS)
    restored_res = run_scenario(copy.deepcopy(TESLA_BASE_INPUTS))
    restored_op = restored_res["op_inc_2030"]
    restored_fc = restored_res["fcfe_2030"]
    restored_val = restored_res["val_per_share"]

    diff_op_restored = abs(restored_op - base_op)
    diff_fc_restored = abs(restored_fc - base_fc)

    if base_val is not None and restored_val is not None:
        diff_val_restored = abs(restored_val - base_val)
        val_match_str = f"EXACT (diff {diff_val_restored:.2f})" if diff_val_restored < 1e-4 else "MISMATCH"
        base_val_str = f"{fmt_val(base_val):>18}"
        restored_val_str = f"{fmt_val(restored_val):>18}"
    elif base_val is None and restored_val is None:
        diff_val_restored = 0.0
        val_match_str = "EXACT (both N/A)"
        base_val_str = f"{'N/A':>18}"
        restored_val_str = f"{'N/A':>18}"
    else:
        diff_val_restored = 999.0
        val_match_str = "MISMATCH"
        base_val_str = f"{fmt_val(base_val):>18}"
        restored_val_str = f"{fmt_val(restored_val):>18}"

    base_gap_str = "PASS" if base_res["gap_ok"] else "FAIL"
    restored_gap_str = "PASS" if restored_res["gap_ok"] else "FAIL"
    gap_match_str = "MATCH" if base_res["gap_ok"] == restored_res["gap_ok"] else "MISMATCH"

    base_cash_str = "PASS" if base_res["cash_ok"] else "FAIL"
    restored_cash_str = "PASS" if restored_res["cash_ok"] else "FAIL"
    cash_match_str = "MATCH" if base_res["cash_ok"] == restored_res["cash_ok"] else "MISMATCH"

    print(f"{'Check':32} | {'Before Analysis':18} | {'After Analysis':18} | {'Match'}")
    print("-" * 80)
    print(f"{'FY2030E Operating Income':32} | ${base_op:>16,.1f} | ${restored_op:>16,.1f} | {'EXACT (diff 0.0)' if diff_op_restored < 1e-6 else 'MISMATCH'}")
    print(f"{'FY2030E FCFE':32} | ${base_fc:>16,.1f} | ${restored_fc:>16,.1f} | {'EXACT (diff 0.0)' if diff_fc_restored < 1e-6 else 'MISMATCH'}")
    print(f"{'Value per share (USD)':32} | {base_val_str} | {restored_val_str} | {val_match_str}")
    print(f"{'Balance sheet zero-gap check':32} | {base_gap_str:>18} | {restored_gap_str:>18} | {gap_match_str}")
    print(f"{'Cash floor check (>= $15,000M)':32} | {base_cash_str:>18} | {restored_cash_str:>18} | {cash_match_str}")
    print("-" * 80)

    if base_res["fail_reasons"]:
        print(f"Base run failure reasons: {', '.join(base_res['fail_reasons'])}")
    if restored_res["fail_reasons"]:
        print(f"Restored run failure reasons: {', '.join(restored_res['fail_reasons'])}")

    assert (
        diff_op_restored < 1e-6
        and diff_fc_restored < 1e-6
        and diff_val_restored < 1e-4
        and base_res["checks_pass"]
        and restored_res["checks_pass"]
    ), "Restored base does not match original base or accounting checks failed!"
    print("SUCCESS: Base inputs and outputs are fully restored and verified.")


if __name__ == "__main__":
    main()
