#!/usr/bin/env python3
"""Produce native integration parts ledger split into A23 core, host and offboard.
No fabricated host prices, NO FAB. Native BOM from KiCad 10 is sole source for fitted parts."""
import csv,sys,json,re
from pathlib import Path
from decimal import Decimal
VENDOR=Path("hardware/modules/TripPower_REV6_A/REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv")
MAPPING={"U201":"U921","Q201":"Q941","Q202":"Q942","R201":"R941","R204":"R944","C201":"C941","C202":"C942","C203":"C943"}
HEAD=("category","ref","qty","manufacturer","mpn","footprint","eur_exVAT_1","eur_exVAT_10","eur_exVAT_100","status")
COST=["eur_exVAT_1","eur_exVAT_10","eur_exVAT_100"]
SHEETS=[Path("hardware/kicad/TripTracer_A23_Integration/01_TPS26631_A23_INTEGRATED.kicad_sch"),
        Path("hardware/kicad/TripTracer_A23_Integration/02_5V_A23_INTEGRATED.kicad_sch")]
def source_mpn(ref):
    for sheet in SHEETS:
        s=sheet.read_text(encoding="utf-8")
        start=s.find('(property "Reference" "'+ref+'"')
        if start<0:continue
        end=s.find('(instances ',start)
        if end<0 or end-start>3000:raise AssertionError(("cannot bound native placed symbol",ref,sheet))
        field=re.search(r'\(property "MPN" "([^"]+)"',s[start:end])
        if not field:raise AssertionError(("placed A23 component missing MPN",ref,str(sheet)))
        return field.group(1)
    raise AssertionError(("A23 placed component not found",ref))
def run(native,output,summary):
 with open(VENDOR,newline="",encoding="utf-8") as f: old=list(csv.DictReader(f))
 source={MAPPING.get(p["ref"],p["ref"]):p for p in old if p["ref"]!="SUMMARY_23_FITTED"}
 assert len(source)==23 and len(set(source))==23
 with open(native,newline="",encoding="utf-8") as f: n=list(csv.DictReader(f))
 assert n, "No native KiCad BOM"
 result=[];found=set();host_missing=[]
 for item in n:
  refs=[x.strip() for x in item["Refs"].split(",") if x.strip()]
  for ref in refs:
   assert ref not in found,("native duplicate",ref)
   found.add(ref)
   if ref in source:
    v=source[ref]
    # KiCad is authority, do not tolerate MPN substitution
    assert source_mpn(ref)==v["mpn"],("placed source MPN vs order list",ref,source_mpn(ref),v["mpn"])
    native_footprint=item["Footprint"]
    expected=v["KiCad_footprint"]
    if ref=="U921":expected="TripPowerFP:TI_TPS26631_PWP_EP"
    if ref=="L101":expected="TripPowerFP:L_Bourns_SRP7050TA_150M"
    assert native_footprint==expected,("native KiCad Footprint mismatch",ref,native_footprint,expected)
    result.append(["A23_CORE",ref,"1",v["manufacturer"],v["mpn"],v["KiCad_footprint"],*[v[z] for z in COST],"A23_VENDOR_QUOTE_NOT_FAB"])
   else:
    v={key:str(value) for key,value in item.items()}
    mpn=v.get("MPN","").strip()
    if ref=="R907":mpn="AC1206FR-0710KL"
    if not mpn:host_missing.append(ref)
    result.append(["HOST_EXISTING_OR_NEW",ref,"1","NOT_FULLY_AUDITED",mpn or "UNSPECIFIED",v.get("Footprint",""),"","","","HOST_UNPRICED_OR_MPN_UNVERIFIED"])
 assert set(source).issubset(found),(set(source)-found)
 for ref,val in (("J902","M8 source connector physical OFFBOARD only"),("F901","external BAT fuse"),("F902","external ACC fuse"),("J901","external current limited LAB pigtail")):
  assert ref not in found,("Offboard represented as fitted!",ref)
  result.append(["OFFBOARD_NOT_FITTED",ref,"0","EXTERNAL_ONLY",val,"","","","","NOT_PART_OF_ANY_PCB_BOM"])
 with open(output,"w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(HEAD);w.writerows(result)
 prices={q:str(sum((Decimal(row[6+i]) for row in result if row[0]=="A23_CORE"),Decimal(0))) for i,q in enumerate(COST)}
 assert [prices[z] for z in COST]==["20.2570","13.5610","10.6266"],prices
 status={"A23_core_populated":23,"host_populated":len(found)-23,"offboard_not_fitted":4,
    "A23_vendor_EUR_exVAT_module_at_quantities_1_10_100":[prices[z] for z in COST],
    "host_unpriced_missing_MPN_refs":sorted(host_missing),"complete_host_cost_EUR":None,
    "module_core_only_no_mounting_shipping_VAT":True,"all_required_host_85C_RAW_controls_present":False,
    "no_production_release":True}
 Path(summary).write_text(json.dumps(status,indent=2),encoding="utf-8")
 print(json.dumps(status,indent=2))
if __name__=="__main__":run(*sys.argv[1:])
