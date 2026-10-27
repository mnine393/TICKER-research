"""As-of information-set example using only Python's standard library."""

from collections import defaultdict
from datetime import date


# EDITABLE INPUTS -----------------------------------------------------------
DECISION_DATE = "2026-03-31"
TABLE = """Row | Ticker | Month measured | Published on | Index
1 | AAA | 2026-01 | 2026-02-10 | 101.0
2 | AAA | 2026-02 | 2026-03-10 | 104.0
3 | AAA | 2026-03 | 2026-04-10 | 109.0
4 | AAA | 2026-02 | 2026-03-25 | 103.0
5 | BBB | 2026-01 | 2026-02-10 | 98.0
6 | BBB | 2026-02 | 2026-03-10 | 97.0
7 | BBB | 2026-02 | 2026-03-10 | 97.0
8 | BBB | 2026-03 | 2026-04-10 | 92.0
9 | CCC | 2026-01 | 2026-02-10 | 110.0
10 | CCC | 2026-02 | 2026-04-05 | 112.0
11 | (blank) | 2026-02 | 2026-03-10 | 99.0
12 | CCC | 2026-02 | 2026-03-10 | 111.0
"""


def parse_table(text):
    """Turn the editable pipe-delimited table into typed row dictionaries."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    headers = [item.strip() for item in lines[0].split("|")]
    rows = []
    for line in lines[1:]:
        values = [item.strip() for item in line.split("|")]
        row = dict(zip(headers, values))
        row["Row"] = int(row["Row"])
        row["Published on"] = date.fromisoformat(row["Published on"])
        row["Index"] = float(row["Index"])
        rows.append(row)
    return rows


def remove_matching(rows, predicate):
    """Return kept rows and the original row numbers removed by a rule."""
    removed = [row["Row"] for row in rows if predicate(row)]
    kept = [row for row in rows if not predicate(row)]
    return kept, removed


def remove_exact_duplicates(rows):
    """Treat rows with identical data (apart from their row-number label) as duplicates."""
    seen = set()
    kept, removed = [], []
    for row in rows:
        key = (row["Ticker"], row["Month measured"], row["Published on"], row["Index"])
        if key in seen:
            removed.append(row["Row"])
        else:
            seen.add(key)
            kept.append(row)
    return kept, removed


def keep_latest_revisions(rows):
    """Keep the latest publication for each ticker-month pair."""
    latest = {}
    for row in rows:
        key = (row["Ticker"], row["Month measured"])
        if key not in latest or row["Published on"] > latest[key]["Published on"]:
            latest[key] = row
    kept = [row for row in rows if latest[(row["Ticker"], row["Month measured"])] is row]
    removed = [row["Row"] for row in rows if row not in kept]
    return kept, removed


def print_funnel(funnel):
    print("ROW FUNNEL")
    for rule, removed in funnel:
        numbers = ", ".join(map(str, removed)) if removed else "none"
        print(f"{rule}: removed {len(removed)} row(s): {numbers}")


def print_panel(rows, title):
    print(f"\n{title}")
    print("Row | Ticker | Month measured | Published on | Index")
    for row in sorted(rows, key=lambda item: (item["Ticker"], item["Month measured"])):
        print(
            f'{row["Row"]} | {row["Ticker"]} | {row["Month measured"]} | '
            f'{row["Published on"].isoformat()} | {row["Index"]:.1f}'
        )


def print_signals(rows, title):
    print(f"\n{title}")
    by_ticker = defaultdict(list)
    for row in rows:
        by_ticker[row["Ticker"]].append(row)

    for ticker in sorted(by_ticker):
        history = sorted(by_ticker[ticker], key=lambda item: item["Month measured"])
        if len(history) < 2:
            print(f"{ticker}: insufficient months for a signal")
            continue
        previous, latest = history[-2:]
        change = (latest["Index"] / previous["Index"] - 1) * 100
        print(f'{ticker}: {change:+.2f}% to {latest["Month measured"]}')


def main():
    decision_date = date.fromisoformat(DECISION_DATE)
    rows = parse_table(TABLE)

    rows, missing_ticker = remove_matching(
        rows, lambda row: not row["Ticker"] or row["Ticker"].lower() == "(blank)"
    )
    rows, duplicates = remove_exact_duplicates(rows)
    rows, published_late = remove_matching(
        rows, lambda row: row["Published on"] > decision_date
    )
    panel, superseded = keep_latest_revisions(rows)

    print(f"Decision date: {decision_date.isoformat()}")
    print_funnel([
        ("1. Missing ticker", missing_ticker),
        ("2. Exact duplicate", duplicates),
        ("3. Published after decision date", published_late),
        ("4. Superseded revision", superseded),
    ])
    print_panel(panel, "AS-OF PANEL")
    print_signals(panel, "AS-OF SIGNALS")

    # Comparison: apply only rules 1 and 2, then use every publication date.
    naive_rows = parse_table(TABLE)
    naive_rows, _ = remove_matching(
        naive_rows, lambda row: not row["Ticker"] or row["Ticker"].lower() == "(blank)"
    )
    naive_rows, _ = remove_exact_duplicates(naive_rows)
    naive_panel, _ = keep_latest_revisions(naive_rows)
    print_signals(naive_panel, "NAIVE SIGNALS (ignores publication date)")


if __name__ == "__main__":
    main()
