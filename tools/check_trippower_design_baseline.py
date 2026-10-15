#!/usr/bin/env python3
"""TripPower REV5 machine-checked BOM/constraint lock and transparent limits.

A passing status means the *committed KiCad properties* match the controlled
engineering baseline, NOT that a first-run, thermal, load dump, PCB or vehicle
operating envelope is guaranteed. This is intentionally read-only.
Sources are linked in REV5_DESIGN_BASELINE.json.
"""
import json
import math
import re
from pathlib import Path

base = Path("hardware/modules/TripPower_5V2A")
d = json.loads((base / "REV5_DESIGN_BASELINE.json").read_text(encoding="utf-8"))
contract = json.loads((base / "module_contract.json").read_text(encoding="utf-8"))
assert d["schema_version"] == 1 and d["stage"] == "REV5_ENGINEERING_BASELINE_ONLY"
assert d["authorization"]["schematic_baseline_locked"] is True
for unsafe in ("automotive_released","manufacturing_released","pcb_routed","nine_volt_start_guaranteed"):
    assert d["authorization"][unsafe] is False, unsafe
a=d["target"]
assert a["VIN_at_connector_v"] == [9,30] and a["regulated_output_v"]==5
assert a["regulated_continuous_output_a"]==2
assert a["raw_auxiliary_current_design_target_a"]==1
assert a["separate_unsuppressed_load_dump_target"]=={"v":200,"duration_s":0.35}
assert a["f_main_external_replaceable_required"] is True
assert contract["requirements"]["main_vehicle_fuse"]["required"] is True
assert contract["no_manufacturing_or_vehicle_approval"] is True

def property_value(section, name):
    m=re.search(r'\(property "'+re.escape(name)+r'" "([^"]*)"', section)
    return None if m is None else m.group(1)

checked=[]
for sheet, components in d["fixed_placements"].items():
    schematic=(base / sheet).read_text(encoding="utf-8")
    for ref, expected in components.items():
        prefix=f'(property "Reference" "{ref}"'
        assert schematic.count(prefix)==1, f"one and only one physical component {sheet}:{ref}"
        at=schematic.index(prefix)
        end=schematic.index("(instances ", at)
        block=schematic[at:end]
        assert "(pin " in block, f"{sheet}:{ref} no physical symbol pins"
        for key,field in (("value","Value"),("mpn","MPN"),("footprint","Footprint")):
            if key in expected:
                actual=property_value(block,field)
                assert actual==expected[key], f"{sheet}:{ref} {field}: {actual!r} != expected {expected[key]!r}"
        if "dnp_default_auto" in expected:
            header=schematic.rfind("(symbol (lib_id",0,at)
            assert header>=0 and "(dnp yes)" in schematic[header:at], f"{ref} should be DNP in AUTO"
        checked.append(f"{sheet}:{ref}")

assert len(checked)>=20, "BOM lock was truncated"
assert d["assembly"]["default_mode"]=="AUTO"
assert d["assembly"]["verified_placement_count_change"]=={"REV4_fit":71,"REV5_AUTO_fit_expected":57,"REV5_RUN_fit_expected":58}
all_schematics=[(base/sh).read_text(encoding="utf-8") for sh in d["fixed_placements"]]
all_active=sum(len(re.findall(r'\(symbol \(lib_id [^\n]+\(dnp no\)', text)) for text in all_schematics)
assert all_active==57, f"unexpected actual pick-and-place placements: {all_active} vs 57"
assert all('(property "Reference" "'+ref+'"' not in "".join(all_schematics) for ref in ("Q303","Q304","Q305")), "obsolete BJT must be physically gone"

protection=(base/"01_Protection_LM74930.kicad_sch").read_text()
control=(base/"03_VS_READY_TPS3760.kicad_sch").read_text()
assert protection.count('(property "Value" "10uF 100V VS STARTUP RESERVOIR X7R REV4"')==2
assert '0R AUTO VS TO RUN_SENSE; DNP IN RUN' in protection
assert 'D305' not in protection and 'D302' in protection
assert '715k 1% VS_READY VIN TOP' in control
assert 'TPS38A010122DSKRQ1' in control and 'PMBTA92-Q' not in control

# Caution: not worst-case charge pump input current and not vendor pulse approval.
rvs=3*3300.0
vin_pulse=200.0
v_z_typ=56.0
pulse_s=.350
i_rvs=(vin_pulse-v_z_typ)/rvs
p_all_rvs=(vin_pulse-v_z_typ)**2/rvs
p_each_rvs=p_all_rvs/3
e_each_rvs=p_each_rvs*pulse_s
p_zener=v_z_typ*i_rvs
e_zener=p_zener*pulse_s
assert 0.69<p_each_rvs<0.71 and 0.24<e_each_rvs<0.27
assert 0.80<p_zener<0.85 and 0.28<e_zener<0.31

# Yageo AC1206FR-07750KL: 200 V continuous rating / 0.25 W at 70C.
# Two 750k high-side resistors per divider, 25.5k and 130k low side.
# This is normal topology stress at 200 V (NOT peak pin transients/faults).
divider={}
for label,bottom in (("OV",25500.0),("UVLO",130000.0)):
    i=vin_pulse/(2*750000+bottom)
    v_per=i*750000
    p_per=i*i*750000
    assert v_per<200 and p_per<.25
    divider[label]={"high_resistor_v_each":round(v_per,2),
                    "high_resistor_mw_each":round(p_per*1000,3),
                    "still_requires_layout_pulse_and_single_fault_check":True}

# TA-I RLM25FEER005 rated 2W: this only proves nominal shunt dissipation
# << nameplate under a hypothetical limit, not sensing accuracy or temp.
shunt_w_at_4a=4**2*.005
assert shunt_w_at_4a<2.0
# Separate CAP/VS/RESET timing analyses still explicitly unproven.
i_rvs_ready_9v=(9-7.510)/rvs
assert 145e-6<i_rvs_ready_9v<155e-6
# Nominal mlcc is NEVER guaranteed effective C after DC bias and aging.
c_nom_uF=1+10+10
c_ctr_nom_nf=330
r_ctr_typ=1e6
t_delay_typ=-math.log(.28)*r_ctr_typ*c_ctr_nom_nf*1e-9
assert abs(t_delay_typ-.420)<.002

critical=d["provisional_stop_gates"]
assert len(critical)>=10 and len({item["id"] for item in critical})==len(critical)
assert all(item["severity"] in ("CRITICAL","HIGH") and item["needed"] for item in critical)
assert not list(base.glob("*.kicad_pcb")), "PCB unexpectedly created: update freeze and require KiCad DRC"

print(json.dumps({
    "result":"PASS_SOURCE_LOCK_ONLY__HARDWARE_RELEASE_BLOCKED",
    "baseline":d["stage"],"hardware_schematic_properties_locked":len(checked),
    "locked_references":checked,
    "assembly_mode_default":"AUTO",
    "component_placements_rev4":71,
    "component_placements_rev5_auto":all_active,
    "component_placements_saved":71-all_active,
    "limits_using_specified_ratings_and_nominal_operating_assumptions":{
       "Yageo_AC1206_200V_continuous_250mW_reference":divider,
       "TAI_shunt_5mR_at_4A_w_nominal":round(shunt_w_at_4a,4),
       "RVS_200V_56V_nominal_zener_current_mA":round(i_rvs*1000,3),
       "RVS_each_2512_350ms_pulse_power_W":round(p_each_rvs,3),
       "RVS_each_2512_350ms_rectangular_energy_J":round(e_each_rvs,3),
       "zener_350ms_power_W":round(p_zener,3),
       "zener_350ms_energy_J":round(e_zener,3),
       "9V_7p510V_READY_RVS_feed_uA_model_only":round(i_rvs_ready_9v*1e6,2),
       "VS_total_MLCC_nominal_uF_NOT_CEFF_MIN":c_nom_uF,
       "C311_TPS38_typical_reset_delay_ms_not_min":round(t_delay_typ*1000,2)
     },
    "unresolved_stop_gate_ids":[x["id"] for x in critical],
    "vehicle_released":False,"pcb_fabrication_released":False,
    "note":"Pure KiCad-property and arithmetic source lock; live SOA/surge/capacitance/ESR/PCB tests NOT performed."
},indent=2,ensure_ascii=False))
