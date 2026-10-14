#!/usr/bin/env python3
"""Assert manifest is consistent with ACTUAL KiCad power block symbol MPNs.
No claim of functional/thermal/automotive approval; this is a source-of-truth check.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "hardware" / "kicad"
data = json.loads((BASE / "power_selection.json").read_text(encoding="utf-8"))
assert data["selection"] == "KEEP_EXISTING_COTS_AUTOMOTIVE_BUCK"
assert data["release"]["ready_to_order_pcb"] is False
assert data["release"]["ready_for_vehicle"] is False
assert data["release"]["source_verified_stock_for_D902"] == "NO"
for key, expected in data["assembled_on_active_schematic"].items():
    s = (BASE / expected["sheet"]).read_text(encoding="utf-8")
    # Verify that a genuine instantiated REF is followed by its VALUE property.
    anchor = f'(property "Reference" "{expected["ref"]}"'
    at = s.find(anchor)
    assert at >= 0, f"{key}: missing {expected['ref']} in active schematic"
    tail = s[at:at + 800]
    assert f'(property "Value" "{expected["mpn"]}"' in tail, (
        f"{key}: KiCad part value differs from selected COTS manifest"
    )
root = (BASE / "TripTracer_V1.kicad_sch").read_text(encoding="utf-8")
entry = (BASE / "01_Eingangsschutz.kicad_sch").read_text(encoding="utf-8")
assert '"01_Eingangsschutz.kicad_sch"' in root
for s in ("02_5V_Buck.kicad_sch", "03_3V3_USB.kicad_sch"):
    assert f'"{s}"' in root, f"{s} not in root"
assert '"01G_SIMPLE_INPUT.kicad_sch"' in entry, "Manifest front-end is not active"
# An unqualified historical LM74930 circuit must NEVER be counted as present.
assert '"01D_INPUT_PROTECTION.kicad_sch"' not in entry, "Selection manifest obsolete: 01D is active"
assert any(c["mpn"] == "TI LM74930-Q1" and c["status"] != "ACTIVE_BUCK" for c in data["compared_cots"])
print(json.dumps({
    "ok": True, "description": "Actual active power-stage MPNs and hierarchy match the COTS selection",
    "selected": data["selection"],
    "verified_refs": {k:v["ref"] for k,v in data["assembled_on_active_schematic"].items()},
    "not_checked": ["ERC","DRC","electrical waveform","thermal","ISO pulses","stock confirmation"],
    "fabrication_release": False, "vehicle_release": False
}, indent=2, ensure_ascii=False))
