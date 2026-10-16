#!/usr/bin/env python3
"""Native all-severity KiCad10 ERC gate. Explicitly reports known warnings; never silently waives errors."""
import collections,json,sys
x=json.load(open(sys.argv[1],encoding="utf-8"))
v=[r for s in x.get("sheets",[]) for r in s.get("violations",[])]
fatal=[a for a in v if a.get("severity")=="error"]
allow={
 ("isolated_pin_label","Global Label 'ACC_INV_N'"),
 ("isolated_pin_label","Global Label 'MCU_HOLD_REQ'"),
 ("lib_symbol_mismatch","Symbol U921 [TPS26631_PWP20]")}
unexpected=[]
for a in v:
 if a.get("severity")=="error":continue
 item=a.get("items",[{}])[0].get("description","")
 if (a.get("type"),item) not in allow:unexpected.append((a.get("type"),item,a.get("description")))
result={"native_ERC_errors":len(fatal),"native_ERC_warnings":len(v)-len(fatal),
 "warnings_explicitly_unresolved":[{"type":a["type"],"items":[z.get("description") for z in a.get("items",[])]} for a in v if a.get("severity")!="error"],
 "error_types":dict(collections.Counter(x.get("type") for x in fatal)),
 "unexpected_new_warnings":unexpected,
 "complete_ERC_clean":len(v)==0,
 "automotive_fab_qualified":False}
print(json.dumps(result,indent=2))
if fatal or unexpected:raise SystemExit("ERC failed: errors or newly unreviewed warnings")
