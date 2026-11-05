---
name: burry-cash-and-balance-sheet
description: Evaluate a company's cash conversion and latest balance-sheet leverage from a saved SEC-only five-year 10-K fact record. Use when the user wants a downside-focused cash-flow and liabilities screen, not a price target or investment recommendation.
---

Use this skill only after `buffett-owner-earnings/buffett_facts.py` has created `output/TICKER_facts.json`.

1. Run `python .codex/skills/burry-cash-and-balance-sheet/burry_cash_balance.py TICKER` from the project root.
2. The script reads only the saved fact record; it does not download data or estimate missing values.
3. The checks are: operating cash flow at least net income in every available fiscal year, and latest liabilities no more than twice year-end equity.
4. After reviewing the printed output, write `memos/TICKER_burry_memo.md` as a short Burry-style memo. Use only numbers the script printed; treat a `not known` check as not known, never as a pass or fail.
5. This is an educational, incomplete downside screen. It does not assess price, off-balance-sheet obligations, or the full investor philosophy and is not investment advice.
