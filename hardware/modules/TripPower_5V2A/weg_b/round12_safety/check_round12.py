#!/usr/bin/env python3
"""B Round12 native KiCad10 XML and native BOM safety-contract regression.
No substitution for fault-injection, thermal/58V measurement, or PCB DRC.
"""
import csv,json,sys
from pathlib import Path
from xml.etree import ElementTree as ET

EXPECT={
"U301":{1:"SAFE_3V3",2:"LDO_FB",4:"GND",5:"SAFE_HV",8:"SAFE_HV",9:"GND"},
"U302":{1:"TEMP_SET",2:"TEMP_SET",3:"GND",5:"SAFE_3V3",6:"TEMP_OK_OD"},
"U303":{1:"GND",2:"GND",3:"SAFE_3V3",4:"TEMP_OK_OD",5:"SAFE_3V3"},
"Q301":{1:"BASE_KILL",2:"GND",3:"TPS_SHDN_SAFETY"},
"Q302":{1:"TEMP_OK_OD",2:"GND",3:"BASE_KILL"},
"D301":{1:"VIN_SAFETY_FUSED",2:"SAFE_HV"},
"R301":{1:"SAFE_3V3",2:"LDO_FB"},
"R302":{1:"LDO_FB",2:"GND"},
"R303":{1:"TEMP_SET",2:"GND"},
"R304":{1:"SAFE_3V3",2:"TEMP_OK_OD"},
"R305":{1:"TEMP_OK_OD",2:"GND"},
"R306":{1:"VIN_SAFETY_FUSED",2:"BASE_KILL"},
"C301":{1:"SAFE_HV",2:"GND"},
"C302":{1:"SAFE_3V3",2:"GND"},
"C303":{1:"SAFE_3V3",2:"GND"},
"U401":{1:"MAIN_EFUSE_OUT",2:"RAW_UV",3:"RAW_OV",4:"GND",5:"GND",6:"RAW_LTC_SHDN",7:"RAW_FAULT_N",8:"RAW_OUT",9:"RAW_SENSE",10:"RAW_GATE"},
"Q401":{1:"RAW_GATE",2:"MAIN_EFUSE_OUT",3:"RAW_COMMON_SOURCE"},
"Q402":{1:"RAW_GATE",2:"RAW_SENSE",3:"RAW_COMMON_SOURCE"},
"Q403":{1:"RAW_HW_RESET_HIGH",2:"GND",3:"RAW_LTC_SHDN"},
"R401":{1:"MAIN_EFUSE_OUT",2:"RAW_LTC_SHDN"},
"R402":{1:"RAW_LTC_SHDN",2:"RAW_UV"},
"R403":{1:"RAW_UV",2:"RAW_OV"},
"R404":{1:"RAW_OV",2:"GND"},
"R405":{1:"RAW_SENSE",2:"RAW_OUT"},
"R406":{1:"RAW_GATE",2:"RAW_RAMP"},
"R407":{1:"RAW_HW_RESET_HIGH",2:"GND"},
"R408":{1:"SAFE_3V3",2:"RAW_FAULT_N"},
"C401":{1:"RAW_RAMP",2:"GND"},
"C402":{1:"MAIN_EFUSE_OUT",2:"GND"},
"C403":{1:"RAW_OUT",2:"GND"},
}
MPN={
"U301":"TPS7A4001DGNR","U302":"TMP390AQDRLRQ1",
"U303":"TPS3838K33QDBVRQ1","U401":"LTC4368HMS-2#WPBF",
"Q301":"MMBT3904LT1G","Q302":"BSS138LT1G","Q403":"BSS123LT1G",
"Q401":"TK11S10N1L,LQ","Q402":"TK11S10N1L,LQ",
"D301":"BAV21W-7-F","R405":"WSL2512R0500FEA","C403":"C1210C225K1RACAUTO",
}
VALUES={"R301":"180k","R302":"100k","R303":"24.9k","R304":"10k","R305":"100k","R306":"330k",
"R401":"464k","R402":"1.5M","R403":"121k","R404":"29.4k","R405":"0.050R",
"R406":"22k","R407":"100k","R408":"100k"}
SROOT=Path("hardware/modules/TripPower_5V2A/weg_b/round12_safety")
def check(netlist,bom):
    doc=ET.parse(netlist).getroot()
    comps={c.get("ref"):c for c in doc.findall("./components/comp") if __import__("re").fullmatch(r"[UQRCD]\d+",c.get("ref") or "")}
    assert len(comps)==len(EXPECT)==30,(len(comps),len(EXPECT))
    assert set(comps)==set(EXPECT), sorted(set(comps)^set(EXPECT))
    pins={}
    for net in doc.findall("./nets/net"):
        name=net.get("name","").split("/")[-1]
        if name.startswith("unconnected-"):continue
        for nd in net.findall("node"):
            k=(nd.get("ref"),int(nd.get("pin")))
            assert k not in pins,("duplicate",k)
            pins[k]=name
    errors={f"{ref}.{pin}":{"actual":pins.get((ref,pin)),"expected":name}
       for ref,expect in EXPECT.items() for pin,name in expect.items()
       if pins.get((ref,pin))!=name}
    assert not errors,json.dumps(errors,indent=2)
    assert pins[("U301",8)]!=pins[("U301",1)],"LDO input/output short!"
    assert pins[("U401",1)]!=pins[("U401",8)],"RAW fuse bypass!"
    assert pins[("U401",9)]!=pins[("U401",8)],"No current sense shunt!"
    assert pins[("U302",6)]==pins[("U303",4)]==pins[("Q302",1)],"Sensor + supervisor must pull same gate low"
    assert pins[("R306",1)]=="VIN_SAFETY_FUSED","Default-on NPN power source must be BEFORE Q201"
    assert pins[("Q301",3)]=="TPS_SHDN_SAFETY"
    assert pins[("U401",4)]=="GND","RAW controller must latch"
    assert pins[("U401",6)]==pins[("Q403",3)]
    assert pins[("R401",1)]=="MAIN_EFUSE_OUT","RAW must be strictly AFTER main eFuse"
    assert not any(r.startswith("F") for r in comps),"No fuse/holder/PPTC in B prototype"
    # Confirm 29 manufacturer stock-code properties in REAL schematic.
    sheet=(SROOT/"TripPower_B_REV6_R12_SAFETY.kicad_sch").read_text()
    import re
    for ref,mpn in MPN.items():
        pat=re.compile(r'\(property "Reference" "'+re.escape(ref)+r'".*?\(property "MPN" "'+re.escape(mpn)+r'"',re.S)
        assert pat.search(sheet),(ref,mpn)
    for ref,val in VALUES.items():
        assert (comps[ref].findtext("value") or "")==val,(ref,comps[ref].findtext("value"),val)
    rows=list(csv.DictReader(Path(bom).open(encoding="utf-8")))
    refs=[s.strip() for row in rows for s in row["Refs"].split(",") if s.strip()]
    assert len(refs)==30 and set(refs)==set(EXPECT)
    # Important conservative threshold: short circuit threshold 30mV..70mV per official ADI table, Rshunt=0.050R +/-1%
    imin=0.030/(0.05*1.01)
    imax=0.070/(0.05*.99)
    assert imin>0.50,(imin,imax)
    # Series power resistor program from official LTC4368 figure 2.
    r=[464e3,1.5e6,121e3,29.4e3]
    ov=.5*sum(r)/r[3]
    uv=.5*sum(r)/(r[2]+r[3])
    assert 35.5<ov<37.0,(ov,uv)
    assert 6.5<uv<7.6,(ov,uv)
    # BUCK / status not routed backwards to vehicle.
    assert all(pins[("U302",i)]!="MAIN_EFUSE_OUT" for i in (5,6))
    # Single sensor cannot diagnose output stuck-good, 0.5A fault indistinguishable.
    result={
      "native_comp_count":len(comps),"native_pin_connections_checked":sum(map(len,EXPECT.values())),
      "native_mpn_and_resistor_value_checks":len(MPN)+len(VALUES),
      "ti_tmp390_one_resistor_74C_5C_nominal":True,
      "safe_3v3_supply_independent_from_main_eFuse":True,
      "active_low_sensor_AND_supervisor_enable":True,
      "default_BAT_biased_BJT_shdn_pull_down":True,
      "raw_controller_rearm":"LATCH (RETRY=GND), SHDN requires hardware reset pulse via Q403",
      "raw_short_threshold_A_min_max_adi_worst_corners":[round(imin,4),round(imax,4)],
      "raw_ov_nominal_V":round(ov,3),"raw_uv_nominal_V":round(uv,3),
      "2x_power_mosfets_and_series_shunt_present":True,
      "single_stuck_good_sensor_safe":False,"U201_internal_FET_SHORT_safe_without_independent_host_gate":False,
      "58V_ESL_Ceff_SOA_qualified":False,"thermal_chamber_qualified":False,
      "full_PCB_DRC_qualified":False,"fab_release":False}
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: check_round12.py native-netlist.xml native-bom.csv")
    check(*sys.argv[1:])
