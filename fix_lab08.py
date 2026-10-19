"""Three final citation / wording fixes for Lab_08_comps_dcf.md (exact byte matches)."""

FILES = [
    r"Lab_08_comps_dcf.md",
    r"03_Comps\Lab_08_comps_dcf.md",
]

# Fix A: cash p.31 and debt Note 9 p.72
# File stores dollars as \\$ and uses \xa0 for non-breaking space and \u2014 for em-dash
FIX_A_OLD = (
    "[Tesla Form 10-K, Item 7, Liquidity and Capital Resources, p.\xa036]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$44.1B cash and investments) and [Item 8, Note 12\u2014Debt, pp.\xa079\u201381]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$8.4B total debt), and"
)
FIX_A_NEW = (
    "[Tesla Form 10-K, Item 7, MD&A, p.\xa031]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$44.06B cash and investments) and [Item 8, Note 9\u2014Debt and Finance Leases, p.\xa072]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$8.18B total debt), and"
)

# Fix B: soften unsourced $100B+ GM Financial claim in the colleague critique
FIX_B_OLD = (
    "GM carries \\$100B+ of debt inside GM Financial, sells via franchised dealers with lower gross margins, "
    "and has negligible utility-scale energy storage. Applying GM\\'s 15.2\u00d7 multiple to Tesla ignores "
    "Tesla\\'s net cash balance sheet (+\\$35.7B net cash) and its 27% growing Energy segment (\\$12.8B revenue). "
    "You are penalizing Tesla for legacy automaker structural constraints it does not share."
)
FIX_B_NEW = (
    "GM\\'s captive-finance business (GM Financial) adds material capital-structure differences, "
    "it sells via franchised dealers with lower gross margins, and it has negligible utility-scale energy storage. "
    "Applying GM\\'s 15.2\u00d7 multiple to Tesla\\'s earnings ignores Tesla\\'s net cash position "
    "and its growing Energy segment (\\$12.8B revenue). "
    "You are penalizing Tesla for legacy automaker structural constraints it does not share."
)

FIXES = [
    ("Fix A – cash/debt page citation", FIX_A_OLD, FIX_A_NEW),
    ("Fix B – soften GM Financial debt claim", FIX_B_OLD, FIX_B_NEW),
]


def apply_fixes(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for label, old, new in FIXES:
        if old in content:
            content = content.replace(old, new, 1)
            print(f"  {label}: APPLIED")
        else:
            print(f"  {label}: NOT FOUND — trying repr scan")
            # Show a snippet near the closest keyword for debugging
            keyword = old[:30]
            idx = content.find(keyword)
            if idx >= 0:
                print(f"    Context: {repr(content[max(0,idx-5):idx+len(old)+10])}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  -> Written: {filepath}\n")


for fp in FILES:
    print(f"\n=== {fp} ===")
    apply_fixes(fp)

print("All done.")
