#!/usr/bin/env python3
"""STATIC measurement-plan integrity + voluntary numerical capture reviewer.

No acquisition, no hardware-pass declaration, no SPICE simulator. Missing data
must never count as pass. A trace summary without oscilloscope raw data is
NOT an electrical qualification.
"""
import argparse
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATRIX = HERE / "ROUND12_A23_INSTRUMENTATION_PIN_LIMIT_MATRIX_2026-10-16.csv"
PROVENANCE = HERE / "ROUND12_A23_PARAMETER_PROVENANCE_2026-10-16.csv"

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def plan_integrity():
    m, p = read_csv(MATRIX), read_csv(PROVENANCE)
    require(len(m) >= 40, "Unexpected measurement-point count")
    require(len({x["id"] for x in m}) == len(m), "Duplicate measurement IDs")
    require(all(x["physical_point_or_differential_pair"] and x["source_url"] for x in m), "Incomplete point")
    required = {
        "P02": "M8_BAT4-M8_GND3",
        "P06": "EFUSE_IN",
        "P07": "EFUSE_IN",
        "P08": "EFUSE_IN",
        "P09": "VIN_FUSED",
        "P11": "R6_B_GATE-VIN_FUSED",
        "P14": "R6_B_GATE-VIN_FUSED",
        "P17": "R6_B_GATE-VIN_FUSED",
        "P19": "R6_DRV-VIN_FUSED",
        "P20": "VIN_FUSED-GND",
        "P21": "VIN_PROTECTED_UNFUSED",
        "P30": "VIN_PROTECTED_UNFUSED",
        "P32": "BOOT-SW",
        "P39": "I_FIXTURE_PLUS",
    }
    by_id = {r["id"]:r for r in m}
    for k, v in required.items():
        require(by_id[k]["A23_net_or_pin"] == v, f"Wrong pin/network mapping: {k}")
    require(by_id["P02"]["stage"] == "FULL_INSTALL", "M8 boundary conflated with module fixture")
    require(by_id["P09"]["recommended_max_v"] == "60", "TPS IN_SYS max should be 60V recommended")
    require(by_id["P09"]["absolute_max_v"] == "67", "TPS IN_SYS abs should be 67V")
    require(by_id["P14"]["absolute_max_v"] == "50", "Q202 differential VDS 50V")
    require(by_id["P32"]["absolute_max_v"] == "5.5", "Buck BOOT-SW max 5.5V")
    require(len(p) >= 25, "Expected source/unknown parameter register")
    require(all(x["mpn"] and x["source_url"] for x in p), "Missing manufacturer provenance")
    require(all(x["value"] == "" for x in p if x["data_status"].startswith("OFFEN")),
            "Invented measurement in open parameter row")
    require(not any("F_MAIN" in (r["refdes"] or "") for r in p), "Off-board fuse counted as A23")
    return {"status":"PLAN_INTEGRITY_ONLY", "point_count":len(m),
            "parameter_rows":len(p), "vendor_pspice":"NOT_RUN",
            "hardware_measurements":"NOT_RUN", "pcb_drc":"NOT_RUN"}

def finite_nonnegative(v, field):
    require(isinstance(v, (int,float)) and math.isfinite(v) and v >= 0, f"{field} invalid")
    return float(v)

def assess_capture(capture, *, stage="BENCH_A23"):
    """Only checks reported voltage extrema; does not validate raw trace or scope."""
    points = {r["id"]:r for r in read_csv(MATRIX)}
    submitted = capture.get("measurements", [])
    require(isinstance(submitted, list), "measurements must be list")
    require(capture.get("stage") == stage, "stage must be declared; no M8-to-module equivalence")
    require(capture.get("run_id") and capture.get("equipment_ids"), "run and instruments required")
    seen, results = set(), []
    for v in submitted:
        k = v.get("point_id")
        require(k in points and k not in seen, f"invalid/duplicate point_id {k}")
        seen.add(k)
        row = points[k]
        require(row["stage"] == stage, f"point {k} belongs to {row['stage']}")
        umax = finite_nonnegative(v.get("expanded_uncertainty_v"), "expanded_uncertainty_v")
        mx = v.get("max_v"); mn = v.get("min_v")
        require(all(isinstance(z,(int,float)) and math.isfinite(z) for z in (mx,mn)),
                f"missing/non-finite extrema {k}")
        require(mx >= mn, f"negative extrema range {k}")
        require(v.get("raw_waveform_path") and v.get("probe_id"), f"missing source waveform/probe {k}")
        states = []
        def get_limit(name):
            try: return float(row[name])
            except (ValueError,TypeError): return None
        recommended_hi = get_limit("recommended_max_v")
        recommended_lo = get_limit("recommended_min_v")
        absolute_hi = get_limit("absolute_max_v")
        absolute_lo = get_limit("absolute_min_v")
        # Absolute violation is a more severe stop than recommended violation.
        if (absolute_hi is not None and mx + umax >= absolute_hi or
            absolute_lo is not None and mn - umax <= absolute_lo):
            states.append("ABSOLUTE_LIMIT_STOP")
        elif (recommended_hi is not None and mx + umax > recommended_hi or
              recommended_lo is not None and mn - umax < recommended_lo):
            states.append("RECOMMENDED_LIMIT_REVIEW_OR_FAIL")
        elif recommended_hi is None and recommended_lo is None:
            states.append("NO_NUMERIC_RECOMMENDED_LIMIT_REVIEW")
        else:
            states.append("NUMERIC_WITHIN_RECOMMENDED_ONLY")
        results.append({"point_id":k,"numeric_status":states[0]})
    needed = [r["id"] for r in points.values()
              if r["stage"] == stage and r["mandatory_first_lab"] == "YES"]
    missing = sorted(set(needed)-seen)
    return {
        "status":"ENGINEER_REVIEW_REQUIRED_NOT_HARDWARE_PASS",
        "missing_required_points":missing,
        "results":results,
        "notes":"Raw oscilloscope waveform, probe/bandwidth and all device pin limits need independent review."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check-plan",action="store_true")
    parser.add_argument("--assess",type=Path)
    parser.add_argument("--stage",choices=["BENCH_A23","FULL_INSTALL"],default="BENCH_A23")
    args=parser.parse_args()
    if not args.check_plan and not args.assess: parser.error("choose --check-plan or --assess")
    try:
        if args.assess:
            result=assess_capture(json.loads(args.assess.read_text(encoding="utf-8")),stage=args.stage)
        else:
            result=plan_integrity()
        print(json.dumps(result,indent=2))
    except (ValueError, KeyError) as err:
        parser.exit(status=2,message=f"MEASUREMENT_GATE_ERROR: {err}\n")
