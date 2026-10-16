# TripTracer: 24-V load-dump protection gate (2026-10-14)

**STATUS: NOT RELEASED for a vehicle. This note is not an ISO 16750-2:2023 test report.** Only the schematic has been touched; PCB work is intentionally deferred.

## Actual parts/nets checked

- Vehicle J901 BAT+ (external user-serviceable fuse) -> D901 Comchip SS510C-HF (100 V, 5 A Schottky/rectifier) -> `HV_PROTECTED_AFTER_EFUSE` -> TI LMR38020SQDDARQ1 U101 VIN/pin3.
- D902 Littelfuse `5.0SMDJ36A` protects from `HV_PROTECTED_AFTER_EFUSE` to system `GND` with reversed-biased polarity, i.e. no short during ordinary 9–30 V continuous battery operation.
- Per Littelfuse, D902 has **36 V standoff**, VBR = **40–44.2 V at 1 mA**, maximum VC **58.1 V at 86.1 A** and **5 kW rated for the 10/1000 µs waveform**. These numbers do **not** establish a 350-ms thermal rating.
- Per TI LMR38020-Q1 Rev B, U101 has **80 V recommended maximum VIN** and **85 V absolute maximum**. For a 24-V *centrally clamped* ~58-V Test-B pulse, the buck voltage rating is potentially adequate, **provided the actual surge waveform, local overshoot and J901/D901/D902 interactions are confirmed**. It is not adequate for unrestricted ~202-V Test-A pulses.

## Why the current TVS is a release blocker

A **350-ms pulse** is hundreds of times longer than the `10/1000µs` waveform for which 5 kW peak rating is specified. **Do not multiply 5 kW by 350 ms** to invent a permissible energy. The datasheet has a pulse-width derating chart; junction/PCB temperature, repetition and source impedance matter.

To illustrate the energy risk *without claiming any device model*, suppose a bench-source Thevenin pulse holds 58 V for 350 ms and a TVS approximately clamps to a hypothetical 50 V. Then:

| Hypothetical effective source resistance | TVS current | TVS power | 350-ms energy |
|---|---:|---:|---:|
| 1 Ω | 8 A | 400 W | 140 J |
| 2 Ω | 4 A | 200 W | 70 J |
| 4 Ω | 2 A | 100 W | 35 J |

These are purely illustrative upper-source calculations. The clamp voltage is **not fixed at 50 V**, nor are the source resistances asserted ISO test parameters; actual current depends on VBR temperature, dynamic resistance, harness impedance and whether the central generator already clamps the pulse. **None of the table values can be compared directly with the 5-kW / 10/1000µs rating to declare survival.**

## Required before vehicle wiring

1. Determine actual chosen ISO 16750-2:2023 Test B voltage waveform, pulse length, source impedance, repetition count and generator central-clamp topology for 12-V and 24-V vehicles. Test A remains explicitly unsupported by the present frontend.
2. Measure and bound transient voltage at U101 VIN, including cable inductance and D901 recovery; compare under all extremes with its **80-V functional** and 85-V abs-max ratings.
3. Calculate and/or measure D902 voltage, current and accumulated pulse energy at the relevant cold/hot extremes, with the manufacturer's applicable long-pulse derating. Select an appropriate **genuine 350-ms-qualified load-dump solution**, or keep this as **LAB ONLY**. Do not replace it blindly with another 5-kW TVS whose rating uses the same short waveform.
4. Verify D901 average/repetitive surge current, thermal rise and dissipation under max continuous load, and choose external automotive DC-rated BAT+ and ACC cable fuses with real fault-current coordination, wire size and connector strain relief.
5. Check input reverse-polarity, short-to-battery, short-to-ground, cold crank, repeated transients and electrostatic protection in a fused current-limited bench setup. Record oscilloscope plots and pass/fail criteria.

**Sources**: Littelfuse product specifications https://www.littelfuse.com/de/products/overvoltage-protection/tvs-diodes/surface-mount/5-0smdj/5-0smdj36a ; TI https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf .

**Development decision:** do not add a randomly larger TVS, second MOSFET or expensive upstream controller merely to quiet the ERC. Either qualify the actual D902 for the actual source pulse or select a specified long-load-dump protective approach on evidence. Zero schematic ERC warnings alone are not safety evidence.
