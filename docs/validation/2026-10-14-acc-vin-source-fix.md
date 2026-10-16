# ACC-only EN overstress correction — 2026-10-14

Electrical schematic correction; native KiCad 10.0.6 verification below. No PCB or vehicle release.

**Follow-on:** [prearmed ACC-off HOLD correction](2026-10-14-prearmed-acc-hold.md) supersedes the Q912/Q913 inversion and edge-trigger timer description below. The VIN-only startup correction and its evidence remain valid.

## Actual circuit

Removed direct ACC -> R911/R912/D911 -> EN divider. New Q914 NPN sinks Q915 PNP base through R922. Q915 emitter is exclusively U101 VIN (HV_PROTECTED_AFTER_EFUSE); its collector feeds EN through R911. R912 pulls Q915 base to its emitter when ACC is absent. R923 feeds Q914 base from ACC; R924 ensures fail-off. Existing D911 is reused as reverse base-emitter clamp (anode ground, cathode Q914 base), rather than an ACC-to-EN OR diode. Thus ACC=30V with BAT/VIN=0 has no resistor/forward-diode supply path to EN. The new source is independent of 5V/3V3 for cold start.

R911 and R915 are now 33k, R913=10k. Lower EN pull-down improves off-state leakage margin and both startup/HOLD sources retain usable 9V headroom. Q912/Q913 3V3 ACC detection, 555 trigger/reset/AND, MCU GPIO, optical HOLD, USB mux and downstream rails retain their previous electrical nets. Original Q912 reverse-ACC stress remains a separate pre-existing qualification item.

## Parts and manufacturer checks

- Q914 Nexperia **PMBT5551,215**, NPN 160V: B1/E2/C3.
  https://assets.nexperia.com/documents/data-sheet/PMBT5551.pdf
- Q915 Diodes **MMBT5401-7-F**, PNP 150V: B1/E2/C3.
  https://www.diodes.com/datasheet/download/MMBT5401.pdf
- Both use existing local Tripmaster:Q_SOT23_1B2E3C: pads1/2 at x=-/+0.95mm, y=1.1mm; pad3 x=0,y=-1.1mm, 0.85x0.95mm lands. Pin numbering and 1.9mm pitch match SOT23; manufacturer body envelopes checked. Pad size differs from vendor minimum recommended land pattern; solder-process/courtyard/thermal qualification stays OPEN before PCB.
- R922/R923 **Panasonic ERJP08F1002V**, 10k 1%, 1206 high-power candidate (>=0.5W required; manufacturer product page confirms 0.66W at nominal rating conditions); R924 **ERJP08F4701V**, 4.7k 1%. All hand-solderable. Existing resistor footprint is reused. No new footprint file or PCB change.
- LCSC IDs/JLC categories, live German stock, landed costs and 2/10/100-device purchases are **ungeprüft**, not zero. No purchase made.

## Cost decision

Net addition: **2 SOT23 transistors + 3 resistors**, reuse D911 and R912, change R911/R913/R915 values. No extra power IC or always-on auxiliary regulator. Complete delta including assembly/shipping is **NICHT BELASTBAR** until quotes exist. Rejected a second low-current optocoupler startup source: guaranteed low-current CTR at 9V/cold is not established. Rejected a simple diode clamp into VIN: +0.3V compliance and ACC backfeed cannot be assumed. Existing direct divider was electrically invalid for separately fused BAT/ACC. This small discrete stage repairs that concrete fault rather than adding a redundant safety controller.

## Checks and limits

tools/check_triptracer_powerpath_v2.py asserts all new-stage pins from the actual native KiCad root netlist, including absence of ACC_EN_BIAS and old R911-on-ACC/D911-on-EN connections. Existing timer, USB and 3V3 assertions remain active. Native BOM exporter requires all five new parts.

tools/check_acc_vin_startup.py checks 16 DC corner combinations, ±1% resistors, engineering stress assumptions VBE=1V, NPN VCE=0.3V, PNP VCE=0.5V, optical output VCE=1V, EN sink leakage=20uA and forced-beta target 10. These values are deliberately stated **model assumptions**, not guaranteed transistor limits over temperature. 8.2V VIN represents an assumed 0.8V input-diode loss from a 9V source. Minimum calculated startup EN=1.611V and HOLD EN=1.496V, vs TI start threshold 1.4V. 51uA assumed combined off leakage yields EN=0.515V, below TI 0.95V off threshold. Real leakage may exceed that at unqualified temperatures.

TI EN absolute maximum VIN+0.3V and thresholds:
https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf

Still required: hot/cold DC qualification, rapid VIN collapse/EN charge injection, ACC-off start-to-HOLD overlap, timer deadline and GPIO fault injection, reverse ACC/BAT, input TVS pulse energy, USB reverse-current measurements and all prior vehicle gates. No EN hold capacitor was added, because retained EN charge during VIN collapse needs independent evaluation. Native connectivity/ERC cannot prove these analog or laboratory gates. The new 01H drawing groups actual visible wires by startup, optical hold and ACC sense; native rendered visual inspection remains to be completed.


D911 package audit: replaced the inherited A1/K2 cache with explicit BAT54WS_CLAMP **K1/A2** mapping to standard Diode_SMD:D_SOD-323 cathode-pad1. D911.1 is now ACC_START_BASE, D911.2 GND; the drawn diode anode remains at ground. Candidate Diodes BAT54WS-7-F cathode-band orientation must match footprint pad1 on assembly. Source: https://www.diodes.com/datasheet/download/BAT54WS.pdf . No physical PCB was changed.

## Executed native verification

Verified schematic/code revision: **d144dd2cf68c2e949ef577d31cbd0ec2e84c7efb**.
[KiCad 10.0.6 Actions run 38559910683](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38559910683), job 115838130937, completed 2026-10-14.

- PASS: complete root hierarchy; existing custom pinout guard.
- PASS: native root netlist export.
- PASS: input diode/TVS, LMR38020 power nets.
- PASS: exact Q914/Q915, R911/R912/R913/R922/R923/R924 and D911 startup net assertions; direct ACC divider absent.
- PASS: 555/AND supply pins, trigger clamp polarity/POR/MCU fail-off; optical HOLD terminal connections.
- PASS: all TPS2116 pins, MCP1826S rails, USB-C VBUS and ground/harness.
- PASS: analytical DC corner script executed in Actions (16 combinations; min START=1.6107V; min HOLD=1.4962V; assumed-leakage OFF=0.5151V).
- PASS: 58-component active power BOM exported, including both new transistors and all three new resistors.
- ERC still FAIL: **34 pin_not_connected errors**, all on existing ESP32 sheet. No new ERC findings; no off-grid/library mismatch.
- DRC still FAIL: existing 5 violations and 79 unconnected items; schematic-parity differences now 82 rather than 77 because five components were added to schematic only. PCB intentionally unchanged.
- Full workflow correctly remains failure because ERC/DRC release gates are not satisfied.
- [Original report artifact](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38559910683/artifacts/11890664012), SHA256 1df7091e9da3ab2232016743a3d68d4ae154066ebc31dcb3ee5a102c3d9aa573. Artifact retention is one day; this report preserves the key revision-bound findings.

This closes the identified **direct DC ACC-to-EN supply path defect at schematic level**. It does not close unmeasured transient, hot/cold, negative-ACC, optical timing or hardware qualification gates listed above. No simulated/measured USB reverse-current pass is claimed; only the existing native connectivity regression passed.
