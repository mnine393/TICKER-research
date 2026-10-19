from __future__ import annotations
from dataclasses import dataclass, asdict
import pandas as pd

YEARS = [2026, 2027, 2028, 2029, 2030]  # first five full fiscal years after FY2025 seed

@dataclass
class Assumption:
    key: str; label: str; values: list[float]; kind: str; source: str; rationale: str; revision: str = "v1 | 2026-09-24 | initial model"
    def row(self): return asdict(self)

def defaults() -> dict[str, Assumption]:
    # Values are scenario-ready base values; judgment assumptions are intentionally editable.
    a = [
      Assumption("mass_delivery_growth", "Mass-market delivery growth", [.08,.10,.10,.08,.06], "judgment", "Tesla 2025 10-K Item 7; Tesla does not disclose category revenue", "Delivery mix is disclosed only at aggregate level; gradual volume growth reflects mature Model 3/Y demand and capacity utilization."),
      Assumption("other_delivery_growth", "Other-model delivery growth", [.12,.15,.12,.10,.08], "judgment", "Tesla 2025 10-K Item 7", "A modest recovery assumption for Cybertruck/S/X category; no separately reported revenue permits a hard estimate."),
      Assumption("mass_asp_change", "Mass-market ASP change", [-.03,-.02,-.01,0,.01], "judgment", "Tesla 2025 10-K Item 7 automotive revenue discussion", "Assumes pricing pressure eases as mix and product refreshes improve; it is not management guidance."),
      Assumption("other_asp_change", "Other-model ASP change", [-.02,0,.01,.01,.01], "judgment", "Tesla 2025 10-K Item 7", "Higher-priced model mix partially offsets discounting; disclosure is insufficient to separate ASP by category."),
      Assumption("energy_deploy_growth", "Energy deployment growth", [.22,.20,.18,.15,.12], "judgment", "Tesla 2025 10-K Item 7 (46.7 GWh 2025 deployments)", "Fades from strong reported storage deployment growth as the installed base scales."),
      Assumption("energy_asp_change", "Energy revenue per deployment change", [-.03,-.02,-.01,0,0], "judgment", "Tesla 2025 10-K Item 7 notes lower Megapack ASP", "Retains documented pricing pressure initially, then stabilizes."),
      Assumption("services_growth", "Services and other revenue growth", [.12,.11,.10,.09,.08], "judgment", "Tesla 2025 10-K Item 7", "Service/charging fleet attachment grows with installed vehicles; excludes unverified robotaxi revenue."),
      Assumption("auto_margin", "Automotive gross margin", [.17,.18,.19,.20,.20], "judgment", "Tesla 2025 10-K Item 7", "Moderate recovery from 2025 pricing pressure; regulatory credits are modeled separately and not embedded in core margin."),
      Assumption("energy_margin", "Energy gross margin", [.20,.21,.22,.22,.22], "judgment", "Tesla 2025 10-K Item 7", "Scale and manufacturing utilization support modest expansion; no unsupported step-change assumed."),
      Assumption("services_margin", "Services gross margin", [.05,.06,.07,.08,.08], "judgment", "Tesla 2025 10-K Item 7", "Gradual improvement from service/charging scale, with early investment retained."),
      Assumption("rd_pct", "R&D as % revenue", [.043,.042,.041,.040,.040], "judgment", "Tesla 2025 10-K Item 7", "Continued investment in AI and products, with modest scale leverage."),
      Assumption("sga_pct", "SG&A as % revenue", [.055,.053,.051,.050,.050], "judgment", "Tesla 2025 10-K Item 7", "Scale leverage assumption; excludes material one-off restructuring charges."),
      Assumption("capex_pct", "Capex as % revenue", [.16,.13,.11,.10,.09], "guidance", "Tesla 2025 10-K Item 7, 2026 outlook: capex expected to exceed $20bn", "2026 is set to reflect the stated >$20bn direction; later years normalize judgmentally."),
      Assumption("da_pct", "D&A as % opening PP&E", [.16,.16,.15,.15,.14], "judgment", "Tesla 2025 10-K Item 8 cash flow statement", "Proxy useful-life pattern calibrated to reported depreciation; editable."),
      Assumption("inventory_days", "Inventory days", [52,50,49,48,48], "judgment", "Tesla 2025 10-K balance sheet", "Gradual inventory efficiency improvement while maintaining global service stock."),
      Assumption("ar_days", "Receivables days", [18,18,18,18,18], "judgment", "Tesla 2025 10-K balance sheet", "Held near historical working-capital relationship; no guidance exists."),
      Assumption("ap_days", "Payables days", [70,69,68,68,68], "judgment", "Tesla 2025 10-K balance sheet", "Modest normalization while preserving supplier-payment cadence."),
      Assumption("deferred_pct", "Deferred revenue as % revenue", [.035,.035,.034,.034,.034], "judgment", "Tesla 2025 10-K balance sheet", "Continuity assumption for customer deposits and deferred services."),
      Assumption("tax_rate", "Effective tax rate", [.22,.22,.22,.22,.22], "judgment", "Tesla 2025 10-K Note 14", "Normalized rate; excludes discrete and non-recurring tax effects."),
      Assumption("minimum_cash", "Minimum operating cash", [8000]*5, "judgment", "Tesla 2025 10-K liquidity discussion", "Liquidity floor set as a conservative operating policy, not company guidance."),
      Assumption("rf", "Risk-free rate", [.042]*5, "history", "US Treasury / user editable market input", "Latest observable 10-year Treasury proxy; refreshed by user for valuation date."),
      Assumption("erp", "Equity risk premium", [.050]*5, "judgment", "Market convention", "Long-run ERP convention; it is not a Tesla filing fact."),
      Assumption("observed_beta", "Observed beta", [1.80]*5, "history", "Market-data provider / user editable", "Observed beta must be date-checked; used alongside bottom-up beta."),
      Assumption("terminal_growth", "Terminal growth", [.030]*5, "judgment", "Long-run nominal growth convention", "Conservative long-run nominal growth; validation requires it below cost of equity."),
      Assumption("share_growth", "Diluted share-count growth", [.010,.010,.008,.006,.005], "judgment", "Tesla 2025 10-K Note 4 and Note 13", "Captures SBC dilution net of assumed buybacks; no buyback authorization assumed unless entered."),
      Assumption("buybacks", "Buybacks", [0]*5, "history", "Tesla 2025 10-K cash flow statement", "Set to zero because no recurring authorization is assumed in seed forecast."),
    ]
    return {x.key:x for x in a}

def table(assumptions: dict[str, Assumption]) -> pd.DataFrame:
    return pd.DataFrame([x.row() for x in assumptions.values()])

def scenario(assumptions, name: str):
    # applies coherent changes, then reruns entire model; changes are never additive sensitivities
    import copy
    x=copy.deepcopy(assumptions)
    if name == "Bull":
        for k in ("mass_delivery_growth","other_delivery_growth","energy_deploy_growth","services_growth"): x[k].values=[v+.04 for v in x[k].values]
        for k in ("auto_margin","energy_margin","services_margin"): x[k].values=[v+.02 for v in x[k].values]
    elif name in ("Bear","Recession / Downside"):
        delivery = -.05 if name=="Bear" else -.10; margin = -.025 if name=="Bear" else -.05
        for k in ("mass_delivery_growth","other_delivery_growth","energy_deploy_growth","services_growth"): x[k].values=[v+delivery for v in x[k].values]
        for k in ("auto_margin","energy_margin","services_margin"): x[k].values=[v+margin for v in x[k].values]
        x["capex_pct"].values=[v+.02 for v in x["capex_pct"].values]
    return x
