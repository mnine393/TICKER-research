# Lab 07 — Comparable-Company Policy and Implied Range: Asbury Automotive (`ABG`) Case

**Course:** FIN 43900 (AI Finance Applications, Purdue University)  
**Valuation Date:** December 31, 2024 (Retrospective Training Case)  
**Target Company:** Asbury Automotive Group, Inc. (NYSE: `ABG`)  
**Reference Document:** [The Training-Case Comps, Worked End to End](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/teach-comps-worked-example.md)  

---

## 1. Define / Discover — What P/E Tells Us

### What Is Price-to-Earnings (P/E)?
* **Price per share:** The market value required to purchase one diluted common share of ownership today.
* **Diluted Earnings per Share (EPS):** Total net income available to common shareholders divided by the diluted share count (accounting for stock options, restricted stock units, and convertible instruments).
* **The P/E Multiple (\(\text{Price} / \text{EPS}\)):** Represents how many dollars investors are willing to pay today for each dollar of trailing annual accounting earnings. It is an **equity multiple**; net income sits below interest expense and taxes, meaning equity earnings already belong exclusively to common equity holders.

### Why Use P/E in Valuation?
* **Size Normalization:** Comparing raw share prices or market capitalizations across companies is meaningless. Dividing market price by earnings per share normalizes for scale, allowing direct comparison between a \$5B dealership group and a \$20B dealership network.
* **Independent Market Interrogation of the DCF:** While a Discounted Cash Flow (DCF) model is an argument about the *future* (requiring explicit cash flow, capex, and discount rate assumptions), trading multiples report the *present*: what real market participants are paying right now for similar earning streams. Multiples provide an objective check against DCF optimism or pessimism.
* **The Bridge Trap (Critical Distinction):**  
  * **Enterprise multiples (EV/EBITDA, EV/EBIT):** Price the entire operating firm and require bridging to equity (\(\text{Equity} = \text{EV} + \text{Cash} - \text{Debt}\)).
  * **Equity multiples (P/E):** Price common equity directly. **Never bridge P/E with cash or debt**; doing so double-counts financial leverage.

### When Is P/E Useful — and When Is It Misleading?
* **Useful:** When comparing mature companies in the same industry with similar operating margins, capital structures, reinvestment needs, and GAAP accounting standards.
* **Misleading:**
  * **Negative or Near-Zero Earnings:** If a company reports a net loss, P/E becomes negative or undefined ("not meaningful").
  * **Capital Structure / Leverage Distortions:** Two companies with identical operating performance (EBIT) will have radically different P/E ratios if one carries high debt (higher interest expense suppresses EPS, artificially inflating or distorting P/E).
  * **One-Time Items:** Non-operating gains, legal settlements, asset impairments, or tax valuation allowance releases distort GAAP net income.
  * **Growth Differences:** A high-growth business commands a higher P/E multiple than a stagnant business.
* **Why a Lower P/E Does Not Mean a "Better" Investment:**  
  A low P/E multiple is frequently a **value trap**. It often reflects higher financial leverage, structurally lower returns on invested capital (ROIC), cyclical peak earnings destined to decline, or elevated operational risk.

---

## 2. Represent — Peer Selection Policy & Case Decisions

### Why Business Drivers Matter More Than Industry Labels
Filtering solely by SIC or NAICS codes like "Automotive Retail" groups franchised new-vehicle dealerships with used-vehicle online aggregators (e.g., Carvana) or rental fleets (e.g., Hertz). Franchised dealership economics are fundamentally unique:
1. **Parts and Service / Warranty Repair:** High-margin (~45–55% gross margin) recurring revenue stream that cushions economic downturns.
2. **Finance & Insurance (F&I):** Near-100% margin fee generation from auto loan origination and warranty contracts.
3. **Manufacturer Franchise Agreements:** High barriers to entry and geographic protection granted by automotive OEMs.

### Candidate Peer Decisions (Asbury Automotive Case)

| Candidate Peer | Decision | Business Rationale & Comparison to Asbury (`ABG`) |
| :--- | :---: | :--- |
| **AutoNation, Inc. (`AN`)** | **USE** | Pure-play U.S. franchised automotive retailer operating new/used vehicle sales, F&I, and parts/service departments. Comparable domestic operating footprint, customer financing dynamics, and capital structure. |
| **Group 1 Automotive, Inc. (`GPI`)** | **QUALIFY** | Operates a very similar franchised dealership model with strong parts/service cash flows, but has material international exposure in the United Kingdom (~20–25% of revenues). UK dealership operations face distinct consumer credit environments, regulatory regimes, and foreign exchange exposure that require analytical qualification. |

---

## 3. Implement — Frozen Case Inputs and Execution

### Input Data (December 31, 2024 Closing Prices & FY2024 GAAP Diluted EPS)

| Company | Role | Dec 31, 2024 Price | FY2024 Diluted EPS |
| :--- | :--- | :---: | :---: |
| **Asbury Automotive Group (`ABG`)** | Target | **$243.03** | **$21.50** |
| **AutoNation, Inc. (`AN`)** | Candidate Peer | **$169.84** | **$16.92** |
| **Group 1 Automotive, Inc. (`GPI`)** | Qualified Candidate Peer | **$421.48** | **$36.81** |

---

## 4. Validate — Execution Output (`python comps.py`)

Run from your terminal in `FIN 439`:

```powershell
python comps.py
```

### Complete Terminal Output

```text
====================================================================
LAB 07: COMPARABLE-COMPANY P/E VALUATION ENGINE
====================================================================
Target: Asbury Automotive Group (ABG)
December 31, 2024 Closing Price: $243.03
FY2024 Total GAAP Diluted EPS:   $21.50
--------------------------------------------------------------------

Peer Multiples (Price / Diluted EPS):
  AutoNation (AN) P/E: 10.037825x (Price: $169.84, EPS: $16.92)
  Group 1 Automotive (GPI) P/E: 11.450149x (Price: $421.48, EPS: $36.81)

Usable peers: 2
Peer median P/E: 10.743987x
Asbury peer-implied range: $215.81 - $246.18
Asbury at peer median:     $231.00

Leave-One-Peer-Out Sensitivity:
  Remove AN: remaining GPI estimate = $246.18 (change from full-peer estimate: +15.18)
  Remove GPI: remaining AN estimate = $215.81 (change from full-peer estimate: -15.18)
```

### Verification Against Lab Benchmarks

| Metric / Checkpoint | Model Result | Expected Benchmark | Status |
| :--- | :---: | :---: | :---: |
| **AutoNation P/E** | `10.037825×` | `10.037825×` | **Exact Match** |
| **Group 1 P/E** | `11.450149×` | `11.450149×` | **Exact Match** |
| **Peer Median P/E** | `10.743987×` | `10.743987×` | **Exact Match** |
| **Asbury Peer-Implied Range** | **$215.81 – $246.18** | **$215.81 – $246.18** | **Exact Match** |
| **Asbury at Peer Median** | **$231.00** | **$231.00** | **Exact Match** |
| **Remove GPI: Remaining AN Estimate** | **$215.81** | **$215.81** | **Exact Match** |
| **Change from Two-Peer Midpoint** | **-$15.18** | **-$15.18** | **Exact Match** |

---

## 5. Evolve — Changing the Peer Set & Prediction

### Prediction Before Reading Output
* Group 1 trades at **11.450149×**, while AutoNation trades at **10.037825×**.
* Because Group 1 is the higher-multiple peer, removing Group 1 must pull the peer median multiple down from 10.74× to AutoNation’s 10.04×.
* **Prediction Confirmed:** The implied price for Asbury falls from **$231.00 to $215.81**, a drop of **-$15.18** (-6.6%).

### Why One Remaining Peer Gives a Reference Estimate, Not a Range
* A **valuation range** requires observable dispersion between multiple independent market prices.
* With only one peer (AutoNation remaining), there is zero dispersion and zero degrees of freedom. The single remaining multiple (10.04×) yields a single point estimate ($215.81). Labeling a single observation as a "range" creates false precision; it serves strictly as a **reference estimate**.

---

## 6. Reflect — Explaining Before Applying

### Why the Comparison Does Not Prove Asbury Is Mispriced
* Asbury traded at **$243.03** on December 31, 2024, which is inside its two-peer implied range ($215.81 to $246.18) but above the peer median of **$231.00**.
* Trading at a premium to the peer median does not prove Asbury is overvalued:
  1. **Operational Outperformance:** Asbury may generate superior parts/service gross margins or stronger inventory turnover.
  2. **Capital Structure:** Asbury’s leverage profile or share repurchase aggressiveness may justify a higher multiple.
  3. **Methodological Limits:** Comparable multiples price by analogy to peers at a frozen snapshot in time; they do not establish intrinsic cash generation.

### Connection to Our Target Company (Tesla, Inc. / `TSLA`)
In Lab 08, when applying comparable multiples to Tesla:
* We cannot compare Tesla to legacy automotive OEMs (trading at 6–10× P/E) or pure software hyperscalers (trading at 30–45× P/E) without an explicit, source-supported peer-selection policy.
* Because Tesla’s market price ($356.09) is 9.0× its fundamental DCF value ($39.74), observing peer dispersion will be central to determining whether the market prices Tesla as an automotive manufacturer or a software monopoly.
