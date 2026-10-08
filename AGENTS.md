# FIN 439 Project Standing Rules

- The project of record is `tsla-proforma-model/`. Older `Lab_*` files are history; do not edit them.
- Never commit or push. The student reviews the diff and commits personally.
- After any code change, run `cd tsla-proforma-model && python -m pytest -q` and `python export_visible_output.py`, then report the results.
- Never put API keys, passwords, or `.env` files in the repository.
- Explain every change in plain language that a finance student can repeat in a video.
- At the end of every session, append one row to `docs/ai-use-log.md` with: date, tool (Codex + model name shown in the app), task, what you produced, and a blank `My check / Accept-Modify-Reject` column for the student to fill in.
