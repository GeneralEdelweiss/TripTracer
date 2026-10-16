#!/usr/bin/env python3
"""REV6 A input ringing sensitivity; NOT a waveform validation.

Ideal lossless/series R-L harness step model into eFuse local input ceramic C.
Assumes a step on the UPSTREAM side of the lumped series L, no load and
no semiconductors switching. Actual connector and pin probe R/L/C needed.
"""
import math,json

def step_peak(v_from=32.,v_to=58.,l_h=0.5e-6,c_f=1e-6,r_ohm=.05):
    assert l_h>0 and c_f>0 and r_ohm>=0 and v_to>=v_from
    natural_hz=1/(2*math.pi*math.sqrt(l_h*c_f))
    damping=r_ohm/(2*math.sqrt(l_h/c_f))
    factor=0 if damping>=1 else math.exp(-math.pi*damping/math.sqrt(1-damping**2))
    peak=v_to+(v_to-v_from)*factor
    return {"source_step_v":[v_from,v_to],"L_h":l_h,"C_f":c_f,
      "series_R_ohm_ASSUMED":r_ohm,"LC_resonance_frequency_Hz":natural_hz,
      "damping_ratio":damping,"ideal_1st_peak_at_pin_v":peak,
      "TPS26631_60v_operating_violation_in_example":peak>60,
      "TPS26631_67v_absolute_violation_in_example":peak>67,
      "58V_conditioned_source_does_NOT_suffice_to_prove_chip_pin_at58":True,
      "real_vehicle_spectrum_or_lab_proof":False}
def hypothetical_resistor_tradeoff(series_r,vin=10.,eff=.8,raw=.5):
    i=10/(vin*eff)+raw
    return {"R_series_ohm":series_r,"i_at10v_A_hypothetical":i,
            "steady_drop_at10v_V":i*series_r,
            "power_dissipation_W":i*i*series_r,
            "safe_part_selected":False}
def study():
    return {"limitations":"simple 2nd-order STEP sensitivity not ISO pulse qualification",
            "cases":[step_peak(r_ohm=r) for r in (.05,.2,.5,1.)],
            "series_resistor_1ohm_example":hypothetical_resistor_tradeoff(1.),
            "safety":["58V/350ms at connector is a maximum, require captured max at ALL eFuse pins including L*di/dt",
                      "TPS26631 recommended input max60V, abs max67V; 75V only 10ms/25C not 350ms",
                      "No small 58V breakdown TVS guarantees a clamp below60V for 350ms",
                      "If local 60V bound not credible, prefer a genuinely higher-rated protection architecture; do not claim release"],
            "release":False}
if __name__=="__main__": print(json.dumps(study(),indent=2))
