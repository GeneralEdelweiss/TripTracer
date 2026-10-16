"""Exploratory linear TripPower A23 AFTER-M8 TPS26631 input node model.

NOT TI PSpice: fixed Q201 fully ON, no gate-driver/LMR/UVLO/fault physics.
Uses SciPy matrix exponentials. Ceff, R/L, Coss are HYPOTHESES, not measured.
"""
from dataclasses import dataclass, asdict, replace
import argparse
import json
import numpy as np
from scipy.linalg import expm

@dataclass(frozen=True)
class Params:
    l_after_m8_h: float = 0.05e-6
    r_after_m8_ohm: float = 0.08
    c_at_in_pins_f: float = 2e-9     # UNKNOWN IN pin/trace-to-GND capacity
    c201_eff_f: float = 0.5e-6       # unverified C201 DC bias at 58 V
    q201_coss_f: float = 0.655e-9    # Vishay typical Coss at 25 V, NOT at 58 V
    q201_rds_ohm: float = 0.020      # simplified fixed ON at warm temperature
    rise_s: float = 1e-6
    fall_s: float = 20e-6
    plateau_s: float = 350e-3
    load_a: float = 0
    off_delay_s: float = 14e-6      # ASSUMED interruption, not TI GATE delay
    off_fall_s: float = 2e-6
    mode: str = 'already_off'       # already_off, assumed_trip, fet_short

def matrices(p, vslope=0, islope=0):
    l,r,cp,cs,cm,rq = (p.l_after_m8_h,p.r_after_m8_ohm,p.c_at_in_pins_f,
                      p.c201_eff_f,p.q201_coss_f,p.q201_rds_ohm)
    det = cp*cs+cm*(cp+cs)
    a = np.array([[-r/l,-1/l,0],
                  [(cs+cm)/det,-cs/rq/det,cs/rq/det],
                  [cm/det,cp/rq/det,-cp/rq/det]])
    m=np.zeros((6,6))
    m[:3,:3]=a
    m[:3,3]=[1/l,0,0]         # local boundary voltage
    m[:3,4]=[0,-cm/det,-(cp+cm)/det] # prescribed eFuse input current
    m[3,5]=vslope
    m[4,5]=islope
    return m

def source(t,p):
    rise=p.rise_s
    down=rise+p.plateau_s
    if t<=0:return 32.0
    if t<rise:return 32+26*t/rise
    if t<down:return 58.0
    if t<down+p.fall_s:return 58-26*(t-down)/p.fall_s
    return 32.0

def load(t,p):
    if p.mode=='already_off':return 0.0
    if p.mode=='fet_short':return p.load_a
    trip=(35.4-32)/26*p.rise_s+p.off_delay_s
    if t<trip:return p.load_a
    if t<trip+p.off_fall_s:return p.load_a*(1-(t-trip)/p.off_fall_s)
    return 0.0

def simulate(p):
    for name in ('l_after_m8_h','r_after_m8_ohm','c_at_in_pins_f','c201_eff_f',
                 'q201_rds_ohm','rise_s','fall_s','plateau_s','off_fall_s'):
        if getattr(p,name)<=0:raise ValueError(name)
    if min(p.q201_coss_f,p.load_a,p.off_delay_s)<0:raise ValueError('negative setting')
    if p.mode not in ('already_off','assumed_trip','fet_short'):raise ValueError('mode')
    i=load(0,p)
    y=np.array([i,32-p.r_after_m8_ohm*i,32-(p.r_after_m8_ohm+p.q201_rds_ohm)*i,
                32.0,i,1.0])
    down=p.rise_s+p.plateau_s
    off=(35.4-32)/26*p.rise_s+p.off_delay_s
    bounds=sorted(set(v for v in [0,p.rise_s,off,off+p.off_fall_s,down,down+p.fall_s]
                      if 0<=v<=down+p.fall_s))
    peaks={'pre_tps_in_v':-float('inf'),'post_in_sys_v':-float('inf'),
           'abs_line_current_a':0.0,'abs_q201_vds_v':0.0}
    windows=[]
    for begin,end in zip(bounds[:-1],bounds[1:]):
        dt_all=end-begin
        v0=source(begin+1e-15,p);v1=source(end-1e-15,p)
        i0=load(begin+1e-15,p);i1=load(end-1e-15,p)
        y[3]=source(begin,p)
        y[4]=load(begin,p)
        m=matrices(p,(v1-v0)/dt_all,(i1-i0)/dt_all)
        near=min(dt_all,0.00012)
        resolution=min(20e-9,max(0.5e-9,p.rise_s/20))
        n=min(12000,max(2,int(np.ceil(near/resolution))))
        step=expm(m*(near/n))
        local={key:-float('inf') if key in ('pre_tps_in_v','post_in_sys_v') else 0.0
               for key in peaks}
        for j in range(n+1):
            pre,post,curr=float(y[1]),float(y[2]),float(y[0])
            samples={'pre_tps_in_v':pre,'post_in_sys_v':post,
                     'abs_line_current_a':abs(curr),'abs_q201_vds_v':abs(pre-post)}
            for key,v in samples.items():
                peaks[key]=max(peaks[key],v)
                local[key]=max(local[key],v)
            if j<n:y=step@y
        if dt_all>near:
            # Exact LINEAR network propagation across the 350-ms plateau.
            # No assumption about thermal/gate behavior should be inferred.
            y=expm(m*(dt_all-near))@y
            final={'pre_tps_in_v':float(y[1]),'post_in_sys_v':float(y[2]),
                   'abs_line_current_a':abs(float(y[0])),
                   'abs_q201_vds_v':abs(float(y[1]-y[2]))}
            for key,v in final.items():
                peaks[key]=max(peaks[key],v)
                local[key]=max(local[key],v)
        windows.append({'t0_s':begin,'t1_s':end,**{k:round(v,5) for k,v in local.items()}})
    return {'settings':asdict(p),
            'boundary':'58 V at M8 connector, L/R modeled STRICTLY AFTER this boundary',
            'method':'linear 3-state RLC; fixed Q201 ON; idealized eFuse input current, NOT vendor',
            'peaks':{k:round(v,5) for k,v in peaks.items()},
            'over_recommended_60_v':max(peaks['pre_tps_in_v'],peaks['post_in_sys_v'])>60,
            'at_or_over_absmax_67_v':max(peaks['pre_tps_in_v'],peaks['post_in_sys_v'])>=67,
            'windows':windows}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--sweep',action='store_true')
    args=parser.parse_args()
    if args.sweep:
        cases=[simulate(replace(Params(),l_after_m8_h=l,c201_eff_f=c,rise_s=rise))
            for l in (0.02e-6,0.05e-6,0.2e-6)
            for c in (0.2e-6,0.5e-6,1e-6)
            for rise in (0.2e-6,1e-6,20e-6)]
        print(json.dumps({'scenario_count':len(cases),
                          'over_60':sum(x['over_recommended_60_v'] for x in cases),
                          'at_or_over_67':sum(x['at_or_over_absmax_67_v'] for x in cases),
                          'cases':cases},indent=2))
    else:
        print(json.dumps(simulate(Params()),indent=2))
