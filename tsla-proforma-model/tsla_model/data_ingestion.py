"""Data ingestion: seed data, live SEC EDGAR retrieval, live market data and the source table.

Design:
* ``seed_filings.json`` holds every historical line item with its filing, page/section and
  accession number. It was compiled from Tesla's FY2023-FY2025 10-Ks, the Q2 2026 10-Q and the
  8-K Ex. 99.1 production/delivery releases.
* At runtime we try to (1) discover the most recent 10-K/10-Q filings through the EDGAR
  submissions API, (2) verify every XBRL-tagged seed value against the companyfacts API and
  (3) refresh market inputs (price, 10-year Treasury, betas, peer market caps).
* Any failure falls back to the seed values and is recorded in ``DataBundle.status`` so the UI can
  show exactly what is live and what is fallback.
"""
from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime

import numpy as np
import pandas as pd

from . import config

try:  # requests is optional at import time so tests can run offline
    import requests
except ImportError:  # pragma: no cover
    requests = None

HTTP_TIMEOUT = 12
BROWSER_UA = {"User-Agent": "Mozilla/5.0 (educational valuation model)"}


def _sec_headers() -> dict:
    return {"User-Agent": os.environ.get("SEC_USER_AGENT", config.DEFAULT_SEC_USER_AGENT)}


@dataclass
class DataBundle:
    financials: dict            # full seed_financials structure (possibly with live flags)
    market: dict                # price, risk_free, beta, peers
    status: list = field(default_factory=list)          # (component, "live"|"fallback"|"warning"|"info", message)
    verification: dict = field(default_factory=dict)     # (item, period) -> "match"|"mismatch: x"|...
    latest_filings: list = field(default_factory=list)   # dicts from submissions API

    # -------- convenience accessors --------
    def value(self, item: str, period: str) -> float:
        li = self.financials["line_items"].get(item) or self.financials["operating"].get(item)
        return float(li["values"][period])

    def series(self, item: str) -> dict:
        li = self.financials["line_items"].get(item) or self.financials["operating"].get(item)
        return dict(li["values"])

    def obligation(self, key: str):
        ob = self.financials["obligations"][key]
        return ob.get("values", ob.get("value"))

    @property
    def is_live(self) -> bool:
        return any(s[1] == "live" for s in self.status)


# --------------------------------------------------------------------------------------------
# Seed loading
# --------------------------------------------------------------------------------------------
def load_seed() -> DataBundle:
    with open(config.SEED_FINANCIALS, encoding="utf-8") as fh:
        fin = json.load(fh)
    with open(config.SEED_MARKET, encoding="utf-8") as fh:
        mkt = json.load(fh)
    b = DataBundle(financials=fin, market=mkt)
    b.status.append(("seed", "info", f"Seed data compiled {fin['meta']['seed_compiled']} loaded (used wherever live data is unavailable)."))
    return b


# --------------------------------------------------------------------------------------------
# SEC EDGAR
# --------------------------------------------------------------------------------------------
def fetch_recent_filings(n_10k: int = 3, n_10q: int = 1) -> list[dict]:
    url = f"https://data.sec.gov/submissions/CIK{config.CIK:010d}.json"
    r = requests.get(url, headers=_sec_headers(), timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    rec = r.json()["filings"]["recent"]
    out, k, q = [], 0, 0
    for i, form in enumerate(rec["form"]):
        if form == "10-K" and k < n_10k:
            k += 1
        elif form == "10-Q" and q < n_10q:
            q += 1
        else:
            continue
        acc = rec["accessionNumber"][i]
        out.append({
            "form": form,
            "filed": rec["filingDate"][i],
            "period_end": rec["reportDate"][i],
            "accession": acc,
            "url": f"https://www.sec.gov/Archives/edgar/data/{config.CIK}/{acc.replace('-', '')}/{rec['primaryDocument'][i]}",
        })
        if k >= n_10k and q >= n_10q:
            break
    return out


def fetch_companyfacts() -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{config.CIK:010d}.json"
    r = requests.get(url, headers=_sec_headers(), timeout=HTTP_TIMEOUT * 2)
    r.raise_for_status()
    return r.json()


_PERIOD_WINDOWS = {
    "FY2023": ("2023-12-31", 350, 380),
    "FY2024": ("2024-12-31", 350, 380),
    "FY2025": ("2025-12-31", 350, 380),
    "H1_2026": ("2026-06-30", 170, 190),
}
_INSTANTS = {"FY2023": "2023-12-31", "FY2024": "2024-12-31", "FY2025": "2025-12-31", "Q2_2026": "2026-06-30"}


def xbrl_value(facts: dict, tag: str, period: str, instant: bool) -> float | None:
    """Return the value (USD millions or shares in millions) for a tag/period, or None."""
    node = facts.get("facts", {}).get("us-gaap", {}).get(tag)
    if not node:
        return None
    unit_vals = next(iter(node["units"].values()))
    scale = 1e6
    for v in unit_vals:
        if instant:
            if "start" in v or v["end"] != _INSTANTS.get(period):
                continue
        else:
            if "start" not in v or period not in _PERIOD_WINDOWS:
                continue
            end, lo, hi = _PERIOD_WINDOWS[period]
            days = (date.fromisoformat(v["end"]) - date.fromisoformat(v["start"])).days
            if v["end"] != end or not (lo <= days <= hi):
                continue
        return float(v["val"]) / scale
    return None


def verify_against_xbrl(bundle: DataBundle, facts: dict) -> None:
    """Compare every XBRL-tagged seed line item with the live companyfacts value."""
    n_match = n_mis = 0
    for item, li in bundle.financials["line_items"].items():
        tag = li.get("xbrl")
        if not tag:
            continue
        instant = li["stmt"] == "BS"
        for period, seed_v in li["values"].items():
            live_v = xbrl_value(facts, tag, period, instant)
            if live_v is None and li.get("xbrl_components"):
                parts = [xbrl_value(facts, t, period, instant) for t in li["xbrl_components"]]
                live_v = sum(parts) if all(x is not None for x in parts) else None
            if live_v is None:
                bundle.verification[(item, period)] = "not found in XBRL"
                continue
            if abs(live_v - float(seed_v)) <= max(1.0, 0.001 * abs(float(seed_v))):
                bundle.verification[(item, period)] = "XBRL match"
                n_match += 1
            else:
                bundle.verification[(item, period)] = f"XBRL mismatch (live {live_v:,.0f})"
                n_mis += 1
    level = "live" if n_mis == 0 else "warning"
    bundle.status.append(("SEC XBRL verification", level,
                          f"{n_match} seed values matched live XBRL; {n_mis} mismatches."))


def refresh_sec(bundle: DataBundle) -> None:
    try:
        filings = fetch_recent_filings()
        bundle.latest_filings = filings
        seed_accs = {f["accession"] for f in bundle.financials["filings"].values()}
        newer = [f for f in filings if f["accession"] not in seed_accs]
        if newer:
            msg = ", ".join(f"{f['form']} for period ending {f['period_end']} (filed {f['filed']})" for f in newer)
            bundle.status.append(("SEC filings", "warning",
                                  f"Newer filing(s) detected at runtime: {msg}. The model base remains "
                                  f"FY2025A + H1 2026; update data/seed_filings.json to roll the base forward."))
        else:
            bundle.status.append(("SEC filings", "live",
                                  "Seed uses the most recent three 10-Ks and latest 10-Q available on EDGAR."))
    except Exception as exc:  # network or parsing failure
        bundle.status.append(("SEC filings", "fallback", f"EDGAR submissions unavailable ({exc.__class__.__name__}); using seed filing list."))
    try:
        facts = fetch_companyfacts()
        verify_against_xbrl(bundle, facts)
    except Exception as exc:
        bundle.status.append(("SEC XBRL verification", "fallback", f"companyfacts unavailable ({exc.__class__.__name__}); seed values unverified this session."))


# --------------------------------------------------------------------------------------------
# Market data
# --------------------------------------------------------------------------------------------
def fetch_price(ticker: str = config.TICKER) -> tuple[float, str]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1d"
    r = requests.get(url, headers=BROWSER_UA, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    meta = r.json()["chart"]["result"][0]["meta"]
    ts = datetime.fromtimestamp(meta["regularMarketTime"]).date().isoformat()
    return float(meta["regularMarketPrice"]), ts


def fetch_risk_free() -> tuple[float, str]:
    yr = date.today().year
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
           f"{yr}/all?type=daily_treasury_yield_curve&field_tdr_date_value={yr}&page&_format=csv")
    try:
        df = pd.read_csv(url, storage_options=BROWSER_UA)
        row = df.iloc[0]
        return float(row["10 Yr"]) / 100.0, pd.to_datetime(row["Date"]).date().isoformat()
    except Exception:
        df = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")
        df = df[pd.to_numeric(df.iloc[:, 1], errors="coerce").notna()]
        row = df.iloc[-1]
        return float(row.iloc[1]) / 100.0, str(row.iloc[0])


def _monthly_closes(ticker: str) -> pd.Series:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5y&interval=1mo"
    r = requests.get(url, headers=BROWSER_UA, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    return pd.Series(res["indicators"]["adjclose"][0]["adjclose"], index=res["timestamp"], dtype=float)


def regression_beta(stock: pd.Series, market: pd.Series) -> tuple[float, int]:
    """OLS beta of periodic returns: cov(r_s, r_m) / var(r_m)."""
    df = pd.concat([stock, market], axis=1, join="inner").dropna()
    rets = df.pct_change().dropna()
    if len(rets) < 24:
        raise ValueError("insufficient return history")
    rs, rm = rets.iloc[:, 0].to_numpy(), rets.iloc[:, 1].to_numpy()
    beta = float(np.cov(rs, rm, ddof=1)[0, 1] / np.var(rm, ddof=1))
    return beta, len(rets)


def fetch_market_cap(ticker: str) -> float:
    url = f"https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks"
    r = requests.get(url, headers=BROWSER_UA, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    raw = r.json()["data"]["summaryData"]["MarketCap"]["value"]
    return float(str(raw).replace(",", "")) / 1e6


def refresh_market(bundle: DataBundle) -> None:
    m = bundle.market
    today = date.today().isoformat()
    try:
        px, asof = fetch_price()
        m["price"] = {"value": px, "as_of": asof, "source": "Yahoo Finance chart API (live)", "type": "history"}
        bundle.status.append(("Share price", "live", f"TSLA ${px:,.2f} as of {asof}."))
    except Exception as exc:
        bundle.status.append(("Share price", "fallback", f"Live price unavailable ({exc.__class__.__name__}); seed ${m['price']['value']:,.2f} as of {m['price']['as_of']}."))
    try:
        rf, asof = fetch_risk_free()
        m["risk_free"] = {"value": rf, "as_of": asof, "source": "U.S. Treasury 10-year par yield (live; FRED DGS10 fallback)", "type": "history"}
        bundle.status.append(("Risk-free rate", "live", f"10-year Treasury {rf:.2%} as of {asof}."))
    except Exception as exc:
        bundle.status.append(("Risk-free rate", "fallback", f"Treasury/FRED unavailable ({exc.__class__.__name__}); seed {m['risk_free']['value']:.2%}."))
    try:
        spx = _monthly_closes("%5EGSPC")
        b, n = regression_beta(_monthly_closes(config.TICKER), spx)
        m["tsla_beta_observed"] = {"value": round(b, 3), "as_of": today, "method": f"OLS slope, 5y monthly returns vs S&P 500, {n} observations",
                                   "source": "Yahoo Finance chart API (live)", "type": "history"}
        from concurrent.futures import ThreadPoolExecutor

        def peer_live(p):
            try:
                return p, round(regression_beta(_monthly_closes(p["ticker"]), spx)[0], 3), round(fetch_market_cap(p["ticker"]), 0)
            except Exception:
                return p, None, None

        n_ok = 0
        with ThreadPoolExecutor(max_workers=6) as pool:
            for p, beta_p, mcap in pool.map(peer_live, m["peers"]):
                if beta_p is None:
                    p["notes"] = p.get("notes", "") + " [live refresh failed: seed beta/market cap used]"
                    continue
                p["beta"], p["market_cap"] = beta_p, mcap
                n_ok += 1
        m["peer_market_data"] = {**m.get("peer_market_data", {}), "as_of": today}
        bundle.status.append(("Betas", "live", f"TSLA observed beta {b:.2f}; {n_ok}/{len(m['peers'])} peers refreshed live."))
    except Exception as exc:
        bundle.status.append(("Betas", "fallback", f"Price history unavailable ({exc.__class__.__name__}); seed betas used."))


def get_data(live: bool = True) -> DataBundle:
    """Main entry point. Always returns a usable bundle (seed fallback on any failure)."""
    bundle = load_seed()
    bundle.financials = copy.deepcopy(bundle.financials)
    if live and requests is not None:
        refresh_sec(bundle)
        refresh_market(bundle)
    elif live:
        bundle.status.append(("network", "fallback", "requests not installed; seed data only."))
    else:
        bundle.status.append(("network", "fallback", "Offline mode selected; seed data only."))
    return bundle


# --------------------------------------------------------------------------------------------
# Source table
# --------------------------------------------------------------------------------------------
def _source_type(form: str) -> str:
    if form.startswith("10-K"):
        return "Annual report (10-K)"
    if form.startswith("10-Q"):
        return "Quarterly report (10-Q)"
    if form.startswith("8-K"):
        return "Current report (8-K Ex. 99.1, IR release filed with SEC)"
    return form


def build_source_table(bundle: DataBundle) -> pd.DataFrame:
    fin = bundle.financials
    filings, smap = fin["filings"], fin["source_map"]
    rows = []

    def add(item, li, period, src, section):
        doc = filings[src["doc"]]
        rows.append({
            "Item ID": item, "Line item": li["label"], "Section": section, "Period": period,
            "Value": li["values"][period] if period in li["values"] else li.get("value"),
            "Unit": li.get("unit", "USD m") if section != "Operating KPI" else ("units" if "deliveries" in item else "GWh"),
            "Filing / document": f"{doc['form']} - {doc['period']}", "Accession": doc["accession"],
            "Page / section": src["loc"], "Source type": _source_type(doc["form"]),
            "Verification": bundle.verification.get((item, period), "not XBRL-tagged (read from filing text)"),
            "Notes": li.get("notes", ""), "URL": doc["url"],
        })

    for item, li in fin["line_items"].items():
        for period in li["values"]:
            src = (li.get("source") or {}).get(period) or smap[li["stmt"]][period]
            add(item, li, period, src, {"IS": "Income statement", "BS": "Balance sheet", "CF": "Cash flow", "SEG": "Segment note"}[li["stmt"]])
    for item, li in fin["operating"].items():
        for period in li["values"]:
            add(item, li, period, li["source"][period], "Operating KPI")
    for key, ob in fin["obligations"].items():
        doc = filings[ob["source"]["doc"]]
        val = ob.get("value", None)
        if val is None:
            val = "; ".join(f"{k}: {v:,}" for k, v in ob["values"].items())
        rows.append({"Item ID": key, "Line item": ob["label"], "Section": "Obligations / guidance", "Period": "as disclosed",
                     "Value": val, "Unit": "USD m" if "shares" not in key else "shares m",
                     "Filing / document": f"{doc['form']} - {doc['period']}", "Accession": doc["accession"],
                     "Page / section": ob["source"]["loc"], "Source type": _source_type(doc["form"]),
                     "Verification": "read from filing text", "Notes": ob.get("qualifier", ""), "URL": doc["url"]})
    m = bundle.market
    for key in ("price", "risk_free", "tsla_beta_observed"):
        rows.append({"Item ID": key, "Line item": key.replace("_", " "), "Section": "Market data", "Period": m[key]["as_of"],
                     "Value": m[key]["value"], "Unit": "USD/share" if key == "price" else "ratio",
                     "Filing / document": m[key]["source"], "Accession": "", "Page / section": m[key].get("method", ""),
                     "Source type": "Market data", "Verification": "live" if "live" in m[key]["source"] else "seed",
                     "Notes": "", "URL": ""})
    for p in m["peers"]:
        rows.append({"Item ID": f"peer_{p['ticker']}", "Line item": f"Peer {p['ticker']} beta / market cap / debt", "Section": "Market data",
                     "Period": m["peer_market_data"]["as_of"], "Value": f"beta {p['beta']}, mcap {p['market_cap']:,.0f}, debt {p['debt']:,.0f}",
                     "Unit": "mixed", "Filing / document": "Yahoo/Nasdaq market data; SEC XBRL (debt)", "Accession": "",
                     "Page / section": "", "Source type": "Market data" if p["debt_type"] == "history" else "Market data + judgment (debt)",
                     "Verification": "", "Notes": p["notes"], "URL": ""})
    return pd.DataFrame(rows)


def historical_table(bundle: DataBundle) -> pd.DataFrame:
    """Wide table of reported historicals (rows = line items, columns = periods)."""
    fin = bundle.financials
    rows = []
    for item, li in list(fin["line_items"].items()) + list(fin["operating"].items()):
        row = {"Item ID": item, "Line item": li["label"], "Statement": li.get("stmt", "KPI")}
        for p in ["FY2023", "FY2024", "FY2025", "H1_2026", "Q2_2026"]:
            row[p] = li["values"].get(p, np.nan)
        rows.append(row)
    return pd.DataFrame(rows)
