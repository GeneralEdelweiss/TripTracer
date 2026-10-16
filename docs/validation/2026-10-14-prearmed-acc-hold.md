# Prearmed ACC-off HOLD correction — 2026-10-14

Schematic development, not vehicle or manufacturing approval. Native KiCad 10.0.6 results recorded below.

## Electrical change

The previous 555 output was LOW throughout ACC ON. C502 generated a negative trigger only after ACC fell. Thus U911 optical HOLD had to turn ON after the independent Q914/Q915 startup source was turning OFF. Netlist correctness alone did not remove this timing dependency.

Now global **ACC_INV_N** from Q912 drives U501 TRIG/pin2 directly. While ACC is ON, TRIG is LOW and the TLC555 output is HIGH (after POR); existing U502 AND MCU_HOLD_REQ can therefore illuminate U911 before ACC falls. D503 low-leak diode and R505 hold the timer capacitor discharged through Q912. With ACC OFF, Q912 releases TRIG to 3V3; D503 is reverse biased and the timer capacitor charges. Timer output retains its previous HIGH state until THRES terminates the window. MCU release can still remove HOLD earlier. No EN capacitor or extra supply IC was added.

Unused Q913/R917/R920/R921 inversion stage is removed, so ACC_INV_N rises close to V3V3 rather than being loaded by Q913 base. Old C502 edge coupling and its D501/D502 input clamps are removed. Those clamps are unnecessary for a ground-referenced, pulled-up DC trigger and would add hot leakage. D912 clamps Q912 base negative excursions; the inherited unclamped reverse-ACC base path is repaired.

Manufacturer basis: TI TLC555-Q1 Rev D Table 6-1 describes the relevant trigger, retained-state and threshold behavior (its shown fractions are nominal).
https://www.ti.com/lit/ds/symlink/tlc555-q1.pdf

## Parts, leakage and cost

- D503 **Diodes BAS116Q-7-F**, existing project symbol BAS116Q_SOT23: A1 / NC2 / K3; NC2 explicitly unconnected. Source: https://www.diodes.com/datasheet/download/BAS116.pdf . 80nA maximum reverse leakage at 150C/75V is the selection rationale; reverse leakage in this topology injects charge into RC, rather than creating a discharge path. Its effect on minimum time is included as a stress case.
- R505 **Panasonic ERJP08F1002V**, 10k 1% 1206: limits capacitor discharge through D503/Q912. Uses existing resistor geometry.
- D912 **Diodes BAT54WS-7-F**, K1 at Q912 base, A2 ground, existing SOD323 symbol/footprint.
- R501 changes 2.2M -> **1M 1%**, candidate Panasonic **ERJP08F1004V**, same 1206 package. C501 changes 10uF -> **22uF 25V X7R 1210**, candidate Murata **GRM32ER71E226KE15L**, same footprint. Nominal R*C stays 22s while charging current more than doubles, improving tolerance to sink leakage.
- Murata product family/model source: https://ds.murata.com/simsurfing/mlcc.html?partnumbers=%5B%22GRM32ER71E226KE15%22%5D . Effective capacitance at 3.3V, temperature, aging and insulation leakage remain qualification gates, not nominal-value guarantees.
- Geometries/pin numbering reuse existing library definitions. Existing standard SOT23 land pattern still needs manufacturing comparison against the Diodes drawing; no new footprint or PCB file.
- Net component count change: remove C502,D501,D502,Q913,R917,R920,R921 (7), add D503,D912,R505 (3): **four fewer components**. Reuses already selected diode families.
- Rejected a separate transistor RC clamp because its hot off-state leakage could defeat a megaohm timer. A TMUX1101 low-leak switch was also evaluated: Mouser Europe listing EUR 1.84/1, 1.37/10, 1.12/100 plus passives; it is unnecessary after unloading the inverse-ACC node. Source: https://eu.mouser.com/ProductDetail/Texas-Instruments/TMUX1101DBVR?qs=vLWxofP3U2ztm0eUVm6rmg%3D%3D . No extra IC selected.
- New exact live stock, VAT/shipping, 2/10/100-device delta, LCSC IDs and JLCPCB categories are **ungeprüft**. Full cost delta **NICHT BELASTBAR**; no invented saving or purchase.

## Executable checks and explicit limits

Native root netlist guard asserts U501 TRIG, R502, D503 cathode and Q912 collector share global ACC_INV_N; R505/D503 anode reach TIMER_RC; D912 clamp polarity; retired parts/nets are absent. Existing VIN-only startup, MCU AND, mux and LDO checks remain enabled.

tools/check_acc_hold_prearm.py follows TI's functional table and RC exponential model. Scenarios: continuous prearmed HOLD through ACC-off; early MCU release; stuck-high MCU deadline; ACC returning and falling again; USB-only not armed. It also sweeps 96 declared sensitivity combinations: VDD=3.0..3.6V, R±1%, C-effective=10..26.4uF, clamp residual=0.5..1.3V, threshold fraction=.54..78, net leakage=-80nA..+500nA. These are stress assumptions, not a guaranteed 3.3V device specification. The sweep gives **1.96..68.13 seconds**, nominal example **18.92s**. Thus this change does NOT guarantee a three-second minimum or a production maximum deadline. Actual full-temperature timer/capacitor qualification remains mandatory.

Q912 model now includes both pull-ups and initial RC discharge; assumed VBE=1V/VCE=.3V and 9V ACC give forced gain target ~7.74. Full-temperature BJT behavior remains unmeasured.

ACC sensor stuck LOW or shorted RC can defeat timeout. This timer bounds a stuck MCU request with healthy ACC sensing, not every component fault. Short ACC chatter may not fully discharge C501; sufficient rearm time and waveform behavior must be bench-tested. GPIO default LOW, USB source isolation, BAT-absent DC startup fix and all automotive/thermal gates remain unchanged. Native rendered visual QA and oscilloscope measurements remain OPEN.

## Executed native evidence

Verified electrical/code head: **623171d983dee64fad0bc468cc35853772a39c68**.
[Actions run 38561884651](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38561884651), job 115844715782, KiCad 10.0.6, 2026-10-14.

- PASS: hierarchy and existing custom safety pinout checks.
- PASS: native root netlist export.
- PASS: input diode/TVS, LMR38020 topology, VIN-only startup.
- PASS: prearmed TRIG / RC reset D503 and R505, Q912 reverse-base D912, retired parts and second-inverter nets absent.
- PASS: all TLC555/AND terminal checks, MCU release pulldown, optical HOLD.
- PASS: TPS2116 / MCP1826S / physical USB VBUS-GND / vehicle harness regression.
- PASS: previous 16 startup DC corner assumptions.
- PASS: all five prearmed HOLD scenarios and 96 declared RC sensitivity combinations. Nominal model 18.924s; sensitivity 1.963..68.126s. These results are NOT a guaranteed hardware timing specification.
- PASS: native BOM exported **54** active supply components (previous 58).
- ERC **FAIL**, unchanged **34** pin_not_connected errors solely on the existing ESP32 page; no new warnings/errors.
- Existing PCB DRC **FAIL**: 5 violations, 79 unconnected items; parity 78 rather than 82 after schematic net four-part reduction. No PCB file changed.
- Overall workflow remains failure as required by unresolved project ERC/DRC gates.
- [Raw artifact](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38561884651/artifacts/11892481523), SHA256 **2179241bfebb80cfd156413ffe829f21f979c5e36f73a27973f930930f6fcb50**, one-day retention. This committed report preserves key observations.

Netlist regression confirms the new timer uses the existing inverse ACC node and continues to feed the same MCU AND/opto/VIN-only EN path. Models demonstrate the intended prearmed sequence under stated assumptions. Oscilloscope proof of continuous power and a qualified actual deadline is still outstanding.
