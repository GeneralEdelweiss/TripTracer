"""Check known safety-critical custom KiCad symbol pinouts.

No claims about other pinouts, footprints, ERC, or automotive safety.
Run: python3 tools/check_kicad_custom_pinouts.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "hardware" / "kicad"

def block(text, token):
    start = text.index(token)
    depth, quoted, slash = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if quoted:
            if slash:
                slash = False
            elif ch == "\\":
                slash = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    raise AssertionError(f"unbalanced {token}")

def check():
    lib = (ROOT / "TripTracer_V1.kicad_sym").read_text()
    sheet = (ROOT / "01F_RC_SHUTDOWN.kicad_sch").read_text()
    for txt, symbol_name in ((lib, "BAS116Q_SOT23"),
                             (sheet, "TripTracer_V1:BAS116Q_SOT23")):
        symbol = block(txt, f'(symbol "{symbol_name}"')
        pins = re.findall(
            r'\(pin\s+(\w+)\s+line.*?\(name "([^"]+)"[^\n]*?'
            r'\(number "([0-9]+)"', symbol)
        assert sorted(pins) == sorted([
            ("passive", "A1", "1"),
            ("no_connect", "NC2", "2"),
            ("passive", "K3", "3"),
        ]), (symbol_name, pins)
    assert '(xy 83.82 106.68)' not in sheet, "BAS116 NC2 remains connected"
    for txt, sym_name in ((lib, "NMOS_GDS_127"),
                          (sheet, "TripTracer_V1:NMOS_GDS_127")):
        sym = block(txt, f'(symbol "{sym_name}"')
        for suffix in ("0_1", "1_1"):
            assert f'(symbol "NMOS_GDS_127_{suffix}"' in sym
    for txt, sym_name in ((lib, "NMOS_GDS_127"),
                          (sheet, "TripTracer_V1:NMOS_GDS_127")):
        sym = block(txt, f'(symbol "{sym_name}"')
        pins = re.findall(
            r'\(pin\s+(\w+)\s+line.*?\(name "([^"]+)"[^\n]*?'
            r'\(number "([0-9]+)"', sym)
        assert sorted(pins) == sorted([
            ("input", "G", "1"), ("passive", "S", "2"),
            ("passive", "D", "3"),
        ]), (sym_name, pins)
    active = (ROOT / "01D_INPUT_PROTECTION.kicad_sch").read_text()
    expected_fets = (
        ("IPB17N25S3_100", "TO-263-3_TabPin2"),
        ("IPD90N10S4_06", "TO-252-3_TabPin2"),
    )
    for suffix, footprint in expected_fets:
        for txt, full in ((lib, suffix), (active, f"TripTracer_V1:{suffix}")):
            body = block(txt, f'(symbol "{full}"')
            pins = re.findall(
                r'\(pin\s+(\w+)\s+line.*?\(name "([^"]+)"[^\n]*?'
                r'\(number "([0-9]+)"', body)
            assert sorted(pins) == sorted((
                ("input", "G", "1"), ("passive", "D", "2"),
                ("passive", "S", "3")
            )), (full, pins)
            assert footprint in body, (full, "footprint mismatch")
    q1 = block(active, '(symbol (lib_id "TripTracer_V1:IPB17N25S3_100"')
    q2 = block(active, '(symbol (lib_id "TripTracer_V1:IPD90N10S4_06"')
    assert '(property "Reference" "Q401"' in q1
    assert '(property "Reference" "Q402"' in q2
    print("PASS: BAS116Q A1 / NC2 / K3 DMN2056U and Q401/Q402 gate/drain/source pinouts")

if __name__ == "__main__":
    check()
