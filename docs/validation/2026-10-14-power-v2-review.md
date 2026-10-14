# TripTracer power V2 – implementation, price, risk review (2026-10-14)

**Development hardware only. NO approved automotive power supply, no production signoff.**

## Actual implemented KiCad 10 hierarchy

| Area | Schematic | Existing functionality / remaining work |
| --- | --- | --- |
| Input | `01G_SIMPLE_INPUT.kicad_sch` | Series rectifier D901 **Comchip SS510C-HF** 5A/100V SMC followed by TVS D902 **Littelfuse 5.0SMDJ36A** between VIN and GND. Correct diode polarity asserted in native exported netlist. BAT fuse / ACC connector upstream not yet physically resolved. |
| Buck | `02_5V_Buck.kicad_sch` | **LMR38020SQDDARQ1** generates V5_BUCK_RAW. 15µH/FCH0650-150M provisional inductor footprint must be requalified for exact 7.5x6.8mm body. EN true upstream. |
| Cold start / hold | `01H_ACC_HOLD_GATE.kicad_sch` | ACC resistor divider starts buck without own 5V; U911 80V optotransistor keeps buck EN activated via VIN *only while gated by TLC555 and MCU*. U912 80V opto senses ACC onto V3V3_SYS. R914 330Ω, R917 47kΩ. MCU GPIO21 = MCU_HOLD_REQ. |
| Timeout | `01C_HOLD_TIMER.kicad_sch` | TLC555QDRQ1 with 2.2MΩ × 10µF MLCC nominal t=24.2s, AND with MCU_HOLD_REQ. Hardware limit concept, but trigger and capacitor bias/temperature/restart behavior not bench-proven. |
| USB and 3.3V | `03_3V3_USB.kicad_sch` | TPS2116DRLR VIN1=V5_BUCK_RAW M8 priority, VIN2=USB_VBUS_RAW, VOUT=V5_SYS. NCV1117ST33T3G generates V3V3_SYS. Mux ST to GPIO33 (USB_ACTIVE_N) with 10k 3V3 pull-up. M8-first intended through PR1 and MODE linked to VIN1. GPIO status interpretation and no SD concurrent ownership require firmware. |
| Archives | Git history | No active 01A relay-AUX, 01B relay ACC, 01D LM74930, 01E latch, 01F RC alternatives. Files preserved on branch. |

**Validation:** native KiCad 10 checks `check_simple_input_netlist.py`, `check_lmr38020_netlist.py`, `check_triptracer_powerpath_v2.py` pass on last verified commit. Native BOM exporter counts 44 active supply components. Last confirmed ERC 183 messages and 5 DRC violations, plus PCB parity issues; this is not a functioning assembled PCB. The main connector-level ACC+BAT physical hardware is still a stub and M8 pin mapping needs explicit review. The SD/RTC sheet is not yet a fully wired storage implementation. V5_SYS USB-only power supports the MCU 3V3 rail concept but does not by itself make USB-MSC usable.

## KNOWN REAL PART PRICES (EUR NET per piece, from referenced distributor listings, provisional)

| Item | Qty | 1-piece | 10-piece | 100-piece | Evidence / comment |
| --- | ---: | ---: | ---: | ---: | --- |
| TI LMR38020SQDDARQ1 | 1 | 3.920 | 2.980 | 2.490 | Mouser DE; stock varies |
| TI TPS2116DRLR | 1 | 0.903 | 0.646 | 0.512 | Mouser DE |
| onsemi NCV1117ST33T3G | 1 | 0.516 | 0.362 | 0.268 | Mouser DE; heatsink copper required |
| TI TLC555QDRQ1 | 1 | 1.050 | 0.759 | 0.605 | Mouser DE |
| TI SN74LVC1G08QDBVRQ1 | 1 | 0.224 | 0.153 | 0.117 | Mouser DE |
| Würth 140356145000 80V | 2 | 0.335 | 0.296 | 0.248 | Mouser DE; min CTR only characterized at 5mA, 25C |
| Comchip SS510C-HF 5A100V SMC | 1 | 0.998 | 0.711 | 0.443 | Mouser DE |
| Littelfuse 5.0SMDJ36A | 1 | 2.110 | 1.353 | 0.921 | DigiKey DE; **10/1000µs power rating is NOT 350ms test** |
| **Known-priced semiconductors subtotal, excluding ALL passives** | | **10.391** | **7.556** | **5.852** | **Indicative, no shipping/VAT/assembly** |

15uH FCH0650-150M coil LCSC price in USD (~$0.1579 at 5 pcs), cannot add to EUR sum without conversion. Other supply inductors, capacitors, resistors, connectors, 100V MLCC, PCB, tooling, shipping, VAT, full assembly not yet completely priced. **The <8 EUR @10 units COMPLETE SUPPLY target is NOT achieved based on these 10-unit costs**: already 7.556 EUR before a single capacitor/coil/resistor. Optimize sourcing/architecture without silently removing protective functionality.

## First-order thermal & failure analysis – NOT a physical qualification

- D901 SS510C-HF dissipates I×VF; for *illustrative*, not verified VF 0.55V at 0.5A -> **0.275W**, 0.65V at 1.5A -> **0.975W**. Junction temperature at 85C ambient plus actual PCB copper is unverified.
- U302 NCV1117 LDO dissipates (5-3.3)×I3V3: **0.51W at 0.3A; 0.68W at 0.4A; 0.85W at 0.5A**. With a hot enclosed vehicle and weak SOT223 copper, this can cause thermal limiting; may need small synchronous 3V3 buck if net system power 3V3 remains high. 3V3 peak current still to measure.
- D902 5.0SMDJ36A rated **36V standoff** and approx **58.1V clamping at a specified short-pulse current**. It may draw very high *350ms duration* current during centrally limited 58V Test B, including when load dump is already centrally clamped! TVS should only be selected after verifying VIN peak/current and system source impedance. **No 24V Test B thermal approval.**
- U911/U912 Würth 80V VCEO (previous EL817S VCEO35V was unsafe with potential 58V pulse); **CTR min 50% guaranteed only at IF=5mA at 25C**, whereas U912 at 9V with R9166.8k is roughly 1.1mA, so GPIO ACC sense remains unqualified at cold conditions. This is a blocker even though native netlist passes.
- EN network D911 BAT54 / resistor values vs TI guaranteed 0.95V LOW and 1.4V HIGH should be checked at 9 and 30V across leakage and temperature. Internal thermal and hardware watchdog behavior must be fault-injection tested (stuck GPIO, 555 cap open/short, ACC intermittence).
- TPS2116DRLR and optocoupler PCB footprints are *provisional* until source datasheet drawing/courtyard measured; validate manufacturer solder mask/paste and EMC layout. USB5V may droop to 4.75V; NCV1117 input dropout under 3.3V headroom must be assessed.
- Actual vehicle BAT+ and ACC protection/fuses, USB CC and power input, reverse feed faults, 24V Load Dump Test B bench injection are **not yet qualified**.

## Sources

- https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf
- https://www.ti.com/lit/ds/symlink/tps2116.pdf
- https://www.we-online.com/components/products/datasheet/140356145000.pdf
- https://www.littelfuse.com/products/tvs-diodes/surface-mount/5-0smdj.aspx
- https://www.mouser.de and https://www.digikey.de (quotes seen 2026-10-14, not guaranteed)

## Acceptance gate (none of the electrical or safety approvals has been passed)

1. Fully routed and schematic-parity-clean KiCad PCB, ERC and DRC clean.
2. Direct BAT+ and ACC fuse + M8 routing implemented, AC/DC transients and disconnect behavior validated.
3. Bench: power at 9–30V, with realistic 0.3–1A output; low-input 9V cold start and load-dependent buck ripple.
4. ACC/Microcontroller HOLD: 555 triggered falling ACC, saved SD within window; stuck GPIO and timer faults fail off; no extra 5V startup supply needed.
5. USB-only enables MCU+SD after storage implementation, M8 priority and no reverse-feed measured with both connected and during transitions.
6. TVS Load Dump Test B ISO profile thermally/electrically safe; 200V unsuppressed Test A is excluded by scope but no dangerous thermal failure permitted.
7. Qualified manufacturer MPN+footprint+price for each item, purchases and actual PSU BOM subtotal recalculated.

**There is no permission to manufacture, install, or use the design in a vehicle at this stage.**
