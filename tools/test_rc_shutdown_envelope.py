"""Closed-form analog RC-envelope test for TripTracer 01F candidate.

No SPICE model / datasheet guarantee. Current directions and voltages are
assumptions, not LM74930 validation. Run: python3 tools/test_rc_shutdown_envelope.py
"""
from math import exp, isinf
from analyze_rc_shutdown import cutoff_seconds


def voltage(t_s, v0, r_ohms, c_farads, source_a=0):
    """Discharge with constant positive current injected into HOLD_CAP."""
    vinf = source_a * r_ohms
    return vinf + (v0-vinf)*exp(-t_s/(r_ohms*c_farads))


def check():
    # Sweep capacitor effective values, resistance tolerance, threshold
    # corners and leakage; positive injection is the dangerous direction.
    cases = 0
    safe = 0
    unsafe = 0
    for cuf in (4.7, 10, 22, 47, 68):
        for r in (326700, 330000, 333300):
            for falling in (0.41, 0.70):
                for source_na in (0, 200, 800, 1240, 1500, 2000):
                    current = source_na * 1e-9
                    t = cutoff_seconds(r, cuf*1e-6, 4.5, falling, current)
                    if isinf(t):
                        assert current*r >= falling
                        unsafe += 1
                    else:
                        assert t >= 0
                        # Before the threshold, voltage remains above threshold.
                        if t > 1e-9:
                            assert voltage(t/2, 4.5, r, cuf*1e-6, current)>falling
                        assert abs(voltage(t,4.5,r,cuf*1e-6,current)-falling)<1e-8
                        safe += 1
                    cases+=1
    assert cases==180
    assert safe>0 and unsafe>0
    # Removing a GPIO discharge command never charges a disconnected RC.
    # However a fully charged effective 68uF may exceed a hypothetical 30s
    # deadline substantially; no guaranteed time window is yet established.
    assert cutoff_seconds(330000,68e-6,4.5,0.41)>30
    print(f"PASS: {cases} analytical RC envelope cases ({safe} finite, {unsafe} non-cutoff)")
    print("NOT PASSED: guaranteed shutdown; circuit leakage and capacitance unverified")


if __name__=="__main__":
    check()
