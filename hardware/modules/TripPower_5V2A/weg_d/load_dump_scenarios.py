#!/usr/bin/env python3
"""TripPower D round 6 scenario calculator, stdlib only. NOT an ISO emulator.

Use: python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_d -p 'test_round6.py' -v
     python3 hardware/modules/TripPower_5V2A/weg_d/load_dump_scenarios.py

For each 350 ms waveform, idealize TVS as a CONSTANT 61.2 V clamp and supply
as a Thevenin source with Ri. This is a deliberately nonphysical sensitivity
model: no clamp I-V curve, self-heating, tolerance, generator compliance,
cable L, output load, source ringing or guaranteed survival.
"""
import math
from dataclasses import dataclass

US = 200.0
UB = 28.0
TD = 0.350
VC_EXAMPLE_25C = 61.2

@dataclass(frozen=True)
class Scenario:
    ri_ohm: float
    waveform: str
    i_peak_a: float
    p_peak_w: float
    energy_j: float


def source_voltage(t_s: float, waveform: str, us=US, ub=UB, td=TD) -> float:
    if not 0 <= t_s <= td:
        raise ValueError("t outside pulse")
    if waveform == "constant":
        return us
    if waveform == "linear_to_28":
        return us - (us - ub) * t_s / td
    if waveform == "exp_to_10pct":
        return ub + (us - ub) * math.exp(-math.log(10.0) * t_s / td)
    raise ValueError("unknown waveform")


def scenario(ri_ohm: float, waveform: str, vc=VC_EXAMPLE_25C, steps=20000) -> Scenario:
    if ri_ohm <= 0 or vc <= 0 or steps <= 0:
        raise ValueError("invalid Ri, Vc, steps")
    dt = TD / steps
    e = 0.0
    peak_i = 0.0
    peak_p = 0.0
    for n in range(steps):
        vs = source_voltage((n + 0.5) * dt, waveform)
        # Excludes downstream load: conservative TVS-current comparison.
        i = max(0.0, (vs - vc) / ri_ohm)
        p = vc * i
        e += p * dt
        peak_i = max(peak_i, i)
        peak_p = max(peak_p, p)
    return Scenario(ri_ohm, waveform, peak_i, peak_p, e)


def tvs_short(ri_ohm, us=US, td=TD):
    # Hypothetical constant voltage and pure R; NOT fuse opening time.
    i = us / ri_ohm
    return {"current_a": i, "source_i2t_a2s": i * i * td}


def inductive_spike(inductance_uh: float, di_a: float, dt_us: float) -> float:
    if inductance_uh < 0 or dt_us <= 0:
        raise ValueError("invalid L or dT")
    return inductance_uh * di_a / dt_us  # µH * A / µs = V


def main():
    print("MODEL: 200V peak, 350ms duration, 28V baseline, 61.2V idealized fixed clamp.")
    print("NO qualification for +125C, pulse class, TVS SOA, 60/65/80V ICs or F_MAIN.")
    print("Ri  waveform        I_peak_A    P_peak_W   Energy_J")
    for ri in (1.0, 3.5, 4.5, 6.0):
        for wave in ("constant", "linear_to_28", "exp_to_10pct"):
            x = scenario(ri, wave)
            print(f"{ri:3.1f} {wave:15s} {x.i_peak_a:10.2f} {x.p_peak_w:11.1f} {x.energy_j:10.1f}")
    print("SHORT Ri=3.5:", tvs_short(3.5))
    print("L=1uH di=42.8A dt=10us:", inductive_spike(1,42.8,10),"V")
    print("L=0.5uH di=42.8A dt=1us:", inductive_spike(.5,42.8,1),"V")


if __name__ == "__main__":
    main()
