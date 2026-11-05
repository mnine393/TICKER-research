---
name: graham-defensive-investor
description: Evaluate a company's simple Graham-style defensive financial condition from a saved SEC-only five-year 10-K fact record. Use when the user wants a conservative balance-sheet and earnings-record screen, not a price target or investment recommendation.
---

Use this skill only after `buffett-owner-earnings/buffett_facts.py` has created `output/TICKER_facts.json`.

1. Run `python .codex/skills/graham-defensive-investor/graham_defensive.py TICKER` from the project root.
2. The script reads only the saved fact record; it does not download data or estimate missing values.
3. The checks are: latest current ratio at least 2.0, positive net income in every available fiscal year, and net-income growth from the first fiscal year to the last.
4. After reviewing the printed output, write `memos/TICKER_graham_memo.md` as a short Graham-style memo. Use only numbers the script printed; treat a `not known` check as not known, never as a pass or fail.
5. This is an educational, incomplete defensive screen. It does not assess price, dividends, or the full Graham framework and is not investment advice.
