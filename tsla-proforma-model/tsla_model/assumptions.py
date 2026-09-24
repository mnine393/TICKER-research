"""Central, editable assumption registry.

Every forecast driver lives here - one place - with:
  * ``kind``: "history" (held at / derived from reported data), "guidance" (company-stated),
    or "judgment" (analyst estimate; always carries a plain-English rationale),
  * ``source``: where the anchor number comes from,
  * scenario-specific values for each forecast year (FY2026E-FY2030E),
  * a revision history of every edit.

Historical reference values for each driver are derived from the seed data in
``historical_drivers`` so the UI can show "what the filings say" next to each assumption.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from . import config
from .data_ingestion import DataBundle

YEARS = config.FORECAST_YEARS
N = len(YEARS)
KINDS = ("history", "guidance", "judgment")


@dataclass
class Assumption:
    id: str
    label: str
    category: str
    unit: str              # "pct", "k_units", "usd_k", "usd_m", "gwh", "usd_m_per_gwh", "days", "ratio"
    kind: str
    source: str
    rationale: str
    values: dict           # scenario -> list[float] (len N)
    core: bool = False     # included in one-variable sensitivity / tornado
    shock: tuple = ("rel", 0.10)   # ("rel", 0.10) = +/-10% relative; ("abs", 0.01) = +/-1pt
    bounds: tuple = (None, None)

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"{self.id}: kind must be one of {KINDS}")
        if self.kind == "judgment" and not self.rationale.strip():
            raise ValueError(f"{self.id}: judgment assumptions require a rationale")
        base = self.values["base"]
        for s in config.SCENARIOS:
            self.values.setdefault(s, list(base))
            if len(self.values[s]) != N:
                raise ValueError(f"{self.id}/{s}: expected {N} yearly values")
            self.values[s] = [float(v) for v in self.values[s]]


@dataclass
class Param:
    """Single-value valuation / structural parameter."""
    id: str
    label: str
    value: object
    unit: str
    kind: str
    source: str
    rationale: str
    bounds: tuple = (None, None)


@dataclass
class Revision:
    timestamp: str
    item: str
    scenario: str
    year: str
    old: object
    new: object
    note: str = ""


@dataclass
class AssumptionSet:
    drivers: dict = field(default_factory=dict)   # id -> Assumption
    params: dict = field(default_factory=dict)    # id -> Param
    revisions: list = field(default_factory=list)

    # ---- access -------------------------------------------------------------------------
    def get(self, item: str, scenario: str = "base") -> np.ndarray:
        return np.array(self.drivers[item].values[scenario], dtype=float)

    def p(self, item: str):
        return self.params[item].value

    def copy(self) -> "AssumptionSet":
        return copy.deepcopy(self)

    # ---- editing (all edits are logged) -------------------------------------------------
    def set_value(self, item: str, scenario: str, year_idx: int, new: float, note: str = "") -> None:
        old = self.drivers[item].values[scenario][year_idx]
        if float(old) == float(new):
            return
        self.drivers[item].values[scenario][year_idx] = float(new)
        self.revisions.append(Revision(datetime.now().isoformat(timespec="seconds"), item, scenario,
                                       str(YEARS[year_idx]), old, float(new), note))

    def set_param(self, item: str, new, note: str = "") -> None:
        old = self.params[item].value
        if old == new:
            return
        self.params[item].value = new
        self.revisions.append(Revision(datetime.now().isoformat(timespec="seconds"), item, "all", "-", old, new, note))

    def shocked(self, item: str, scenario: str, direction: float, size: float | None = None) -> "AssumptionSet":
        """Return a copy with ``item`` shocked in every forecast year (no revision logged)."""
        new = self.copy()
        a = new.drivers[item]
        kind, default = a.shock
        amt = default if size is None else size
        vals = np.array(a.values[scenario], dtype=float)
        vals = vals * (1 + direction * amt) if kind == "rel" else vals + direction * amt
        lo, hi = a.bounds
        if lo is not None:
            vals = np.maximum(vals, lo)
        if hi is not None:
            vals = np.minimum(vals, hi)
        a.values[scenario] = list(vals)
        return new

    def scaled(self, item: str, scenario: str, factor: float = 1.0, add: float = 0.0) -> "AssumptionSet":
        new = self.copy()
        a = new.drivers[item]
        a.values[scenario] = list(np.array(a.values[scenario], dtype=float) * factor + add)
        return new

    def core_drivers(self) -> list[str]:
        return [k for k, a in self.drivers.items() if a.core]

    def table(self, scenario: str = "base"):
        import pandas as pd
        rows = []
        for a in self.drivers.values():
            row = {"ID": a.id, "Category": a.category, "Assumption": a.label, "Unit": a.unit, "Type": a.kind}
            for i, y in enumerate(YEARS):
                row[f"FY{y}E"] = a.values[scenario][i]
            row["Same as base"] = scenario != "base" and a.values[scenario] == a.values["base"]
            row["Source"] = a.source
            row["Rationale"] = a.rationale
            rows.append(row)
        return pd.DataFrame(rows)

    def params_table(self):
        import pandas as pd
        return pd.DataFrame([{"ID": p.id, "Parameter": p.label, "Value": p.value, "Unit": p.unit, "Type": p.kind,
                              "Source": p.source, "Rationale": p.rationale} for p in self.params.values()])

    def revisions_table(self):
        import pandas as pd
        cols = ["timestamp", "item", "scenario", "year", "old", "new", "note"]
        return pd.DataFrame([r.__dict__ for r in self.revisions], columns=cols)


# --------------------------------------------------------------------------------------------
# Historical driver derivations (shown next to assumptions; also used in tests)
# --------------------------------------------------------------------------------------------
OTHER_ASP_PREMIUM = 2.0  # judgment: "other models" ASP as a multiple of Model 3/Y ASP for history split


def historical_drivers(b: DataBundle) -> dict:
    """Derive driver metrics for FY2023-FY2025 and H1 2026 (annualised where relevant)."""
    out: dict = {}
    periods = ["FY2023", "FY2024", "FY2025", "H1_2026"]
    bs_map = {"FY2023": "FY2023", "FY2024": "FY2024", "FY2025": "FY2025", "H1_2026": "Q2_2026"}
    for p in periods:
        v = lambda k: b.value(k, p)
        ann = 2.0 if p == "H1_2026" else 1.0
        d3, do = v("deliveries_3y") / 1e3, v("deliveries_other") / 1e3
        asp3 = v("rev_auto_sales") / (d3 + OTHER_ASP_PREMIUM * do)
        # D&A embedded in segment cost of revenues; auto-segment D&A allocated pro-rata to COGS
        auto_cogs = v("cogs_auto_sales") + v("cogs_auto_leasing") + v("cogs_services")
        da_auto = v("da_cogs_auto")
        alloc = lambda c: da_auto * v(c) / auto_cogs
        cash_gm = lambda r, c: (v(r) - (v(c) - alloc(c))) / v(r)
        da_opex = v("da_total") - v("da_cogs_auto") - v("da_cogs_energy")
        opex = v("rd") + v("sga")
        rev = v("rev_total")
        q = bs_map[p]
        bsv = lambda k: b.value(k, q)
        nfa = bsv("ppe") + bsv("olv") + bsv("energy_systems")
        cogs_ann = v("cogs_total") * ann
        rev_ann = rev * ann
        out[p] = {
            "deliveries_3y": d3, "deliveries_other": do,
            "blended_asp": v("rev_auto_sales") / (d3 + do),
            "asp_3y": asp3, "asp_other": asp3 * OTHER_ASP_PREMIUM,
            "reg_credits": v("rev_reg_credits"), "auto_leasing_rev": v("rev_auto_leasing"),
            "services_rev": v("rev_services"),
            "storage_gwh": v("storage_gwh"), "energy_rev_per_gwh": v("rev_energy") / v("storage_gwh"),
            "gm_auto_sales": cash_gm("rev_auto_sales", "cogs_auto_sales"),
            "gm_leasing": cash_gm("rev_auto_leasing", "cogs_auto_leasing"),
            "gm_services": cash_gm("rev_services", "cogs_services"),
            "gm_energy": (v("rev_energy") - (v("cogs_energy") - v("da_cogs_energy"))) / v("rev_energy"),
            "gaap_gm_auto_sales": (v("rev_auto_sales") - v("cogs_auto_sales")) / v("rev_auto_sales"),
            "gaap_gm_energy": (v("rev_energy") - v("cogs_energy")) / v("rev_energy"),
            "gaap_gm_services": (v("rev_services") - v("cogs_services")) / v("rev_services"),
            "rd_pct": (v("rd") - da_opex * v("rd") / opex) / rev,
            "sga_pct": (v("sga") - da_opex * v("sga") / opex) / rev,
            "sbc_pct": v("sbc") / rev,
            "da_cogs_share": (v("da_cogs_auto") + v("da_cogs_energy")) / v("da_total"),
            "capex": v("capex"),
            "dso": bsv("ar") / rev_ann * 365, "dio": bsv("inventory") / cogs_ann * 365,
            "dpo": bsv("ap") / cogs_ann * 365, "prepaid_pct": bsv("prepaid") / rev_ann,
            "accrued_pct": (bsv("accrued_current") + bsv("other_ltl") - bsv("op_lease_liab")) / rev_ann,
            "deferred_rev_pct": (bsv("deferred_rev_current") + bsv("deferred_rev_noncurrent")) / rev_ann,
            "tax_rate": v("tax") / v("pretax"),
            "net_fixed_assets": nfa,
            "cash_and_investments": bsv("cash") + bsv("st_investments"),
        }
    # D&A rate on beginning net fixed assets
    for p, prev in (("FY2024", "FY2023"), ("FY2025", "FY2024"), ("H1_2026", "FY2025")):
        ann = 2.0 if p == "H1_2026" else 1.0
        out[p]["da_rate"] = b.value("da_total", p) * ann / out[prev]["net_fixed_assets"]
        prev_cash = out[prev]["cash_and_investments"]
        out[p]["interest_yield"] = b.value("interest_income", p) * ann / ((prev_cash + out[p]["cash_and_investments"]) / 2)
    out["FY2023"]["da_rate"] = np.nan
    out["FY2023"]["interest_yield"] = np.nan
    return out


# --------------------------------------------------------------------------------------------
# Default assumptions
# --------------------------------------------------------------------------------------------
def default_assumptions(b: DataBundle) -> AssumptionSet:
    h = historical_drivers(b)
    f25, h26 = h["FY2025"], h["H1_2026"]
    capex_guid = b.obligation("capex_guidance_2026")
    mats = b.obligation("debt_maturities")
    fl_pay = b.obligation("finance_lease_payments")
    revolver = b.obligation("unused_committed_credit_q2_2026")
    A = []

    def add(**kw):
        A.append(Assumption(**kw))

    # ---------------- Automotive volume & price ----------------
    add(id="deliveries_3y", label="Model 3/Y deliveries (thousand units)", category="Automotive volume & price",
        unit="k_units", kind="judgment", core=True, bounds=(0, None),
        source=f"8-K Ex. 99.1 delivery releases: FY2025 {f25['deliveries_3y']:,.0f}k; H1 2026 {h26['deliveries_3y']:,.0f}k",
        rationale="FY2026 = H1 2026 actual (~810k) plus an H2 slightly below H2 2025, which was pulled forward by the "
                  "Sept-2025 U.S. EV tax-credit expiry. Thereafter low-single-digit growth as the refreshed/standard "
                  "trims and new markets offset an ageing line-up and intensifying Chinese competition.",
        values={"base": [1650, 1720, 1790, 1850, 1900],
                "bull": [1690, 1830, 1970, 2100, 2220],
                "bear": [1610, 1620, 1650, 1680, 1710],
                "recession": [1620, 1380, 1450, 1560, 1640]})
    add(id="deliveries_other", label="Other models deliveries incl. Cybercab/Semi (thousand units)", category="Automotive volume & price",
        unit="k_units", kind="judgment", core=True, bounds=(0, None),
        source=f"8-K Ex. 99.1: FY2025 {f25['deliveries_other']:,.1f}k; H1 2026 {h26['deliveries_other']:,.1f}k; Cybercab production began H1 2026 (10-Q p.29)",
        rationale="S/X/Cybertruck volumes are small and declining; growth comes from Cybercab and Semi, which Tesla "
                  "began producing in 2026. The ramp is a judgment - Tesla gives no unit guidance.",
        values={"base": [58, 110, 190, 280, 360],
                "bull": [60, 160, 320, 520, 750],
                "bear": [55, 70, 100, 130, 160],
                "recession": [55, 60, 90, 140, 200]})
    add(id="asp_3y", label="Model 3/Y average selling price ($ thousand)", category="Automotive volume & price",
        unit="usd_k", kind="judgment", core=True, bounds=(10, None),
        source=f"Derived: automotive sales / (3Y + {OTHER_ASP_PREMIUM:.0f}x other deliveries). FY2025 ${f25['asp_3y']:.1f}k; H1 2026 ${h26['asp_3y']:.1f}k",
        rationale="Tesla does not disclose revenue by model. History is split assuming other models carry ~2x the 3/Y "
                  "price (list-price relationship). Forecast holds near the H1 2026 level, drifting down ~1%/yr for "
                  "price competition and mix toward cheaper trims; FSD revenue recognised in automotive sales supports ASP.",
        values={"base": [40.8, 40.4, 40.0, 39.6, 39.2],
                "bull": [41.2, 41.4, 41.6, 41.8, 42.0],
                "bear": [40.2, 39.4, 38.8, 38.4, 38.0],
                "recession": [40.4, 37.5, 37.0, 37.5, 38.0]})
    add(id="asp_other", label="Other models ASP ($ thousand)", category="Automotive volume & price",
        unit="usd_k", kind="judgment", core=False, bounds=(10, None),
        source=f"Derived history = {OTHER_ASP_PREMIUM:.0f}x 3/Y ASP (FY2025 ${f25['asp_other']:.0f}k)",
        rationale="Declines as the mix shifts from S/X/Cybertruck (~$80k+) toward Cybercab, which Tesla has said will be "
                  "priced far below current models; blended value reaches the high-$40ks by 2030.",
        values={"base": [80, 65, 55, 50, 47],
                "bull": [80, 62, 52, 48, 45],
                "bear": [78, 68, 60, 55, 52],
                "recession": [76, 64, 56, 52, 49]})
    add(id="reg_credits", label="Regulatory credit revenue ($M)", category="Automotive other revenue",
        unit="usd_m", kind="judgment", bounds=(0, None),
        source=f"10-K FY2025 p.37: ${f25['reg_credits']:,.0f}M (-28%); 10-Q Q2 2026 p.31: H1 ${h26['reg_credits']:,.0f}M (-49%); OBBBA restricted credit programs",
        rationale="FY2026 ~ H1 run-rate plus a smaller H2; then continued decline as U.S. programs are curtailed "
                  "(OBBBA) and other OEMs become self-sufficient in credits. High-margin, so the decline hits profit directly.",
        values={"base": [850, 500, 350, 250, 200],
                "bull": [950, 700, 500, 400, 300],
                "bear": [800, 300, 150, 100, 50],
                "recession": [800, 300, 150, 100, 50]})
    add(id="auto_leasing_rev", label="Automotive leasing revenue ($M)", category="Automotive other revenue",
        unit="usd_m", kind="judgment", bounds=(0, None),
        source=f"FY2025 ${f25['auto_leasing_rev']:,.0f}M; H1 2026 ${h26['auto_leasing_rev']:,.0f}M (10-Q p.31)",
        rationale="Only ~1-2% of deliveries are now subject to operating-lease accounting (8-K Ex. 99.1), so the lease "
                  "book is running off; revenue stabilises around $1.3B.",
        values={"base": [1450, 1350, 1300, 1300, 1300]})
    # ---------------- Services & autonomy ----------------
    add(id="services_growth", label="Services & other revenue growth (%)", category="Services & autonomy",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.05),
        source=f"FY2025 ${f25['services_rev']:,.0f}M (+19%); H1 2026 +46% YoY (10-Q p.31)",
        rationale="Paid Supercharging, insurance, used vehicles, parts and service scale with Tesla's growing installed fleet. "
                  "FY2026 reflects the +46% H1 run-rate tapering in H2; growth then fades toward mid-teens.",
        values={"base": [0.35, 0.20, 0.18, 0.16, 0.14],
                "bull": [0.38, 0.26, 0.24, 0.22, 0.20],
                "bear": [0.30, 0.12, 0.10, 0.08, 0.07],
                "recession": [0.30, 0.04, 0.08, 0.10, 0.10]})
    add(id="autonomy_rev", label="Robotaxi / autonomy network revenue ($M)", category="Services & autonomy",
        unit="usd_m", kind="judgment", core=True, bounds=(0, None),
        source="No separate disclosure. Robotaxi service launched June 2025; Cybercab production began H1 2026 (10-Q p.28-29)",
        rationale="Tesla does not report robotaxi revenue; any current amount sits in services & other. This line is an "
                  "explicit, isolated judgment for incremental ride-hailing revenue so its value contribution is visible. "
                  "Base assumes a gradual multi-city ramp; bear assumes no material commercial scale by 2030.",
        values={"base": [0, 800, 2500, 5000, 8000],
                "bull": [0, 2000, 7000, 15000, 25000],
                "bear": [0, 0, 300, 700, 1200],
                "recession": [0, 200, 800, 2000, 3500]})
    add(id="gm_autonomy", label="Autonomy revenue cash gross margin (%)", category="Services & autonomy",
        unit="pct", kind="judgment", shock=("abs", 0.05), bounds=(-1, 1),
        source="No disclosure",
        rationale="A company-owned fleet carries vehicle depreciation (captured via capex/D&A), energy, cleaning, "
                  "insurance and remote-operations costs. A 40% cash gross margin is an assumption, not a Tesla figure.",
        values={"base": [0.40] * 5, "bull": [0.50] * 5, "bear": [0.25] * 5, "recession": [0.35] * 5})
    # ---------------- Energy ----------------
    add(id="storage_gwh", label="Energy storage deployed (GWh)", category="Energy",
        unit="gwh", kind="judgment", core=True, bounds=(0, None),
        source=f"10-K: 14.7 / 31.4 / 46.7 GWh (FY2023-25); 10-Q p.28: H1 2026 {h26['storage_gwh']} GWh",
        rationale="Lathrop and Shanghai Megafactories are ramping and a Houston Megafactory is under construction "
                  "(10-Q p.30). Growth slows from the 2023-25 pace as tariffs weigh on the U.S. business.",
        values={"base": [50, 60, 72, 84, 95],
                "bull": [52, 68, 88, 110, 135],
                "bear": [47, 50, 54, 58, 62],
                "recession": [47, 44, 50, 58, 66]})
    add(id="energy_rev_per_gwh", label="Energy revenue per GWh deployed ($M/GWh)", category="Energy",
        unit="usd_m_per_gwh", kind="judgment", core=True, bounds=(50, None),
        source=f"Derived: FY2025 ${f25['energy_rev_per_gwh']:.0f}M; H1 2026 ${h26['energy_rev_per_gwh']:.0f}M (includes solar & services)",
        rationale="Megapack ASPs are falling (10-K p.38 cites lower Megapack ASP) as cell costs fall and competition "
                  "rises; the ratio drifts down ~2-3% per year from the H1 2026 level.",
        values={"base": [245, 238, 232, 226, 220],
                "bull": [250, 246, 242, 238, 234],
                "bear": [240, 228, 216, 205, 195],
                "recession": [240, 225, 215, 210, 205]})
    # ---------------- Margins (cash = excluding D&A) ----------------
    add(id="gm_auto_sales", label="Automotive sales cash gross margin, ex-D&A (%)", category="Margins",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.02), bounds=(-1, 1),
        source=f"Derived from 10-K/10-Q with segment D&A (Note 16): FY2025 {f25['gm_auto_sales']:.1%}; H1 2026 {h26['gm_auto_sales']:.1%}; GAAP FY2025 {f25['gaap_gm_auto_sales']:.1%}",
        rationale="Margins are modelled before D&A so capex and depreciation flow through explicitly. Base holds near the "
                  "H1 2026 level, with modest improvement from cost-down and own-cell/cathode ramps offset by tariffs.",
        values={"base": [0.210, 0.210, 0.215, 0.220, 0.220],
                "bull": [0.215, 0.225, 0.235, 0.245, 0.250],
                "bear": [0.200, 0.195, 0.190, 0.190, 0.190],
                "recession": [0.205, 0.160, 0.175, 0.190, 0.200]})
    add(id="gm_leasing", label="Automotive leasing cash gross margin (%)", category="Margins",
        unit="pct", kind="history", shock=("abs", 0.02), bounds=(-1, 1),
        source=f"Derived: FY2025 {f25['gm_leasing']:.1%}; H1 2026 {h26['gm_leasing']:.1%}",
        rationale="Held at the FY2025/H1 2026 level.",
        values={"base": [0.50] * 5})
    add(id="gm_services", label="Services & other cash gross margin (%)", category="Margins",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.02), bounds=(-1, 1),
        source=f"Derived: FY2025 {f25['gm_services']:.1%}; H1 2026 {h26['gm_services']:.1%}",
        rationale="Operating leverage in Supercharging and service as the fleet grows; H1 2026 already showed a step-up.",
        values={"base": [0.16, 0.17, 0.18, 0.19, 0.20],
                "bull": [0.17, 0.19, 0.21, 0.23, 0.25],
                "bear": [0.15, 0.14, 0.14, 0.14, 0.14],
                "recession": [0.15, 0.11, 0.13, 0.15, 0.16]})
    add(id="gm_energy", label="Energy cash gross margin, ex-D&A (%)", category="Margins",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.02), bounds=(-1, 1),
        source=f"Derived: FY2025 {f25['gm_energy']:.1%}; H1 2026 {h26['gm_energy']:.1%} (GAAP Q2 2026 fell to 20.4% on tariffs, 10-Q p.32)",
        rationale="Below the FY2025 level because the 10-Q flags tariffs weighing more heavily on energy than autos; "
                  "partially offset by manufacturing credits and Shanghai Megafactory scale.",
        values={"base": [0.29, 0.30, 0.30, 0.30, 0.30],
                "bull": [0.31, 0.32, 0.33, 0.33, 0.33],
                "bear": [0.27, 0.25, 0.24, 0.24, 0.24],
                "recession": [0.28, 0.23, 0.25, 0.26, 0.27]})
    # ---------------- Operating expenses ----------------
    add(id="rd_pct", label="R&D ex-D&A (% of revenue)", category="Operating expenses",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2025 {f25['rd_pct']:.1%}; H1 2026 {h26['rd_pct']:.1%}",
        rationale="AI training, Optimus and Cybercab keep R&D elevated at the H1 2026 intensity, easing slightly as revenue grows. "
                  "Bear keeps the base ratios (management trims spend as growth stalls); recession shows a temporary spike as revenue falls faster than costs.",
        values={"base": [0.074, 0.072, 0.070, 0.068, 0.066],
                "bull": [0.074, 0.070, 0.066, 0.063, 0.060],
                "recession": [0.075, 0.080, 0.076, 0.072, 0.070]})
    add(id="sga_pct", label="SG&A ex-D&A (% of revenue)", category="Operating expenses",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2025 {f25['sga_pct']:.1%}; H1 2026 {h26['sga_pct']:.1%} (includes 2025 CEO award SBC, 10-Q p.33)",
        rationale="Held near the H1 2026 ratio, which includes ~$1.1B/yr of 2025 CEO Performance Award expense; modest leverage thereafter. "
                  "Bear keeps the base ratios; recession shows a temporary spike as revenue falls faster than costs.",
        values={"base": [0.064, 0.062, 0.060, 0.058, 0.056],
                "bull": [0.064, 0.060, 0.057, 0.054, 0.052],
                "recession": [0.065, 0.070, 0.067, 0.064, 0.062]})
    add(id="sbc_pct", label="Stock-based compensation (% of revenue, non-cash, within costs)", category="Operating expenses",
        unit="pct", kind="judgment", shock=("abs", 0.005), bounds=(0, 1),
        source=f"CF statement: FY2025 {f25['sbc_pct']:.1%}; H1 2026 {h26['sbc_pct']:.1%}; $9.82B unrecognised CEO award cost over 9.2 yrs (10-Q p.21)",
        rationale="SBC is already inside the cost ratios above; this line only sizes the non-cash add-back and APIC build. "
                  "Declines as a share of revenue while CEO award expense stays roughly flat in dollars.",
        values={"base": [0.042, 0.040, 0.038, 0.036, 0.034]})
    # ---------------- D&A and capex ----------------
    add(id="da_rate", label="D&A (% of beginning net fixed assets)", category="D&A & capex",
        unit="pct", kind="history", core=True, shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2024 {h['FY2024']['da_rate']:.1%}; FY2025 {f25['da_rate']:.1%}; H1 2026 ann. {h26['da_rate']:.1%}",
        rationale="Held at the three-period average. Net fixed assets = PP&E + operating-lease vehicles + energy systems.",
        values={"base": [0.13] * 5})
    add(id="da_cogs_share", label="Share of D&A recorded in cost of revenues (%)", category="D&A & capex",
        unit="pct", kind="history", bounds=(0, 1),
        source=f"Segment note D&A in COGS / total D&A: FY2025 {f25['da_cogs_share']:.0%}; H1 2026 {h26['da_cogs_share']:.0%}",
        rationale="Presentation only (splits D&A between gross profit and opex); no effect on EBIT or cash flow.",
        values={"base": [0.67] * 5})
    add(id="capex", label="Capital expenditures ($M)", category="D&A & capex",
        unit="usd_m", kind="guidance", core=True, bounds=(0, None),
        source=f"10-Q Q2 2026 p.35: 2026 capex 'in excess of ${capex_guid/1000:,.0f} billion'; H1 2026 actual ${h26['capex']:,.0f}M",
        rationale="FY2026 = guidance floor. 2027-30 are judgment: AI compute, Cybercab/Optimus lines and cell factories "
                  "keep spend elevated before easing toward ~1.2x D&A. Bear and recession cases assume Tesla slows "
                  "projects as cash generation weakens, which the 10-Q (Liquidity section) says it can do; without that "
                  "cut the bear case breaches the minimum-cash rule even with the revolver fully drawn.",
        values={"base": [capex_guid, 22000, 18000, 16000, 15000],
                "bull": [capex_guid, 24000, 21000, 19000, 18000],
                "bear": [capex_guid, 16000, 12000, 11000, 10500],
                "recession": [capex_guid, 15000, 13000, 13000, 13000]})
    add(id="strategic_investment", label="Strategic equity investments ($M, non-operating)", category="D&A & capex",
        unit="usd_m", kind="history", bounds=(0, None),
        source="10-Q CF p.8-9: purchase of SpaceX equity investment $2,002M in H1 2026",
        rationale="H1 2026 actual; no further investments assumed. Excluded from FCFE and valued separately at carrying value.",
        values={"base": [2002, 0, 0, 0, 0]})
    # ---------------- Working capital ----------------
    add(id="dso", label="Receivable days (DSO, on revenue)", category="Working capital",
        unit="days", kind="history", core=True, shock=("abs", 3.0), bounds=(0, None),
        source=f"Derived: FY2023 {h['FY2023']['dso']:.1f}; FY2024 {h['FY2024']['dso']:.1f}; FY2025 {f25['dso']:.1f}",
        rationale="Held at the FY2025 level.", values={"base": [round(f25["dso"], 1)] * 5})
    add(id="dio", label="Inventory days (DIO, on cost of revenues)", category="Working capital",
        unit="days", kind="history", core=True, shock=("abs", 5.0), bounds=(0, None),
        source=f"Derived: FY2023 {h['FY2023']['dio']:.1f}; FY2024 {h['FY2024']['dio']:.1f}; FY2025 {f25['dio']:.1f}",
        rationale="Held at the FY2025 level; recession case assumes an inventory build.",
        values={"base": [round(f25["dio"], 1)] * 5,
                "recession": [round(f25["dio"], 1), 70, 64, round(f25["dio"], 1), round(f25["dio"], 1)]})
    add(id="dpo", label="Payable days (DPO, on cost of revenues)", category="Working capital",
        unit="days", kind="history", core=True, shock=("abs", 5.0), bounds=(0, None),
        source=f"Derived: FY2023 {h['FY2023']['dpo']:.1f}; FY2024 {h['FY2024']['dpo']:.1f}; FY2025 {f25['dpo']:.1f}",
        rationale="Held at the FY2025 level.", values={"base": [round(f25["dpo"], 1)] * 5})
    add(id="prepaid_pct", label="Prepaid & other current assets (% revenue)", category="Working capital",
        unit="pct", kind="history", shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2024 {h['FY2024']['prepaid_pct']:.1%}; FY2025 {f25['prepaid_pct']:.1%}",
        rationale="Held at the FY2025 level.", values={"base": [round(f25["prepaid_pct"], 4)] * 5})
    add(id="accrued_pct", label="Accrued & other liabilities ex-leases (% revenue)", category="Working capital",
        unit="pct", kind="history", shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived (current accrued + other LT liabilities - operating lease liabilities): FY2024 {h['FY2024']['accrued_pct']:.1%}; FY2025 {f25['accrued_pct']:.1%}",
        rationale="Held at the FY2025 level (warranty reserves, taxes, capex payables).",
        values={"base": [round(f25["accrued_pct"], 4)] * 5})
    add(id="deferred_rev_pct", label="Deferred revenue, current + non-current (% revenue)", category="Working capital",
        unit="pct", kind="history", shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2024 {h['FY2024']['deferred_rev_pct']:.1%}; FY2025 {f25['deferred_rev_pct']:.1%}",
        rationale="Held at the FY2025 level (FSD, connectivity, Supercharging and energy contracts).",
        values={"base": [round(f25["deferred_rev_pct"], 4)] * 5})
    # ---------------- Financing & capital structure ----------------
    add(id="debt_issued", label="New debt issuance ($M)", category="Financing & capital structure",
        unit="usd_m", kind="judgment", bounds=(0, None),
        source=f"CF history: $3.9B / $5.7B / $5.6B (FY2023-25); H1 2026 $4.7B (10-Q CF)",
        rationale="Tesla's debt is mostly non-recourse auto/energy ABS that is refinanced continuously. FY2026 = H1 actual "
                  "plus a smaller H2; later years roughly refinance scheduled maturities.",
        values={"base": [6000, 3000, 3000, 3000, 3000]})
    add(id="debt_repaid", label="Debt repayments ($M)", category="Financing & capital structure",
        unit="usd_m", kind="judgment", bounds=(0, None),
        source=f"10-K Note 9 p.75 scheduled maturities: " + ", ".join(f"{k} ${v:,}M" for k, v in mats.items()) + "; H1 2026 repaid $3.9B",
        rationale="FY2026 = H1 actual plus H2 scheduled amortisation; later years = scheduled maturities (incl. the 2029 "
                  "bullet) plus ABS amortisation of new issuance.",
        values={"base": [5000, 3000, 2500, 5500, 2500]})
    add(id="fl_additions", label="New finance leases ($M, non-cash)", category="Financing & capital structure",
        unit="usd_m", kind="judgment", bounds=(0, None),
        source="Finance lease liability $223M (FY2025) -> $281M (Q2 2026)",
        rationale="Small; set so the finance-lease balance stays roughly stable.", values={"base": [140, 80, 80, 80, 80]})
    add(id="fl_principal", label="Finance lease principal payments ($M)", category="Financing & capital structure",
        unit="usd_m", kind="history", bounds=(0, None),
        source="10-K Note 10 finance-lease maturity table: " + ", ".join(f"{k} ${v}M" for k, v in fl_pay.items()),
        rationale="Contractual schedule plus run-off of new leases.", values={"base": [80, 80, 80, 80, 80]})
    add(id="op_lease_growth", label="Operating lease liability growth (%, non-cash)", category="Financing & capital structure",
        unit="pct", kind="judgment", bounds=(-1, 1),
        source="Operating lease liabilities $5,410M -> $6,343M -> $6,738M (FY2024, FY2025, Q2 2026)",
        rationale="Store, service and Supercharger footprint growth; the ROU asset moves one-for-one, so no cash or equity effect.",
        values={"base": [0.08] * 5})
    add(id="interest_rate_debt", label="Interest rate on debt & finance leases (% of beginning balance)", category="Financing & capital structure",
        unit="pct", kind="history", shock=("abs", 0.01), bounds=(0, 1),
        source="FY2025 interest expense $338M / average debt & finance leases ~$8.3B = 4.1%",
        rationale="Held at FY2025 effective rate; applied to beginning balances to avoid circularity.",
        values={"base": [0.041] * 5})
    add(id="interest_yield_cash", label="Interest yield on cash & investments (% of beginning balance)", category="Financing & capital structure",
        unit="pct", kind="history", shock=("abs", 0.01), bounds=(0, 1),
        source=f"Derived: FY2025 {f25['interest_yield']:.2%}; H1 2026 ann. {h26['interest_yield']:.2%}",
        rationale="Held at the H1 2026 annualised yield. Excluded from valuation FCFE (cash is valued separately).",
        values={"base": [round(h26["interest_yield"], 4)] * 5})
    add(id="option_proceeds", label="Proceeds from option exercises / ESPP ($M)", category="Financing & capital structure",
        unit="usd_m", kind="history", bounds=(0, None),
        source="CF history: $700M / $1,241M / $1,186M (FY2023-25); H1 2026 $468M",
        rationale="Approximately the three-year average.", values={"base": [900] * 5})
    add(id="share_issuance_pct", label="Gross share issuance from equity plans (% of beginning diluted shares)", category="Financing & capital structure",
        unit="pct", kind="history", bounds=(0, 1),
        source="Diluted weighted shares 3,485M -> 3,498M -> 3,528M -> 3,540M (FY2023 to Q2 2026)",
        rationale="Average historical net dilution of ~0.6%/yr.", values={"base": [0.006] * 5})
    add(id="buybacks", label="Share repurchases ($M)", category="Financing & capital structure",
        unit="usd_m", kind="history", bounds=(0, None),
        source="No repurchases in FY2023-FY2025 or H1 2026 cash-flow statements",
        rationale="No authorised programme is disclosed; kept at zero. Editable to test a buyback policy.",
        values={"base": [0] * 5})
    add(id="min_cash_pct", label="Minimum cash & investments (% of revenue)", category="Financing & capital structure",
        unit="pct", kind="judgment", bounds=(0, 1),
        source="Tesla does not state a minimum; it held $43.5B (86% of H1 2026 annualised revenue) at 2026-06-30",
        rationale="About two months of costs is a prudent operating buffer for a capital-intensive manufacturer. Cash above "
                  "this level is treated as excess (non-operating) in the valuation.",
        values={"base": [0.15] * 5})
    add(id="nci_income", label="Net income attributable to NCI ($M)", category="Tax & other",
        unit="usd_m", kind="history", source="$62M / $61M (FY2024-25); H1 2026 $28M",
        rationale="Held at recent level.", values={"base": [60] * 5})
    add(id="nci_distributions", label="Distributions to NCI ($M)", category="Tax & other",
        unit="usd_m", kind="history", source="$144M / $104M / $78M (FY2023-25); H1 2026 $91M",
        rationale="Held near recent level.", values={"base": [90] * 5})
    add(id="tax_rate", label="Effective tax rate (%)", category="Tax & other",
        unit="pct", kind="judgment", core=True, shock=("abs", 0.03), bounds=(0, 1),
        source=f"FY2024 {h['FY2024']['tax_rate']:.1%}; FY2025 {f25['tax_rate']:.1%}; H1 2026 {h26['tax_rate']:.1%} incl. $274M CA valuation-allowance release (10-Q p.23)",
        rationale="Non-deductible 2025 CEO award expense (10-Q p.23) lifts the rate while pre-tax income is small; it "
                  "converges toward ~23% as profits grow. One-off valuation-allowance releases are excluded.",
        values={"base": [0.26, 0.25, 0.24, 0.23, 0.23]})

    s = AssumptionSet(drivers={a.id: a for a in A})

    m = b.market
    P = [
        Param("risk_free", "Risk-free rate (10-year U.S. Treasury)", m["risk_free"]["value"], "pct", "history",
              f"{m['risk_free']['source']}, {m['risk_free']['as_of']}", "Observed market yield matching the long-dated equity cash flows.", (0.0, 0.15)),
        Param("erp", "Equity risk premium", 0.045, "pct", "judgment", "Analyst judgment",
              "Within the ~4-5% range of implied U.S. ERP estimates (e.g. Damodaran's monthly implied ERP) in 2024-2026. "
              "Update to the latest estimate before use.", (0.02, 0.10)),
        Param("beta_method", "Beta used in CAPM", "bottom-up", "choice", "judgment", "Model setting",
              "Bottom-up peer beta is less noisy than a single regression and reflects the business mix; the observed "
              "regression beta is shown as an alternative discount-rate case.", (None, None)),
        Param("beta_observed", "Observed TSLA beta (5y monthly vs S&P 500)", m["tsla_beta_observed"]["value"], "ratio", "history",
              f"{m['tsla_beta_observed']['source']}, {m['tsla_beta_observed']['as_of']}", m["tsla_beta_observed"]["method"], (0.0, 4.0)),
        Param("peer_weight_auto", "Bottom-up beta: weight on auto peers vs energy peers", 0.85, "pct", "judgment",
              "Revenue mix: automotive & services ~87% / energy ~13% of FY2025 revenue (10-K p.37)",
              "Weights the unlevered-beta averages of the auto (legacy + EV) and energy peer groups by Tesla's revenue mix.", (0.0, 1.0)),
        Param("tax_rate_beta", "Marginal tax rate for relevering", 0.21, "pct", "history", "U.S. federal statutory rate",
              "Standard Hamada relevering input.", (0.0, 0.5)),
        Param("terminal_growth", "Terminal FCFE growth (Gordon)", 0.03, "pct", "judgment", "Analyst judgment",
              "Below the 5.1% risk-free rate (a proxy for long-run nominal growth); a mature Tesla growing with nominal GDP.", (-0.02, 0.08)),
        Param("terminal_capex_to_da", "Terminal capex / D&A", 1.15, "ratio", "judgment", "Analyst judgment",
              "In steady state capex must exceed depreciation enough to fund growth; 1.15x supports ~3% growth on "
              "Tesla's asset base without the 2026-28 AI/capacity build-out.", (0.8, 2.5)),
        Param("add_back_sbc", "Add back SBC as a non-cash charge in FCFE", True, "bool", "judgment", "Model setting",
              "The requested FCFE definition adds back non-cash charges. Because SBC is a real economic cost, set this to "
              "False for a conservative case; share dilution is modelled separately.", (None, None)),
        Param("include_ceo_award_shares", "Include 423.7M unearned 2025 CEO award shares in diluted count", False, "bool", "judgment",
              "10-Q Note 9 p.21", "Excluded by default, consistent with GAAP diluted EPS (not yet earned). Set to True to "
              "value per share as if all market-cap milestones (which imply a far higher price) are achieved.", (None, None)),
        Param("mid_year", "Mid-period discounting convention", False, "bool", "judgment", "Model setting",
              "End-of-period discounting by default (more conservative); mid-period assumes cash arrives evenly.", (None, None)),
        Param("revolver_capacity", "Revolver capacity ($M)", revolver, "usd_m", "history",
              "10-Q Q2 2026 p.35: $5.00B unused committed credit", "Only drawn if cash falls below the minimum.", (0, 50000)),
        Param("revolver_rate", "Revolver interest rate", 0.060, "pct", "judgment", "Analyst judgment",
              "Approximately SOFR plus an investment-grade margin; only matters if the revolver is drawn.", (0.0, 0.2)),
        Param("pe_multiple_low", "Cross-check: forward P/E low", 15.0, "ratio", "judgment", "Analyst judgment",
              "Roughly a large-cap industrial/auto multiple; secondary cross-check only.", (1, 200)),
        Param("pe_multiple_high", "Cross-check: forward P/E high", 40.0, "ratio", "judgment", "Analyst judgment",
              "Roughly a high-growth large-cap technology multiple; secondary cross-check only.", (1, 300)),
    ]
    s.params = {p.id: p for p in P}
    return s
