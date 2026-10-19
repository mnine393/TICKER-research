from __future__ import annotations
import pandas as pd
from .assumptions import YEARS

def _v(a,k,i): return a[k].values[i]
def build_forecast(a, historical):
    """Integrated forecast. Cash is the CFS result; no balance-sheet plug is used."""
    h=historical.set_index("line")[2025]
    # Tesla reports Model 3/Y and Other Models delivery buckets but no revenue by bucket.
    mass_deliv, other_deliv = 1550.0, 90.0  # thousands; judgmental allocation of reported 1.64m total
    mass_asp, other_asp = 38.0, 55.0       # $000; calibrated category assumptions, not filings
    energy_gwh, energy_rev_per_gwh = h["Energy deployments (GWh)"], h["Energy revenue"]/h["Energy deployments (GWh)"]
    vehicle_rev=(mass_deliv*mass_asp+other_deliv*other_asp)/1000
    auto_other=h["Automotive revenue"]-vehicle_rev
    ppe=h["PP&E, net"]; cash=h["Cash"]; sti=h["Short-term investments"]; ar=h["Receivables"]; inv=h["Inventory"]
    other_assets=h["Other assets"]; ap=h["Payables"]; deferred=h["Deferred revenue"]; debt=h["Debt & finance leases"]; other_liab=h["Other liabilities"]
    assets0=cash+sti+ar+inv+ppe+other_assets; liab0=ap+deferred+debt+other_liab
    equity=assets0-liab0 # opening equity derives from the balance sheet identity; avoids rounding mismatch in seed presentation
    shares=h["Diluted shares"]
    rows=[]
    for i,y in enumerate(YEARS):
        mass_deliv*=1+_v(a,"mass_delivery_growth",i); other_deliv*=1+_v(a,"other_delivery_growth",i)
        mass_asp*=1+_v(a,"mass_asp_change",i); other_asp*=1+_v(a,"other_asp_change",i)
        vehicle_rev=(mass_deliv*mass_asp+other_deliv*other_asp)/1000
        auto_other*=1+0.02  # explicit recurring leasing/credits/other bridge; no one-time gain assumed
        automotive=vehicle_rev+auto_other
        energy_gwh*=1+_v(a,"energy_deploy_growth",i); energy_rev_per_gwh*=1+_v(a,"energy_asp_change",i); energy=energy_gwh*energy_rev_per_gwh
        services=h["Services and other revenue"]*(1+_v(a,"services_growth",i)) if i==0 else services*(1+_v(a,"services_growth",i))
        revenue=automotive+energy+services
        gross_profit=automotive*_v(a,"auto_margin",i)+energy*_v(a,"energy_margin",i)+services*_v(a,"services_margin",i)
        rd=revenue*_v(a,"rd_pct",i); sga=revenue*_v(a,"sga_pct",i); da=ppe*_v(a,"da_pct",i)
        ebit=gross_profit-rd-sga-da; interest=debt*.045; pretax=ebit-interest; tax=max(0,pretax*_v(a,"tax_rate",i)); ni=pretax-tax
        capex=revenue*_v(a,"capex_pct",i); ppe_next=ppe+capex-da
        cogs=revenue-gross_profit
        ar_next=revenue*_v(a,"ar_days",i)/365; inv_next=cogs*_v(a,"inventory_days",i)/365; ap_next=cogs*_v(a,"ap_days",i)/365
        deferred_next=revenue*_v(a,"deferred_pct",i); other_assets_next=other_assets*(1+max(-.02,revenue/(rows[-1]["Revenue"] if rows else h["Total revenue"])-1))
        other_liab_next=other_liab*(1+max(-.02,revenue/(rows[-1]["Revenue"] if rows else h["Total revenue"])-1))
        sbc=shares*_v(a,"share_growth",i)*250 # approximate noncash SBC expense, tied to share dilution assumption
        scheduled_principal=min(debt*.05,debt); provisional_cfo=ni+da+sbc-(ar_next-ar)-(inv_next-inv)-(other_assets_next-other_assets)+(ap_next-ap)+(deferred_next-deferred)+(other_liab_next-other_liab)
        pre_financing_cash=cash+provisional_cfo-capex-scheduled_principal
        financing=max(0,_v(a,"minimum_cash",i)-pre_financing_cash)
        debt_next=debt-scheduled_principal+financing; cfo=provisional_cfo; cash_next=pre_financing_cash+financing
        buybacks=_v(a,"buybacks",i); shares_next=shares*(1+_v(a,"share_growth",i))-buybacks/max(1,250)
        equity_next=equity+ni+sbc-buybacks
        assets=cash_next+sti+ar_next+inv_next+ppe_next+other_assets_next; liabilities=ap_next+deferred_next+debt_next+other_liab_next
        nwc=(ar_next+inv_next+other_assets_next)-(ap_next+deferred_next+other_liab_next)
        net_borrowing=financing-scheduled_principal
        fcfe=ni+da+sbc-capex-(nwc-((ar+inv+other_assets)-(ap+deferred+other_liab)))+net_borrowing
        rows.append(dict(Year=y, Mass_deliveries_000=mass_deliv, Other_deliveries_000=other_deliv, Mass_ASP_000=mass_asp, Other_ASP_000=other_asp, Energy_GWh=energy_gwh, Automotive_revenue=automotive, Energy_revenue=energy, Services_revenue=services, Revenue=revenue, Gross_profit=gross_profit, R_D=rd, SG_A=sga, D_A=da, EBIT=ebit, Interest=interest, Tax=tax, Net_income=ni, Capex=capex, CFO=cfo, FCFE=fcfe, Cash=cash_next, Short_term_investments=sti, Receivables=ar_next, Inventory=inv_next, Other_assets=other_assets_next, PPE=ppe_next, Payables=ap_next, Deferred_revenue=deferred_next, Debt_leases=debt_next, Other_liabilities=other_liab_next, Equity=equity_next, Assets=assets, Liabilities=liabilities, Shares=shares_next, Net_borrowing=net_borrowing, SBC=sbc, Buybacks=buybacks, NWC=nwc, Financing=financing, Scheduled_principal=scheduled_principal))
        ppe,cash,ar,inv,other_assets,ap,deferred,debt,other_liab,equity,shares=ppe_next,cash_next,ar_next,inv_next,other_assets_next,ap_next,deferred_next,debt_next,other_liab_next,equity_next,shares_next
    return pd.DataFrame(rows)

def checks(forecast, a):
    out=[]
    prev_ppe=35000.; prev_debt=8376.; prev_shares=3528.; prev_cash=16513.
    for i,r in forecast.iterrows():
        coe=_v(a,"rf",i)+_v(a,"observed_beta",i)*_v(a,"erp",i)
        out += [
          (r.Year,"Balance sheet",abs(r.Assets-(r.Liabilities+r.Equity))<.01,r.Assets-(r.Liabilities+r.Equity)),
          (r.Year,"Cash link",abs(r.Cash-(prev_cash+r.CFO-r.Capex-r.Scheduled_principal+r.Financing))<.01,r.Cash-(prev_cash+r.CFO-r.Capex-r.Scheduled_principal+r.Financing)),
          (r.Year,"PP&E roll-forward",abs(r.PPE-(prev_ppe+r.Capex-r.D_A))<.01,r.PPE-(prev_ppe+r.Capex-r.D_A)),
          (r.Year,"Debt/lease roll-forward",abs(r.Debt_leases-(prev_debt-r.Scheduled_principal+r.Financing))<.01,r.Debt_leases-(prev_debt-r.Scheduled_principal+r.Financing)),
          (r.Year,"Share roll-forward",abs(r.Shares-(prev_shares*(1+_v(a,"share_growth",i))-r.Buybacks/250))<.01,r.Shares-(prev_shares*(1+_v(a,"share_growth",i))-r.Buybacks/250)),
          (r.Year,"Minimum cash / financing",r.Cash>=_v(a,"minimum_cash",i)-.01,r.Cash-_v(a,"minimum_cash",i)),
          (r.Year,"Terminal growth < cost of equity",_v(a,"terminal_growth",i)<coe,coe-_v(a,"terminal_growth",i))]
        prev_ppe,prev_debt,prev_shares,prev_cash=r.PPE,r.Debt_leases,r.Shares,r.Cash
    return pd.DataFrame(out,columns=["Year","Check","Pass","Difference"])
