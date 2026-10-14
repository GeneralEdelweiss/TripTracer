# TripTracer KiCad 10 ERC/DRC – latest checked supply baseline

CI run: [38542922950](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38542922950), branch `design/solid-state-power-v1`, 2026-10-14. Native artifacts `erc.json`, `drc.json` and native `TripTracer.net` were generated; electrical release **NOT GRANTED**.

## ERC – **187** violations (from native JSON)

| KiCad sheet | Count | Types |
| --- | ---: | --- |
| Root/hierarchy reporting bucket `/` | 150 | 132 endpoint_off_grid; 16 lib_symbol_mismatch; 1 lib_symbol_issues; 1 isolated_pin_label |
| 5-V buck | 1 | 1 power_pin_not_driven |
| ESP32 USB | 36 | 34 pin_not_connected; 2 power_pin_not_driven |
| **Total** | **187** | |

**Root reporting bucket is not exclusively root sheet:** first off-grid items explicitly belong to `01C_HOLD_TIMER.kicad_sch` (e.g. R502 pin end x=58.57 mm / y=169 mm and C502). Off-grid warning can be cured only by a consistent KiCad-grid correction of symbol positions, wire endpoints, label endpoints, and junctions **together**. Blind rounding risks breaking connected schematic nets. 16 symbol mismatches largely originate from ad hoc local R/C symbol definitions in the 01H ACC and 03 USB sheets, not a proven board error; synchronize their geometry/pin definitions to the portable canonical `Tripmaster_Sym` library and rerun native netlist guards. Isolated `BUCK_PG` label is currently attached to one pin only; remove unimplemented signal or connect properly to chosen diagnostic input with valid PG pullup.

**Do not insert fictitious `PWR_FLAG` components** to silence the three supply-driver warnings. Confirm VIN from real external fused source, ESP32 3V3 from a real supply, and low-voltage LDO data sheet. 34 unconnected ESP32 pins must be inspected intentionally before using no-connect markers.

## DRC

Native PCB DRC reports **5 violations** for the existing PCB. PCB schematic-parity warning exists because the power schematic now contains J901, ACC gate and TPS2116 etc which have not yet been transferred/routed on PCB. Consequently PCB is **not production-ready**. Reference current CI artifact for exact locations/types; never claim PCB passes based on electrical netlist checks.

## Passed functional connectivity regression tests

- Input diode BAT polarity and TVS orientation checked from native netlist.
- Buck U101 VIN, SW, BOOT, output separation checked.
- Entire eight-pad TPS2116 mux exact pins/net names checked; no direct USB VBUS-to-V5 or V3V3 bypass.
- J901 BAT+/ACC/GND pin assignment, two-NPN ACC logic and timed HOLD, ESP32 control GPIO net checks.
- 50 active schematic power components exported to preliminary BOM; prices incomplete.

## Next actionable gates

1. Synchronize local R/C embedded symbols (no circuit change); verify ERC `lib_symbol_mismatch` reduction and all netlist regression checks unchanged.
2. Correct off-grid problems in 01C using a documented point-based graph rewrite or KiCad eeschema interactive move preserving node connectivity; retest entire netlist.
3. Define actual PCB physical connector/strain relief, component footprints, protection and routed copper before PCB parity/DRC.
4. Verify 9–30V ACC thresholds/555 and USB supply transitions thermally and electrically on bench.
5. TVS 350ms Test B energy + diode and 3.3V LDO thermal SOA proof mandatory before hardware use.
