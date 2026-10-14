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
    "F901": ("Littelfuse 0997003.WXN 3A 58V", "", "", "", "", "OFFBOARD near vehicle source, replaceable holder/OEM fused circuit; price recheck"),
    "F902": ("Littelfuse 0997002.WXN 2A 58V", "EUR", 0.886, 0.668, 0.501, "OFFBOARD; Mouser DE catalog, VAT/shipping not established; recheck"),
    "R914": ("YAGEO RC1206FR-07154RL 154ohm 1% 1206 0.25W", "USD", 0.10, 0.047, 0.0247, "DigiKey catalog stock5000; LED drive engineering envelope, hot/cold CTR open"),
    "R911": ("Panasonic ERJP08F2492V 24.9k 1% 1206", "", "", "", "", "VIN startup cold-headroom update; price/availability unverified"),
    "R915": ("Panasonic ERJP08F2492V 24.9k 1% 1206", "", "", "", "", "VIN HOLD cold-headroom update; price/availability unverified"),
    "R207": ("Panasonic ERJP08F1003V 100k 1% 1206", "", "", "", "", "MCU ACC sense fault isolation; price/LCSC unverified"),
    "U101": ("LMR38020SQDDARQ1", "EUR", 3.92, 2.98, 2.49, "Mouser DE, stock recheck"),
    "U301": ("TPS2116DRLR", "EUR", 0.903, 0.646, 0.512, "Mouser DE"),
    "U302": ("MCP1826S-3302E/EB", "EUR", 1.14, "", "", "Mouser DE: 1pc EUR 1.14; DDPAK-3 improved thermal area, 10/100pc unpriced"),
    "D901": ("Diodes S5MC-13-F 5A 1000V SMC", "USD", 1.03, 0.637, 0.4126, "DigiKey US observed14Oct2026 stock51879; no DE landed quote; cold Vf/thermal/pulse unqualified"),
    "D902": ("TI TVS5800VEBR 58V flat clamp VEB6", "USD", 0.72, 0.512, 0.4025, "DigiKey US observed14Oct2026: stock0, expected12Jan2027; NOT a purchasable/landed quote; 20A8/20us clamp75V at27C only"),
    "L101": ("FCH0650-150M provisional 15uH", "", "", "", "", "footprint and Isat verification missing"),
    "U911": ("Wuerth 140356145000 80V SOP4", "EUR", 0.335, 0.296, 0.248, "CTR guaranteed at IF5mA only: 9V and hot/cold pending"),
    "D911": ("Diodes BAT54WS-7-F", "", "", "", "", "SOD323 K1/A2 negative Q914 base clamp; re-used component, prices unverified"),
    "R922": ("Panasonic ERJP08F1002V 10k 1% 1206", "", "", "", "", "minimum 0.5W requirement; pricing and derating recheck"),
    "R923": ("Panasonic ERJP08F1002V 10k 1% 1206", "", "", "", "", "minimum 0.5W requirement; pricing and derating recheck"),
    "R924": ("Panasonic ERJP08F4701V 4.7k 1% 1206", "", "", "", "", "base pulldown; pricing unverified"),
    "Q914": ("Nexperia PMBT5551,215", "", "", "", "", "VIN-startup sink; SOT23 B1 E2 C3; price/LCSC unverified"),
    "Q915": ("Diodes MMBT5401-7-F", "", "", "", "", "VIN-only startup source; SOT23 B1 E2 C3; price/LCSC unverified"),
    "D503": ("Diodes BAS116Q-7-F", "", "", "", "", "low-leak RC rearm A1 NC2 K3; price unverified"),
    "D912": ("Diodes BAT54WS-7-F", "", "", "", "", "Q912 negative base clamp K1 A2; price unverified"),
    "R505": ("Panasonic ERJP08F1002V 10k 1% 1206", "", "", "", "", "RC discharge current limit; price unverified"),
    "R501": ("Panasonic ERJP08F1004V 1M 1% 1206", "", "", "", "", "lower timing R for leakage margin; price unverified"),
    "C501": ("Murata GRM32ER71E226KE15L 22uF 25V X7R 1210", "", "", "", "", "effective capacitance at bias/temperature must be qualified; price unverified"),
    "Q912": ("MMBT5551 SOT23", "", "", "", "", "ACC level shifter; pricing pending"),
    "U501": ("TLC555QDRQ1", "EUR", 1.05, 0.759, 0.605, "prearmed ACC-off timer; see model-only RC sensitivity study, not a guaranteed hold time"),
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
        if sheet not in POWER_SHEETS and ref != "R207":
            continue
        mpn,curr,p1,p10,p100,status=PARTS.get(ref,("","","","","","Mfr MPN and price open"))
        rows.append((sheet,ref,value,fp,mpn,curr,p1,p10,p100,status,"VEHICLE_EXTERNAL" if ref in {"F901","F902"} else "PCB"))
    rows.sort(key=lambda x:(x[0],x[1]))
    assert rows, "No power components from native KiCad hierarchy"
    refs={r[1] for r in rows}
    assert {"R207","U101","U301","U302","D901","D902","U911","Q912","D503","D912","R505","Q914","Q915","R922","R923","R924","U501","U502"} <= refs, "Missing mandatory active power parts"
    with open(dest,"w",newline="",encoding="utf-8") as fh:
        writer=csv.writer(fh)
        writer.writerow(("sheet","reference","KiCad_value","KiCad_footprint","selected_or_candidate_MPN","price_currency","single_unit","ten_unit","hundred_unit","qualification_status","installation"))
        writer.writerows(rows)
    board=sum(row[-1]=="PCB" for row in rows)
    print(f"PASS: exported {len(rows)} native power components ({board} PCB, {len(rows)-board} vehicle-external) to {dest}; NOT a priced complete BOM")

if __name__=="__main__":
    export(sys.argv[1],sys.argv[2])
