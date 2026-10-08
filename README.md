# FIN 43900 Project 1: Tesla, Inc. (TSLA)

**Decision:** Should the fund initiate a position in TSLA, put it on watch or defer, or not initiate?
**Current answer:** WATCH / DEFER. Do not initiate at the current market price. Supporting records are in `docs/`.
**Valuation date:** 24 Sep 2026 · **Currency:** USD millions except per-share figures · **Share basis:** diluted,
3,540.0M shares (unearned 2025 CEO award shares excluded).

## Start here

| If you want to... | Go to |
|---|---|
| See the results without running anything | [`tsla-proforma-model/output/visible_output.md`](tsla-proforma-model/output/visible_output.md) (also `.json` and `TSLA_model.xlsx`) |
| Run the product (the driver panel, statements, checks and valuation) | [`tsla-proforma-model/`](tsla-proforma-model/) (see "Cold run" below) |
| Read how the model works | [`tsla-proforma-model/README.md`](tsla-proforma-model/README.md) and [`MODEL_SUMMARY.md`](tsla-proforma-model/MODEL_SUMMARY.md) |
| See validation and AI use | [`docs/validation-and-ai-use.md`](docs/validation-and-ai-use.md) |

**The project of record is `tsla-proforma-model/`.** Every other file in this repo is earlier lab work, kept as
the history of how the analysis evolved (see the table below).

## Cold run (fresh machine, about 3 minutes)

Requires Python 3.10 or newer. No API keys or accounts are needed, and the default seed data works offline.

```bash
cd tsla-proforma-model
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                  # expect: 66 passed
python export_visible_output.py      # rewrites output/ ; expect "Base value/share: 29.05  status=OK"
streamlit run app.py                 # opens the app at http://localhost:8501
```

## Lab history (superseded and kept for evidence)

These files are earlier stages of the same analysis. Their per-share numbers use **different dates, cash-flow
conventions and assumptions**. They are not inputs to the current result and should not be averaged with it.

| File(s) | Lab | What it is | Status |
|---|---|---|---|
| `01_Research/Tesla_2026-09-03_report.md` | Research | Company research report | Background |
| `Tesla_dcf_inputs.md`, `dcf.py` (also copies in `02_Valuation/` and `FIN 439/`) | Lab 06 | Standalone five-year FCFF DCF, sensitivity grid and reverse DCF | Superseded by the app |
| `Lab_07_comps.md`, `comps.py` (also in `03_Comps/`) | Lab 07 | P/E comps engine on the Asbury (ABG) training case | Method practice |
| `Lab_08_comps_dcf.md` (also in `03_Comps/`) | Lab 08 | Tesla peer comparison and DCF/comps triangulation | Superseded by the app |
| `Lab_09_proforma_engine.md`, `proforma.py` | Lab 09 | Three-statement engine, reproduces the ABG known answer of $291.75 | Known-answer validation |
| `Lab_09_proforma_fcfe.md` | Lab 09 | Write-up of the full Tesla app | Current |
| `Lab_10_proforma_tsla.md`, `proforma_tsla.py` | Lab 10 | Simplified Tesla pro-forma | Superseded by the app |
| `Lab_11_proforma_sensitivity.md`, `sensitivity_tsla.py` | Lab 11 | One-at-a-time sensitivity with the **Locked Prediction Record** | Validation evidence |
| `Lab_12_presentation_review.md` | Lab 12 | Presentation and peer review (Marriott partner) | Recommendation draft |
| `FIN 439/` | n/a | Duplicate copies of the files above | Duplicate; ignore |

## Disclaimer

This repo is for education only. It is not investment advice.
