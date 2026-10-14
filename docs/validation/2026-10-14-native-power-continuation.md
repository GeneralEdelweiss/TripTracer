# TripTracer power continuation — 2026-10-14

Status: schematic development; NO manufacturing or vehicle approval.

## Changes actually delivered

- USB power/ESP32 sheet pin endpoints, connected wires and labels aligned to 1.27 mm KiCad connection grid. The matching project-local ESP32, USB-C and ESD symbol definitions were synchronized. Pin numbers, selected MPNs and footprints were retained.
- Root hierarchy positions aligned; its status text updated. This change alone did NOT reduce ERC findings: KiCad had attributed off-grid USB-sheet objects to "/". Native UUID diagnostics identified the actual sheet.
- Native-netlist assertions now require every TLC555 and AND-gate pin on its exact rail, both trigger clamp polarities, AC trigger capacitor, POR components and MCU-HOLD fail-off resistor.
- ERC triage prints original item UUIDs and positions, without suppressing findings.

## Revision-bound native evidence

Baseline: 8734fc10245babc433a5b32ce8cf2ccd26fefdae; previous native run [38554476050](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38554476050): 116 ERC = 82 endpoint_off_grid warnings + 34 unconnected MCU pins.

Verified code/schematic head: **dd2fbd8b3d4b051699126eb4580be588043bb01d**.
[Native KiCad 10.0.6 run 38557303159](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38557303159), job 115829510408:

- ERC: **34 errors**, all pin_not_connected on ESP32 sheet. **0 endpoint_off_grid; 0 lib_symbol_mismatch**. Overall ERC still FAIL.
- Hierarchy: PASS; custom pinout guard: PASS.
- Native root netlist export: PASS.
- Input diode/TVS guard: PASS.
- LMR38020 buck topology: PASS.
- Exact timer/AND supply pins, clamp polarities, POR and fail-off: PASS.
- TPS2116 all eight pins, MCP1826S rail mapping, USB-C VBUS contacts and J901 source mapping: PASS.
- Supply BOM export: PASS, 53 components.
- Existing PCB: 5 DRC violations, 79 unconnected items, 77 schematic-parity issues. Overall workflow correctly FAILS.
- Compare baseline to verified head: only two schematic files, one symbol library and two check scripts changed. **No PCB file changed.**

These are connectivity and ERC findings, not waveform, reverse-leakage, thermal or surge measurements. No complete native netlist equivalence comparison or rendered visual inspection was performed in this turn. Existing USB/MCU/vehicle power net assertions passed after the coordinate changes.

## Newly identified electrical blocker: ACC live with BAT absent

01H R911 is fed from ACC_PROTECTED_IN, while U101 VIN comes from the separately fused BAT branch. With BAT disconnected/blown fuse and ACC still high, the passive R911/R912/D911/R913 path can raise BUCK_ENABLE while VIN is near zero.

TI LMR38020-Q1 Rev B section 6.1 specifies EN absolute maximum VIN+0.3 V; section 6.3 recommends EN no higher than VIN. [Manufacturer datasheet](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf).

Using only an illustrative 0.35 V D911 drop and nominal 100k/47k/100k values:
EN = (ACC/100k - 0.35*(1/100k+1/47k)) / (1/100k+1/47k+1/100k).
This gives approximately 1.92 V at ACC=9 V and 7.00 V at ACC=30 V, against 0.3 V absolute ceiling when VIN=0. Actual internal clamp current/rail backfeed depends on the device and must not be treated as safe merely because R911 is large.

**Not repaired or qualified in this change.** The startup path must be redesigned to reference its drive to available buck VIN, with independent ACC sensing, preserved cold start and bounded MCU hold. A generic Schottky clamp cannot simply be assumed to guarantee the +0.3 V limit over current/temperature. Verify BAT absent/ACC live, both source connection orders, reverse BAT/ACC, USB-only and ACC fall before approval. Existing TVS long-pulse/Test A/Test B gates remain open.

## Cost and scope

No components added, no MPN changes, no BOM quantity delta or new architecture selected. No purchasing or PCB work. Existing complete cost remains **NICHT BELASTBAR**; this change adds no claimed price saving. The remaining 34 GPIO errors are not hidden with no-connect markers because other functional sheets are still incomplete.
