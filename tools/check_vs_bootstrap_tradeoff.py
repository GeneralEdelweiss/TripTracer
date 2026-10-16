"""Quantify why a passive 10k VS feed is not 6V-start + 200V-pulse qualified.

Assumptions: 6V starting VIN, VS minimum 4V (TI LM74930-Q1 input
operating range), 0.65mA *typical* active current per TI summary; not an
upper-bound, includes no extra gate charge currents. 200V/350ms is a
conservative rectangular sensitivity case, NOT an ISO waveform.
"""
def vs_drop(vin, r, iq):
    return vin-r*iq


def pulse(r, vin=200, clamp=50, duration=0.35):
    i=(vin-clamp)/r
    return {"i":i,"r_power":i*i*r,"r_joule":i*i*r*duration,
            "clamp_power":i*clamp,"clamp_joule":i*clamp*duration}


def main():
    iq=.00065
    maxr=(6-4)/iq
    print(f"6V start at 4V VS with 0.65mA typical active: RVS <= {maxr:.0f} ohm (typical only)")
    print("RVS   VS@6V / 0.65mA     200V->50V clamp, 350ms RVS energy")
    for r in (1000,2200,3000,4700,10000):
        p=pulse(r)
        print(f"{r:5d}  {vs_drop(6,r,iq):7.2f}V                  {p['r_joule']:6.3f}J")
    assert vs_drop(6,10000,iq)<4  # 10k TI 200V reference unsuitable for 6V start
    assert vs_drop(6,2200,iq)>4   # ONLY at typical current; not worst-case
    assert pulse(2200)['r_joule']>3
    assert pulse(10000)['r_joule']>.7
    print("PASS: passive resistor cannot be approved without 6V-current/pulse energy co-design.")
if __name__=="__main__":
    main()
