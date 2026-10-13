"""Vehicle-sourced ACC/HOLD DC candidate. Generic MOS models, NOT manufacturer validation.
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
    def value(s):
        vec=lib.ngGet_Vec_Info(s.encode())
        if not vec or vec.contents.length!=1 or not vec.contents.realdata:
            raise RuntimeError('Missing DC vector '+s)
        return vec.contents.realdata[0]
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    # This topology sources HOLD permission only from the vehicle buck output,
    # instead of biasing EN continuously from BAT/VS.
    profiles=[('nominal',0,0),('diodes_bss84_stress',2e-6,5e-6),
              ('onsemi_bss84_stress',60e-6,5e-6)]
    for profile,vin,acc,hold,qual in itertools.product(profiles,[6,9,30],[0,1],[0,1],[0,1]):
        leakage,lp,ln=profile
        net=[f'ACC diode OR vehicle-powered HOLD {leakage} {vin}V {acc}{hold}{qual}',
            f'Vacc acc 0 {vin*acc}',f'Vhold hold 0 {2.4*hold}',f'Vqual raw5 0 {5*qual}',
            'Racc1 acc am 100k','Racc2 am ac 100k','Dz 0 ac DZ',
            'Dacc ac en DS','Ren en 0 100k','Cen en 0 10n',
            'Rpg raw5 pg 4.7k','Mp pd pg raw5 raw5 PM',
            'Dhold pd en DS','Rh hold hg 10k','Rhp hg 0 100k','Mn pg hg 0 0 NM',
            '.model NM NMOS(VTO=1.5 KP=0.1 RD=3 RS=3)',
            '.model PM PMOS(VTO=-2 KP=0.01 RD=10 RS=10)',
            '.model DZ D(IS=1e-14 BV=4.7 IBV=10u)',
            '.model DS D(IS=1e-14 N=1)',
            f'Bpleak raw5 pd I={lp}*min(1,max(v(raw5,pd)/0.1,0))',
            f'Bnleak pg 0 I={ln}*min(1,max(v(pg)/0.1,0))',
            'Benleak en 0 I=200n*min(1,max(v(en)/0.1,0))','.op','.end']
        command('destroy all');start=len(lines)
        encoded=[s.encode() for s in net]+[None]
        lib.ngSpice_Circ((C.c_char_p*len(encoded))(*encoded));command('run')
        if any('error' in s.lower() for s in lines[start:]):
            raise RuntimeError('ngspice error: '+str(lines[start:]))
        en=value('v(en)');expected=bool(acc or (hold and qual))
        consistent=en>1.05 if expected else en<0.41
        results.append(dict(leakage=leakage,vin_V=vin,acc=acc,hold=hold,
                    vehicle_5V_present=qual,expected_enable=expected,en_V=en,
                    acc_current_uA=-value('i(vacc)')*1e6,
                    vehicle_5V_current_uA=-value('i(vqual)')*1e6,
                    meets_DC_logic_in_this_model=consistent))
        if leakage=='nominal' and vin==6 and (acc,hold,qual)==(0,1,0):
            (out/'usb-only-hold.cir').write_text('\n'.join(net)+'\n',encoding='utf-8')
    report=dict(status='Generic DC design candidate; not KiCad/lab/full-system validation',
                model_limitations=['No TI controller, buck, USB power path, startup or switching transients',
                    'V5_BUCK_RAW must remain isolated from USB; ideal independent source used here',
                    '2.4V GPIO high assumed; MOS/zener/diode models generic and not full temperature corners',
                    'Hot stress currents specified at different VDS than circuit; no guaranteed whole-circuit proof',
                    'EN drive with VS absent and stuck MCU HOLD/deadline remain open'],cases=results,
                model_logic_failures=sum(not x['meets_DC_logic_in_this_model'] for x in results))
    (out/'dc-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (out/'ngspice.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for mode in [p[0] for p in profiles]:
        cases=[r for r in results if r['leakage']==mode]
        print(mode, 'cases',len(cases),'failures',sum(not r['meets_DC_logic_in_this_model'] for r in cases))
if __name__=='__main__':main()
