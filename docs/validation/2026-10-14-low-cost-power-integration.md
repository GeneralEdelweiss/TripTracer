# TripTracer V1 – Low-cost-power integration, 2026-10-14

Status: **NOT FUNCTIONAL AS A COMPLETE POWER SYSTEM; NO VEHICLE OR FABRICATION APPROVAL.** This is an executable worklist and an honest component/thermal snapshot.

## Current actual electrical hierarchy

- **01G_SIMPLE_INPUT:** BAT fused label -> D901 STPS5H100 (series reverse protection) -> HV_PROTECTED_AFTER_EFUSE, D902 5.0SMDJ36A from protected input to GND. Native KiCad netlist assertion passed on previous CI. TVS long-duration 24-V load-dump capability **not proven**. STPS5H100 nominal 100-V reverse rating does **not** make 01G survive a 200-V unsuppressed pulse.
- **02_5V_Buck:** VIN at HV_PROTECTED_AFTER_EFUSE, LMR38020-Q1 400 kHz, nominal 5 V/2 A, output V5_BUCK_RAW. Native KiCad netlist guard passed.
- **01C_HOLD_TIMER:** previous automotive TLC555-Q1 + logic gate timeout candidate stays in active hierarchy ONLY as a WIP. Hardware feedback **does not yet drive BUCK_ENABLE**. A 5-V-supplied timeout cannot itself start a de-energized 5-V regulator. The cold bootstrap must come from protected ACC/BAT and the always-safe independent EN circuitry; MCU_HOLD is 3.3-V logic, input attenuation/isolation mandatory.
- **01B_ACC_WAKE:** previous relay-drive topology required 5V_AUX_COIL, which is no longer generated and had chicken-and-egg startup. **Retired from active hierarchy**, archived in Git.
- **01E_OFF_LATCH**, **01F_RC_SHUTDOWN**: competing unconnected candidates retired from active hierarchy, archived in Git. No claim that MCU-controlled delayed shutdown exists in their absence.
- **04_ESP32_USB:** USB VBUS enters the connector sheet, but currently NO validated dual-input 5-V power mux; plugging USB may not correctly power the SD/MCU and may backfeed the buck input through an uncharacterized internal path. Do NOT simply tie USB VBUS to V5_BUCK_RAW or use a single diode without evaluating reverse leakage. M8 priority/USB-only behavior still incomplete.

## Required ACC+MCU_HOLD circuit before PCB

1. **Cold boot:** ACC protected, vehicle source present -> BUCK_ENABLE crosses TI guaranteed EN-high threshold independently of 5-V or 3V3 feedback. EN cannot float.
2. **Retention:** V5_SYS/3V3 alive -> MCU requests hold, but ACC may fall. During grace interval BUCK_ENABLE must stay high; GPIO default/strapping states must fail off.
3. **Fault timeout:** monostable or other *independent*, power-on-valid hardware removes hold after bounded time when ACC remains low even if GPIO sticks high. Timer capacitor effective at DC bias and temperature. Existing 01C is a candidate, not proven to achieve this chain.
4. **Recovery:** ACC returns while saving -> keep supply stable. Spurious ACC surges, reverse battery and ESD must not overstress EN or 3V3 GPIO. OFF standby remains below 100uA goal including input-sense dividers.
5. **Bench test:** trigger ACC off while writing SD, MCU_RELEASE immediate, MCU stuck high, GPIO floats, brownout and USB-only. Measure hold duration across tolerances.

## USB power decision still open

A dedicated dual-input ideal-diode/power mux is a technically attractive solution for reliable USB-vs-M8 priority and reverse isolation. Example **TI TPS2121RUXR**, Mouser DE 2.10 EUR/1, 1.57 EUR/10, 1.28 EUR/100, *part only* (https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS2121RUXR). In a near-8-EUR target, this price is significant. A cheaper two-Schottky diode-OR network is a cost candidate but loses voltage, may not ensure strict M8 priority and cannot safely be assumed without buck reverse-current review. **Neither option has been wired yet**; do not include them as delivered functionality.

## Price control, VAT and shipping excluded (Mouser EUR unit-price evidence)

| Item | 1 pc | 10 pcs | 100 pcs | Note |
| --- | ---: | ---: | ---: | --- |
| LMR38020SQDDARQ1 | 3.92 | 2.98 | 2.49 | Automotive low-Iq variant actually placed in KiCad; Mouser Germany listing, supply availability must be reconfirmed at order |
| TPS2121RUXR optional power mux | 2.10 | 1.57 | 1.28 | Not yet selected; USB/M8 priority possible, requires actual input wiring |

LMR source: https://www.mouser.de/de/c/semiconductors/power-management-ics/voltage-regulators-voltage-controllers/switching-voltage-regulators/?series=LMR38020 .

**No accurate final BOM sum**: D901, D902, main inductor, 100-V MLCC, timing IC, 3.3-V supply, USB interface/mux, ACC input transistor(s), fuse holder and PCB assembly still need qualified MPN/prices. An asserted <8 EUR *complete* supply is currently a cost target, not verified.

## Thermal first-order bounds – NOT part release

- Series Schottky D901 conduction dissipates `P=I_vehicle*V_F(I,T)`. As illustration, **0.6 A at 0.55 V = 0.33 W**; **1.5 A at 0.65 V = 0.975 W**. These are assumed forward voltages, not guaranteed component performance at the given operating points. At 9-V crank the diode also subtracts Vf from the buck input. Ambient 70–85C + PCB copper + junction-to-ambient rating require a worst-case analysis of Tj before approval.
- D902 5.0SMDJ36A has 36-V reverse-standoff. Its advertised high pulse power applies to a specified **short** pulse, *not* automatically a 350-ms battery-disconnect/load-dump. If the 24-V central regulator clamps to ~58 V, the local 36-V TVS can conduct through the long pulse; actual current/energy depends on source impedance and vehicle layout. **No pass claim even for clamped Test B** until the applied pulse, local dynamic Vc, and SOA/thermal model are checked.
- LMR38020 80-V normal operating ceiling and 85-V abs-max do not shield diode or TVS against an isolated 200-V fault; test A no survival guarantee by product decision.

## KiCad validity

Run native KiCad-10 schematic hierarchy/ERC/netlist/PCB DRC in CI on every change; preserve exact errors and never mask a missing real source with arbitrary power flags. Retiring unused experimental sheets reduces errors without demonstrating any electronic repair. ERC/DRC-clean, tested ACC/USB and validated thermal results remain mandatory before ordering boards.

## Requested five implementation tasks – verified status

| Task | Actual status as of 14 Oct 2026 |
| --- | --- |
| ACC MCU-HOLD with hard timeout | **Not completed.** 01C timer study remains; missing guaranteed cold-start EN driver and final shutdown gate. |
| Retire obsolete alternatives | **Done in active hierarchy** for relay AUX 01A, relay ACC 01B, and unconnected latch/RC 01E/01F. Files remain in Git. |
| USB-C 5V mux with M8 priority/no backfeed | **Not completed.** USB input exists at J201; no tested power routing to core; parts comparison only. |
| Native KiCad ERC/DRC | **Run; not clean.** Run 38533356691: 179 ERC, 5 DRC, VIN diode/TVS path and LMR38020 topology regression pass. |
| BOM and thermal review | **Partial.** Confirmed IC price tiers; other exact MPN/thermal/TVS pulse ratings outstanding. |

The remaining issues must not be disguised as five finished tasks.

## EN and USB manufacturer verification — 2026-10-14

**TI LMR38020-Q1, datasheet Rev B section 7.3.3:** EN below 0.95 V means OFF, above 1.4 V required to start; must never float; `VEN <= VIN+0.3V` absolute constraint. This rules out tying an unprotected vehicle ACC input to EN, and requires protection at 30V plus transient. Any MCU-HOLD signal needs fail-off and no reverse current into the unpowered 3V3 MCU. Source: https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf .

**TI TPS2121:** genuine priority input selector, internally reverse-current blocking, can implement M8 first on IN1 and USB VBUS second on IN2 with PR1 properly biased. But its 2.8–22V operating voltage and max-24V pins prohibit connecting either input directly to 30V BAT+; M8 **regulated** 5V must feed IN1. TPS2121 current consumption ~300uA typ while active, thus it should only be supplied from switched 5V or USB, not continuous BAT. Sources: https://www.ti.com/product/TPS2121 and https://www.ti.com/lit/ds/symlink/tps2121.pdf .

**Unresolved implementation dependency:** No dedicated regulator or independent protected startup supply presently drives BUCK_ENABLE on initial ACC assertion, and no validated 5V voltage-domain power mux currently exists. Never tie USB_VBUS_RAW directly to V5_BUCK_RAW or 3V3 SYS while this is open. The missing functions are genuine open gates to meeting user request, not optional polish.
