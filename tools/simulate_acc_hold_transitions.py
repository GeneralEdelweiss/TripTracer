"""Idealized ACC/HOLD switching transitions. Generic MOS models, NOT manufacturer validation.
Run with --dll pointing to an installed ngspice shared library, --output DIR.
"""
import argparse, ctypes as C, itertools, json, os
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dll',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    dll=Path(args.dll).resolve()
    if os.name=='nt':
        dll_dir=os.add_dll_directory(str(dll.parent))
    lib=C.CDLL(str(dll))
    lines=[]
    CHAR=C.CFUNCTYPE(C.c_int,C.c_char_p,C.c_int,C.c_void_p)
    EXIT=C.CFUNCTYPE(C.c_int,C.c_int,C.c_bool,C.c_bool,C.c_int,C.c_void_p)
    @CHAR
    def output(s,ident,user):
        lines.append(s.decode('utf-8',errors='replace'));return 0
    @CHAR
    def status(s,ident,user):return 0
    @EXIT
    def stopped(code,immediate,isquit,ident,user):
        lines.append('Controlled exit: '+str(code));return 0
    lib.ngSpice_Init.argtypes=[C.c_void_p]*7
    lib.ngSpice_Command.argtypes=[C.c_char_p]
    lib.ngSpice_Circ.argtypes=[C.POINTER(C.c_char_p)]
    lib.ngSpice_Init(output,status,stopped,None,None,None,None)
    class Complex(C.Structure):
        _fields_=[('real',C.c_double),('imag',C.c_double)]
    class Vector(C.Structure):
        _fields_=[('name',C.c_char_p),('type',C.c_int),('flags',C.c_short),
                  ('realdata',C.POINTER(C.c_double)),('complexdata',C.POINTER(Complex)),
                  ('length',C.c_int)]
    lib.ngGet_Vec_Info.argtypes=[C.c_char_p]
    lib.ngGet_Vec_Info.restype=C.POINTER(Vector)
    def command(s):return lib.ngSpice_Command(s.encode())
    def vector(s):
        vec=lib.ngGet_Vec_Info(s.encode())
        if not vec or not vec.contents.realdata:
            raise RuntimeError('Missing transient vector '+s)
        return [vec.contents.realdata[i] for i in range(vec.contents.length)]
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    command('version')
    for vin,scenario in itertools.product([6,9,30],['normal','usb_only','stuck_hold','acc_bounce']):
        if scenario=='usb_only':
            acc='0';hold='2.4'
        else:
            acc=f'PWL(0 0 10m 0 10.1m {vin} 100m {vin} 100.1m 0 180m 0 180.1m {vin} 200m {vin})'
            if scenario=='acc_bounce':
                acc=f'PWL(0 0 10m 0 10.1m {vin} 60m {vin} 60.1m 0 60.8m 0 60.9m {vin} 100m {vin} 100.1m 0 180m 0 180.1m {vin} 200m {vin})'
            hold='PWL(0 0 20m 0 20.1m 2.4 130m 2.4 130.1m 0 200m 0)'
            if scenario=='stuck_hold':hold='PWL(0 0 20m 0 20.1m 2.4 200m 2.4)'
        net=[f'Exploratory ACC HOLD transition {vin}V {scenario}',
            f'Vacc acc 0 {acc}',f'Vhold hold 0 {hold}',
            'Videal5 ideal5 0 5','SBUCK ideal5 raw5 en 0 BUCKSW',
            '.model BUCKSW SW(RON=0.05 ROFF=1e12 VT=0.73 VH=0.32)',
            'Cout raw5 0 220u IC=0','Rload raw5 0 2.5',
            'Racc1 acc am 100k','Racc2 am ac 100k','Dz 0 ac DZ','Dacc ac en DS',
            'Ren en 0 100k','Cen en 0 10n IC=0',
            'Rpg raw5 pg 4.7k','Mp pd pg raw5 raw5 PM','Dhold pd en DS',
            'Rh hold hg 10k','Rhp hg 0 100k','Mn pg hg 0 0 NM',
            '.model NM NMOS(VTO=1.5 KP=0.1 RD=3 RS=3)',
            '.model PM PMOS(VTO=-2 KP=0.01 RD=10 RS=10)',
            '.model DZ D(IS=1e-14 BV=4.7 IBV=10u)', '.model DS D(IS=1e-14 N=1)',
            'Bpleak raw5 pd I=2u*min(1,max(v(raw5,pd)/0.1,0))',
            'Bnleak pg 0 I=5u*min(1,max(v(pg)/0.1,0))',
            'Benleak en 0 I=200n*min(1,max(v(en)/0.1,0))',
            '.options reltol=0.001','.tran 50u 200m 0 50u uic','.end']
        command('destroy all');start=len(lines)
        encoded=[s.encode() for s in net]+[None]
        lib.ngSpice_Circ((C.c_char_p*len(encoded))(*encoded));command('run')
        if any('error' in s.lower() for s in lines[start:]):
            raise RuntimeError('ngspice error: '+str(lines[start:]))
        t=vector('time');en=vector('v(en)');v5=vector('v(raw5)')
        if len(t)<100:raise RuntimeError('No complete transient data')
        def sample(at):
            i=min(range(len(t)),key=lambda i:abs(t[i]-at))
            return dict(time_s=t[i],en_V=en[i],vehicle_5V_V=v5[i])
        samples={str(x):sample(x) for x in [0.005,0.03,0.065,0.12,0.17,0.195]}
        checks={}
        if scenario=='usb_only':
            checks['USB_only_does_not_start']=max(v5)<0.1 and max(en)<0.41
        else:
            checks['ACC_start_in_idealized_model']=samples['0.03']['vehicle_5V_V']>4.75
            checks['HOLD_after_ACC_off']=samples['0.12']['vehicle_5V_V']>4.75
            if scenario=='stuck_hold':
                # Failure demonstration; there is no real timer in this circuit.
                checks['demonstrated_absence_of_deadline']=samples['0.17']['vehicle_5V_V']>4.75
            else:
                checks['release_HOLD_stops_power']=samples['0.17']['vehicle_5V_V']<0.1
                checks['ACC_restart']=samples['0.195']['vehicle_5V_V']>4.75
            if scenario=='acc_bounce':checks['bounce_held']=samples['0.065']['vehicle_5V_V']>4.75
        results.append(dict(vin_V=vin,scenario=scenario,points=len(t),samples=samples,checks=checks,
                            hardware_deadline_implemented=False))
        rows=['time_s,en_V,vehicle_5V_V']
        # Preserve all source samples: no interpolation or smoothed threshold results.
        rows += [f'{a:.9g},{b:.9g},{c:.9g}' for a,b,c in zip(t,en,v5)]
        (out/f'{vin}V-{scenario}.csv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
        (out/f'{vin}V-{scenario}.cir').write_text('\n'.join(net)+'\n',encoding='utf-8')
    report=dict(status='Idealized switch feedback experiment, NOT TI/buck/LAB validation',
                limitations=['Main power path replaced by ideal 5V source and hysteretic switch',
                    'No controller startup/gate delays, UVLO/OVP, inductance, VS clamp or motor-start sag',
                    'Generic MOS/diodes and fixed leakage stress, not manufacturer temperature models',
                    'USB isolation assumed by separate raw5 source; no USB network simulated',
                    'No hardware deadline: stuck HOLD remains powered'],cases=results)
    (out/'transient-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (out/'ngspice.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(len(results),'transients; failed experiment checks',
          sum(not v for r in results for v in r['checks'].values()))
    print('Stuck-HOLD deadline absent in all 3 voltage scenarios; no release.')
if __name__=='__main__':main()
