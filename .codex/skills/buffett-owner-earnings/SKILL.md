---
name: buffett-owner-earnings
description: Evaluate whether a company is a Buffett business, or prepare a Buffett memo on a ticker, using five years of SEC 10-K owner-earnings evidence.
---

Use this skill when the user asks whether a company is a Buffett business or asks for a Buffett memo on a ticker. This is an educational business-quality review, not investment advice.

## Evidence workflow

1. Run `python .codex/skills/buffett-owner-earnings/buffett_facts.py TICKER` from the project root. The script uses only SEC EDGAR Company Tickers and Company Facts data and saves `output/TICKER_facts.json`.
2. Use only the values and check results printed by the script. Do not add price data, market multiples, outside data sources, estimates, or invented figures.
3. Write `memos/TICKER_buffett_memo.md`. Use a short owner-oriented memo with one conclusion: **own the business**, **watch it**, or **pass**. Judge the business rather than the share price.
4. Discuss the three coded checks: ROE at least 15% in every available fiscal year, positive owner earnings in every available fiscal year, and owner-earnings growth from the first fiscal year to the last.
5. If any check is `not known`, say plainly that the memo cannot judge that part of the business because the necessary 10-K input was not found. Do not fill the gap with an estimate.

## Judgment boundary

Apply the owner mindset: favor durable cash generation and consistently strong returns on shareholder capital; treat a result as evidence, not proof of a durable competitive advantage. Keep the conclusion conditional on the five-year SEC record and explain what the owner would continue to watch.

