#!/usr/bin/env python3
"""Round11 A23 priced BOM audit; no component/hardware qualification.

Usage:
  python3 rev6_round11_a23_cost_audit.py --bom path/to/REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv --protection path/to/01_TPS26631_REV6_FACTORY_OVP.kicad_sch --buck path/to/02_5V_LMR38020_FACTORY_OVP.kicad_sch
Prices are EUR net per fitted reference at breaks of 1/10/100 from A order BOM
and explicitly cited vendor snapshots. The A source is pinned by Git blob hash.
"""
import argparse
import csv
from decimal import Decimal
import hashlib
from pathlib import Path
import re

EXPECTED_A23_BLOB = "ea8cf61eef9f18f5585581a9a9ea67abb47951c8"
EXPECTED_MPN = {
    "U201": "TPS26631PWPR", "Q201": "SQM100N10-10_GE3",
    "Q202": "BSS138LT1G", "R201": "AC1206FR-07330KL",
    "R204": "CRCW12066K04FKEAHP", "C201": "C1210C105K1RACAUTO",
    "C202": "C1210C105K1RACAUTO", "C203": "C1206C104K1RACAUTO",
    "U101": "LMR38020SQDDARQ1", "L101": "SRP7050TA-150M",
    "C102": "C1206C104K1RACTU", "R101": "RC1206FR-07100KL",
    "R102": "RC1206FR-0724K9L", "R103": "RC1206FR-0764K9L",
    "C101": "12101C475K4Z2A", "C107": "C1206C104K1RACTU",
    "C104": "MCAST32MSB7226KPNA01",
    "C105": "MCAST32MSB7226KPNA01",
    "C106": "MCAST32MSB7226KPNA01",
    "C108": "12101C475K4Z2A", "R501": "RC1206FR-07100KL",
    "R502": "RC1206FR-071ML", "Q501": "BVSS123LT1G",
}
BREAKS = ("1", "10", "100")
D = Decimal
QUOTE = {
    # Exact same Vishay MPN, DigiKey DE indexed 2026-10-16
    "vishay_dk": (D("3.7600"), D("2.4720"), D("1.7404")),
    # Exact same Bourns MPN, DigiKey DE indexed 2026-10-16
    "bourns_dk": (D("0.9500"), D("0.7830"), D("0.6435")),
    # Toshiba alternate, DigiKey EUR indexed 2026-10-16; NEEDS QUALIFICATION
    "toshiba_dk": (D("1.2200"), D("0.7670"), D("0.5074")),
    # KYOCERA AVX standard terminal, Round10 source snapshot, NOT EQUIVALENT
    "kam_unqualified": (D("0.7830"), D("0.4950"), D("0.3490")),
    # Supplemental 68k 1206 A24 hypothetical, Round10 snapshot
    "a24_68k": (D("0.0860"), D("0.0220"), D("0.0150")),
}
SOURCES = {
    "vishay_dk": "https://www.digikey.de/de/products/detail/vishay-siliconix/SQM100N10-10-GE3/8556397",
    "bourns_dk": "https://www.digikey.de/en/products/detail/bourns-inc/SRP7050TA-150M/5429680",
    "toshiba_dk": "https://www.digikey.it/de/products/detail/toshiba-semiconductor-and-storage/TK11S10N1L-LQ/12758189",
    "kam_unqualified": "C-Round10 quotation only; live stock/price not refreshed",
    "a24_68k": "A-Round5 / C-Round10 estimate; no proven extra function",
}

def read_source(path):
    data = Path(path).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    assert blob == EXPECTED_A23_BLOB, f"A23 source changed ({blob}); RE-AUDIT, do not silently reprice"
    text = data.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    parts = [r for r in rows if r["ref"] != "SUMMARY_23_FITTED"]
    assert len(parts) == 23
    assert set(r["ref"] for r in parts) == set(EXPECTED_MPN)
    assert len({r["ref"] for r in parts}) == 23
    for row in parts:
        assert row["mpn"] == EXPECTED_MPN[row["ref"]], row
        assert int(row["qty"]) == 1, row
        assert row["KiCad_footprint"], row
        assert all(D(row["eur_exVAT_" + n]) >= 0 for n in BREAKS)
        assert not any(t in row["ref"].upper() for t in ("FUSE", "F_MAIN", "HOLDER"))
    totals = tuple(sum(D(r["eur_exVAT_" + n]) for r in parts) for n in BREAKS)
    assert totals == (D("20.2570"), D("13.5610"), D("10.6266")), totals
    assert rows[-1]["ref"] == "SUMMARY_23_FITTED"
    return parts, totals

def check_schematics(parts, protection, buck):
    if not (protection and buck):
        return "SKIPPED (no A23 .kicad_sch paths supplied)"
    sheets = Path(protection).read_text(encoding="utf-8") + "\n" + Path(buck).read_text(encoding="utf-8")
    refs = re.findall(r'\(property\s+"Reference"\s+"([A-Z][A-Z0-9]+)"', sheets)
    # KiCad embeds full library symbols; count only explicit fitted references.
    actual = {ref for ref in refs if ref in EXPECTED_MPN}
    assert set(EXPECTED_MPN) <= actual, set(EXPECTED_MPN) - actual
    for ref in ("R202", "R203"):
        assert ref not in refs, f"{ref} legacy divider appeared in A23"
    # This verifies fitted references, not electrical nets, ERC or padmap.
    return "PASS reference-presence, NOT ERC/electrical qualification"

def matrices(parts):
    p = {r["ref"]: r for r in parts}
    def quote(ref, k, n):
        return QUOTE[k][BREAKS.index(n)]
    def baseline(ref, n):
        return D(p[ref]["eur_exVAT_" + n])
    def scenario(name, overrides, *, a24=False, status=""):
        unit = []
        for n in BREAKS:
            val = sum((quote(ref, k, n) if ref in overrides else baseline(ref, n))
                      for ref, k in ((ref, overrides.get(ref, "")) for ref in p))
            if a24:
                val += quote("R_EXTRA", "a24_68k", n)
            unit.append(val.quantize(D("0.0001")))
        return name, (24 if a24 else 23), unit, status
    return [
        scenario("A23_as_drawn_source_quotes", {}, status="REAL_A23_DESIGN_NOT_FAB"),
        scenario("A23_same_MPN_dk_vishay_bourns",
                 {"Q201": "vishay_dk", "L101": "bourns_dk"},
                 status="PURCHASING_ONLY_NO_ELECTRICAL_CHANGE"),
        scenario("A23_toshiba_dk_UNQUALIFIED", {"Q201": "toshiba_dk"},
                 status="NO_GO_UNTIL_Q201_GATE_SOA_THERMAL_PCB"),
        scenario("A23_toshiba_plus_bourns_dk_UNQUALIFIED",
                 {"Q201": "toshiba_dk", "L101": "bourns_dk"},
                 status="NO_GO_UNTIL_Q201_GATE_SOA_THERMAL_PCB"),
        scenario("A23_toshiba_bourns_KAM_RESEARCH_ONLY",
                 {"Q201": "toshiba_dk", "L101": "bourns_dk",
                  "C101": "kam_unqualified", "C108": "kam_unqualified"},
                 status="NO_GO_TOSHIBA_AND_FLEXITERM_CEFF_UNVERIFIED"),
        scenario("A24_68k_NOT_BUILT", {}, a24=True,
                 status="OPTION_ONLY_UVLO_BROWNOUT_PROOF_ABSENT"),
    ]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bom", required=True)
    ap.add_argument("--protection")
    ap.add_argument("--buck")
    ap.add_argument("--output")
    args = ap.parse_args()
    parts, totals = read_source(args.bom)
    sheet = check_schematics(parts, args.protection, args.buck)
    data = matrices(parts)
    expected = {
        "A23_as_drawn_source_quotes": ("20.2570", "13.5610", "10.6266"),
        "A23_same_MPN_dk_vishay_bourns": ("20.2070", "13.5170", "10.5957"),
        "A23_toshiba_dk_UNQUALIFIED": ("17.6970", "11.8380", "9.3840"),
        "A23_toshiba_plus_bourns_dk_UNQUALIFIED": ("17.6670", "11.8120", "9.3627"),
        "A23_toshiba_bourns_KAM_RESEARCH_ONLY": ("17.5130", "11.7080", "9.2855"),
        "A24_68k_NOT_BUILT": ("20.3430", "13.5830", "10.6416"),
    }
    for name, qty, values, status in data:
        assert tuple(f"{v:.4f}" for v in values) == expected[name], (name, values)
        assert qty in (23, 24)
        print(f"{name}: {qty} positions, EUR/unit={values}, status={status}")
    print("SOURCE_PINNED Git_blob=", EXPECTED_A23_BLOB, "SCHEMATIC_CHECK=", sheet)
    print("NOT INCLUDED: connectors, RAW/temp, mainboard, offboard fuses, wiring, PCB, stencil, assembly, tax, freight.")
    print("NOT ASSERTED: full 23/23 real-time stock, MLCC Ceff, PCB DRC, KiCad ERC, 58V or +60C hardware approval.")
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as handle:
            w = csv.writer(handle)
            w.writerow(["variant", "populated_positions", "eur_exVAT_1_per_unit",
                        "eur_exVAT_10_per_unit", "eur_exVAT_100_per_unit", "status"])
            for name, qty, values, status in data:
                w.writerow([name, qty, *[f"{v:.4f}" for v in values], status])
    print("PASS pinned reference/MPN/pricing arithmetic and scenario status labeling")

if __name__ == "__main__":
    main()
