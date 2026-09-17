# Lab 08 — Deal Evidence and Valuation Triangulation: Tesla, Inc. (`TSLA`) Case

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Valuation Date:** September 1, 2026, 16:00 EDT (Market Close)  
**Target Company:** Tesla, Inc. (NASDAQ: `TSLA`)  
**Primary Target Source:** [Tesla, Inc. Form 10-K for the fiscal year ended December 31, 2025](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) (filed January 29, 2026; accession `0001628280-26-003952`)  
**Anchor Labs:** Lab 06 (DCF, Sensitivity Grid, and Reverse DCF) and Lab 07 (Comparable-Company Valuation Engine)  

---

## 1. Define / Discover — Understanding Tesla First

### The Central Valuation Question
> **What would Tesla's share be worth at defensible peer P/E multiples, why does its observed trading multiple (329.71×) diverge so significantly from both its DCF (\$39.74) and peer benchmarks, and how does that comparison inform an investment initiation decision?**

### How Tesla Earns Money (FY2025 Form 10-K Primary Evidence)
Tesla operates through **two reportable segments**, with an additional high-valuation speculative layer ([Item 8, Note 16—Segment Reporting and Information about Geographic Areas, pp. 92–93](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)):
1. **Automotive Segment (\$82,056M combined revenue / 86.5% of total revenue):**  
   * Designs, manufactures, sells, and leases pure battery electric passenger vehicles (Model 3, Model Y, Model S, Model X, Cybertruck) and commercial Semi trucks.  
   * Operates a direct-to-consumer sales and service infrastructure without third-party franchised dealers.  
   * Earns zero-cost **automotive regulatory credits of \$1,993M** from traditional OEMs failing to satisfy governmental emissions mandates ([Item 8, Consolidated Statements of Operations, p. 50](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)).  
   * Includes a **Services and Other sub-line (\$12,530M / 13.2% of total revenue):** the global Supercharger fast-charging network, non-warranty maintenance, collision repair, automotive insurance, parts, and retail merchandise—reported within the Automotive segment, not separately.
2. **Energy Generation and Storage Segment (\$12,771M revenue / 13.5% of total revenue):**  
   * Deploys utility-scale stationary energy storage (**Megapack**) and residential/commercial systems (**Powerwall**).  
   * Grew **26.6% year-over-year** in 2025 (up from \$10,086M in 2024), deploying **46.7 GWh** of storage capacity ([Item 7, MD&A—2025 Highlights, p. 31](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)).
3. **Autonomous Software & Robotics Development (Option Value — not a reportable segment):**  
   * Invests in AI compute clusters, Full Self-Driving (FSD) neural networks, Robotaxi/Cybercab fleet platforms, and Optimus humanoid robotics ([Item 7, MD&A—2026 Outlook, pp. 31–32](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)). Revenue from Robotaxi operations is not separately disclosed in the audited financial statements.

### Are Tesla's Reported Annual Earnings Positive?
* **Yes.** For the fiscal year ended December 31, 2025, Tesla reported **GAAP Net Income Attributable to Common Stockholders of \$3,794 million** ([Item 8, Consolidated Statements of Operations, p. 50](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)).
* Dividing by the diluted weighted-average share count of **3,528.0 million shares** ([Item 8, Note 4—Earnings per Share, p. 61](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm)) yields **FY2025 Total GAAP Diluted EPS of \$1.08**.
* At the September 1, 2026 closing price of **\$356.09** ([Nasdaq Market Activity: TSLA Historical Data](https://www.nasdaq.com/market-activity/stocks/tsla/historical)), Tesla trades at an observed trailing P/E multiple of:
  $$\text{Observed P/E} = \frac{\$356.09}{\$1.08} = \mathbf{329.71\times}$$

### Research Needs & Methodological Limitation
Tesla cannot be valued soundly by mechanically pasting a legacy automotive P/E multiple. We must investigate whether traditional automotive peers share Tesla's economics, document why key competitors report negative GAAP earnings, and evaluate whether Tesla's 329.71× market multiple reflects manufacturing cash flows or unmodeled software option value.

---

## 2. Represent — Peer Selection Policy & Candidate Decisions

### Peer Selection Policy (Stated Before Candidate Selection)
To maintain analytical rigor, the candidate peer policy was fixed prior to reviewing multiples:
1. **Business Model Fit:** Candidates must design, engineer, and manufacture motor vehicles and powertrain hardware at commercial scale.
2. **Regulatory & Accounting Consistency:** Publicly traded on major U.S. exchanges with audited SEC reporting (Form 10-K or 20-F) denominated in USD under compatible GAAP standards.
3. **Earnings Standard:** Must report **positive annual GAAP diluted EPS** public by the September 1, 2026 valuation date. Single-quarter results and management-adjusted "non-GAAP" earnings are strictly excluded.
4. **Qualification Policy:** Legacy automotive manufacturers undergoing EV transitions are **qualified** for material structural differences: heavy reliance on internal combustion engines (ICE), franchised dealer networks, captive finance balance sheet debt, and lack of utility-scale energy storage.
5. **Exclusion Policy:** Companies reporting negative annual GAAP earnings are **excluded as unusable** because negative earnings cannot mathematically support a positive P/E multiple without producing misleading negative prices. Pure-play software companies without physical manufacturing are excluded.

### Sourced Candidate Investigation

| Company / Role | Trading Price (Sep 1, 2026) | FY2025 Reported Diluted EPS | Fiscal Year-End & Filing Date | Decision | Business Reason & Primary Source Locator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tesla, Inc. (`TSLA`)**<br>*(Target)* | **\$356.09**<br>[Nasdaq Quote](https://www.nasdaq.com/market-activity/stocks/tsla/historical) | **\$1.08** | Dec 31, 2025<br>Filed Jan 29, 2026 | **Target** | [Tesla 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm): Item 8, Statement of Operations, p. 50 (Net income \$3,794M); Note 4, p. 61 (Diluted shares 3,528M). Pure-play EV, stationary energy storage, and autonomous software. |
| **General Motors (`GM`)**<br>*(Candidate 1)* | **\$49.78**<br>[Nasdaq Quote](https://www.nasdaq.com/market-activity/stocks/gm/historical) | **\$3.27** | Dec 31, 2025<br>Filed Jan 27, 2026 | **QUALIFY** | [GM 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1467858/000146785826000013/gm-20251231.htm): Item 1, Business, pp. 1–5; Item 8, Consolidated Statements of Income, p. 62; Note 22, p. 102. Global vehicle manufacturer with Ultium EV platform. Qualified due to >85% legacy ICE mix, franchised dealership distribution, and captive finance debt liabilities (GM Financial). |
| **Ford Motor Company (`F`)**<br>*(Candidate 2)* | **\$10.50**<br>[Nasdaq Quote](https://www.nasdaq.com/market-activity/stocks/f/historical) | **\$(2.06)** | Dec 31, 2025<br>Filed Feb 11, 2026 | **EXCLUDE / UNUSABLE** | [Ford 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm): Item 1, Business, pp. 1–4; Item 8, Consolidated Statement of Operations, p. 68. Global automaker with distinct EV segment ('Ford Model e'). Excluded from P/E calculation due to reported GAAP net loss of \$(2.06) per share caused by EV program asset write-downs and restructuring charges. |

---

## 3. Implement — Valuation Engine Execution (`python comps.py`)

Inputs were entered into [`comps.py`](https://github.com/mnine393/TICKER-research/blob/main/comps.py) holding the valuation date at **September 1, 2026**.

### Python Input Block
```python
TARGET = {
    "ticker": "TSLA",
    "name": "Tesla",
    "price": 356.09,  # USD per share, Nasdaq closing price as of September 1, 2026
    "diluted_eps": 1.08,  # USD per share, FY2025 total GAAP diluted EPS (Form 10-K)
}

PEERS = [
    {
        "ticker": "GM",
        "name": "General Motors",
        "price": 49.78,  # USD per share, NYSE closing price as of September 1, 2026
        "diluted_eps": 3.27,  # USD per share, FY2025 total GAAP diluted EPS (Form 10-K)
    },
    {
        "ticker": "F",
        "name": "Ford Motor Company",
        "price": 10.50,  # USD per share, NYSE closing price as of September 1, 2026
        "diluted_eps": -2.06,  # USD per share, FY2025 total GAAP diluted EPS (Form 10-K, net loss)
    },
]
```

### Complete Terminal Output
```text
====================================================================
LAB 08: COMPARABLE-COMPANY P/E VALUATION ENGINE
====================================================================
Target: Tesla (TSLA)
September 1, 2026 Closing Price: $356.09
FY2025 Total GAAP Diluted EPS:   $1.08
--------------------------------------------------------------------

Peer Multiples (Price / Diluted EPS):
  General Motors (GM) P/E: 15.223242x (Price: $49.78, EPS: $3.27)
  Ford Motor Company (F): not meaningful (Price: $10.50, EPS: $-2.06)

Usable peers: 1
Peer median P/E: 15.223242x
Tesla reference estimate: $16.44 (one valid peer; no range)

Leave-One-Peer-Out Sensitivity:
  Remove GM: no estimate (no remaining peers)
```

---

## 4. Validate — Arithmetic Checks & Sensitivity Diagnostics

### 1. Hand-Checked Arithmetic Verification
* **Admitted Peer (General Motors):**
  $$\text{GM P/E} = \frac{\text{Price}}{\text{EPS}} = \frac{\$49.78}{\$3.27} = 15.22324159\dots \approx \mathbf{15.223242\times}$$
* **Target Implied Valuation (Tesla):**
  $$\text{Implied Price} = \text{GM P/E} \times \text{Tesla Diluted EPS} = 15.22324159\dots \times \$1.08 = \$16.4411009\dots \approx \mathbf{\$16.44}$$
* **Result:** Hand-calculated arithmetic matches the calculator output to the exact cent.

### 2. Diagnosis of Why Ford Is Unusable for P/E
* In FY2025, Ford reported a net loss of \$8.2B, producing a GAAP diluted EPS of **\$(2.06)** ([Ford 2025 Form 10-K, Item 8, p. 68](https://www.sec.gov/Archives/edgar/data/37996/000003799626000015/f-20251231.htm)).
* Dividing Ford's market price of \$10.50 by \$(2.06) produces a negative multiple of \(-5.10\times\). Applying a negative multiple to Tesla's positive earnings (\$1.08) would generate a mathematically invalid negative equity value of \(-\$5.51\).
* In accordance with Lab 07 & 08 policy, negative earnings are classified as **"not meaningful"** and excluded from the multiple calculation. This diagnosis highlights a structural industry reality: legacy automakers face substantial capital expenditures and non-cash asset impairment charges associated with electric vehicle programs, leaving General Motors as the sole profitable domestic legacy candidate.

### 3. Leave-One-Peer-Out Sensitivity & Single-Peer Limitation
* **Prediction Before Run:** Because General Motors is the only usable peer with positive annual GAAP earnings, removing GM leaves zero usable peers. Removing GM must completely eliminate the valuation estimate.
* **Observed Run Confirmed:** The engine outputs: `Remove GM: no estimate (no remaining peers)`.
* **Why One Peer Gives a Reference Estimate, Not a Range:**  
  A **valuation range** requires observable dispersion across multiple independent market transactions. With only one peer (GM), there are zero degrees of freedom and zero dispersion. Labeling \$16.44 as a "range" would present false precision. It serves strictly as a **one-peer reference estimate**.

---

## 5. Evolve — Valuation Triangulation & Skeptical Colleague Review

### Valuation Triangulation Table

| Valuation Method | Tesla Result (Sep 1, 2026) | Main Assumptions & Methodological Limitations |
| :--- | :---: | :--- |
| **Week 3 DCF Model** | **\$39.74** | **Forecast & Discount Assumptions:** Starting FCFF of \$6,433.27M; explicit growth fading from 8% to 3%; WACC of 10.0%; terminal growth of 3.0%. **DCF Sensitivity Range: \$34.06 to \$54.60** (across WACC 9.0%–11.0% and $g$ 2.0%–4.0%). Reverse DCF shows that reaching \$356.09 would require an aggressive +72.77 percentage point uniform shift across all explicit years, which far exceeds historical precedent. |
| **Peer P/E Multiples** | **\$16.44** *(Reference)* | **Peer Choices & Earnings Basis:** **One-peer reference estimate of \$16.44** from General Motors (15.22× P/E) applied to Tesla's FY2025 GAAP diluted EPS (\$1.08). Ford is unusable due to negative EPS (\$(2.06)). Limitation: Reflects legacy cyclical automaker pricing, giving zero valuation credit to Tesla's net cash balance sheet, energy storage growth, or autonomous software development. |
| **Observed Market Price** | **\$356.09** | **Market-Implied Expectations:** Trades at **329.71× trailing earnings** (9.0× fundamental DCF baseline; 21.7× automotive peer reference). Reflects a substantial valuation premium over traditional automotive manufacturing benchmarks, pricing in unproven software and robotics optionality. |

*Note: In accordance with course guidelines, the DCF sensitivity range (\$34.06–\$54.60) and the peer P/E reference estimate (\$16.44) are kept strictly separate; they are derived from fundamentally different valuation objects and are not blended or averaged.*

---

### Skeptical Colleague Review & Source-Checked Judgment

To test this triangulation against rigorous scrutiny, we review the comparison as a skeptical colleague and evaluate three specific challenges:

```text
Skeptical Colleague Challenge:
"Review my valuation comparison as a skeptical colleague. Identify the weakest supported
assumption and any mismatch in company, date, valuation object or earnings definition.
Do not invent a missing range or average the methods. Ask one question that could change
my decision. I will check your criticism against my sources before revising my call."
```

#### Challenge 1: The Capex and Near-Term Cash Flow Contradiction
* **Colleague's Criticism:**  
  *"Your DCF assumes starting FCFF of \$6,433M and positive cash flow growth every year. But in Item 7 MD&A (p. 32), Tesla management stated that 2026 capital expenditures will exceed \$20 billion (up from \$8.53B in 2025). If capex jumps to \$20B+, FY2026 FCFF will be deeply negative, putting downward pressure on your DCF cash flow trajectory."*
* **Author's Judgment:** **ACCEPT.**
* **Evidentiary Defense:** Sourced directly in [Tesla 2025 Form 10-K, Item 7, p. 32](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm). Tesla's AI compute, data center, and manufacturing expansion requires >\$20B in 2026 capex. Operating cash flow in 2025 was \$14,747M. If operating cash flow does not grow by at least 40% in 2026, FCFF will turn negative. This critique reinforces our conservative stance: Tesla's near-term fundamental cash flows are under severe reinvestment pressure, widening the disconnect with the \$356.09 market price.

#### Challenge 2: The Automotive Comparability Mismatch
* **Colleague's Criticism:**  
  *"General Motors is an imperfect benchmark for Tesla. GM carries \$100B+ of debt inside GM Financial, sells via franchised dealers with lower gross margins, and has negligible utility-scale energy storage. Applying GM's 15.2× multiple to Tesla ignores Tesla's net cash balance sheet (+\$35.7B net cash) and its 27% growing Energy segment (\$12.8B revenue). You are penalizing Tesla for legacy automaker structural constraints it does not share."*
* **Author's Judgment:** **ACCEPT (with Qualification).**
* **Evidentiary Defense:** Confirmed by [Tesla Form 10-K, Note 4, p. 70](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) (showing \$44.1B cash/investments vs \$8.4B debt) and [Note 16, Segment Reporting, pp. 92–93](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm). GM's different capital structure—including captive finance debt that Tesla does not carry—makes it a qualified, imperfect comparison. GM is the only profitable domestic vehicle manufacturing peer. This does not mean Tesla is worth \$16.44; rather, it demonstrates that **P/E multiples of legacy automakers cannot capture Tesla's multi-segment business model**, exposing the degree to which market pricing depends on non-automotive expectations.

#### Challenge 3: The Skeptical Deciding Question
* **Colleague's Question:**  
  *"Given that Tesla's fundamental DCF value is \$39.74 and its peer-implied auto value is \$16.44, does the \$356.09 market price reflect an unsustainable valuation premium, or are you modeling the wrong company by treating Tesla primarily as an automaker instead of an autonomous software and robotics platform?"*
* **Author's Judgment:** **UNRESOLVED (Central Strategic Question).**
* **Evidentiary Defense:** In SEC filings, **73.3% of revenue still derives from the Automotive segment (including Services and Other)**. [Item 1 (pp. 2–5)](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) describes Robotaxi, Cybercab, and Optimus under development outlooks; revenue from Robotaxi operations is not separately disclosed in the audited financial statements. Fundamental financial analysis bound to audited accounting evidence cannot capitalize hypothetical revenues that have not yet materialized. Therefore, current market pricing reflects growth expectations far in excess of current operational performance.

---

## 6. Reflect — Defending the Investment Decision

### Why the Valuation Methods Differ
1. **The DCF (\$39.74 baseline; range \$34.06–\$54.60):** Values Tesla on fundamental operating cash generation, factoring in fading automotive margins, tax provisions, working capital, and steady reinvestment. It confirms that on physical vehicle manufacturing and energy storage alone, Tesla's fundamental operating value is approximately \$40 per share.
2. **The Peer Reference (\$16.44):** Prices Tesla's earnings (\$1.08) through the multiple of a mature, cyclical automaker (GM at 15.2×). It reflects commodity automotive earnings without growth optionality.
3. **The Market Price (\$356.09):** Reflects market expectations of exponential revenue growth from autonomous mobility, software subscriptions, and robotics.

### What the Comparison Adds to the DCF
The peer comparison confirms that **comparable multiples do not support Tesla's market price**. Investigating Ford shows that peers are facing margin compression during EV development, while GM's multiple demonstrates that traditional manufacturing economics command modest valuations.

### Final Conditional Recommendation: WATCH / DEFER

* **Rating:** **WATCH / DEFER (Do Not Initiate a Position)**
* **Independent Valuation Anchors:**
  * **DCF Sensitivity Range:** **\$34.06 – \$54.60** (WACC 9.0%–11.0%, $g$ 2.0%–4.0%).
  * **Peer P/E Reference Estimate:** **\$16.44** (one-peer reference from GM; no range).
* **Core Rationale:**  
  At **\$356.09**, Tesla trades at **9.0× its fundamental DCF baseline** and **21.7× its automotive peer reference**, with a trailing P/E of **329.71×**. There is **no margin of safety** for a fundamental investor. Initiating a position today requires paying \$356.09 for \$1.08 of trailing earnings during a period when management has guided capital expenditures to exceed \$20B in 2026.

### What Specific Evidence Would Change This Decision?
1. **Evidence to Upgrade to Initiate (Buy):**  
   * A market price correction toward the **DCF sensitivity range (\$34.06–\$54.60)**, providing fundamental valuation support.
   * **Audited 10-K/10-Q disclosures** demonstrating that commercial Robotaxi operations or FSD software subscriptions are generating high-margin, recurring software cash flows (gross margins >70%), establishing a revenue trajectory independent of vehicle manufacturing margins.
2. **Evidence to Downgrade to Do Not Initiate (Sell / Avoid):**  
   * Capital expenditures exceeding \$20B in 2026 while automotive gross margins (excluding regulatory credits) compress below 14%, indicating that elevated capital intensity is not yielding operating leverage.
   * Legislative or regulatory curtailment of automotive regulatory credits (\$1,993M in 2025), which exceed half of Tesla's net income attributable to common stockholders (\$3,794M in FY2025).

---

## 7. Checkout & File Index

| File Name | GitHub Source Link | Purpose & Description | Status |
| :--- | :--- | :--- | :---: |
| **`comps.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/comps.py) | Python P/E comparable engine configured for Tesla, GM, and Ford. | **Verified & Running** |
| **`03_Comps/comps.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/03_Comps/comps.py) | Folder copy of comparable valuation engine. | **Verified & Running** |
| **`Lab_08_comps_dcf.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Lab_08_comps_dcf.md) | Full Lab 08 report, sourcing table, validation, and triangulation defense. | **Submission-Ready** |
| **`03_Comps/Lab_08_comps_dcf.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/03_Comps/Lab_08_comps_dcf.md) | Folder copy of Lab 08 triangulation report. | **Submission-Ready** |
| **`dcf.py`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/dcf.py) | Week 3 / Lab 06 five-year FCFF DCF model, sensitivity grid, and reverse DCF. | **Archived Benchmark** |
| **`Tesla_dcf_inputs.md`** | [View on GitHub](https://github.com/mnine393/TICKER-research/blob/main/Tesla_dcf_inputs.md) | Week 3 DCF inputs write-up and SEC filing citations. | **Archived Benchmark** |

*All code, data tables, and analysis conform strictly to FIN 43900 academic standards and use verified SEC EDGAR primary source filings.*
