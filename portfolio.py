"""Compare allocation rules using editable return, volatility, and correlation inputs."""

from math import sqrt

import pandas as pd


# EDITABLE INPUTS -----------------------------------------------------------
# Returns and volatilities are written as decimals: 3.5% is 0.035.
SLEEVES = (
    ("Treasury bills", 0.035, 0.005),
    ("Treasury 10-year note", 0.043, 0.070),
    ("Investment-grade bond fund", 0.050, 0.060),
    ("Global equity index fund", 0.080, 0.160),
)

# The row and column order must match SLEEVES exactly.
CORRELATION = (
    (1.00, 0.10, 0.05, 0.00),
    (0.10, 1.00, 0.80, -0.10),
    (0.05, 0.80, 1.00, 0.25),
    (0.00, -0.10, 0.25, 1.00),
)

OBJECTIVE_RETURN = 0.065
RESERVE_ELIGIBLE_SLEEVES = ("Treasury bills", "Treasury 10-year note")

# Names used by the Streamlit learning demonstration.  These aliases deliberately
# point to the same inputs that the command-line example uses.
MERIDIAN_SLEEVES = SLEEVES
MERIDIAN_CORRELATION = CORRELATION
MERIDIAN_OBJECTIVE_RETURN = OBJECTIVE_RETURN
MERIDIAN_RESERVE_ELIGIBLE_SLEEVES = RESERVE_ELIGIBLE_SLEEVES


def sleeve_names(sleeves):
    """Return sleeve names in input order."""
    return tuple(sleeve[0] for sleeve in sleeves)


def expected_returns(sleeves):
    """Return expected returns in input order."""
    return tuple(sleeve[1] for sleeve in sleeves)


def volatilities(sleeves):
    """Return volatilities in input order."""
    return tuple(sleeve[2] for sleeve in sleeves)


def validate_correlation_table(correlation):
    """Raise ValueError unless the correlation table is square, bounded, and symmetric."""
    size = len(correlation)
    if any(len(row) != size for row in correlation):
        raise ValueError("Correlation table must be square: it needs the same number of rows and columns.")
    for row_index, row in enumerate(correlation):
        for column_index, value in enumerate(row):
            if value != correlation[column_index][row_index]:
                raise ValueError(
                    f"Correlation table is not symmetric at row {row_index + 1}, column {column_index + 1}."
                )
            if not -1.0 <= value <= 1.0:
                raise ValueError(
                    f"Correlation at row {row_index + 1}, column {column_index + 1} is {value}; "
                    "every correlation must be between -1 and 1."
                )


def build_covariance_matrix(correlation, volatility):
    """Convert correlations to covariances: correlation × volatility × volatility."""
    return tuple(
        tuple(correlation[i][j] * volatility[i] * volatility[j] for j in range(len(volatility)))
        for i in range(len(volatility))
    )


def benchmark_weights(number_of_sleeves):
    """Return the stated 40% IG-bond / 60% global-equity benchmark weights."""
    weights = [0.0] * number_of_sleeves
    weights[2] = 0.40
    weights[3] = 0.60
    return tuple(weights)


def equal_weight_weights(number_of_sleeves):
    """Allocate equally across every sleeve."""
    return tuple(1.0 / number_of_sleeves for _ in range(number_of_sleeves))


def inverse_volatility_weights(volatility):
    """Allocate in proportion to one divided by each sleeve's volatility."""
    if any(value <= 0 for value in volatility):
        raise ValueError("Every volatility must be greater than zero for inverse-volatility weights.")
    inverse_volatility = tuple(1.0 / value for value in volatility)
    total_inverse_volatility = sum(inverse_volatility)
    return tuple(value / total_inverse_volatility for value in inverse_volatility)


def portfolio_expected_return(weights, returns):
    """Calculate the weighted expected return."""
    return sum(weight * expected_return for weight, expected_return in zip(weights, returns))


def portfolio_variance(weights, covariance):
    """Calculate w'Σw, the portfolio variance."""
    return sum(
        weights[i] * covariance[i][j] * weights[j]
        for i in range(len(weights))
        for j in range(len(weights))
    )


def portfolio_volatility(weights, covariance):
    """Calculate the square root of portfolio variance."""
    return sqrt(portfolio_variance(weights, covariance))


def reserve_eligible_weight(weights, names, eligible_names):
    """Sum weights assigned to reserve-eligible sleeves."""
    return sum(weight for weight, name in zip(weights, names) if name in eligible_names)


def meets_objective(portfolio_return, objective_return):
    """Return whether expected return reaches the stated objective."""
    return portfolio_return >= objective_return


def search_long_only_mix(sleeves, correlation, objective_return, eligible_names,
                         minimum_reserve_weight, step=0.05):
    """Return the lowest-volatility feasible long-only mix on a fixed weight grid.

    Every candidate has non-negative weights that add to 100%.  With the default
    five-point grid, four sleeves produce 1,771 candidates.  ``None`` means no
    candidate met both the return objective and the reserve minimum.
    """
    if not 0 < step <= 1 or round(1 / step) * step != 1:
        raise ValueError("Step must divide 100% exactly, such as 0.05 for five-point steps.")
    if not 0 <= minimum_reserve_weight <= 1:
        raise ValueError("Minimum reserve weight must be between 0% and 100%.")
    if len(sleeves) == 0:
        raise ValueError("At least one sleeve is required.")
    if len(correlation) != len(sleeves):
        raise ValueError("Correlation table size must match the number of sleeves.")
    validate_correlation_table(correlation)

    names = sleeve_names(sleeves)
    returns = expected_returns(sleeves)
    covariance = build_covariance_matrix(correlation, volatilities(sleeves))
    units = round(1 / step)
    best = None

    def consider(prefix, remaining, positions_left):
        nonlocal best
        if positions_left == 1:
            weight_units = prefix + (remaining,)
            weights = tuple(unit * step for unit in weight_units)
            candidate_return = portfolio_expected_return(weights, returns)
            candidate_reserve = reserve_eligible_weight(weights, names, eligible_names)
            if candidate_return + 1e-12 < objective_return or candidate_reserve + 1e-12 < minimum_reserve_weight:
                return
            candidate_volatility = portfolio_volatility(weights, covariance)
            candidate = {
                "weights": weights,
                "expected_return": candidate_return,
                "volatility": candidate_volatility,
                "reserve_eligible_weight": candidate_reserve,
            }
            if best is None or candidate_volatility < best["volatility"] - 1e-12:
                best = candidate
            return
        for weight_units in range(remaining + 1):
            consider(prefix + (weight_units,), remaining - weight_units, positions_left - 1)

    consider((), units, len(sleeves))
    return best


def estimate_from_monthly_prices(prices, last_36_months=False):
    """Estimate annual inputs from a date-first, oldest-first monthly-price table.

    Monthly simple returns are calculated from adjacent prices.  Expected returns
    are the monthly arithmetic means times 12; volatility is sample monthly
    standard deviation times square root of 12; correlations use those returns.
    """
    table = prices.copy()
    if table.shape[1] < 2:
        raise ValueError("The CSV needs a date column followed by at least one ticker column.")
    date_column = table.columns[0]
    parsed_dates = pd.to_datetime(table[date_column], errors="coerce")
    if parsed_dates.isna().any() or not parsed_dates.is_monotonic_increasing or parsed_dates.duplicated().any():
        raise ValueError("The first column must contain unique dates in oldest-first order.")
    price_columns = list(table.columns[1:])
    numeric_prices = table[price_columns].apply(pd.to_numeric, errors="coerce")
    if numeric_prices.isna().any().any() or (numeric_prices <= 0).any().any():
        raise ValueError("Each ticker price must be a positive number with no missing values.")
    monthly_returns = numeric_prices.pct_change(fill_method=None).iloc[1:]
    if last_36_months:
        monthly_returns = monthly_returns.tail(36)
    if len(monthly_returns) < 2:
        raise ValueError("At least three monthly price rows are required to estimate volatility and correlation.")
    return {
        "names": tuple(price_columns),
        "returns": tuple((monthly_returns.mean() * 12).tolist()),
        "volatilities": tuple((monthly_returns.std(ddof=1) * sqrt(12)).tolist()),
        "correlation": tuple(tuple(row) for row in monthly_returns.corr().to_numpy()),
        "monthly_returns": monthly_returns,
    }


def estimate_from_csv(csv_source, last_36_months=False):
    """Read a monthly-price CSV and return annualized estimates for the app or a script."""
    return estimate_from_monthly_prices(pd.read_csv(csv_source), last_36_months=last_36_months)


# Clear names for callers that prefer a verb describing the result.
find_lowest_volatility_mix = search_long_only_mix
search_long_only_mixes = search_long_only_mix


def define_portfolios(volatility):
    """Build all requested portfolio weight sets from the supplied inputs."""
    count = len(volatility)
    return (
        ("Benchmark", benchmark_weights(count)),
        ("Equal weight", equal_weight_weights(count)),
        ("Inverse volatility", inverse_volatility_weights(volatility)),
    )


def format_weights(names, weights):
    """Format sleeve weights as percentages to one decimal place."""
    return ", ".join(f"{name}: {weight:.1%}" for name, weight in zip(names, weights))


def print_portfolio(name, weights, names, returns, covariance, eligible_names, objective_return):
    """Print all requested results for one portfolio."""
    expected_return = portfolio_expected_return(weights, returns)
    volatility = portfolio_volatility(weights, covariance)
    reserve_weight = reserve_eligible_weight(weights, names, eligible_names)
    objective_status = "Yes" if meets_objective(expected_return, objective_return) else "No"
    print(f"\n{name}")
    print(f"  Weights: {format_weights(names, weights)}")
    print(f"  Expected return: {expected_return:.2%}")
    print(f"  Volatility: {volatility:.2%}")
    print(f"  Reserve-eligible weight: {reserve_weight:.1%}")
    print(f"  Meets {objective_return:.1%} objective: {objective_status}")


def main():
    """Validate inputs, calculate the covariance matrix, and report all portfolios."""
    names = sleeve_names(SLEEVES)
    returns = expected_returns(SLEEVES)
    volatility = volatilities(SLEEVES)
    validate_correlation_table(CORRELATION)
    if len(CORRELATION) != len(SLEEVES):
        raise ValueError("Correlation table size must match the number of sleeves.")
    covariance = build_covariance_matrix(CORRELATION, volatility)
    for name, weights in define_portfolios(volatility):
        print_portfolio(name, weights, names, returns, covariance, RESERVE_ELIGIBLE_SLEEVES, OBJECTIVE_RETURN)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Input error: {error}")
