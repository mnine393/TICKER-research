"""Lab 06: Five-year FCFF DCF model with sensitivity grid and reverse DCF.

Uses only Python's standard library. All monetary inputs and outputs are in USD
millions, except per-share values, which are in USD per share.
Edit only the input block below for new cases.
"""

import sys

# -----------------------------------------------------------------------------
# Input Block (Tesla, Inc. / TSLA — FY2025 Form 10-K reported facts + placeholders)
# -----------------------------------------------------------------------------
# Operating cash flow (14,747) + after-tax interest (292 * (1 - 0.2696) = 213.27) - capex (8,527) = 6,433.27
STARTING_FCFF = 6433.27  # USD millions; corrected starting FCFF
GROWTH_RATES = [0.08, 0.06, 0.05, 0.04, 0.03]  # Years 1 through 5; placeholder — unresolved forecast
WACC = 0.10  # placeholder — unresolved cost of capital kept at training value
TERMINAL_GROWTH = 0.03  # placeholder — unresolved terminal growth kept at training value
NON_OPERATING_CASH = 44059.0  # USD millions; cash ($16,513M) + short-term investments ($27,546M)
DEBT = 8376.0  # USD millions; net carrying value of debt and finance leases ($8,376M)
DILUTED_SHARES = 3528.0  # Millions of shares; FY2025 diluted weighted-average

# Sensitivity grid parameters (two editable lists)
GRID_WACC_VALUES = [0.09, 0.10, 0.11]
GRID_TERMINAL_GROWTH_VALUES = [0.02, 0.03, 0.04]

# Reverse DCF parameters
REVERSE_DCF_TARGET_PRICE = 356.09  # USD per share (TSLA close as of September 1, 2026; 30.00 for training case)
REVERSE_DCF_LOWER_BOUND = -0.05  # -5 percentage points (-0.05)
REVERSE_DCF_UPPER_BOUND = 0.10  # +10 percentage points (+0.10)
#   NON_OPERATING_CASH = 44059.0
#   DEBT = 8376.0
#   DILUTED_SHARES = 3528.0
#   REVERSE_DCF_TARGET_PRICE = 356.09)


def calculate_dcf(fcff0, growths, wacc, g, cash, debt, shares):
    """Compute 5-year FCFF DCF and return key metrics, or None if invalid."""
    if g >= wacc or shares <= 0 or fcff0 <= 0:
        return None
    for r in growths:
        if r <= -1.0:
            return None

    fcff_by_year = []
    curr = fcff0
    for r in growths:
        curr *= 1 + r
        fcff_by_year.append(curr)

    pv_explicit = sum(f / ((1 + wacc) ** i) for i, f in enumerate(fcff_by_year, 1))
    tv5 = fcff_by_year[-1] * (1 + g) / (wacc - g)
    pv_tv = tv5 / ((1 + wacc) ** len(growths))
    ev = pv_explicit + pv_tv
    eq = ev + cash - debt
    val_per_share = eq / shares
    tv_share = pv_tv / ev

    return {
        "fcff_by_year": fcff_by_year,
        "pv_explicit": pv_explicit,
        "tv5": tv5,
        "pv_tv": pv_tv,
        "ev": ev,
        "eq": eq,
        "val_per_share": val_per_share,
        "tv_share": tv_share,
    }


def print_sensitivity_grid(fcff0, growths, cash, debt, shares, wacc_list, g_list):
    """Print sensitivity grid table of value per diluted share."""
    print("\n--- SENSITIVITY GRID: VALUE PER DILUTED SHARE ($) ---")
    header_col = "WACC \\ g"
    col_headers = [f"{g * 100:.1f}%".rjust(9) for g in g_list]
    print(f"{header_col:<12} | " + " | ".join(col_headers))
    print("-" * 12 + "-+-" + "-+-".join(["-" * 9 for _ in g_list]))

    for w in wacc_list:
        row_vals = []
        for g in g_list:
            res = calculate_dcf(fcff0, growths, w, g, cash, debt, shares)
            if res is None:
                row_vals.append("invalid".rjust(9))
            else:
                row_vals.append(f"{res['val_per_share']:9.2f}")
        print(f"{w * 100:5.1f}%{'':<6} | " + " | ".join(row_vals))


def run_reverse_dcf(
    fcff0,
    base_growths,
    wacc,
    g,
    cash,
    debt,
    shares,
    target_price,
    lower_bound,
    upper_bound,
):
    """Solve for uniform growth shift by bisection holding all else fixed."""
    print("\n--- REVERSE DCF ---")
    print(f"Target share price: ${target_price:.2f}")
    print("Held fixed:")
    print(f"  - Starting FCFF: {fcff0:.2f} USD million")
    print(f"  - Baseline growth rates: {[round(r, 4) for r in base_growths]}")
    print(f"  - WACC: {wacc * 100:.2f}%")
    print(f"  - Terminal growth: {g * 100:.2f}%")
    print(f"  - Non-operating cash: {cash:.2f} USD million")
    print(f"  - Debt: {debt:.2f} USD million")
    print(f"  - Diluted shares: {shares:.2f} million")
    print(
        f"Search bracket (uniform shift): [{lower_bound * 100:+.2f}%, {upper_bound * 100:+.2f}%]"
    )

    # Refuse any bracket that pushes an annual growth rate to -100% or below
    for i, r in enumerate(base_growths, 1):
        if r + lower_bound <= -1.0:
            print(
                f"Error: lower bound shift pushes Year {i} growth to -100% or below. Search refused."
            )
            return

    res_lo = calculate_dcf(
        fcff0, [r + lower_bound for r in base_growths], wacc, g, cash, debt, shares
    )
    res_hi = calculate_dcf(
        fcff0, [r + upper_bound for r in base_growths], wacc, g, cash, debt, shares
    )

    if res_lo is None or res_hi is None:
        print("Error: model is invalid at search bounds.")
        return

    val_lo = res_lo["val_per_share"]
    val_hi = res_hi["val_per_share"]

    if target_price < val_lo or target_price > val_hi:
        print(
            f"No solution in that bracket: target price ${target_price:.2f} "
            f"cannot be reached inside [{lower_bound * 100:+.2f}%, {upper_bound * 100:+.2f}%]. "
            f"(Bracket yields ${val_lo:.2f} to ${val_hi:.2f})."
        )
        return

    lo = lower_bound
    hi = upper_bound
    for _ in range(100):
        mid = (lo + hi) / 2
        shifted = [r + mid for r in base_growths]
        res_mid = calculate_dcf(fcff0, shifted, wacc, g, cash, debt, shares)
        if res_mid["val_per_share"] < target_price:
            lo = mid
        else:
            hi = mid

    solved_shift = mid
    solved_growths = [r + solved_shift for r in base_growths]
    print(
        f"Solved uniform growth shift: {solved_shift * 100:+.2f} percentage points ({solved_shift:+.4f})"
    )
    print(
        f"Implied growth rates: {[f'{r * 100:.2f}%' for r in solved_growths]}"
    )


def main():
    if len(GROWTH_RATES) != 5:
        sys.exit("Error: enter exactly five annual growth rates.")

    if TERMINAL_GROWTH >= WACC:
        sys.exit(
            "Error: terminal growth must be strictly less than WACC "
            "for the Gordon-growth terminal value formula."
        )

    if DILUTED_SHARES <= 0:
        sys.exit("Error: diluted shares must be greater than zero.")

    # 1. Base DCF calculation (exactly twelve lines)
    base_res = calculate_dcf(
        STARTING_FCFF,
        GROWTH_RATES,
        WACC,
        TERMINAL_GROWTH,
        NON_OPERATING_CASH,
        DEBT,
        DILUTED_SHARES,
    )

    if base_res is None:
        sys.exit("Error: base case DCF parameters are invalid.")

    for year, year_fcff in enumerate(base_res["fcff_by_year"], start=1):
        print(f"FCFF Year {year}: {year_fcff:.4f}")
    print(f"Present value of the explicit FCFF: {base_res['pv_explicit']:.4f}")
    print(f"Terminal value at Year 5: {base_res['tv5']:.4f}")
    print(f"Present value of the terminal value: {base_res['pv_tv']:.4f}")
    print(f"Enterprise value: {base_res['ev']:.4f}")
    print(f"Equity value: {base_res['eq']:.4f}")
    print(f"Value per diluted share: {base_res['val_per_share']:.4f}")
    print(
        "Present value of the terminal value as a share of enterprise value: "
        f"{base_res['tv_share']:.4f}"
    )

    # 2. Sensitivity grid
    print_sensitivity_grid(
        STARTING_FCFF,
        GROWTH_RATES,
        NON_OPERATING_CASH,
        DEBT,
        DILUTED_SHARES,
        GRID_WACC_VALUES,
        GRID_TERMINAL_GROWTH_VALUES,
    )

    # 3. Reverse DCF
    run_reverse_dcf(
        STARTING_FCFF,
        GROWTH_RATES,
        WACC,
        TERMINAL_GROWTH,
        NON_OPERATING_CASH,
        DEBT,
        DILUTED_SHARES,
        REVERSE_DCF_TARGET_PRICE,
        REVERSE_DCF_LOWER_BOUND,
        REVERSE_DCF_UPPER_BOUND,
    )


if __name__ == "__main__":
    main()
