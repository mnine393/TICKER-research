# Lab 18: Buffett owner earnings skill

## Question

Can an investor's philosophy become a skill your AI runs the same way every time — every number computed by code from the 10-K, the judgment the model's?

## What I built

The reusable instruction file is [buffett-owner-earnings skill](.codex/skills/buffett-owner-earnings/SKILL.md). It tells the model to use the fact-gathering program first and then write a short owner memo using only the printed results.

The fact-gathering program is [buffett_facts.py](.codex/skills/buffett-owner-earnings/buffett_facts.py). It retrieves annual filing facts from the United States Securities and Exchange Commission, keeps only annual reports, calculates return on equity and owner earnings, and saves the results.

The viewer is [buffett_app.py](tsla-proforma-model/buffett_app.py). It displays the results, the source labels, the checks, and any owner memo. It also flags a number in a memo when that number was not printed by the fact-gathering program.

The owner memos are [Costco memo](memos/COST_buffett_memo.md) and [JPMorgan Chase memo](memos/JPM_buffett_memo.md).

From the FIN 439 folder, run the fact-gathering program with:

```powershell
python .codex\skills\buffett-owner-earnings\buffett_facts.py COST
```

Then run the viewer with:

```powershell
cd tsla-proforma-model
streamlit run buffett_app.py
```

## Costco known answer

All dollar amounts are in millions. Every value below matches the known answer saved in `output/COST_facts.json`.

| Fiscal year ended | Revenue | Net income | Operating cash flow | Capital spending | Equity | Return on equity | Owner earnings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2022-08-28 | $226,954.0 | $5,844.0 | $7,392.0 | $3,891.0 | $20,642.0 | 28.3% | $3,501.0 |
| 2023-09-03 | $242,290.0 | $6,292.0 | $11,068.0 | $4,323.0 | $25,058.0 | 25.1% | $6,745.0 |
| 2024-09-01 | $254,453.0 | $7,367.0 | $11,339.0 | $4,710.0 | $23,622.0 | 31.2% | $6,629.0 |
| 2025-08-31 | $275,235.0 | $8,099.0 | $13,335.0 | $5,498.0 | $29,164.0 | 27.8% | $7,837.0 |
| 2026-08-30 | $303,154.0 | $9,226.0 | $15,817.0 | $6,435.0 | $35,803.0 | 25.8% | $9,382.0 |

The three checks all pass:

- Return on equity was at least 15 percent in every fiscal year.
- Owner earnings were positive in every fiscal year.
- Owner earnings grew from the first fiscal year to the last fiscal year.

## Probes

- For JPMorgan Chase, capital spending and owner earnings are `not found` in every fiscal year in the saved fact record. Both owner-earnings checks are `not known`. The return-on-equity check fails. The memo says that it cannot judge owner earnings because the needed input was not found.
- Typing 40.0 percent into the Costco memo was flagged by the viewer because the fact-gathering program did not print that number.
- A fresh browser chat with no skill produced the same year-end return on equity, but used third-party websites, showed no source labels, mixed return on equity calculated with average equity, and mixed in share price. This skill keeps the calculation source and the business judgment separate from share price.

## Bugs found and fixed

- The fact-gathering program requested compressed data but did not unzip it. Removing that request fixed the unreadable response.
- The address for the company facts was missing `CIK`. Adding `CIK` before the company identification number fixed the missing-page response.

## My decision


## Learn


## Reflect

