#!/usr/bin/env python3
"""Round12: pinned A23 sourcing + 3D file existence + missing D parameters.
Checks evidence consistency, NOT vendor API, KiCad ERC, PCB DRC or fab approval.
"""
import argparse,csv,hashlib,json,re
from pathlib import Path
from collections import Counter
from decimal import Decimal as D

GIT_BLOB="ea8cf61eef9f18f5585581a9a9ea67abb47951c8"
REFS=set("U201 Q201 Q202 R201 R204 C201 C202 C203 U101 L101 C102 R101 R102 R103 C101 C107 C104 C105 C106 C108 R501 R502 Q501".split())

def read(p):
    with open(p,encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def check(args):
    data=Path(args.source_bom).read_bytes()
    h=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    assert h==GIT_BLOB,("A23 source changed",h)
    source=[r for r in read(args.source_bom) if r["ref"]!="SUMMARY_23_FITTED"]
    ledger=read(args.ledger); ds=read(args.d_matrix)
    assert len(source)==len(ledger)==23
    assert {r["ref"] for r in source}=={r["ref"] for r in ledger}==REFS
    orig={r["ref"]:r for r in source}
    for p in ledger:
        q=orig[p["ref"]]
        assert all(p[k]==q[k] for k in ("ref","qty","manufacturer","mpn")),p["ref"]
        assert p["kicad_footprint"]==q["KiCad_footprint"]
        assert p["freshness"] in ("INDEXED","A23_ONLY")
        assert p["source_url"].startswith("https://")
        assert p["lifecycle_evidence"] and p["risk_notes"] is not None
        assert p["mpn"] and not re.search(r"fuse|holder",p["mpn"],re.I)
        for n in ("1","10","100"):
            assert D(p["a23_eur_unit_"+n])==D(q["eur_exVAT_"+n])
            assert D(p["vendor_index_eur_unit_"+n])>0
    baseline=[sum(D(x["eur_exVAT_"+n]) for x in source) for n in ("1","10","100")]
    assert baseline==[D("20.2570"),D("13.5610"),D("10.6266")]
    assert len({x["mpn"] for x in ledger})==17
    assert {d["ref_group"] for d in ds}==set("C201 C202 C101+C108 C104+C105+C106 Q201_COSS PARASITIC_PRE_FET".split())
    for d in ds:
        assert d["source_class"]!="VENDOR_VERIFIED"
        assert all(not d[k] for k in ("ceff_uF_verified","esr_ohm_verified","esl_nH_verified"))
        if d["ref_group"]=="C201":assert "IN_SYS" in d["physical_node"]
        if d["ref_group"]=="C202":assert "after eFuse" in d["physical_node"]
        if d["ref_group"]=="C101+C108":assert "after eFuse" in d["physical_node"]
        if d["ref_group"]=="C104+C105+C106":
            assert "5V_OUT" in d["physical_node"] and float(d["dc_bias_V"])<=25
    assert any(d["ref_group"]=="C201" and d["dc_bias_V"]=="58" for d in ds)
    module=Path(args.a_module)
    models=[]
    for p in ledger:
        fp=p["kicad_footprint"]; lib,name=fp.split(":",1)
        if lib!="Tripmaster":
            status="KICAD_STANDARD_LIBRARY_AND_MODEL_NOT_CHECKED"
            model=""
        else:
            f=module/"Tripmaster.pretty"/(name+".kicad_mod")
            assert f.is_file(),("MISSING_CUSTOM_FOOTPRINT",f)
            txt=f.read_text(encoding="utf-8")
            found=re.findall(r'\(model\s+"([^"]+)"',txt)
            assert len(found)<=1
            model=found[0] if found else ""
            if not model:status="NO_CUSTOM_3D_REFERENCE"
            elif model.startswith("\x24{KIPRJMOD}/"):
                rel=model.removeprefix("\x24{KIPRJMOD}/")
                status="CUSTOM_MODEL_PRESENT" if (module/rel).is_file() else "BROKEN_CUSTOM_MODEL_PATH"
            else:status="CUSTOM_MODEL_PATH_NOT_RESOLVED"
        models.append(dict(ref=p["ref"],mpn=p["mpn"],footprint=fp,model=model,model_status=status,
                           fab_status="UNVERIFIED_LANDPATTERN_3D_PLACEMENT"))
    batches=[]
    for n in (1,10,100):
        original=sum(D(p["a23_eur_unit_"+str(n)]) for p in ledger)
        mixed=sum(D(p["vendor_index_eur_unit_"+str(n)]) for p in ledger)
        issues=[]
        for p in ledger:
            stock=p["indexed_stock_or_snapshot"]
            if p["freshness"]!="INDEXED":reason="NOT_REFRESHED"
            elif not stock:reason="UNKNOWN"
            elif int(stock)<n*int(p["qty"]):reason="INSUFFICIENT"
            else:reason=""
            if reason:issues.append(p["ref"]+":"+p["mpn"]+":"+reason)
        assert any(x.startswith("U101:") for x in issues)
        assert any(x.startswith("Q501:") for x in issues)
        batches.append(dict(modules=n,original_A23_snapshot_unit_EUR=str(original),
                            indexed_mixed_unorderable_unit_EUR=str(mixed),
                            original_A23_total_EUR=str(original*n),
                            indexed_mixed_unorderable_total_EUR=str(mixed*n),
                            incomplete_or_insufficient=issues,
                            release="BLOCKED_NO_CONFIRMED_FULL_CART"))
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    with open(out/"round12_footprint_3d_gaps.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(models[0]));w.writeheader();w.writerows(models)
    obj=dict(source_blob=GIT_BLOB,positions=23,unique_mpns=17,
             indexed_positions=sum(p["freshness"]=="INDEXED" for p in ledger),
             unrefreshed_positions=sum(p["freshness"]=="A23_ONLY" for p in ledger),
             d_parameter_records=len(ds),vendor_ceff_records=0,vendor_esr_records=0,vendor_esl_records=0,
             model_status_counts=dict(Counter(m["model_status"] for m in models)),
             batches=batches,qualifications="NO FAB/PCB/58V/THERMAL; CI checks source and pricing arithmetic only")
    (out/"round12_bom_procurement_gate.json").write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(obj,indent=2))
    print("PASS source/23-ref/MPN/price/3D existence/D-dataset-integrity, PURCHASING BLOCKED")
def main():
    p=argparse.ArgumentParser()
    for x in ("source-bom","ledger","d-matrix","a-module","out-dir"):p.add_argument("--"+x,required=True)
    check(p.parse_args())
if __name__=="__main__":main()
