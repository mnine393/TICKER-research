# Lab 19: Three-investor panel

## Question

When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?

The professor replaced Graham with Cathie Wood in this panel.

## Project links and command

The three investor instructions and their check programs are:

- [Buffett owner-earnings instructions](.codex/skills/buffett-owner-earnings/SKILL.md) and [fact program](.codex/skills/buffett-owner-earnings/buffett_facts.py)
- [Wood disruptive-innovation instructions](.codex/skills/wood-disruptive-innovation/SKILL.md) and [check program](.codex/skills/wood-disruptive-innovation/wood_innovation.py)
- [Burry cash-and-balance-sheet instructions](.codex/skills/burry-cash-and-balance-sheet/SKILL.md) and [check program](.codex/skills/burry-cash-and-balance-sheet/burry_cash_balance.py)

The panel viewer is [buffett_app.py](tsla-proforma-model/buffett_app.py). Run it from the FIN 439 folder:

```powershell
python -m streamlit run tsla-proforma-model/buffett_app.py
```

The six memos are:

- Costco: [Buffett](memos/COST_buffett_memo.md), [Wood](memos/COST_wood_memo.md), and [Burry](memos/COST_burry_memo.md)
- NVIDIA: [Buffett](memos/NVDA_buffett_memo.md), [Wood](memos/NVDA_wood_memo.md), and [Burry](memos/NVDA_burry_memo.md)

## Known answer: Costco

All of the Costco panel results match the saved five-year record.

| Measure | Five yearly results |
|---|---|
| Current ratio | 1.02, 1.07, 0.97, 1.03, 1.06 |
| Liabilities divided by equity | 2.11, 1.75, 1.96, 1.64, 1.49 |

Current ratio is shown for the five-year record but is no longer used by a panel check.

| Investor | Check one | Check two | Check three | Score |
|---|---|---|---|---|
| Buffett | Return on equity: pass | Owner earnings positive: pass | Owner earnings grew: pass | 3 of 3 |
| Wood | Revenue growth of 7.5% a year versus 15% minimum: fail | Revenue grew every year: pass | Research and development not found: not known | 1 of 3 |
| Burry | Operating cash flow at least net income: pass | Latest liabilities divided by equity: pass | Not used | 2 of 2 |

The viewer found no unprinted numbers in any Costco memo.

## Threshold probe

Lowering Wood's revenue-growth minimum to 7% made Costco pass the growth check, for a score of 2 of 3. Lowering the research-and-development minimum to 8% made NVIDIA pass all three checks, for a score of 3 of 3. I keep the 15% and 10% thresholds.

## My company: NVIDIA

NVIDIA, ticker NVDA, was the largest holding in the Vanguard Total World Stock exchange-traded fund, ticker VT, at 4.54% as of 30 September 2026. [Stock Analysis holdings page](https://stockanalysis.com/etf/vt/holdings/)

| Investor | Result |
|---|---|
| Buffett | 3 of 3 |
| Wood | 2 of 3; revenue growth of 68.3% a year: pass; revenue grew every year: pass; research and development of 8.6% of revenue versus 10%: fail |
| Burry | 1 of 2; operating cash flow was below net income in four of five years, while liabilities divided by equity of 0.31 passed |

Costco's research and development was marked "not found," so its Wood research-and-development check was "not known." NVIDIA had no gaps: no value was marked "not found" or "not known."

## Bugs fixed

The Burry program had no main block, so running it printed nothing. It now has a main block. The Graham and Burry programs also wrote memos in code (Graham was later replaced by Wood). They now only calculate and print checks; the artificial intelligence writes the memos after reviewing the printed output. The Wood label in the panel success message still said Graham; that label was fixed.

## Bull and bear

**Bear (my partner):** Burry fails NVIDIA because its operating cash flow was lower than its net income in four of the five years. Last year it brought in $102,718 million of cash on $120,067 million of profit, so some of that profit hasn't turned into cash yet, and that could turn into write-offs if demand slows down.

**Bull (me):** Buffett gives NVIDIA 3 out of 3, and Wood passes it on growth: revenue grew 68.3% a year and went up every year. ROE never went below 19.8%, owner earnings went from $8,132 million to $96,676 million, and Burry's own debt check passes at 0.31, so the cash gap comes from growing really fast, not from a weak balance sheet.

## My decision

Only with a condition. I would let the panel screen companies for Project 2 as long as any company that fails a check gets reviewed by hand before I add it, and I set the thresholds before I look at the results. Lowering Wood's research and development minimum to 8% flipped NVIDIA from a fail to a pass, so the threshold can change the answer.

## Learn

A panel of AI agents is a few AI "investors" that each follow their own rules and read the same facts. Each skill has its own checks and its own way of thinking, so they disagree because they care about different things, not because the numbers are different. Buffett looks at returns and owner earnings, Wood looks at fast growth and spending on innovation, and Burry looks at whether the profits are actually turning into cash. Having them side by side shows where a company is strong and where it might have a weak spot.

## Reflect

On NVIDIA the panel agreed that the business is strong and growing: Buffett passed it on every check, Wood passed it on both growth checks, and Burry's debt check passed too. It split in two places. Wood failed it because research and development was only 8.6% of revenue, since revenue grew so fast that R&D became a smaller share, and Burry failed it because operating cash flow was below net income in four of the five years.

The threshold probe shows that a screen's verdict is only as good as the threshold someone picked. Costco failed Wood's growth check at 15% and passed it at 7% with the exact same numbers, and NVIDIA went from 2 of 3 to 3 of 3 when the R&D minimum dropped to 8%. That's why the thresholds have to be set before looking at the company, or you can end up changing the rule to get the answer you want.

