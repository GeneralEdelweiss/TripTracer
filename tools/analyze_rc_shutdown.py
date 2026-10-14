"""Analytical RC-controlled LM74930 EN shutdown candidate. NOT SPICE or a qualification.

Derived from TI LM74930-Q1 EN falling threshold 0.41...0.70 V and
max EN current 200 nA. Effective MLCC capacitance, leakage and protection
circuits MUST be measured under voltage/temperature; 47uF is NOT assumed
to be the effective capacity of a 47uF ceramic.
"""
from math import log


def cutoff_seconds(r_ohm, c_effective_f, v_initial, v_falling, i_source_a=0):
    """I_source is positive current *into* capacitor when ACC is OFF."""
    if r_ohm <= 0 or c_effective_f <= 0 or v_initial < 0:
        raise ValueError("invalid R/C/V")
    v_infty = i_source_a * r_ohm
    if v_infty >= v_falling:
        return float("inf")  # never shuts down at constant leakage
    if v_initial <= v_falling:
        return 0.0
    return r_ohm*c_effective_f*log((v_initial-v_infty)/(v_falling-v_infty))


def evaluate():
    r=330_000
    vf=0.41
    print("RC shutdown: R=330k; 4.5V initial; 0.41V falling limit")
    print("C_eff(uF)  no-source(s)  +200nA-source(s)")
    for cuf in [10, 15, 22, 30, 47]:
        a=cutoff_seconds(r,cuf*1e-6,4.5,vf)
        b=cutoff_seconds(r,cuf*1e-6,4.5,vf,200e-9)
        print(f"{cuf:9d}  {a:12.2f}  {b:16.2f}")
    i_limit=vf/r
    print(f"Source leakage causing permanent ON at 0.41V: {i_limit*1e6:.3f} uA")
    assert cutoff_seconds(r,22e-6,4.5,vf,0)>0
    assert cutoff_seconds(r,22e-6,4.5,vf,1.5e-6)==float("inf")
    assert cutoff_seconds(r,22e-6,4.5,vf,200e-9)>cutoff_seconds(r,22e-6,4.5,vf,0)
    # Once a discharge FET pulls the cap below threshold, releasing it
    # while the ACC-qualified charging diode is reverse-biased cannot
    # restore the enable voltage without an external source.
    print("PASS: finite decay without recharging, but no electrical validation")


if __name__=="__main__":
    evaluate()
