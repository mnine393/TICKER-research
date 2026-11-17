**AI use:** OpenAI Codex (GPT-5.6-Terra) wrote this lab file's template and built the Project 2 analysis engine; Claude helped plan and check; the analysis, the prediction and the decision are mine.
**Education, not investment advice.**

# FIN 439 Lab 20: Project 2 Readiness

## 1. Question and links

Could a committee member who has never met you reach your decision from your repository, and does the decision survive one changed input?

- [Project 2 repository: Compass](https://github.com/mnine393/FIN439-Project2)
- [Project 2 readme](https://github.com/mnine393/FIN439-Project2/blob/main/README.md)
- [Visible output](https://github.com/mnine393/FIN439-Project2/blob/main/output/visible_output.md)
- [Decision memo](https://github.com/mnine393/FIN439-Project2/blob/main/docs/decision-memo.md)
- [Validation and artificial-intelligence use record](https://github.com/mnine393/FIN439-Project2/blob/main/docs/validation-and-ai-use.md)

## 2. Readiness table

| Item | Ready? |
|---|---|
| A teammate can move one control in the app's sidebar and read the mandate verdict. | Yes (the trading cost control, used in section 4) |
| The readme has the one command that produces the result. | Yes (install, then `python -m streamlit run app.py`) |
| The decision numbers are readable on GitHub without running anything in `output/visible_output.md`. | Yes |
| `docs/decision-memo.md` matches the output's numbers, dates, and conditions. | No, not written yet (unresolved) |
| `docs/validation-and-ai-use.md` covers the baseline, mandate check, stress run, and Locked Changed-Input Record. | Partly: the locked prediction is on GitHub; the full record is drafted but not pushed yet (unresolved) |
| Videos 1 through 3 and their transcripts have working links. | No, not recorded yet (unresolved) |

## 3. Cold run, written by my partner

*Partner's name:* No partner was available, so this cold run was done by Claude (an AI assistant) acting as a
stranger: a fresh folder, a fresh Python environment, and only the repository link and its README. It is recorded as
an AI cold run, not a partner's.

*Exact command they ran:* `git clone https://github.com/mnine393/FIN439-Project2.git`, then
`python -m pip install -r requirements.txt`, then `python -m streamlit run app.py` (version on GitHub: commit `c0e9dda`).

*First failure they hit:* The app opened and showed the committee summary, but the page stopped partway with
`ValueError: Unknown format code '%' for object of type 'str'`. The Stress tab's table formatter tried to turn the
text column of portfolio weights into a percentage.

*Elapsed time from opening the link to seeing the result:* About 3 minutes (cloned 13:45:19; install finished
13:47:11; app running 13:47:41; result on screen about 13:48).

*Where they found the result:* The app's Committee summary tab (objective 7.35%, stop condition triggered, 2 of 1,771
mixes meet every rule), and without running anything in `output/visible_output.md` on GitHub.

## 4. One changed input, predicted first (artificial intelligence closed)

I will write this prediction myself before running the changed input, then commit and push it.

The input I am changing is the trading cost charged in the point-in-time backtest, from 10 basis points to 25 basis points (0.10% to 0.25% of each trade).

| Measure | Before | After |
|---|---:|---:|
| Constrained portfolio's backtest ending value | $134,296,207 | $129,925,479 |
| Constrained portfolio's return per year | 4.76% | 4.58% |
| 60/40 benchmark's ending value | $200,614,136 | $200,095,126 |
| Stop condition | triggered | triggered |

*My predicted direction for the ending value:* "ends with less money"

*My predicted direction for the gap to the 60/40 benchmark:* not predicted

*Do I predict my decision changes?* "i think yes it would change the amount i would change and reccommend it"

*Time and commit of my prediction:* Written by me without AI and pushed before the run, 2026-11-17 (see the commit
"Lab 20: my prediction (pre-run)" in this repository's history).

### After the run

*What happened:* "it lost more money because it trades a lot"

*Did the decision change?* "decision stays reject"

*Why my prediction matched or did not:* The direction matched: it ended with less money. I predicted my decision would
change, but "it just confirmed what I already decided."

### How to run it

From the Project 2 folder run `python -m pip install -r requirements.txt`, then `python -m streamlit run app.py`.
In the sidebar, change **Backtest trading cost (basis points)** from 10 to 25. Open the **Would it have worked?** tab
to read the new numbers. Set it back to 10 to see the original.

## 5. Explain the code (six minutes, no artificial intelligence)

The decision numbers come from `backtest.py`, in the `run_backtest` function. Each month it chooses the mix from data known that day, holds it for the next month, charges trading costs on turnover, and pays the quarterly payout.

*Practice question (no partner notes were recorded):* How do you know the backtest did not use future data?

*My answer:* Each month, run_backtest only uses the returns up to that month to pick the mix, then it holds that mix for the next month and sees what actually happened.

## 6. Fix one thing

Fixed the first failure: in `app.py`, the `rate` function now leaves text unchanged instead of formatting it as a
percentage, so the Stress table loads. After the fix, the same cold-run copy loads with no error.
Commit of the fix: [`108e075`](https://github.com/mnine393/FIN439-Project2/commit/108e0752fabc26a973a872b2b09fc0af642baeff), pushed 2026-11-17.

## 7. Decision line

**Reject.** I would reconsider if the optimizer beat the 60/40 benchmark in the backtest and stopped changing its mix so much when the data changes.

## 8. Reflect

*What the cold run found that I could not see:* The Stress tab crashed on a fresh copy of my repository. I never saw it on my own computer because I had already fixed it there but had not pushed the fix.

*What I will not touch before the deadline:* The graded four-fund run and my locked prediction, so my results stay the same.

## 9. Checkout

- [This Lab 20 file](https://github.com/mnine393/TICKER-research/blob/main/Lab_20_project2_readiness.md)
- [Project 2 repository: Compass](https://github.com/mnine393/FIN439-Project2)
