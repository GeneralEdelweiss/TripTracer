# Input protection: 58V non-avalanche design — 2026-10-14

Development candidate; no vehicle/manufacturing approval. Replaces the active input pair without adding parts or changing the PCB.

## Why the old TVS is unsuitable
A central58V clamp does not make the alternator a58V Thevenin source with its original source resistance. A lower local clamp can pull the bus below58V and turn the central clamp OFF. An illustrative ideal40V local clamp, diode0.8V, generator174V/Ri1ohm and cable0.1ohm draws121.09A with bus52.91V. This is a counterexample to the previous source assumption, **not a prediction of the real TVS V-I curve or its survival**. The 5.0SMDJ36A's short-pulse label cannot establish350ms survival. SLD8S43A offers a larger die and long-pulse data but still conducts below the central clamp; simply upsizing it does not solve this interaction.

## Implemented candidate
- **D901: Diodes S5MC-13-F**, 1000V rectifier, replacing the100V Schottky. Cathode1 remains protected VIN, anode2 remains BAT. Its higher forward loss is included in the EN revision below. This is a standard catalog part, not an asserted AEC qualification.
- **D902: TI TVS5800VEBR**, replacing the36V TVS. It stands off58V and gives a75V maximum at20A8/20us,27C, initially0V. All three IN pads4/5/6 go to VIN; all GND pads1/2/3 go to GND. No stacked/hidden pins. Its small1.6mm package requires stencil/reflow or suitable hot-air work; this is a deliberate assembly compromise for the narrow58-to80V window.
- **R911/R915:30.1k1%** instead of33k. Candidate Panasonic ERJP08F3012V1206; existing footprints reused. The same startup/HOLD model now permits VIN7.5V at BAT9V (assumed diode drop1.5V). With the prior BJT/opto/leakage assumptions, minimum EN is1.5702V startup and1.4474V HOLD versus1.4V enable requirement. The1.5V cold drop is an engineering allowance, not a manufacturer guarantee over temperature.
- New **local** footprints: S5MC uses2.50x3.30mm pads at x+/-3.45mm; VEB uses0.50x0.20mm pads,0.50mm pitch,1.50mm row separation, no exposed center pad. The manufacturer's bottom-view pin diagram was explicitly compared with the top-view land pattern. S5MC symbol cathode bar now agrees with its K pin. No PCB file or3D model was changed.

## Electrical bounds and their limits
For a **measured terminal waveform never exceeding58V**, D902 need not avalanche. Published maximum leakage at58V gives17.4uW at27C,69.6uW at85C and139.2uW at105C; corresponding350ms energies are6.09/24.36/48.72uJ. This removes the local load-dump energy sink for that bounded profile. It does not cover an actual bus above58V, repetitive pulses, ground offsets, wiring overshoot or an unqualified clamp temperature. RealTestB terminal amplitude/tolerance remains to be verified.

At the specified20A short-pulse point,75V leaves5V to the80V buck and opto boundaries. That is **not** a blanket75V vehicle clamp guarantee: the test is at27C with initial VIN0V; actual bias, temperature, pulse shape, inductance and overshoot still require measurements. The25A8/20us rating is not a350ms rating.

A static -600V input with protected VIN at most80V gives680V reverse stress, below D901's1000V rating; reverse recovery and dynamic undershoot remain untested. The former100V diode did not have that static margin. With10W output, assumed80% buck efficiency and a1.15V diode drop at9V input, input current is1.59A and diode dissipation1.83W. Thus the1000V change costs heat; terminal temperature and copper area must be checked. The datasheet's5A rating is conditional on terminal temperature, with capacitive-load derating.

**Still open:** TestA202V/350ms (not absorbed by this design), complete ISO7637 pulse matrix on BAT and ACC, external replaceable BAT/ACC fuse ratings and clearing/I2t coordination, inrush, full-load/case heat, hot/cold optoCTR, all actual clamp waveforms. No fault or transient qualification is inferred from ERC.

## Sources and procurement
Primary electrical/geometry sources: [TI SLVSII6 Jan2026](https://www.ti.com/lit/ds/slvsii6/slvsii6.pdf), sections5/6/10 and drawingVEB0006A4231688/B June2026; [Diodes DS16007 Rev10-2](https://www.diodes.com/datasheet/download/S5AC.pdf), pages1/2/4; [Panasonic30.1k candidate](https://industrial.panasonic.com/sa/products/pt/small-and-high-power-chip-resistors/models/ERJP08F3012V). Manufacturer PDF package/pin pages were rendered and inspected locally.

Observed14Oct2026, USD, excluding taxes/shipping; these are catalog observations, **not landed German quotes**:

| Part | 1 / 10 / 100 unit prices | Availability observation |
|---|---|---|
| [TVS5800VEBR](https://www.digikey.com/en/products/detail/texas-instruments/TVS5800VEBR/28741038) |0.72 /0.512 /0.4025 | stock0; expected12Jan2027; other cached snapshots differ |
| [S5MC-13-F](https://www.digikey.com/en/products/detail/diodes-incorporated/S5MC-13-F/814735) |1.03 /0.637 /0.4126 | stock51879 in retrieved listing; recheck before ordering |
| [SLD8S43A alternative](https://www.digikey.com/en/products/detail/littelfuse-inc/SLD8S43A/6235036) |4.53 /2.981 /2.1012 | stock7462; bigger pulse capability, but below58V-clamp interaction remains |

TI's own listing also provides no confirmed stock. **Procurement is blocked for a build using D902**, despite its attractive catalog cost. No order, guaranteed savings, JLC Basic/Extended classification or Reichelt availability is asserted. LCSC/JLC listingC53354305 exists but stock was0; category unverified. A currently purchasable substitute must independently satisfy both standoff and actual hot/cold clamp limits; an ordinary60V TVS with clamp near97V is not a drop-in replacement.

## Reproducible checks
Actions now runs exact six-pad TVS native-net checks and source-bound envelope/pad checks; the latter record assumptions and unmet gates in JSON. The power BOM remains55 parts. Existing ERC/DRC failures stay enforced. Native **KiCad10.0.6**, implementation **f56ba9deebb5d0a86c1c4f00d838a64e6c477f7c**, final diagram/readme revision **8374f6244d316508125e24ebcfe9006e8af97bfd**:
- [Final Actions run38567117214](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38567117214), job115862512790. Hierarchy12pages/70symbols, custom pin guard, native netlist, six-pad input guard, input source/pad checks, buck/power-path guards, ACC models and55-part BOM export all pass.
- ERC remains **33pin_not_connected on the MCU sheet**; no new class. DRC remains5violations,79unrouted and80parity issues. Overall **FAIL**, correctly enforced. No PCB file changed in the complete base248bd14..8374f624 comparison.
- The entire native node-to-net mapping of final8374f624 was compared with f56ba9de and is **identical**. Label relocation did not change electrical connectivity.
- Native PDF pages4 and8 were rendered and inspected. The new input device labels/wires and ACC/HOLD/USB-status labels no longer overlap at the corrected locations. This is not whole-project visual/layout or manufacturing approval.
- [Evidence ZIP](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38567117214/artifacts/11896601533), expires28Oct2026; downloaded and SHA256 verified: `d152cc46efda1301ea8910abfe35366f6c44627c0098c1b144352d0888d1bccc`.
- [Durable result snapshot, assumptions and individual report hashes](2026-10-14-input-flat-clamp/native-results.json) is committed with this report. PDF source hash: `30f7b8182c75ea55c4ebd47ebff0caa1acbfb8a10e14358b3ed2f90d1702962b`.
