#!/usr/bin/env python3
"""Auditable *priced IC subset* comparison, 15 Oct 2026 distributor snapshots.

Not a full PCB BOM. Unknowns are represented by None, NOT by invented costs
or zero placements. Only actively stocked and manufacturer-identified parts
enter the alternative columns. No automatic safety release.
"""
import json

# EUR ex VAT per single device for Q1/Q10/Q100, from named part pages;
# do not mix currencies or claim transport / PCBA / taxes are covered.
SUPPLIERS = {
 "LM74930QRGERQ1":{"url":"https://www.digikey.de/en/products/detail/texas-instruments/LM74930QRGERQ1/22147207",
                   "q":[4.42,3.369,2.8175],"stock_observed":1364,
                   "AEC":True,"role":"Baseline protection controller"},
 "LMR38020SQDDARQ1":{"url":"https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286",
                    "q":[3.91,2.965,2.4703],"stock_observed":522,
                    "AEC":True,"role":"Baseline 80V buck"},
 "LTC4380HMS-4#WPBF":{"url":"https://eu.mouser.com/en/ProductDetail/Analog-Devices/LTC4380HMS-4WPBF",
                      "q":[9.07,7.10,6.05],"stock_observed":120,
                      "AEC":True,"role":"Available independent 4..72V surge-stopper candidate"},
 "LTC4366HTS8-2#TRMPBF":{"url":"https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884",
                         "q":[10.42,8.174,6.996],"stock_observed":10186,
                         "AEC":False,"role":"500V floating surge concept; AEC evidence NOT established"}
}
def compare():
    qty=[1,10,100]
    a=SUPPLIERS["LM74930QRGERQ1"]["q"]
    buck=SUPPLIERS["LMR38020SQDDARQ1"]["q"]
    ltc=SUPPLIERS["LTC4380HMS-4#WPBF"]["q"]
    flt=SUPPLIERS["LTC4366HTS8-2#TRMPBF"]["q"]
    return {
      "source_date":"2026-10-15; distributor listings may lag / stock changes",
      "currency":"EUR net (before shipping/VAT)",
      "quantities":qty,
      "stock_and_pricing_sources":SUPPLIERS,
      "priced_IC_subset": [{
           "qty":qty[i],
           "LM74930_plus_LMR38020_eur":round(a[i]+buck[i],4),
           "LTC4380_plus_LMR38020_eur":round(ltc[i]+buck[i],4),
           "LTC4380_delta_eur":round(ltc[i]-a[i],4),
           "LTC4366_plus_LMR38020_eur":round(flt[i]+buck[i],4),
           "LTC4366_delta_eur":round(flt[i]-a[i],4)
       } for i in range(3)],
       "entire_module_fit_AUTO":57,
       "entire_module_fit_RUN":58,
       "full_new_architecture_BOM_placement_count":None,
       "full_new_architecture_cost_EUR":None,
       "B_extra_HV_FET_SOA_and_VCC_clamp_required":True,
       "B_outcome":"No proven full BOM or safety simplification; not released",
       "why_no_total":"No physically validated alternative KiCad schematic, local capacitor/diode/sense/OV network or PCB material stack. A fictitious full-system price/count would be misleading."
    }
if __name__=="__main__":print(json.dumps(compare(),indent=2,sort_keys=True))
