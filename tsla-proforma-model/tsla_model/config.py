"""Project-wide constants. All currency figures are USD millions unless noted."""
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / "data"
SEED_FINANCIALS = DATA_DIR / "seed_filings.json"
SEED_MARKET = DATA_DIR / "seed_market.json"

TICKER = "TSLA"
CIK = 1318605

# SEC asks automated clients to identify themselves. Override with env var SEC_USER_AGENT.
DEFAULT_SEC_USER_AGENT = "TSLA-proforma-educational-model research@example.com"

# Forecast horizon: five fiscal years starting from the latest reported period (FY2025A base,
# FY2026E is anchored on H1 2026 actuals). 2031 is the Gordon-growth terminal (bridge) year.
BASE_YEAR = 2025
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]
TERMINAL_YEAR = 2031

SCENARIOS = ["base", "bull", "bear", "recession"]
SCENARIO_LABELS = {
    "base": "Base",
    "bull": "Bull",
    "bear": "Bear",
    "recession": "Recession / downside",
}

# Tolerance for integrity checks (USD millions).
CHECK_TOL = 0.5

DISCLAIMER = (
    "Educational and research use only. This model is not investment advice and is not a "
    "recommendation to buy, sell or hold TSLA or any other security. Forecasts are hypothetical, "
    "depend on judgment-based assumptions that are clearly labelled, and may be materially wrong. "
    "Historical data are taken from Tesla's SEC filings; verify all figures against the original "
    "documents before relying on them. Past performance does not predict future results."
)
