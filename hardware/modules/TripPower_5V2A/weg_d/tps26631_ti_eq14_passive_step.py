#!/usr/bin/env python3
"""TPS26631 REV6 independent TI Eq.14 + passive series-RLC source-edge checker.

NOT an executed TPS2663 PSpice macromodel; NOT all-pin or production qualification.
InputCase.source is a voltage at the chosen boundary: to claim REV6 input <=58V
it must be the measured M8 voltage (incl. its OWN ringing). Consequently L is
ONLY inductance downstream of the selected boundary. Do not treat L_harness
between generator and M8 as local PCB inductance.

TI Rev G §9.5.1 Eq14 is Vspike~=Vsource+Iload*sqrt(Lin/Cin) for current
interruption; a conservative screening equation, NOT a guaranteed maximum.
The passive step model assumes eFuse OFF and zero preceding harness current,
so its large source-edge transient is DIFFERENT from Eq14 current interruption.
No real Q201 Coss, gate, BGATE, DRV, OVP or LMR regulator equations included.
"""
from dataclasses import dataclass,asdict
from math import sqrt,pi,ceil,isfinite
import argparse,json

@dataclass(frozen=True)
class InputCase:
    l_uh:float=.8            # must correspond to chosen boundary
    c_uf:float=.5            # effective, NOT nameplate nominal
    r_ohm:float=.40
    rise_us:float=20.
    from_v:float=32.
    to_v:float=58.
    current_a:float=1.75     # Eq14 uses it; passive step does NOT use it

def ti_inductive_spike(base_v,current_a,l_uh,c_uf):
    if l_uh<=0 or c_uf<=0 or current_a<0:raise ValueError("invalid LC/I")
    return base_v+current_a*sqrt(l_uh/c_uf)

def required_cap_uf(base_v,target_v,current_a,l_uh):
    if target_v<=base_v or l_uh<=0 or current_a<0:raise ValueError("invalid capacitance screen")
    return l_uh*(current_a/(target_v-base_v))**2

def step_peak(p):
    """RK4 series R,L with ideal shunt C; input at source boundary, load OFF.
    ESR/ESL/PCB coupling and Q201 are NOT separately simulated. No negative-clamp.
    dt chosen automatically for LC period and edge; not a real spice transient.
    """
    if min(p.l_uh,p.c_uf,p.r_ohm,p.rise_us)<=0:raise ValueError("invalid passive case")
    L=p.l_uh*1e-6;C=p.c_uf*1e-6;R=p.r_ohm;edge=p.rise_us*1e-6
    period=2*pi*sqrt(L*C)
    stop=max(10*period,5*edge)
    dt=min(period/240,edge/120)
    count=int(ceil(stop/dt))
    if count>300000:raise ValueError("excessive sampling")
    dt=stop/count
    def source(t):
        return p.from_v+(p.to_v-p.from_v)*min(1.,max(0.,t/edge))
    def f(t,i,v):
        return (source(t)-R*i-v)/L,i/C
    i=0.;v=p.from_v;hi=v;lo=v;ipeak=0.
    for k in range(count):
        t=k*dt
        a,b=f(t,i,v)
        c,d=f(t+dt/2,i+a*dt/2,v+b*dt/2)
        e,g=f(t+dt/2,i+c*dt/2,v+d*dt/2)
        h,j=f(t+dt,i+e*dt,v+g*dt)
        i+=dt*(a+2*c+2*e+h)/6
        v+=dt*(b+2*d+2*g+j)/6
        hi=max(hi,v);lo=min(lo,v);ipeak=max(ipeak,abs(i))
    if not all(isfinite(x) for x in (lo,hi,ipeak)):raise ArithmeticError("nonfinite model")
    return {"pin_peak_V":round(hi,4),"pin_min_V":round(lo,4),
            "harness_I_abs_peak_A":round(ipeak,4),
            "exceeds_TI_60V_operating":hi>60.,
            "reaches_TI_67V_abs":hi>=67.,
            "natural_period_us":round(period*1e6,4),"solver_steps":count,
            "model":"PASSIVE_RLC_SOURCE_EDGE_ONLY_TI_MACRO_NOT_USED"}

def sweep():
    rows=[]
    for L in (.02,.05,.2,.8,2.,5.):
        for C in (.2,.5,1.,2.):
            for R in (.08,.4,1.):
                for edge in (.2,1.,5.,20.):
                    p=InputCase(l_uh=L,c_uf=C,r_ohm=R,rise_us=edge)
                    rows.append({"l_uh":L,"ceff_uf":C,"r_ohm":R,
                                 "rise_us":edge,**step_peak(p)})
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sweep",action="store_true")
    args=ap.parse_args()
    if args.sweep:
        cases=sweep()
        print(json.dumps({"count":len(cases),
                          "exceeds60":sum(z["exceeds_TI_60V_operating"] for z in cases),
                          "reaches67":sum(z["reaches_TI_67V_abs"] for z in cases),
                          "model":"PASSIVE_ONLY_NOT_VENDOR_SPICE",
                          "scenarios":cases},indent=2))
        return
    cases={
     "ti_eq14_screen":[{"i_A":i,"L_uH":L,"ceff_uF":C,
                         "vpeak_screen_V":round(ti_inductive_spike(58,i,L,C),4),
                         "ceff_required_for_60V_uF":round(required_cap_uf(58,60,i,L),4),
                         "ceff_required_for_67V_uF":round(required_cap_uf(58,67,i,L),4)}
                         for i in (1.75,3.) for L,C in ((.8,.5),(.8,1.),(5.,.5),(.05,.5))],
     "passive_steps":[{"input_assumptions":asdict(p),"result":step_peak(p)} for p in (
             InputCase(),InputCase(rise_us=1.),
             InputCase(l_uh=.05,c_uf=.5,r_ohm=.08,rise_us=1.),
             InputCase(l_uh=.05,c_uf=.5,r_ohm=.08,rise_us=.2),
             InputCase(l_uh=5.,c_uf=.2,rise_us=1.))],
     "disclaimer":"TI_PSPICE_NOT_EXECUTED_NOT_HW_QUALIFIED"}
    print(json.dumps(cases,indent=2))
if __name__=="__main__":
    main()
