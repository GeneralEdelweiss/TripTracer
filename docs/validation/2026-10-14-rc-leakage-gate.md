# 2026-10-14 RC deadline: leakage safety gate

Manufacturer reference: [TI LM74930-Q1 datasheet](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf). EN is physical pin 6. It is NOT a guaranteed digital input at zero voltage and has hysteretic thresholds and finite input current. TI's 2.5 µA shutdown figure is controller shutdown consumption, **not** the EN-pin leakage of the completed board.

We cannot yet connect the 01F capacitor straight to EN: the active ACC bootstrap path, positive net leakage into HOLD_CAP, load from EN and any transistor follower, and the 6 V start behavior must be evaluated together. For 330 kΩ bleeder, **1.24 µA sourced into the node** balances 0.41 V at the resistor and makes the simple RC cutoff unbounded. A shorted charging diode, contamination or a biased downstream transistor can violate this. Shorting MCU_SHUTDOWN or HOLD_CAP to GND should force shutdown unless ACC is directly and validly ON. Actual safe voltage level depends on the EN datasheet limits and architecture.

Two alternatives remain test candidates, not a selected solution:
- 01F passive diode + RC + discharge transistor, with worst-case capacitance and leakage proof.
- 01E flip-flop latch plus non-retriggerable hardware timer, with power-on and supply-collapse gates.

The analog RC solution remains disconnected from MAIN_ENABLE deliberately until the worst-case leakage **and** true protected-ACC source are shown. The high-level Python model validates behavior only; it is not a hardware guarantee. `python3 tools/analyze_rc_shutdown.py` now explicitly asserts indefinite on-time for +2 µA injection and checks reduced effective capacitance.

Next non-negotiable component tasks: verify the exact manufacturer's SOT-23 pinout for BAS116Q-7-F (do **not** interchange with Nexperia BAS116-Q without pin mapping); select an actual 47 µF MLCC with DC-bias curve or replace with an appropriately specified capacitor; verify 6 V cold crank charging and no USB-origin feed.
