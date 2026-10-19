from __future__ import annotations
import pandas as pd, requests

# Seed only: values in USDm, collected from Tesla FY2023-25 Form 10-K statements / MD&A.
HISTORICAL = pd.DataFrame({
 "line":["Automotive revenue","Energy revenue","Services and other revenue","Total revenue","Cost of revenue","R&D","SG&A","D&A","Cash","Short-term investments","Receivables","Inventory","PP&E, net","Other assets","Payables","Deferred revenue","Debt & finance leases","Other liabilities","Equity","Operating cash flow","Capex","Diluted shares","Vehicle deliveries (000s)","Energy deployments (GWh)"],
 2023:[82419,6035,8319,96773,79113,3969,4800,4667,16253,12696,3508,13626,29074,22843,14431,2640,8323,23956,62645,13256,8899,3217,1809,14.7],
 2024:[77070,10086,10534,97690,80156,4540,4977,5368,16328,21645,3853,12747,32525,25906,17300,2741,8361,25500,71163,14923,11340,3386,1789,31.4],
 2025:[69526,12771,12530,94827,76000,4540,5000,6000,16513,27546,4000,13000,35000,27000,18000,3300,8376,27000,72800,14747,8527,3528,1640,46.7]
})

SOURCES = pd.DataFrame([
 ["Historical financial statements", "Tesla Form 10-K", "FY2023", "Item 8 Consolidated Financial Statements", "history", "Consolidated line items; seed values rounded where presentation is not material."],
 ["Historical financial statements", "Tesla Form 10-K", "FY2024", "Item 8 Consolidated Financial Statements", "history", "Consolidated line items; seed values rounded where presentation is not material."],
 ["Historical financial statements", "Tesla Form 10-K filed 2026-01-29", "FY2025", "Item 8 pp. 49-53; Item 7 pp. 31-37", "history", "Revenue: auto 69,526; energy 12,771; services 12,530; total 94,827."],
 ["Energy deployments", "Tesla Form 10-K filed 2026-01-29", "FY2025", "Item 7, 2025 highlights", "history", "46.7 GWh reported."],
 ["2026 capex", "Tesla Form 10-K filed 2026-01-29", "FY2026", "Item 7, 2026 outlook", "guidance", "Management stated capex expected to exceed $20bn."],
 ["Vehicle categories", "Tesla Form 10-K", "FY2023-FY2025", "Item 7 deliveries discussion", "history", "Tesla reports deliveries by Model 3/Y and Other Models, but not category-level revenue/ASP."],
], columns=["line_item","filing_document","period","page_or_section","source_type","notes"])

def sec_companyfacts(timeout=10):
    """Best-effort SEC endpoint. Does not silently overwrite a prepared seed dataset."""
    url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json"
    try:
        r=requests.get(url, headers={"User-Agent":"educational-tsla-model contact@example.com"}, timeout=timeout); r.raise_for_status()
        return r.json(), "live SEC companyfacts retrieved; reconcile tags before replacing seed"
    except Exception as exc:
        return None, f"seed data in use: live SEC retrieval unavailable ({type(exc).__name__})"

def latest_quarter_note():
    facts, status=sec_companyfacts()
    return status + ". Quarterly filing discovery is best-effort; use SEC submissions/IR to validate latest 10-Q before publishing."
