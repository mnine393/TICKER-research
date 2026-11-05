# Lab 19: Three-investor panel

## Question

When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?

## Project links and command

The three investor instructions and their check programs are:

- [Buffett owner-earnings instructions](.codex/skills/buffett-owner-earnings/SKILL.md) and [fact program](.codex/skills/buffett-owner-earnings/buffett_facts.py)
- [Graham defensive-investor instructions](.codex/skills/graham-defensive-investor/SKILL.md) and [check program](.codex/skills/graham-defensive-investor/graham_defensive.py)
- [Burry cash-and-balance-sheet instructions](.codex/skills/burry-cash-and-balance-sheet/SKILL.md) and [check program](.codex/skills/burry-cash-and-balance-sheet/burry_cash_balance.py)

The panel viewer is [buffett_app.py](tsla-proforma-model/buffett_app.py). Run it from the FIN 439 folder:

```powershell
python -m streamlit run tsla-proforma-model/buffett_app.py
```

The six memos are:

- Costco: [Buffett](memos/COST_buffett_memo.md), [Graham](memos/COST_graham_memo.md), and [Burry](memos/COST_burry_memo.md)
- NVIDIA: [Buffett](memos/NVDA_buffett_memo.md), [Graham](memos/NVDA_graham_memo.md), and [Burry](memos/NVDA_burry_memo.md)

## Known answer: Costco

All of the Costco panel results match the saved five-year record.

| Measure | Five yearly results |
|---|---|
| Current ratio | 1.02, 1.07, 0.97, 1.03, 1.06 |
| Liabilities divided by equity | 2.11, 1.75, 1.96, 1.64, 1.49 |

| Investor | Check one | Check two | Check three | Score |
|---|---|---|---|---|
| Buffett | Return on equity: pass | Owner earnings positive: pass | Owner earnings grew: pass | 3 of 3 |
| Graham | Latest current ratio of 1.06: fail | Net income positive: pass | Net income grew: pass | 2 of 3 |
| Burry | Operating cash flow at least net income: pass | Latest liabilities divided by equity: pass | Not used | 2 of 2 |

The viewer found no unprinted numbers in any Costco memo.

## Threshold probe

Lowering Graham's current-ratio threshold to 1.0 made Costco pass all three checks, for a score of 3 of 3. I kept the 2.0 threshold because that is the stated rule for this defensive screen.

## My company: NVIDIA

NVIDIA, ticker NVDA, was the largest holding in the Vanguard Total World Stock exchange-traded fund, ticker VT, at 4.54% as of 30 September 2026. [Stock Analysis holdings page](https://stockanalysis.com/etf/vt/holdings/)

| Investor | Result |
|---|---|
| Buffett | 3 of 3 |
| Graham | 3 of 3; latest current ratio was 3.91 |
| Burry | 1 of 2; operating cash flow was below net income in four of five years, while liabilities divided by equity of 0.31 passed |

There were no gaps in the NVIDIA record: no value was marked “not found” or “not known.”

## Bugs fixed

The Burry program had no main block, so running it printed nothing. It now has a main block. The Graham and Burry programs also wrote memos in code. They now only calculate and print checks; the artificial intelligence writes the memos after reviewing the printed output.

## Bull and bear

**Bear (my partner):** Burry fails NVIDIA because its operating cash flow was lower than its net income in four of the five years. Last year it brought in $102,718 million of cash on $120,067 million of profit, so some of that profit hasn't turned into cash yet, and that could turn into write-offs if demand slows down.

**Bull (me):** Buffett and Graham both give NVIDIA 3 out of 3. ROE never went below 19.8%, the current ratio is 3.91, and owner earnings went from $8,132 million to $96,676 million. Burry's own debt check passes at 0.31, so the cash gap comes from growing really fast, not from a weak balance sheet.

## My decision

Only with a condition. I would let the panel screen companies for Project 2 as long as any company that fails a check gets reviewed by hand before I add it, and I set the thresholds before I look at the results. Lowering Graham's threshold to 1.0 flipped Costco from a fail to a pass, so the threshold can change the answer.

## Learn

A panel of AI agents is a few AI "investors" that each follow their own rules and read the same facts. Each skill has its own checks and its own way of thinking, so they disagree because they care about different things, not because the numbers are different. Buffett looks at returns and owner earnings, Graham looks at safety and liquidity, and Burry looks at whether the profits are actually turning into cash. Having them side by side shows where a company is strong and where it might have a weak spot.

## Reflect

On NVIDIA the panel agreed that the business is strong: Buffett and Graham both passed it on every check, and Burry's debt check passed too. It split on cash. Burry failed it because operating cash flow was below net income in four of the five years, which the other two investors don't check.

The threshold probe shows that a screen's verdict is only as good as the threshold someone picked. Costco failed Graham at 2.0 and passed at 1.0 with the exact same numbers. That's why the thresholds have to be set before looking at the company, or you can end up changing the rule to get the answer you want.

