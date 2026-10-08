# Assumption-Challenge Record

This main record contains the six highest-ranked drivers in the retained tornado table in [`Lab_09_proforma_fcfe.md`](../Lab_09_proforma_fcfe.md), plus cost of equity, terminal growth, robotaxi revenue, and capex. The requested `output/visible_output.md` is not currently in this repository, so confirm the six-driver order against the next visible-output export. Values are the base-case FY2026E → FY2030E path unless stated otherwise.

| Driver / value | Basis / source | Challenge | Evidence that would change it |
|---|---|---|---|
| Automotive sales cash GM: 21.0% → 22.0% | FY2025 19.2%; H1 2026 21.2% after segment D&A adjustment | **Lucas Timm (Marriott), Lab 11:** Why test only a ±1.0 percentage-point Tesla gross-margin range when margins can swing 3–5 points in a cycle? | Quarterly automotive margin, tariff/cost trends, and liquidity result from a wider but coherent downside case. |
| SG&A ex-D&A: 6.4% → 5.6% of revenue | FY2025 5.1%; H1 2026 6.5%, including CEO-award SBC | **(draft - Miles to review)** Is operating leverage realistic while new programs scale? | Quarterly SG&A, CEO-award expense, and revenue growth evidence. |
| R&D ex-D&A: 7.4% → 6.6% of revenue | FY2025 5.6%; H1 2026 7.4% | **(draft - Miles to review)** Does the fade understate AI, Optimus, and Cybercab spending? | R&D guidance, compute/capex disclosures, and sustained quarterly R&D intensity. |
| Capex: $25,000 → $15,000M | Q2 2026 10-Q p.35: >$25B in 2026; H1 actual $8,282M | **Lucas Timm (Marriott), Lab 12:** Why is 2026 capex $25B when FY2025 actual capex was $8,527M, and where is it verified? | The Q2 2026 10-Q p.35 supports 2026; future guidance, project cancellations, or disclosed factory/AI spending would change later years. |
| Model 3/Y ASP: $40.8 → $39.2k | Derived from automotive sales and delivery mix | **(draft - Miles to review)** Does the 2× other-model price allocation distort the derived ASP? | Tesla model-level revenue/ASP disclosure or a verified delivery/mix reconciliation. |
| Model 3/Y deliveries: 1,650 → 1,900k | FY2025 1,585k; H1 2026 810k, 8-K releases | **(draft - Miles to review)** Is a low-single-digit rebound defensible against China competition and an aging lineup? | New quarterly delivery releases, regional order/backlog evidence, or material pricing/model-refresh disclosure. |
| Cost of equity: 10.38% base (5.11% risk-free rate + 1.17 beta × 4.5% ERP) | [`Lab_12_presentation_review.md`](../Lab_12_presentation_review.md); `assumptions.py` valuation parameters | **(draft - Miles to review)** Is the bottom-up beta and 4.5% ERP more decision-useful than the observed-beta alternative? | Updated Treasury yield, beta regression, peer capital structures, or a justified ERP source. |
| Terminal growth: 3.0% | [`Lab_12_presentation_review.md`](../Lab_12_presentation_review.md); `assumptions.py` terminal-growth parameter | **(draft - Miles to review)** Does perpetual growth remain below cost of equity and consistent with a mature long-run Tesla cash-flow profile? | Long-run nominal-growth evidence or a changed cost-of-equity assumption. |
| Robotaxi/autonomy revenue: $0 → $8,000M | No separate disclosure; June 2025 service / H1 2026 Cybercab production reference | **(draft - Miles to review)** Does the base case value a business before separate revenue, cost, or unit economics are disclosed? | Separately reported Robotaxi/FSD revenue, take rate, fleet capex, utilization, and margin. |

## Appendix: other registry drivers (not load-bearing)

These drivers remain in the registry but are not one of the retained tornado top six and are not the additional valuation/Robotaxi drivers above. Values and sources only:

| Driver / value | Basis / source |
|---|---|
| Other-model deliveries: 58 → 360k; Other-model ASP: $80 → $47k; regulatory credits: $850 → $200M; automotive leasing revenue: $1,450 → $1,300M | FY2025/H1 2026 delivery, credit, and leasing disclosures in `assumptions.py` |
| Services growth: 35% → 14%; autonomy cash GM: 40%; energy storage: 50 → 95 GWh; energy revenue/GWh: $245 → $220M | Historical services/energy metrics and the no-disclosure autonomy judgment in `assumptions.py` |
| Leasing cash GM: 50%; services cash GM: 16% → 20%; energy cash GM: 29% → 30%; SBC: 4.2% → 3.4%; D&A rate: 13%; D&A in COGS: 67% | FY2025/H1 2026 derived margins, SBC, and D&A metrics in `assumptions.py` |
| Strategic investments: $2,002 → $0M; DSO: 17.6; DIO: 58.2; DPO: 62.8; prepaid: 8.03%; accrued liabilities: 20.88%; deferred revenue: 7.44% | H1 2026 investment and FY2023–25 working-capital history in `assumptions.py` |
| Debt issued: $6,000 → $3,000M; debt repaid: $5,000 → $2,500M; finance-lease additions: $140 → $80M; finance-lease principal: $80M; operating-lease growth: 8% | Cash-flow history and debt/lease maturity schedules in `assumptions.py` |
| Debt interest: 4.1%; cash yield: 3.91%; option/ESPP proceeds: $900M; gross share issuance: 0.6%; buybacks: $0 | FY2023–H1 2026 financing and equity history in `assumptions.py` |
| Minimum cash: 15%; NCI income: $60M; NCI distributions: $90M; effective tax rate: 26% → 23% | H1 2026 liquidity, NCI, and tax-rate history in `assumptions.py` |

## Partner-source record retained verbatim

The appendix intentionally omits challenges. The following preserves Lucas Timm’s third credited challenge exactly as it appeared in the prior record.

| Driver / value | Basis / source | Challenge | Evidence that would change it |
|---|---|---|---|
| Minimum cash: 15% of revenue | Tesla reported $43.5B cash/investments at 30-Jun-2026; no stated minimum | **Lucas Timm (Marriott), Lab 11/12:** The margin-range discussion identified that a wider downside can exhaust the $5B revolver and breach the $15B floor; is this liquidity boundary defensible? | Tesla liquidity policy, committed-facility terms, or a revised working-capital/capex stress test. |

<!-- Superseded pre-filtered record retained below temporarily for traceability; do not use it as the current challenge record.

Values are the current **base-case FY2026E → FY2030E** path in [`tsla_model/assumptions.py`](../tsla-proforma-model/tsla_model/assumptions.py). “Load-bearing” here means every operating driver in that registry, including drivers with a limited presentation or balance-sheet role. This is a working review record, not evidence that an outcome is likely.

| Driver / value | Basis / source | Challenge | Evidence that would change it |
|---|---|---|---|
| Model 3/Y deliveries: 1,650 → 1,900k | FY2025 1,585k; H1 2026 810k, 8-K releases | **(draft - Miles to review)** Is a low-single-digit rebound defensible against China competition and an aging lineup? | New quarterly delivery releases, regional order/backlog evidence, or material pricing/model-refresh disclosure. |
| Other-model deliveries: 58 → 360k | FY2025 50.9k; H1 2026 28.5k; Cybercab production reference | **(draft - Miles to review)** Does this embed an unsupported Cybercab/Semi ramp? | Disclosed Cybercab/Semi production, deliveries, orders, or commercial launch data. |
| Model 3/Y ASP: $40.8 → $39.2k | Derived from automotive sales and delivery mix | **(draft - Miles to review)** Does the 2× other-model price allocation distort the derived ASP? | Tesla model-level revenue/ASP disclosure or a verified delivery/mix reconciliation. |
| Other-model ASP: $80 → $47k | Derived at 2× Model 3/Y ASP | **(draft - Miles to review)** Is the assumed Cybercab mix and price decline evidence-based? | Cybercab pricing, mix, and recognized revenue disclosures. |
| Regulatory credits: $850 → $200M | FY2025 $1,993M; H1 2026 $526M; OBBBA context | **(draft - Miles to review)** Is the assumed run-off too steep or too slow given policy uncertainty? | New credit-program rules, Tesla credit revenue, or OEM compliance disclosures. |
| Automotive leasing revenue: $1,450 → $1,300M | FY2025 $1,712M; H1 2026 $745M | **(draft - Miles to review)** Does a stable $1.3B run rate ignore changes in lease penetration or residual values? | Lease-originations, operating-lease vehicle, and leasing-revenue disclosures. |
| Services growth: 35% → 14% | FY2025 $12,530M; H1 2026 +46% | **(draft - Miles to review)** Is H1 growth repeatable, or is it affected by one-off service/used-car mix? | Segment revenue disclosure, Supercharging utilization, and quarterly services growth. |
| Robotaxi/autonomy revenue: $0 → $8,000M | No separate disclosure; June 2025 service / H1 2026 Cybercab reference | **(draft - Miles to review)** Does the base case value a business before separate revenue, cost, or unit economics are disclosed? | Separately reported Robotaxi/FSD revenue, take rate, fleet capex, utilization, and margin. |
| Autonomy cash gross margin: 40% each year | No disclosure | **(draft - Miles to review)** Is 40% plausible after fleet depreciation, insurance, energy, cleaning, and remote operations? | Fleet unit economics or comparable commercial ride-hailing margins. |
| Energy storage deployed: 50 → 95 GWh | FY2023–25 14.7/31.4/46.7 GWh; H1 2026 22.3 GWh | **(draft - Miles to review)** Can capacity additions overcome tariffs and project timing? | Megafactory capacity, deployment, backlog, and tariff disclosures. |
| Energy revenue/GWh: $245 → $220M | Derived FY2025 $273M; H1 2026 $249M | **(draft - Miles to review)** Does falling revenue/GWh reflect mix, price, solar, or service rather than Megapack ASP? | Storage-only revenue/volume disclosure or contract-price evidence. |
| Automotive sales cash GM: 21.0% → 22.0% | FY2025 19.2%; H1 2026 21.2% after segment D&A adjustment | **Lucas Timm (Marriott), Lab 11:** Why test only a ±1.0 percentage-point Tesla gross-margin range when margins can swing 3–5 points in a cycle? | Quarterly automotive margin, tariff/cost trends, and liquidity result from a wider but coherent downside case. |
| Automotive leasing cash GM: 50% each year | FY2025 50.4%; H1 2026 51.3% | **(draft - Miles to review)** Can the lease portfolio run off without a residual-value or mix shock? | Lease-vehicle balances, lease margin, and residual-value disclosures. |
| Services cash GM: 16% → 20% | FY2025 12.5%; H1 2026 16.5% | **(draft - Miles to review)** Is margin expansion supported by scale rather than temporary mix? | Service/Supercharging profitability or cost disclosures. |
| Energy cash GM: 29% → 30% | FY2025 32.6%; H1 2026 32.2%; Q2 GAAP 20.4% tariff effect | **(draft - Miles to review)** Why does margin stabilize despite the stated tariff pressure? | Quarterly energy gross-margin and tariff-cost evidence. |
| R&D ex-D&A: 7.4% → 6.6% of revenue | FY2025 5.6%; H1 2026 7.4% | **(draft - Miles to review)** Does the fade understate AI, Optimus, and Cybercab spending? | R&D guidance, compute/capex disclosures, and sustained quarterly R&D intensity. |
| SG&A ex-D&A: 6.4% → 5.6% of revenue | FY2025 5.1%; H1 2026 6.5%, including CEO-award SBC | **(draft - Miles to review)** Is operating leverage realistic while new programs scale? | Quarterly SG&A, CEO-award expense, and revenue growth evidence. |
| SBC: 4.2% → 3.4% of revenue | FY2025 3.0%; H1 2026 4.3%; CEO award cost | **(draft - Miles to review)** Does the decline double-count the CEO award through the cost ratios? | Compensation-note expense recognition and updated award-status disclosure. |
| D&A rate: 13% each year | FY2024 13.1%; FY2025 13.3%; H1 2026 annualized 12.8% | **(draft - Miles to review)** Does a fixed rate fit a changing mix of factories, compute, and lease assets? | PP&E/asset-class useful-life and depreciation disclosures. |
| D&A in COGS: 67% each year | FY2025 67%; H1 2026 66% | **(draft - Miles to review)** Is this presentation split stable enough to retain? | Segment-note D&A disclosure. |
| Capex: $25,000 → $15,000M | Q2 2026 10-Q p.35: >$25B in 2026; H1 actual $8,282M | **Lucas Timm (Marriott), Lab 12:** Why is 2026 capex $25B when FY2025 actual capex was $8,527M, and where is it verified? | The Q2 2026 10-Q p.35 supports 2026; future guidance, project cancellations, or disclosed factory/AI spending would change later years. |
| Strategic investments: $2,002 → $0M | H1 2026 SpaceX purchase | **(draft - Miles to review)** Is zero future strategic investment reasonable after a large H1 purchase? | New investing-cash-flow or investment-note disclosures. |
| DSO: 17.6 days each year | FY2023 13.2; FY2024 16.5; FY2025 17.6 | **(draft - Miles to review)** Does the rising historical trend warrant a flat assumption? | Receivable balance and revenue-mix changes. |
| DIO: 58.2 days each year | FY2023 62.9; FY2024 54.7; FY2025 58.2 | **(draft - Miles to review)** Can inventory stay flat through new model and energy-storage ramps? | Inventory balance, production, and delivery disclosures. |
| DPO: 62.8 days each year | FY2023 66.6; FY2024 56.7; FY2025 62.8 | **(draft - Miles to review)** Is supplier financing stable under higher capex and tariff pressure? | Payables trend and supplier-payment disclosures. |
| Prepaid/current assets: 8.03% of revenue | FY2024 5.5%; FY2025 8.0% | **(draft - Miles to review)** Why hold at a recently elevated ratio? | Prepaid/other-current-asset composition in future filings. |
| Accrued/other liabilities: 20.88% of revenue | FY2024 16.2%; FY2025 20.9% | **(draft - Miles to review)** Does the increase represent sustainable operating liabilities or timing items? | Liability-note composition, warranty, tax, and capex-payable disclosures. |
| Deferred revenue: 7.44% of revenue | FY2024 6.6%; FY2025 7.4% | **(draft - Miles to review)** Could FSD, connectivity, or energy-contract recognition change the ratio? | Deferred-revenue roll-forward and FSD recognition disclosures. |
| Debt issued: $6,000 → $3,000M | FY2023–25 $3.9B/$5.7B/$5.6B; H1 2026 $4.7B | **(draft - Miles to review)** Is refinancing availability assumed without a cost or credit-spread stress? | ABS issuance, debt note, and financing-market evidence. |
| Debt repaid: $5,000 → $2,500M (with $5,500M in 2029) | Scheduled maturities plus H1 repayment | **(draft - Miles to review)** Are ABS amortization and the 2029 bullet fully captured? | Debt-maturity table and new securitization disclosures. |
| New finance leases: $140 → $80M | Liability rose $223M to $281M | **(draft - Miles to review)** Does a flat addition keep the liability stable for an economic reason or only mechanically? | Finance-lease additions and maturity disclosures. |
| Finance-lease principal: $80M each year | FY2026–30 maturity table | **(draft - Miles to review)** Does the schedule reflect new leases as well as existing contractual maturities? | Updated lease maturity table. |
| Operating-lease liability growth: 8% each year | Liabilities FY2024 $5,410M; FY2025 $6,343M; Q2 2026 $6,738M | **(draft - Miles to review)** Is 8% consistent with store/service/charger expansion plans? | Store, service-center, and Supercharger footprint data. |
| Debt/finance-lease interest rate: 4.1% each year | FY2025 interest expense ÷ average debt/leases | **(draft - Miles to review)** Does a flat effective rate ignore refinancing and rate-market changes? | New debt coupons, ABS yields, and interest-expense trend. |
| Cash interest yield: 3.91% each year | FY2025 4.17%; H1 2026 annualized 3.91% | **(draft - Miles to review)** Does the yield remain appropriate if cash is drawn down or rates move? | Treasury yields, investment balances, and interest-income disclosure. |
| Option/ESPP proceeds: $900M each year | FY2023–25 $700M/$1,241M/$1,186M; H1 2026 $468M | **(draft - Miles to review)** Is a three-year average appropriate with a changing share price and award mix? | Financing cash-flow and equity-plan disclosures. |
| Gross share issuance: 0.6% each year | Diluted shares 3,485M → 3,540M | **(draft - Miles to review)** Does historical dilution represent future awards and CEO-award contingencies? | Diluted-share reconciliation and award vesting status. |
| Buybacks: $0 each year | No FY2023–H1 2026 repurchases | **(draft - Miles to review)** Could capital-return policy change after capex moderates? | Board authorization or financing-cash-flow disclosure. |
| Minimum cash: 15% of revenue | Tesla reported $43.5B cash/investments at 30-Jun-2026; no stated minimum | **Lucas Timm (Marriott), Lab 11/12:** The margin-range discussion identified that a wider downside can exhaust the $5B revolver and breach the $15B floor; is this liquidity boundary defensible? | Tesla liquidity policy, committed-facility terms, or a revised working-capital/capex stress test. |
| NCI income: $60M each year | FY2024/25 $62M/$61M; H1 2026 $28M | **(draft - Miles to review)** Is a flat amount reasonable if subsidiary economics change? | NCI note and income-attribution disclosure. |
| NCI distributions: $90M each year | FY2023–25 $144M/$104M/$78M; H1 2026 $91M | **(draft - Miles to review)** Does the recent range justify a $90M steady state? | Financing cash-flow and NCI-note disclosures. |
| Effective tax rate: 26% → 23% | FY2024 20.4%; FY2025 27.0%; H1 2026 22.1%, including $274M release | **(draft - Miles to review)** Does convergence to 23% properly remove one-offs while reflecting CEO-award deductibility and jurisdiction mix? | Tax-footnote rate reconciliation, valuation allowances, and CEO-award tax treatment. |

## Partner-source record

The three Lucas entries above preserve the substantive peer challenges from [`Lab_11_proforma_sensitivity.md`](../Lab_11_proforma_sensitivity.md) and [`Lab_12_presentation_review.md`](../Lab_12_presentation_review.md). They are credited to **Lucas Timm (Marriott)**. Every other challenge is an explicitly labelled draft for Miles to review.
-->
