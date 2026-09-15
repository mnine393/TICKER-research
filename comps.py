"""Lab 07: Comparable-Company P/E Valuation Engine.

Uses only Python's standard library — no external packages required.
Calculates peer P/E multiples, peer median P/E, peer-implied target prices,
and leave-one-out peer sensitivity with full unrounded floating precision.
"""

import statistics

# -----------------------------------------------------------------------------
# Input Block (edit target and candidate peer inputs by hand)
# -----------------------------------------------------------------------------
TARGET = {
    "ticker": "ABG",
    "name": "Asbury Automotive Group",
    "price": 243.03,  # USD per share as of December 31, 2024
    "diluted_eps": 21.50,  # USD per share, FY2024 total GAAP diluted EPS
}

PEERS = [
    {
        "ticker": "AN",
        "name": "AutoNation",
        "price": 169.84,  # USD per share as of December 31, 2024
        "diluted_eps": 16.92,  # USD per share, FY2024 total GAAP diluted EPS
    },
    {
        "ticker": "GPI",
        "name": "Group 1 Automotive",
        "price": 421.48,  # USD per share as of December 31, 2024
        "diluted_eps": 36.81,  # USD per share, FY2024 total GAAP diluted EPS
    },
]


def run_comparables_analysis(target, candidate_peers):
    """Execute P/E comparison, implied valuation, and leave-one-out sensitivity."""
    print("=" * 68)
    print("LAB 07: COMPARABLE-COMPANY P/E VALUATION ENGINE")
    print("=" * 68)

    # Dynamic target name/ticker handling
    target_name = target.get("name")
    target_ticker = target.get("ticker", "").strip().upper()
    target_label = target_name if target_name else (target_ticker if target_ticker else "Target")

    if target_name and target_ticker:
        target_header = f"{target_name} ({target_ticker})"
    else:
        target_header = target_label

    # Safe validation of target price and diluted EPS before formatting
    t_price = target.get("price")
    t_eps = target.get("diluted_eps")

    if isinstance(t_price, (int, float)) and t_price > 0:
        price_display = f"${t_price:.2f}"
    else:
        price_display = "not meaningful"

    if isinstance(t_eps, (int, float)) and t_eps > 0:
        eps_display = f"${t_eps:.2f}"
        valid_target_eps = True
    else:
        eps_display = "not meaningful"
        valid_target_eps = False

    print(f"Target: {target_header}")
    print(f"December 31, 2024 Closing Price: {price_display}")
    print(f"FY2024 Total GAAP Diluted EPS:   {eps_display}")
    print("-" * 68)

    # 1. Deduplicate peers and exclude target
    seen_tickers = set()
    cleaned_peers = []

    for peer in candidate_peers:
        ticker = peer.get("ticker", "").strip().upper()
        if not ticker:
            continue
        if target_ticker and ticker == target_ticker:
            print(f"[Excluded] Peer matches target ticker '{ticker}'.")
            continue
        if ticker in seen_tickers:
            print(f"[Deduplicated] Duplicate peer '{ticker}' skipped.")
            continue
        seen_tickers.add(ticker)
        cleaned_peers.append(peer)

    # 2. Compute peer P/E multiples
    valid_peers = []
    print("\nPeer Multiples (Price / Diluted EPS):")
    for peer in cleaned_peers:
        p_name = peer.get("name", "Peer")
        p_ticker = peer.get("ticker", "PEER").strip().upper()
        price = peer.get("price")
        eps = peer.get("diluted_eps")

        if (
            not isinstance(price, (int, float))
            or not isinstance(eps, (int, float))
            or price <= 0
            or eps <= 0
        ):
            print(f"  {p_name} ({p_ticker}): not meaningful (Price: {price}, EPS: {eps})")
            continue

        pe_multiple = price / eps
        peer_entry = dict(peer)
        peer_entry["pe"] = pe_multiple
        valid_peers.append(peer_entry)
        print(
            f"  {p_name} ({p_ticker}) P/E: {pe_multiple:.6f}x "
            f"(Price: ${price:.2f}, EPS: ${eps:.2f})"
        )

    num_valid = len(valid_peers)
    print(f"\nUsable peers: {num_valid}")

    if num_valid == 0:
        print("Result: no usable peers.")
        return

    # 3. Calculate median peer multiple and target implied values
    pe_list = [p["pe"] for p in valid_peers]
    median_pe = statistics.median(pe_list)
    print(f"Peer median P/E: {median_pe:.6f}x")

    if not valid_target_eps:
        print(f"\nResult: not meaningful ({target_label} diluted EPS is {eps_display}).")
        if num_valid == 1:
            print(f"{target_label} reference estimate: not meaningful")
        else:
            print(f"{target_label} peer-implied range: not meaningful")
            print(f"{target_label} at peer median:     not meaningful")
        return

    full_median_implied_price = median_pe * t_eps

    if num_valid == 1:
        print(
            f"{target_label} reference estimate: ${full_median_implied_price:.2f} "
            f"(one valid peer; no range)"
        )
    else:
        min_pe = min(pe_list)
        max_pe = max(pe_list)
        min_implied_price = min_pe * t_eps
        max_implied_price = max_pe * t_eps
        print(f"{target_label} peer-implied range: ${min_implied_price:.2f} - ${max_implied_price:.2f}")
        print(f"{target_label} at peer median:     ${full_median_implied_price:.2f}")

    # 4. Leave-one-out sensitivity analysis
    print("\nLeave-One-Peer-Out Sensitivity:")
    for excluded_peer in valid_peers:
        excluded_ticker = excluded_peer["ticker"]
        remaining = [p for p in valid_peers if p["ticker"] != excluded_ticker]

        if not remaining:
            print(f"  Remove {excluded_ticker}: no estimate (no remaining peers)")
            continue

        rem_pe_list = [p["pe"] for p in remaining]
        rem_median_pe = statistics.median(rem_pe_list)
        rem_implied_price = rem_median_pe * t_eps
        dollar_change = rem_implied_price - full_median_implied_price

        if len(remaining) == 1:
            label = f"remaining {remaining[0]['ticker']} estimate"
        else:
            label = f"remaining median ({len(remaining)} peers)"

        print(
            f"  Remove {excluded_ticker}: {label} = ${rem_implied_price:.2f} "
            f"(change from full-peer estimate: {dollar_change:+.2f})"
        )


def main():
    run_comparables_analysis(TARGET, PEERS)


if __name__ == "__main__":
    main()
