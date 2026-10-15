# TripPower Weg B – Herstellerreferenz AP74502HQ und unabhängige Single-Fault-Prüfung, Runde 4

**Datum 2026-10-15. Branch ausschließlich `design/trippower-b`.** Die Management-Review Runde 2 (`docs/TRIPPOWER_A_B_REVIEW_ROUND2_2026-10-15.md`, Branch `design/trippower-review`) sowie Weg-B-No-Go Runde 2/3 wurden vorab gelesen. **Der TPSM33620-1:1-Tausch bleibt No-Go und wurde nicht neu untersucht.** Weg A und die gemeinsame REV5-Baseline bleiben unverändert. Ziel: lieber harte Gegenbeweise und herstellerbasierte Berechnung statt einen unqualifizierten KiCad-Schaltplan.

## 1. Neue tatsächlich beschaffbare Automotive-Alternative – mit Hersteller-200-V-Schaltung

**A – aktuelles Entwicklungsziel (nicht freigegeben):** LM74930QRGERQ1 + Q301(250-V) + Q302(60-V) + RVS/D301/D302 + LMR38020SQDDARQ1, externer F_MAIN, 9–30V, 5V/2A plus RAW 1A, 200V/350ms, −40..+125°C, 57 AUTO/58 RUN bestückte Positionen. Schwachstellen D301-OFFEN, Q301-KURZ→D302→VS und hot Q301-SOA unverändert kritisch.

**B4 – Hersteller-referenzierte Gegentopologie (nur Machbarkeitskandidat):**

```text
F_MAIN, VIN_FUSED 9–30 V, 200 V / 350 ms fault event
   +-- OVLO divider R2=100k, R3=3.5k -> AP74502HQ OVLO pin
   +-- 10k pulse-rated series R1 -> AP74502 VIN -> Cin>=1uF, Dz~60V GND
   |                                               VCAP-C >=0.1uF
   v
  Q1/Q2 HV NMOS COMMON-SOURCE / back-to-back (each needs real >=200V pulse VDS/SOA)
      GATE driven together by AP74502HQTA8-7; EN/UVLO / POR qualification
   v
  TPS1HTC30AQPWPRQ1: **separate** 6–60V automotive adjustable 2..16A
  overcurrent/short-circuit high-side switch; UVLO/control still to design
   +-- RAW_AUX target 1A, common current limit
   +-- LMR38020SQDDARQ1 (+12 existing regulator BOM placements)
   v
  5V 2A
```

* [**Diodes AP74502Q/AP74502HQ DS47093 Rev2-2, October 2025, page 15–16**](https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf): **original, manufacturer-published 200V surge stopper** with back-to-back MOSFETs, OV cutoff at roughly 37V and its own **R1=10k / Dz=60V** IC-VIN clamp. The oscilloscope trace shows *one demonstration*, but does **NOT** provide a traceable 350ms / 125°C / 2A+RAW / single-fault qualification. Normal VIN supported 4–75V; VIN pin **80V ABS MAX**, output OCP **NOT integrated**, reverse polarity + OV control integrated; AEC-Q100 grade 1 -40..125°C. Exact fitted part **AP74502HQTA8-7** (stronger gate drive than Q version); pinout 1 EN/UVLO, 2 GND, 3 NC, 4 VCAP, 5 VIN, 6 GATE, 7 OVLO, 8 SRC (page 2). **A pull-up/control and proper EN high/low state are required.**
* **TI TPS1HTC30AQPWPRQ1**, [TI product](https://www.ti.com/product/TPS1HTC30-Q1): 6–60V operating input, **2–16A programmable current limit**, ±20% accuracy in stated conditions, internal typical R_ON30mΩ, maximum55mΩ under vendor measurement conditions, AEC-Q100, Grade1, HTSSOP14 with thermal pad. Requires current-set resistor, control/diagnostic wiring and real hot/short thermals. **It is NOT a 200V front-end and must stay downstream of qualified OVP.**
* **LMR38020SQDDARQ1** unchanged 80V AEC-Q100 5V/2A regulator with 15uH discrete inductor; no reduction of Buck/RAW interfaces.

**Availability / price snapshots at time of research** (warehouse prices may vary by region, ALL € net, no freight/VAT):
* AP74502HQTA8-7 [Mouser Europe](https://eu.mouser.com/en/ProductDetail/Diodes-Incorporated/AP74502HQTA8-7) shown **505** in stock, **€0.636/0.450/0.352** at 1/10/100; [LCSC](https://www.lcsc.com/product-detail/C48989247.html) global English page showed 1,990 but the German listing showed 0, so use the explicit Mouser stock claim, do not conflate regional data.
* TPS1HTC30AQPWPRQ1 [Mouser Deutschland](https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS1HTC30AQPWPRQ1) **50** stock, **€4.39/3.35/2.80** (1/10/100); independent [DigiKey Deutschland](https://www.digikey.de/de/products/detail/texas-instruments/TPS1HTC30AQPWPRQ1/22106757) also listed large stock but prices differ.
* LMR38020SQDDARQ1 [Mouser Germany](https://www.mouser.de/ProductDetail/Texas-Instruments/LMR38020SQDDARQ1) has contradictory **4,776 / 0** regional/search observations; [DigiKey Germany](https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286) lists 0. **Do not claim reliably orderable until checkout/recheck.** LM74930QRGERQ1 [Mouser Germany](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74930QRGERQ1) lists 62 stock, DigiKey 0; similarly snapshot-dependent.

## 2. DC-OFF/30V-restart quantitativ: R2=100k, R3=3.5k

AP74502HQ datasheet p4: OVLO rising 1.165/1.250/1.333V, falling 1.063/1.143/1.222V (min/typ/max), OVLO input leakage reported 12..110nA. Illustrative sign-conservative model **±110nA** and 1% each resistor, `Vbat=Vth*(1+R2/R3)+Iov*R2`:

| | min | typical | max |
|---|---:|---:|---:|
| OV trip on rising VIN | **33.781V** | 36.964V | **40.199V** |
| OV retry on falling VIN | **30.822V** | 33.800V | **36.853V** |

This is a **static tolerance-screen only**. It suggests 30V allowed and 30V restart **statically** without a dedicated TPS3760. It does not guarantee cutoff time, post-POR behavior, thermal hysteresis, correct EN, gate turnoff or safe downstream PIN voltage for a fast 200V event. **AP own VIN supply 75V normal/80V ABS and TPS1HTC30 max60V remain independent constraints.** If a slow VIN ramp crosses the trip, downstream can see up to about40.2V before unspecified overshoot, within the 80V LMR/60V smart switch recommended regions *statically*; this is NOT transient coverage.

## 3. Foundry-reference R1/Dz/OV resistor pulse & single-fault contradictions

**Vendor reference R1=10k, Dz=60V, VIN=200V for 350ms (ideal rectangle, fixed Dz):**

* `I=(200-60)/10000=14mA` -> **R1=1.96W / 0.686J**, **Dz=0.84W / 0.294J**. Hot/350ms waveform, 60V Dz dynamic/temperature and pulse-rated resistor MPN **NOT proven**.
* **Dz OPEN**, ideal 1uF VIN bypass, 10k, zero IC load: AP74502 VIN pin reaches **80V ABS MAX in only 5.108ms** from VS0, or **1.542ms** if previously at 60V. After 350ms ideal VIN→200V. This is an *independent single fault*, similar to REV5 D301 OPEN, faster with the reference 1uF than REV5 nominal 21uF. ESD/input internal failure or leakage can reduce pin voltage but not guarantee safety; no ISO/fuse protection proof.
* **Dz SHORT**, ideal 200V/R1 -> 20mA through 10k -> **4W / 1.4J** in 350ms; external F_MAIN rated amperes need not clear. Uncontrolled resistor heating is safety-critical without pulse/thermal proof.
* OVLO top **100k** directly senses 200V: `I=200/(100k+3.5k)=1.932mA`, `V_OV≈6.763V`. Top resistor consumes **0.373W / 0.131J** for 350ms; splitting it into two 50k stages halves power/energy per device but adds a placement and still needs 125°C pulse specification. A generic 1206 rating is **not** a 350ms hot approval.

### Newly confirmed directed MOSFET body-diode flaw — do not claim dual-FET fault redundancy

Manufacturer page15 uses **common-source NMOS**: Q1 input-side D=VIN/S=MID, Q2 output-side S=MID/D=VOUT. With GATE off, intrinsic diode **Q1: MID→VIN** and **Q2: MID→VOUT**. Independent directed-graph check (`ap74502_reference_fault_screen.py`):

| Fault | Positive VIN reaches VOUT with both gates OFF? | Explanation |
|---|---|---|
| Neither FET short | **No** | Q1 input-side diode reverse |
| **Q1 D-S SHORT (single)** | **YES** | VIN directly joins MID; **Q2 body diode conducts MID→VOUT** |
| Q2 D-S SHORT only | **No** | Q1 diode blocks VIN→MID |
| Q1 and Q2 both short | **YES** | Series path short |

**Key consequence:** Using *two 250/300V external MOSFETs does NOT independently withstand an arbitrary single D-S short* in the manufacturer's back-to-back reference. The input-side Q1 short can forward feed 200V into the 60V TPS1HTC30 and 80V LMR38020 even with perfectly working OVLO/EN and a healthy output-side FET. These are ideal directional paths, not an assertion about actual cable inductance or diode destruction energy. A second **independently positive-VIN-blocking** series element/gate system or other proven fault-rated energy limiter is still necessary for stringent single-short safety. It adds components and qualification work; it is not automatically built into AP74502.

This is analogous to the REV5 Q301-SHORT → D302 → VS single fault, although it endangers the **main load output** instead of the VS controller supply. This tradeoff must be assessed at the correct system level.

## 4. Full functional architecture vs genuine BOM cost/placements

Existing REV5 baseline is **57 fitted AUTO / 58 fitted RUN**; Weg B may NOT claim a new complete BOM without chosen, rated, purchasable MPN for all resistors, capacitors, protection FETs, TVS, eFuse set/EN and 200V fault handling. The AP74502 reference is NOT a full off-the-shelf automotive TripPower protection module.

**Minimum functional blocks that must remain**: (a) two >=200V SOA-qualified HV FETs, (b) AP controller and the new 10k/Dz/CVIN/CVCAP supply, (c) OVLO resistive network and power pulse rating, (d) reverse TVS/ISO7637-2 protection, (e) TPS1HTC30 OCP with current-set/control/thermal pad, (f) protected RAW1A and existing 12-placement 5V buck, (g) UV/RUN control, OFF and reset, (h) capacitor inrush and damping, (i) F_MAIN cable/PCB I²t; **and** fault-tolerant protection against Dz-OPEN and Q1-SHORT before this can honestly replace REV5. Some parts of the reference above are shown but are not proven suitable for 200V/350ms or 125°C.

**Priced verified IC subset only**; prices at 1/10/100 unit, EUR net from supplier snapshots, ***not*** a complete system cost:
| Pieces | Existing LM74930 + LMR38020 | B4 AP74502HQ + TPS1HTC30 + LMR38020 | Δ B4-A |
|---:|---:|---:|---:|
| 1 | €8.3300 | €8.9360 | **+€0.6060** |
| 10 | €6.3340 | €6.7650 | **+€0.4310** |
| 100 | €5.2878 | €5.6223 | **+€0.3345** |

For A's LMR/LM74930 this uses earlier dated DigiKey price snapshots; the *current* listing changed, and availability differs among suppliers. **Not a binding 2026 purchase quote.** For B4, prices omit **all** HV FETs, input pulse R/TVS/Zener, current-set R, bypass caps, PCB/thermal/assembly and the extra independent fault gate. Therefore B4 cannot be ranked cheaper or simpler on full system costs. AP HQ offers easier SOT28 hand-assembly than LM74930 24-QFN, but TPS1HTC30 HTSSOP14 thermal pad adds an IC, temperature/creepage/voltage clearances and a separate layout zone. Two HV FETs may be significantly costlier than baseline one 250V+one 60V. **No numeric full-board total fabricated.**

**Alternative COTS screenings already covered**: ADI LTC4380 AEC (automotive surge with external FET, too costly, no 200V+125C+3A qualification), LTC4366 (high voltage but not equivalent ideal diode/OCP/automotive fit), LTC4381 (integrated FET but only 100V surge). This round adds Diodes manufacturer 200V solution, not a reprise of these rejected options.

## 5. Reproducible evidence, CI and next decision

New on B branch:
* `ap74502_reference_fault_screen.py` (manufacturer pin and resistor values, worst tolerance thresholds, Dz-OPEN and SHORT time/energy, 200V resistor pulses, 9V current, 1/10/100 priced IC subset, **directed dual-FET body diode fault graph**).
* `test_ap74502_reference_fault_screen.py` (9 gate regression checks including key Q1-short counterexample).
* `.github/workflows/trippower-b-independent-audit.yml` expanded to run the new executable reference check and upload numerical JSON.

Run from repository root:
```bash
python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_ap74502_reference_fault_screen.py' -v
python3 hardware/modules/TripPower_5V2A/weg_b/ap74502_reference_fault_screen.py > ap-reference-gates.json
```

**CI-Status:** A new workflow commit is NOT proof of PASS; fetch the actual run-id/URL and logs when supported. Native KiCad ERC on the **inherited REV5** is configured separately in the same workflow; no new B4 KiCad sheet exists. No KiCad-10/ERC/PCB-DRC, manufacturer SOA, hardware measurement, 200V pulse or −40/125°C proof asserted.

**Engineering outcome: NO-GO for a simple B4 architecture swap.** The AP74502HQ 200V manufacturer cutoff reference makes it a valuable **manufacturer-anchored alternative for a future fault-safe redesign**. But its single Dz open fault and single input-MOSFET short still can expose downstream low-voltage ICs to destructive voltage, while adding separate OCP and pulse resistor/energy gates. The independent B path has reduced uncertainty via quantified thresholds and a **new directional fault hazard**, not via an unproven KiCad hardware release. Prioritize controlling the dangerous Q301→D302 path on A, document F_MAIN coordination and require independent high-voltage source blocking when single-FET short tolerance is intended.
