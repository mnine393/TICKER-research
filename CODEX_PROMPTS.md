# Codex Prompt Pack: FIN 43900 Project 1 (Week 7)

How to use this file: save it in the root of your TICKER-research folder. Then, in Codex, type
one short line such as:

    Open CODEX_PROMPTS.md and do PROMPT 0 exactly as written.

Do one prompt at a time and read what Codex says before you move on. Codex never commits. You
review the changes, run the tests and commit yourself.

Step 4 has no prompt because it is AI-closed work you do yourself. Steps 5 and 6b go to
Gemini/ChatGPT, not Codex; copy those prompts from this file into those apps.

---

## PROMPT 0: Set up project context

You are helping me finish FIN 43900 Project 1 (Purdue). My target is Tesla (TSLA).

1. Read these course files so you know the requirements:
   - https://raw.githubusercontent.com/CinderZhang/FIN43900-Fall2026/main/projects/project-1-corporate-finance-application.md
   - https://raw.githubusercontent.com/CinderZhang/FIN43900-Fall2026/main/PROJECT-SUBMISSION-ARCHITECTURE.md
   - https://raw.githubusercontent.com/CinderZhang/FIN43900-Fall2026/main/projects/AI-BOUNDARY-CARD.md
   If you cannot fetch URLs, tell me and I will paste them.
2. Read README.md, docs/validation-and-ai-use.md, and everything in tsla-proforma-model/.
3. Create AGENTS.md at the repo root with these standing rules for every future session:
   - The project of record is tsla-proforma-model/. Older Lab_* files are history; do not edit them.
   - Never commit or push. I review the diff and commit myself.
   - After any code change, run `cd tsla-proforma-model && python -m pytest -q` and
     `python export_visible_output.py`, and report the results.
   - Never put API keys, passwords, or .env files in the repo.
   - Explain every change in plain language I can repeat in a video. I am a finance student, not
     a software engineer.
   - At the end of every session, append one row to docs/ai-use-log.md with: date, tool
     (Codex + model name shown in the app), task, what you produced, and a blank
     "My check / Accept-Modify-Reject" column for me to fill in.
4. Create docs/ai-use-log.md with that table header. Add a first row saying Claude (Cowork) on
   2026-10-06 wrote the README project map, export_visible_output.py, and the draft
   docs/validation-and-ai-use.md, and drafted the decision memo on 2026-10-06.
5. Run the tests and the export script. Then give me a short list of which Project 1
   requirements (1-10) this repo already meets and which it doesn't, citing files. Don't fix anything yet.

Before you commit, check: the tests show 66 passed, and the export prints "Base value/share: 29.05".

---

## PROMPT 1a: FCFF plan (no code). ONLY if studio says FCFE isn't enough

Read AGENTS.md. Project 1 requirement 4 needs a five-year FCFF DCF with WACC, a terminal
convention, and a full enterprise-value-to-equity-per-share bridge, driven by the pro-forma's
operating forecast. tsla_model/valuation.py currently does FCFE at the cost of equity.

Do NOT write code yet. Explain in plain language:
1. Which lines in tsla_model/statements.py give EBIT, taxes, D&A, capex and change in NWC per year.
2. How you would define FCFF = EBIT x (1 - tax rate) + D&A - capex - increase in NWC, keeping
   interest income OUT of EBIT (non-operating).
3. How you would build WACC: cost of equity from the existing CAPM; pre-tax cost of debt
   (say where it comes from); tax rate from the model; weights from market equity
   (price x diluted shares) and debt = debt + finance leases + revolver.
4. The equity bridge: EV + excess cash and investments + digital assets + SpaceX stake
   - debt - finance leases - revolver - noncontrolling interest = equity; / 3,540.0M diluted shares.
   Say whether operating leases are treated as debt or as an operating cost, and why, so the
   treatment is consistent with EBIT.
5. How you will reuse the existing valuation date, H1 2026 stub, discounting periods, terminal
   year (2031) and terminal capex/D&A convention so FCFF and FCFE are comparable.
6. The tests you will add.
List the files you will change.

---

## PROMPT 1b: FCFF build

Go ahead with the plan from PROMPT 1a. Requirements:
- New module tsla_model/fcff.py with a function that returns, per forecast year: EBIT, tax on
  EBIT, NOPAT, D&A, capex, change in NWC, FCFF; plus WACC components, PV of FCFF, terminal value,
  PV of terminal value, terminal value share of EV, enterprise value, each bridge line,
  equity value, and value per share.
- Refuse to value (same pattern as the FCFE engine) if any integrity check fails or terminal
  growth >= WACC.
- WACC x terminal-growth sensitivity grid (WACC 8%-13%, g 1%-4%), and a reverse DCF: the WACC
  that makes value per share equal the market price.
- A reconciliation table for each year showing FCFE = FCFF - after-tax interest expense
  + after-tax interest income + net borrowing (debt, finance leases, revolver). Show any residual
  and explain it in a comment. Don't force it to zero.
- Tests in tests/test_fcff.py:
  (a) a tiny synthetic known-answer case I can check by hand (3 years, round numbers);
  (b) g >= WACC refuses; (c) higher WACC -> lower value; higher g -> higher value;
  (d) bridge lines sum to equity value; (e) a broken balance sheet blocks the FCFF valuation.
- Show FCFF next to FCFE on the app's valuation page, with one sentence explaining the difference.
- Add the FCFF headline, bridge, and WACC-g grid to export_visible_output.py.
Run all tests and the export. Then explain the new code to me file by file, as if I'm about to
present it, and give me the 3 questions a professor is most likely to ask about it.

Before you commit: work through the synthetic case by hand or in Excel, confirm FCFF and FCFE per
share are close and that you can explain the gap, and confirm all tests pass.

---

## PROMPT 2a: Propose driver bounds (no code)

Read AGENTS.md and Project 1 requirement 10 ("What to build - the shape"). Look at
app.py's sidebar and assumption controls and at tsla_model/assumptions.py.

Do NOT write code yet. Make a table of the 6-8 load-bearing drivers (use the tornado ranking in
output/visible_output.md plus cost of equity and terminal growth). For each: current base value,
the historical range in seed_filings.json (FY2023-FY2025 and H1 2026), a proposed low/high
bound, and the one-line evidence for that bound (filing and page). Flag any bound you are
unsure about. Also list which current controls should be removed or locked.

YOU then edit that table, because the bounds are your judgment. Paste your final table under PROMPT 2b.

---

## PROMPT 2b: Build the bounded driver panel

Use my bounds table below. Change app.py so that:
1. A "Driver panel" shows ONLY these drivers as sliders, each clamped to my bounds, with the
   evidence line as the help text.
2. Remove or hide the generic "Multiply by / Then add" control from the main view (keep it only
   under an "Advanced - unbounded stress test" expander that is labelled as outside the
   evidence range).
3. "Reset to base" restores every driver and shows "Base restored" so I can demo it.
4. Next to the panel, show: value per share (FCFE and FCFF if built), change vs. base in $ and %,
   and a checks panel that is green when all pass and turns RED listing the failed check.
5. A clearly labelled "Incoherent input demo" button that sets one input combination which
   breaks a check (for example capex so high the minimum-cash rule fails even with the revolver
   fully drawn), so the valuation is refused on screen. Reset must recover it.
Add a headless app test for the reset and for the demo button refusing the valuation.
Run the tests, then give me a 60-second click-by-click demo script for the opening of Video 3:
move one driver, read the result, reset, trigger the failing check, recover.

MY BOUNDS TABLE:
(paste here)

---

## PROMPT 3: Reconcile the old valuation numbers

Read AGENTS.md, Lab_08_comps_dcf.md, Lab_09_proforma_fcfe.md, Lab_10_proforma_tsla.md,
Lab_11_proforma_sensitivity.md and Lab_12_presentation_review.md.

Create docs/valuation-reconciliation.md with ONE table: each per-share value that appears in
those labs, its file, valuation date, cash-flow type (FCFF or FCFE), discount rate, whether
excess cash and non-operating assets were added, share count, and the one-line reason it
differs from the current app result (output/visible_output.md). End with two sentences stating
which number is the result of record and why. Quote exact numbers from the files; if a file
doesn't state something, write "not stated" - do not guess. Don't change any lab file.

---

## STEP 4: You only, with all AI closed (no prompt)

- Locked prediction: fill the Precommit table in docs/validation-and-ai-use.md, commit and push
  only that file ("Locked prediction (pre-run)"), copy the hash and time into the table, THEN make
  the change in the app and fill in the Result table.
- Independent source check: verify one load-bearing number yourself on SEC.gov and add it to the register.
- Partner cold run: a classmate follows only the README. Record the time to output and the first thing that broke.

---

## PROMPT 5: Gemini (paste into Gemini, not Codex). Attach visible_output.md and your memo

You are a skeptical senior analyst on a buy-side investment committee. Attached are my Tesla
valuation output and decision memo (WATCH/DEFER, value range $3-$88/share vs. $378 price,
valuation date 24 Sep 2026).

1. State the single claim my recommendation depends on most.
2. Give me ONE specific counterexample or changed-input test that could break it, with the
   exact numbers and the arithmetic, so I can check it myself.
3. Find the SMALLEST plausible change in a source fact, convention, or assumption that would
   reverse my recommendation (for example, from WATCH to INITIATE or to DO NOT INITIATE). Say
   whether it is merely possible or decision-relevant, and what evidence would show it.
Do not give generic Tesla bull/bear arguments.

Then, with AI closed: redo its math yourself or test it in the app, decide whether to accept, modify,
qualify or reject it, and log it in docs/ai-use-log.md.

---

## PROMPT 6a: Validation record

Read AGENTS.md, docs/validation-and-ai-use.md, docs/ai-use-log.md and the tests folder.
Update docs/validation-and-ai-use.md:
- Add rows to the validation register for every new test (FCFF known answer, WACC/g
  monotonicity, bridge, app reset/demo), each with the test name and file path as evidence.
- Fill "Repository commit" with the current HEAD hash.
- Copy every row of docs/ai-use-log.md into the Named AI-use register.
Do NOT edit anything I wrote: the Locked Changed-Input Record, my Accept/Modify/Reject
columns, the independent source check, or the cold-run log. Where a field still says TODO,
leave it and list those TODOs for me at the end.

---

## PROMPT 6b: ChatGPT. Attach your Edition A PDF from Brightspace and your decision memo

Attached are my Edition A (pre-AI baseline) and my current decision memo for FIN 43900 Project 1.
Draft the A-to-B change table with exactly these rows: Thesis/recommendation, Data/source choice,
Assumption or model design, Risk/limitation/uncertainty. Columns: Edition A | Edition B |
Primary driver of change (course instruction / own analysis / peer challenge / AI / mixed) |
Evidence or test that justified the change. Quote Edition A exactly. If something did not change,
write "No material change" and name the evidence that confirmed it. Leave the driver column
blank if you can't tell from the documents - I will fill it in.

---

## PROMPT 7: Video outline (run once per video: 1, 2, then 3)

Read AGENTS.md, my decision memo (pasted below), docs/validation-and-ai-use.md,
docs/valuation-reconciliation.md, and the video rules in PROJECT-SUBMISSION-ARCHITECTURE.md
sections 4, 5 and 7. For Video [1/2/3], give me a timed talking-point outline (bullets, not
full sentences) that fits under [3:00/5:00] with 20 seconds to spare. For each segment, list
what should be on screen (file, function, or app page). For Video 2, name the exact files and
functions to open, in order. For Video 3, start with the 60-second demo. End with the 3 hardest
questions a committee member could ask and the evidence in my repo that answers each.

## PROMPT 7b: Transcript check (after you save docs/transcript-video-1/2/3.txt)

Compare docs/transcript-video-*.txt against the repo and memo. List every number, ticker or
finance term that doesn't match, with line numbers. Don't edit the files.

---

## PROMPT 8: Final check (Week 8)

Read AGENTS.md. Final pre-submission check, report only, change nothing:
1. Confirm these exist: docs/research-evolution.pdf, docs/decision-memo.pdf,
   docs/validation-and-ai-use.md, docs/transcript-video-1.txt, -2.txt, -3.txt,
   tsla-proforma-model/output/visible_output.md.
2. Search the whole repo and git history for API keys, tokens, passwords or .env files.
3. Check that the value range, base value, recommendation and triggers match across the memo,
   visible_output.md, validation record and transcripts. List every mismatch.
4. Run the tests and export one last time and report.
5. Fill docs/project-submission-manifest-template.csv: repo URL, file paths, current commit hash in
   frozen_or_commit_id. Leave video URLs, durations, timestamps and access_checked for me.
