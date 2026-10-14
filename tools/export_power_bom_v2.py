#!/usr/bin/env python3
"""Generate provisional power BOM from KiCad native root netlist, never manual counts.
Prices are separate procurement observations; not a fabrication-ready BOM.
"""
import csv
import re
import sys
from pathlib import Path

POWER_SHEETS = {
    "01C_HOLD_TIMER.kicad_sch",
    "01G_SIMPLE_INPUT.kicad_sch",
    "01H_ACC_HOLD_GATE.kicad_sch",
    "02_5V_Buck.kicad_sch",
    "03_3V3_USB.kicad_sch",
}
PARTS = {
    "U101": ("LMR38020SQDDARQ1", "EUR", 3.92, 2.98, 2.49, "Mouser DE, stock recheck"),
    "U301": ("TPS2116DRLR", "EUR", 0.903, 0.646, 0.512, "Mouser DE"),
    "U302": ("MCP1826S-3302E/EB", "EUR", 1.14, "", "", "Mouser DE: 1pc EUR 1.14; DDPAK-3 improved thermal area, 10/100pc unpriced"),
    "D901": ("Comchip SS510C-HF (5A 100V SMC)", "EUR", 0.998, 0.711, 0.443, "SMC matching footprint; thermal proof pending"),
    "D902": ("Littelfuse 5.0SMDJ36A", "EUR", 2.11, 1.353, 0.921, "10/1000us rated; NO 350ms load-dump approval"),
    "L101": ("FCH0650-150M provisional 15uH", "", "", "", "", "footprint and Isat verification missing"),
    "U911": ("Wuerth 140356145000 80V SOP4", "EUR", 0.335, 0.296, 0.248, "CTR guaranteed at IF5mA only: 9V and hot/cold pending"),
    "D911": ("Diodes BAT54WS-7-F", "", "", "", "", "SOD323 K1/A2 negative Q914 base clamp; re-used component, prices unverified"),
    "R922": ("Panasonic ERJP08F1002V 10k 1% 1206", "", "", "", "", "minimum 0.5W requirement; pricing and derating recheck"),
    "R923": ("Panasonic ERJP08F1002V 10k 1% 1206", "", "", "", "", "minimum 0.5W requirement; pricing and derating recheck"),
    "R924": ("Panasonic ERJP08F4701V 4.7k 1% 1206", "", "", "", "", "base pulldown; pricing unverified"),
    "Q914": ("Nexperia PMBT5551,215", "", "", "", "", "VIN-startup sink; SOT23 B1 E2 C3; price/LCSC unverified"),
    "Q915": ("Diodes MMBT5401-7-F", "", "", "", "", "VIN-only startup source; SOT23 B1 E2 C3; price/LCSC unverified"),
    "Q912": ("MMBT5551 SOT23", "", "", "", "", "ACC level shifter; pricing pending"),
    "Q913": ("MMBT5551 SOT23", "", "", "", "", "ACC level shifter; pricing pending"),
    "U501": ("TLC555QDRQ1", "EUR", 1.05, 0.759, 0.605, "monostable 24s nominal; effective capacitance and edge check open"),
    "U502": ("SN74LVC1G08QDBVRQ1", "EUR", 0.224, 0.153, 0.117, "hardware gated timer"),
}

def export(src, dest):
    data=Path(src).read_text(encoding="utf-8")
    comps=data.split("\n\t(components",1)[1].split("\n\t(libraries",1)[0]
    rows=[]
    for part in comps.split("\n\t\t(comp")[1:]:
        def find(pattern):
            m=re.search(pattern,part)
            return m.group(1) if m else ""
        ref=find(r'\(ref "([^"]+)"\)')
        value=find(r'\(value "([^"]+)"\)')
        fp=find(r'\(footprint "([^"]+)"\)')
        sheet=find(r'\(name "Sheetfile"\)\s+\(value "([^"]+)"\)')
        if sheet not in POWER_SHEETS:
            continue
        mpn,curr,p1,p10,p100,status=PARTS.get(ref,("","","","","","Mfr MPN and price open"))
        rows.append((sheet,ref,value,fp,mpn,curr,p1,p10,p100,status))
    rows.sort(key=lambda x:(x[0],x[1]))
    assert rows, "No power components from native KiCad hierarchy"
    refs={r[1] for r in rows}
    assert {"U101","U301","U302","D901","D902","U911","Q912","Q913","Q914","Q915","R922","R923","R924","U501","U502"} <= refs, "Missing mandatory active power parts"
    with open(dest,"w",newline="",encoding="utf-8") as fh:
        writer=csv.writer(fh)
        writer.writerow(("sheet","reference","KiCad_value","KiCad_footprint","selected_or_candidate_MPN","price_currency","single_unit","ten_unit","hundred_unit","qualification_status"))
        writer.writerows(rows)
    print(f"PASS: exported {len(rows)} active schematic power components to {dest}; NOT a priced complete BOM")

if __name__=="__main__":
    export(sys.argv[1],sys.argv[2])
