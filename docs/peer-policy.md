# Tesla Peer-Selection Policy

## Existing Lab 08 policy reused

This policy is carried forward from [`03_Comps/Lab_08_comps_dcf.md`](../03_Comps/Lab_08_comps_dcf.md), where it was stated before the candidate multiples were evaluated. Its core language is: “Candidates must design, engineer, and manufacture motor vehicles and powertrain hardware at commercial scale,” and candidates must report “positive annual GAAP diluted EPS” for the P/E screen. Lab 08 also excludes pure-play software businesses and makes negative-earnings companies unusable for P/E.

For the current model, the policy is applied in two layers:

1. **Business model and segment mix:** The peer must have a material vehicle/EV or stationary-energy operating business relevant to Tesla’s automotive and energy mix. Legacy OEMs may remain comparators, but their captive-finance debt, dealer networks, and ICE mix must be disclosed as limitations.
2. **Size and market relevance:** Prefer listed companies with sufficient market value and operating scale for a meaningful beta/multiple observation; smaller or less-mature EV/storage firms may be retained only as explicitly qualified reference points, not treated as identical businesses.
3. **Data availability and definition consistency:** Use companies with public financial statements and available market capitalization, debt, revenue, net income, and beta data at the relevant as-of date. Exclude a company from P/E when trailing annual GAAP net income is non-positive; retain it for EV/revenue only if the numerator and denominator are available and the limitation is stated.

## Candidate decisions

| Candidate | Business/segment fit | Data and earnings screen | Decision and use | Evidence |
|---|---|---|---|---|
| GM | Global vehicle manufacturer; relevant auto/EV reference, but legacy ICE, dealer, and captive-finance differences | Positive FY2025 GAAP EPS in Lab 08; current market-data fields available | Pass with qualification. Use for auto reference, beta, EV/revenue, and P/E when definitions are consistent. | [`03_Comps/Lab_08_comps_dcf.md`](../03_Comps/Lab_08_comps_dcf.md); [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Ford | Global vehicle manufacturer with Ford Model e; legacy/dealer/captive-finance limitations | Negative FY2025 GAAP EPS in Lab 08 | Fails P/E screen; may remain in beta/EV-revenue peer context only if its debt definition is documented. | [`03_Comps/Lab_08_comps_dcf.md`](../03_Comps/Lab_08_comps_dcf.md); [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Rivian | EV pure-play; closer EV production model, but materially smaller and loss-making | Revenue, debt, market cap, and beta available; net loss | Passes operating/data screen; fails P/E screen. Use in EV/revenue and bottom-up beta with a loss-making limitation. | [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Lucid | EV pure-play; small scale and financing-driven capital structure risk | Revenue, debt, market cap, and beta available; net loss | Passes data screen; fails P/E screen. Use only as a qualified EV/beta reference. | [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Enphase | Distributed energy technology; relevant energy-adjacent reference, not a vehicle manufacturer | Revenue, debt, market cap, beta, and positive net income available | Passes energy segment/data screen; use as a qualified energy peer for EV/revenue, beta, and P/E. | [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Fluence | Grid-scale storage; relevant to Tesla Energy but no automotive fit | Revenue, debt, market cap, beta available; net loss | Passes energy/data screen; fails P/E screen. Use as a qualified EV/beta reference. | [`seed_market.json`](../tsla-proforma-model/tsla_model/data/seed_market.json) |
| Lab 08 candidates beyond GM and Ford | None | Lab 08’s Tesla candidate table contains GM and Ford only. | No additional Lab 08 candidate is carried forward. | [`03_Comps/Lab_08_comps_dcf.md`](../03_Comps/Lab_08_comps_dcf.md) |

## Multiple definitions

| Multiple | Definition | Eligibility and interpretation |
|---|---|---|
| **EV / Revenue** (enterprise-value multiple) | **EV = market capitalization + debt − cash**; **EV/Revenue = EV ÷ latest fiscal-year revenue.** The model constructs EV from the peer market-cap and debt fields and uses `revenue_lfy` in `valuation.py:257-269`. | Available for the selected peer set when consistent market and financial fields exist. It is useful for loss-making firms but does not control for margins, growth, or reinvestment needs. |
| **P/E** (equity-value multiple) | **P/E = market price ÷ diluted EPS**, equivalently **market capitalization ÷ net income attributable to common shareholders.** `valuation.py:267-270` excludes non-positive net income. | Use only for profitable peers. Do not add cash or subtract debt from a P/E-derived equity value; Lab 07 explains that P/E already prices common equity. |

The current model labels multiples a secondary cross-check rather than an averaged target price. See `tsla_model/valuation.py` and [`Lab_12_presentation_review.md`](../Lab_12_presentation_review.md).
