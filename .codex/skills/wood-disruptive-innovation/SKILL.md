---
name: wood-disruptive-innovation
description: Evaluate a company's revenue growth and research-and-development intensity from a saved SEC-only five-year 10-K fact record. Use when the user wants a narrow disruptive-innovation screen, not a price target or investment recommendation.
---

Use this skill only after `buffett-owner-earnings/buffett_facts.py` has created `output/TICKER_facts.json`.

1. Run `python .codex/skills/wood-disruptive-innovation/wood_innovation.py TICKER` from the project root.
2. The script reads only the saved fact record; it does not download data or estimate missing values.
3. The checks are: revenue compound annual growth of at least 15% from the first fiscal year to the last, revenue growth in every fiscal year, and latest research and development of at least 10% of revenue.
4. After reviewing the printed output, write `memos/TICKER_wood_memo.md` as a short Cathie Wood-style memo. Use only numbers the script printed; treat a `not known` check as not known, never as a pass or fail. Do not include price data.
5. This is an educational, incomplete innovation screen. It does not establish technology adoption, market size, or a full disruptive-innovation thesis and is not investment advice.
