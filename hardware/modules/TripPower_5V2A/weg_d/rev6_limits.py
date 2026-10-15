#!/usr/bin/env python3
"""TripPower D REV6 electrical bounded-scenario audit. stdlib only.
Reproduce: python3 hardware/modules/TripPower_5V2A/weg_d/rev6_limits.py
            python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_d -p 'test_rev6.py' -v

THIS IS NOT KiCad/ERC, SPICE, a worst-case transient waveform or hardware approval.
Component ranges are direct LTC4368 datasheet Rev C minimum/maximum values.
Assume ALL divider resistors ±tol independent of one another, including temperature drift.
VIN-pin ringing, source inductance, fuse I2t and thermal margins are EXTERNAL inputs.
"""
from dataclasses import dataclass

R_TOP=(475_000.,1_500_000.,121_000.)  # VIN -> SHDN -> UV -> OV
R_BOTTOM=30_200.  # OV -> GND; SPECIAL 0.1% precision option, not stocked/approved yet
R_SENSE=0.015  # 15mΩ approximate; NOT a selected MPN


@dataclass(frozen=True)
class Bounds:
    ov_rising_min:float
    ov_rising_max:float
    ov_falling_min:float
    ov_falling_max:float
    ov_rising_typ:float
    ov_falling_typ:float

def ov_bounds(tol=0.0025, r_top=R_TOP, r_bottom=R_BOTTOM):
    """Combined resistor intrinsic accuracy + adverse TCR up to 0.25% (example)."""
    if not 0 <= tol < 1:raise ValueError("invalid tolerance")
    upper=sum(r_top)
    k_lo=r_bottom*(1-tol)/(upper*(1+tol)+r_bottom*(1-tol))
    k_hi=r_bottom*(1+tol)/(upper*(1-tol)+r_bottom*(1+tol))
    k=r_bottom/(upper+r_bottom)
    return Bounds(0.4925/k_hi,0.5075/k_lo,(0.4925-0.032)/k_hi,
                  (0.5075-0.020)/k_lo,0.5/k,(0.5-0.025)/k)

def sense_trip(rs=R_SENSE):
    # LTC4368 datasheet nominal running fault SENSE-VOUT 40..60mV
    return (0.040/rs,0.050/rs,0.060/rs)

def buck_input_current(vin=10,watts_out=10,eff=0.80,raw_amp=.5):
    """Upper sample input current; RAW AUX design target .5A at VIN."""
    return watts_out/(vin*eff)+raw_amp

def inductive_term(uh, di_a,dt_us):
    if dt_us <=0:raise ValueError("nonpositive transition time")
    return uh*di_a/dt_us

def main():
    for t in (.001,.0025,.005,.01):
        a=ov_bounds(t)
        print(f"div_tol ±{100*t:.2f}%: ON threshold {a.ov_rising_min:.3f}..{a.ov_rising_max:.3f} V; "
              f"OV-recovery {a.ov_falling_min:.3f}..{a.ov_falling_max:.3f} V; "
              f"guarantee by 36 / recovery at 32: "
              f"{a.ov_rising_max<=36 and a.ov_falling_min>32}")
    print("15mΩ current trip (no shunt tolerance)", sense_trip())
    print("10V 10W buck @80% plus 0.5A RAW:",buck_input_current(),"A")
    for L,di,dt in ((.5,2,1),(1,2,.1),(1,5,.1)):
        print(f"L={L}µH di={di}A dt={dt}µs overshoot={inductive_term(L,di,dt):.1f}V")
    print("Takes neither source inductance nor capacitor inrush nor actual pads into account.")
if __name__=="__main__":main()
