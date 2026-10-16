#!/usr/bin/env python3
"""TripPower Weg D REV6 Round8: explicit scenario calculations only, no approval.

Usage:
  python3 hardware/modules/TripPower_5V2A/weg_d/rev6_round8_compare.py
  cd hardware/modules/TripPower_5V2A/weg_d
  python3 -m unittest -v test_rev6_round8

DO NOT use 10ms TI transient absolutes as a 350ms permissible voltage.
Only an actually measured, applicable and manufacturer-qualified V(pin,t)
and hot/short/thermal test can release the 58V implementation.
"""
from dataclasses import dataclass

BUCK_W=10.0
RAW_A=0.5
EFF_LOW=0.8
VIN_LOW=10.0
PULSE_V=58.0

@dataclass(frozen=True)
class Part:
    name:str
    vin_operating_max:float
    vin_abs_350ms:float
    ron_25_ohm:float|None
    limit_max_a:float|None

PARTS=[
 Part("TPS26631",60.,67.,0.031,6.),
 Part("TPS26600",60.,62.,0.150,2.23),
 Part("LTC4368 VIN",60.,100.,None,None)
]

def vin_current(buck_w=BUCK_W,vin=VIN_LOW,eff=EFF_LOW,raw=RAW_A):
    if vin<=0 or not 0<eff<=1 or raw<0:raise ValueError("invalid current model")
    return buck_w/(vin*eff)+raw

def ring_volts(L_microhenry,delta_amp,delta_microsecond):
    """L*di/dt; value ONLY for chosen current polarity and idealized constant L."""
    if L_microhenry<0 or delta_microsecond<=0:raise ValueError("invalid line model")
    return L_microhenry*delta_amp/delta_microsecond

def margins(local_peak_v,part):
    """Nominal VIN-domain margin only; NOT other pins nor operating safety."""
    return (part.vin_operating_max-local_peak_v,
            part.vin_abs_350ms-local_peak_v)

def conduction_w(i_a,ron_ohm):
    return i_a*i_a*ron_ohm

def semiconductors_eur(prices):
    """Sum explicitly priced physical parts only; pass list of per-unit €."""
    return round(sum(prices),4)

def main():
    i=vin_current()
    print("CHASSIS IS 58V MAX ONLY IF M8 INSTALLATION/PULSE VERIFIED")
    print("Buck 5V2A 10W, eta=.8, Vin10, RAW0.5A => Iin=%.3f A"%i)
    print("Indicative 25C eFuse ON dissipation: TPS31 %.3fW, TPS00 %.3fW"%(
        conduction_w(i,.031),conduction_w(i,.150)))
    for L,di,dt in ((.5,2.,1.),(1.,2.,.5),(1.,5.,.1)):
        dv=ring_volts(L,di,dt);v=PULSE_V+dv
        print("ILLUSTRATION only: L=%gµH, dI=%gA, dt=%gµs, add=%gV, Vpin=%gV"%(L,di,dt,dv,v))
        for p in PARTS:print("  ",p.name,"VIN op/ABS margins",margins(v,p))
    print("NOT included: OVP turnoff delay, ringing polarity, PCB-RLC, alternate pins, MOSFET SOA, C input, fuse arc, +85C safe-off, RAW fault")
    print("Semiconductor cost 1/10/100 per frontend in EUR net:")
    for name,tiers in {
       "TPS26631+reverseFET+driver":([3.87,3.78,.292],[2.937,2.49,.129],[2.4461,1.75,.113]),
       "TPS26600":([3.44],[2.594],[2.1495]),
       "LTC4368+2xprovisionalFET":([7.57,2.93,2.93],[5.88,1.91,1.91],[4.99,1.3256,1.3256])
    }.items():
        print(name,[semiconductors_eur(t) for t in tiers])
    print("NO figures above are complete BOM or laboratory / ISO / KiCad ERC proof.")
if __name__=="__main__":main()
