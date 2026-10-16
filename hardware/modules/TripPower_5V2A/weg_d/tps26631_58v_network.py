#!/usr/bin/env python3
"""TPS26631 REV6 reduced-order transient NETWORK, not a TPS2663 PSpice macromodel.
Run: python3 tps26631_58v_network.py --scenario cases|matrix|recovery
Dependency: scipy, numpy. Manufacturer PSpice SLVMD03A (TI) not embedded/licensed.
4 states: harness current, VIN at TPS IN_SYS, TPS OUT, LMR38020 VIN.
Series source/harness/connector/PCB L,R and reverse Q201 R,L. Capacitor
nominal vs biased Ceff is deliberately varied. ESR/ESL are LUMPED as
effective series R,L, not physically resolved high-frequency cap branches;
no accurate B_GATE, DRV, OVP, VGS, ESR/ESL pin transient, junction-SOA, EMI,
source-ground bounce, Coss, USB/RAW fault or vehicle approval is claimed.
"""
from dataclasses import dataclass, replace
from math import tanh
import argparse, json
import numpy as np
from scipy.integrate import solve_ivp

@dataclass(frozen=True)
class P:
    source_r:float=.25
    cable_r:float=.10
    connector_r:float=.015
    pcb_r:float=.010
    cable_l:float=.8e-6
    connector_l:float=.02e-6
    pcb_l:float=.01e-6
    reverse_r:float=.010
    reverse_l:float=.02e-6
    cap_esr_lumped:float=.018
    cap_esl_lumped:float=.003e-6
    c_sys:float=.5e-6        # C201 nominal 1uF100V, bias-adjusted unknown
    c_out:float=.5e-6        # C202 nominal 1uF100V, bias-adjusted unknown
    c_buck:float=3e-6       # C101+C108 nominal 9.4uF100V, effective unknown
    buck_feed_r:float=.06
    efuse_ron:float=.031
    ilim:float=3.
    buck_w:float=10.
    efficiency:float=.85
    raw_a:float=.5
    v0:float=32.
    v1:float=58.
    t0:float=.1e-3
    edge:float=20e-6
    hold:float=.350
    ov_trip:float=34.2    # hypothetical threshold, NOT guaranteed Way A
    ov_return:float=31.0 # nominal ~31V Way A -> restart at32 impossible
    off_delay:float=14e-6 # TI OVP-to-FLT max14us is NOT certified GATE-OFF
    off_slew:float=2e-6
    on_slew:float=.15e-3
    retry_delay:float=.2e-3
    short_at:float=-1.
    short_res:float=.5
    short_delay:float=4.5e-6
    reverse_short:bool=False
    efuse_short:bool=False
    mode:str="pulse"

def src(t,p):
    if p.mode=="unplug":
        return p.v0 if t<=p.t0 else p.v0*max(0.,1.-(t-p.t0)/max(p.edge,1e-9))
    if t<=p.t0:return p.v0
    if t<p.t0+p.edge:return p.v0+(p.v1-p.v0)*(t-p.t0)/p.edge
    if t<p.t0+p.edge+p.hold:return p.v1
    if t<p.t0+2*p.edge+p.hold:
        return p.v1+(p.v0-p.v1)*(t-p.t0-p.edge-p.hold)/p.edge
    return p.v0

def gate(t,p):
    if p.efuse_short:return 1.
    if p.mode=="start":return max(0.,min(1.,(t-p.t0)/p.on_slew))
    if p.mode=="unplug":return max(0.,min(1.,(p.t0+p.off_slew-t)/p.off_slew))
    if p.v1>p.ov_trip and p.v0<p.ov_trip:
        ttrip=p.t0+p.edge*(p.ov_trip-p.v0)/(p.v1-p.v0)
    elif p.v0>p.ov_trip:ttrip=0.
    else:ttrip=float("inf")
    toff=ttrip+p.off_delay
    if p.short_at>=0:toff=min(toff,p.short_at+p.short_delay)
    off=max(0.,min(1.,(toff+p.off_slew-t)/p.off_slew))
    treturn=p.t0+p.edge+p.hold+p.edge
    if p.v0<p.ov_return and t>treturn+p.retry_delay:
        off=max(off,min(1.,(t-treturn-p.retry_delay)/p.on_slew))
    return off

def initial(p):
    if p.v0<=0:return np.zeros(4)
    ib=p.buck_w/(p.efficiency*p.v0)
    ih=ib+p.raw_a
    r=p.source_r+p.cable_r+p.connector_r+p.pcb_r+p.cap_esr_lumped+(0.001 if p.reverse_short else p.reverse_r)
    vi=p.v0-ih*r
    vo=vi-ih*p.efuse_ron
    return np.array((ih,vi,vo,vo-ib*p.buck_feed_r),dtype=float)

def rhs(t,x,p):
    ih,vi,vo,vb=x
    if p.efuse_short:isw=max(0.,(vi-vo)/.004)
    else:isw=gate(t,p)*p.ilim*tanh(max(0.,vi-vo)/(p.efuse_ron*p.ilim))
    ibuck=(vo-vb)/p.buck_feed_r
    # Smooth approximate HV input load, not the internal LMR38020 switching model.
    ilmr=p.buck_w/(p.efficiency*max(vb,6.))*max(0.,min(1.,vb/7.))
    iraw=p.raw_a*max(0.,min(1.,vo/7.))
    if p.short_at>=0 and t>=p.short_at:iraw+=max(0.,vo)/p.short_res
    r=p.source_r+p.cable_r+p.connector_r+p.pcb_r+p.cap_esr_lumped+(0.001 if p.reverse_short else p.reverse_r)
    inductance=p.cable_l+p.connector_l+p.pcb_l+p.cap_esl_lumped+p.reverse_l
    return np.array(((src(t,p)-r*ih-vi)/inductance,(ih-isw)/p.c_sys,
                     (isw-ibuck-iraw)/p.c_out,(ibuck-ilmr)/p.c_buck),dtype=float)

def simulate(p,full=False):
    stop=p.t0+p.edge+p.hold+p.edge+.0004 if full and p.mode!="unplug" else p.t0+p.edge+.0004
    s=solve_ivp(lambda t,y:rhs(t,y,p),(0.,stop),initial(p),method="LSODA",
                rtol=1e-6,atol=1e-8,max_step=20e-6 if full else 5e-7)
    if not s.success or not np.isfinite(s.y).all():raise RuntimeError(s.message)
    di=np.array([rhs(t,s.y[:,i],p)[0] for i,t in enumerate(s.t)])
    # Q201 upstream VIN is an estimate ONLY; no upstream input C / MOSFET Coss.
    qdrain=s.y[1]+s.y[0]*(0.001 if p.reverse_short else p.reverse_r)+di*p.reverse_l
    names=("I_HARNESS_A","TPS_IN_SYS_V","TPS_OUT_V","LMR_VIN_V","Q201_DRAIN_EST_V")
    parts=list(s.y)+[qdrain]
    peaks={n:{"min":round(float(min(a)),4),"max":round(float(max(a)),4)} for n,a in zip(names,parts)}
    return {"mode":p.mode,"full_350ms_plus_return":full,"end_s":round(stop,7),
            "solver_points":len(s.t),"peak":peaks,
            "sys_gt60":peaks["TPS_IN_SYS_V"]["max"]>60,
            "sys_ge67":peaks["TPS_IN_SYS_V"]["max"]>=67,
            "buck_gt80":peaks["LMR_VIN_V"]["max"]>80,
            "restart_at_32_possible":p.ov_return>32.,
            "gate_end":round(gate(stop,p),3) if full else None}

def cases():
    return [
      ("10V_full_load_start",P(mode="start",v0=0.,v1=10.,hold=.001,ov_return=32.5)),
      ("32_to_36",P(v0=32.,v1=36.,hold=.0004)),
      ("32_to_58_350ms",P()),
      ("58_to_32_recovery",P()),
      ("short_at_10V",P(v0=10.,v1=10.,short_at=.15e-3)),
      ("short_at_32V",P(v0=32.,v1=32.,short_at=.15e-3)),
      ("short_at_58V_OV_already_OFF",P(v0=58.,v1=58.,short_at=.15e-3)),
      ("unplug_32V",P(mode="unplug",v0=32.,v1=0.,edge=1e-6)),
      ("Q201_reverse_FET_DS_short",P(reverse_short=True)),
      ("U201_eFuse_DS_short",P(efuse_short=True))]

def matrix():
    rows=[]
    for l in (.2e-6,1e-6,3e-6,5e-6):
      for c in (.2e-6,.5e-6,1e-6):
       for d in (2e-6,14e-6,100e-6):
        for w in (5.,10.):
         for raw in (0.,.5):
          p=P(cable_l=l,c_sys=c,off_delay=d,buck_w=w,raw_a=raw)
          z=simulate(p)
          rows.append({"L_uH":l*1e6,"C201_effective_uF":c*1e6,"delay_us":d*1e6,
                       "buck_W":w,"raw_A":raw,
                       "IN_SYS_peak_V":z["peak"]["TPS_IN_SYS_V"]["max"],
                       "Q201_DRAIN_est_peak_V":z["peak"]["Q201_DRAIN_EST_V"]["max"],
                       "TPS_OUT_peak_V":z["peak"]["TPS_OUT_V"]["max"],
                       "LMR_VIN_peak_V":z["peak"]["LMR_VIN_V"]["max"],
                       "exceeds60":z["sys_gt60"],"reaches67":z["sys_ge67"]})
    return rows

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",choices=["cases","matrix"]+[n for n,p in cases()],default="cases")
    ap.add_argument("--full",action="store_true",help="simulate 350ms hold AND fall; still not hardware")
    a=ap.parse_args()
    if a.scenario=="matrix":out=matrix()
    elif a.scenario=="cases":out={n:simulate(p,a.full and n in ("32_to_58_350ms","58_to_32_recovery")) for n,p in cases()}
    else:out=simulate(next(p for n,p in cases() if n==a.scenario),a.full)
    print(json.dumps(out,indent=2))
