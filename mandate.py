"""Check Meridian Foundation Reserve candidate portfolios."""

# Editable inputs: holding, issuer, days to redeem, reserve eligible.
HOLDINGS = {
    "Cash": ("none", 0, True),
    "Treasury bills": ("U.S. Treasury", 1, True),
    "Treasury 10-year note": ("U.S. Treasury", 1, True),
    "Global equity index fund": ("diversified fund", 2, False),
    "Investment-grade bond fund": ("diversified fund", 3, False),
    "Private real estate fund": ("diversified fund", 90, False),
    "Acme Corp bonds": ("Acme Corp", 4, False),
    "Acme Corp stock": ("Acme Corp", 1, False),
}

CANDIDATES = {
    "A": {"Cash": 2, "Treasury bills": 2, "Treasury 10-year note": 10,
          "Global equity index fund": 60, "Investment-grade bond fund": 26,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0},
    "B": {"Cash": 1, "Treasury bills": 0, "Treasury 10-year note": 0,
          "Global equity index fund": 55, "Investment-grade bond fund": 20,
          "Private real estate fund": 15, "Acme Corp bonds": 5, "Acme Corp stock": 4},
    "C": {"Cash": 1, "Treasury bills": 1, "Treasury 10-year note": 0,
          "Global equity index fund": 70, "Investment-grade bond fund": 20,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 8},
    # AI-proposed D: a Treasury-only reserve exposes the missing S10 optimization choice.
    "D": {"Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 100,
          "Global equity index fund": 0, "Investment-grade bond fund": 0,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0},
    "E": {"Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 0,
          "Global equity index fund": 60, "Investment-grade bond fund": 40,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0},
}

RESERVE_SIZE = 100  # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # business days
MINIMUM_LIQUID_SHARE = 90  # percent
ISSUER_LIMIT = 8  # percent
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}
TOLERANCE = 1e-9


def status(passes):
    """Return the required label for a Boolean result."""
    return "pass" if passes else "FAIL"


def check_candidate(name, weights, reserve_minimum):
    """Measure one portfolio and print its checkable mandate rules."""
    total = sum(weights.values())
    lowest = min(weights.values())
    reserve = sum(weights[holding] for holding, (_, _, eligible) in HOLDINGS.items()
                  if eligible)
    liquid = sum(weights[holding] for holding, (_, days, _) in HOLDINGS.items()
                 if days <= LIQUIDITY_WINDOW)

    # Add securities of each non-exempt company before finding the largest company.
    company_weights = {}
    for holding, (issuer, _, _) in HOLDINGS.items():
        if issuer not in EXEMPT_ISSUERS:
            company_weights[issuer] = company_weights.get(issuer, 0) + weights[holding]
    largest_company = max(company_weights.values(), default=0)

    checks = [
        ("Weights sum to 100", total, abs(total - 100) <= TOLERANCE),
        ("Long-only (lowest weight)", lowest, lowest >= -TOLERANCE),
        ("Reserve-eligible", reserve, reserve >= reserve_minimum - TOLERANCE),
        (f"Redeemable in {LIQUIDITY_WINDOW} days", liquid,
         liquid >= MINIMUM_LIQUID_SHARE - TOLERANCE),
        ("Largest single company", largest_company,
         largest_company <= ISSUER_LIMIT + TOLERANCE),
    ]

    print(f"{name}:")
    for label, value, passes in checks:
        print(f"{label}: {value:.1f} {status(passes)}")
    print("Calendar-year loss: requires CIO clarification")
    failures = sum(not passes for _, _, passes in checks)
    print("passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)")


def main():
    reserve_minimum = QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100
    print(f"Reserve minimum: {reserve_minimum:.1f}%")
    for name, weights in CANDIDATES.items():
        check_candidate(name, weights, reserve_minimum)


if __name__ == "__main__":
    main()
