"""Fix Note 4 citation in Lab_08_comps_dcf.md (handles CRLF line endings)."""

FILES = [
    r"Lab_08_comps_dcf.md",
    r"03_Comps\Lab_08_comps_dcf.md",
]

OLD = (
    "Confirmed by [Tesla Form 10-K, Note 4, p. 70]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(showing \\$44.1B cash/investments vs \\$8.4B debt) and"
)

NEW = (
    "Confirmed by [Tesla Form 10-K, Item 7, Liquidity and Capital Resources, p.\u00a036]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$44.1B cash and investments) and [Item 8, Note 12\u2014Debt, pp.\u00a079\u201381]"
    "(https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) "
    "(\\$8.4B total debt), and"
)

for fp in FILES:
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    if OLD in content:
        content = content.replace(OLD, NEW, 1)
        print(f"  Fix A APPLIED: {fp}")
    else:
        # Try without the backslash-escaped dollars (file stores literal $)
        OLD2 = OLD.replace("\\$", "$")
        NEW2 = NEW.replace("\\$", "$")
        if OLD2 in content:
            content = content.replace(OLD2, NEW2, 1)
            print(f"  Fix A APPLIED (literal $): {fp}")
        else:
            print(f"  Fix A NOT FOUND: {fp}")
            # Print surrounding context to debug
            idx = content.find("Note 4")
            if idx >= 0:
                print("  Context:", repr(content[max(0,idx-30):idx+120]))
            continue

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

print("Done.")

