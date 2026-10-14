#!/usr/bin/env python3
"""Validate source-controlled NEXT-ITERATION MPN freeze and CSV only.

This does not qualify automotive electronics or assert a KiCad-implemented LM74800.
"""
import csv
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
base=root/"hardware"/"kicad"
m=json.loads((base/"power_frontend_design_freeze.json").read_text("utf-8"))
current=json.loads((base/"power_selection.json").read_text("utf-8"))
assert m["decision"]=="FROZEN_FOR_NEXT_PROTOTYPE_PART_SELECTION_ONLY"
assert m["release"]["approved_for_vehicle"] is False
assert m["release"]["approved_for_pcb_order"] is False
assert m["release"]["protection_circuit_present_in_active_kicad"] is False
assert current["selection"]=="KEEP_EXISTING_COTS_AUTOMOTIVE_BUCK"
assert current["planned_input_protection"]["controller"]=="LM74800QDRRRQ1"
required={
    "R_OV_A":"RC1206FR-07330KL",
    "R_OV_B":"RC1206FR-07330KL",
    "R_OV_BOTTOM":"RC1206FR-0723K2L",
    "R_SLEW":"RC1206FR-07100RL",
    "C_SLEW":"C1206C103K1RACTU",
    "C_CAP":"C1206C224K5RACTU",
}
parts={p["ref"]:p for p in m["fixed_candidates"]}
assert len(parts)==len(m["fixed_candidates"]), "duplicate component ref"
for ref,mpn in required.items():
    assert parts[ref]["mpn"]==mpn,(ref,parts[ref].get("mpn"))
for p in parts.values():
    assert isinstance(p.get("mpn"),str) and p["mpn"].strip(),p["ref"]
    assert int(p["qty"])>=1 and p.get("source","").startswith("https://"),p["ref"]
assert m["diode_resolution"]["not_a_zener"] is True
assert parts["D_A_VS"]["mpn"]=="1N4148WSQ-7-F"
with (base/"power_frontend_order_bom.csv").open(encoding="utf-8",newline="") as fp:
    rows=list(csv.DictReader(fp))
assert len(rows)==len(parts),(len(rows),len(parts))
assert {r["Ref"] for r in rows}==set(parts)
for row in rows:
    item=parts[row["Ref"]]
    assert row["MPN"]==item["mpn"] and int(row["Qty"])==item["qty"]
calc=m["standard_passive_selection"]["ov_design_calc"]
assert abs(calc["threshold_nominal_v"]-1.233*(1+660000/23200))<.02
assert calc["vin_normal_max_v"]==30
assert all(x in m["standard_passive_selection"]["selected_refs"] for x in required)
assert not any(item["mpn"]==m["standard_passive_selection"]["reference_evm_extra_component"]["mpn_candidate"] for item in parts.values()),"EVM C10 not reviewed for circuit; must remain separate"
print(json.dumps({"selection":"NEXT_PROTOTYPE_ONLY","standard_parts_mpn_resolved":len(required),"bom_rows":len(rows),"gate":"NOT_SCHEMATIC_OR_VEHICLE_RELEASE","OV_nominal_v":calc["threshold_nominal_v"],"PASS":True},ensure_ascii=False,indent=2))
