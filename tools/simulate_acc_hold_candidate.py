"""Exploratory ACC/HOLD DC checks. Generic MOS models, NOT manufacturer validation.
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
    profiles=[('nominal',0,0,'4.7meg',1.7),
              ('hot_stress',60e-6,5e-6,'4.7meg',1.7),
              ('bss131_nominal',0,0,'680k',1.8),
              ('bss131_stress',5e-6,5e-6,'680k',1.8)]
    for profile,vin,acc,hold,qual in itertools.product(profiles,[6,9,30],[0,1],[0,1],[0,1]):
        # Stress currents reflect source-specific maxima, not a validated combined
        # temperature model: onsemi BSS123 60uA/125C/100V; BSS138 5uA/125C/50V.
        leakage,lk,ll,ren,kill_vto=profile
        net=[f'ACC HOLD candidate {leakage} {vin}V {acc}{hold}{qual}',
            f'Vbat vs 0 {vin}',f'Vacc acc 0 {vin*acc}',
            f'Vhold hold 0 {3.3*hold}',f'Vqual raw5 0 {5*qual}',
            f'Ren vs en {ren}','Cen en 0 10n','Rkill vs kill 330k','Ckill kill 0 1n',
            'Dkill 0 kill DZ','Mkill en kill 0 0 MKILL',
            'Racc1 acc accmid 220k','Racc2 accmid ag 220k','Raccpd ag 0 1meg',
            'Dacc 0 ag DZ','Macc kill ag 0 0 MLOW',
            'Rhold hold hg 10k','Rholdpd hg 0 100k','Mhold kill hg mid mid MLOW',
            'Rqual raw5 qg 33k','Rqualpd qg 0 100k','Mqual mid qg 0 0 MLOW',
            f'.model MKILL NMOS(VTO={kill_vto} KP=0.1 RD=5 RS=5)',
            '.model MLOW NMOS(VTO=1.3 KP=0.1 RD=3 RS=3)',
            '.model DZ D(IS=1e-14 BV=4.7 IBV=10u)',
            f'Bkillleak en 0 I={lk}*min(1,max(v(en)/0.1,0))',
            f'Baccleak kill 0 I={ll}*min(1,max(v(kill)/0.1,0))',
            f'Bholdleak kill mid I={ll}*min(1,max(v(kill,mid)/0.1,0))',
            f'Bqualleak mid 0 I={ll}*min(1,max(v(mid)/0.1,0))',
            'Benleak en 0 I=200n*min(1,max(v(en)/0.1,0))',
            '.op','.end']
        command('destroy all')
        start=len(lines)
        encoded=[s.encode() for s in net]+[None]
        lib.ngSpice_Circ((C.c_char_p*len(encoded))(*encoded))
        command('run')
        if any('error' in s.lower() for s in lines[start:]):
            raise RuntimeError('ngspice reported error: '+str(lines[start:]))
        en=value('v(en)');kill=value('v(kill)')
        expected=bool(acc or (hold and qual))
        # TI EN rising maximum 1.05V; falling minimum 0.41V.
        consistent=en>1.05 if expected else en<0.41
        results.append(dict(leakage=leakage,vin_V=vin,acc=acc,hold=hold,
                            vehicle_5V_present=qual,expected_enable=expected,
                            en_V=en,kill_gate_V=kill,enable_pullup=ren,bias_input_uA=-value('i(vbat)')*1e6,
                            meets_DC_logic_in_this_model=consistent))
        if leakage=='nominal' and vin==6 and (acc,hold,qual)==(0,1,0):
            (out/'usb-only-hold.cir').write_text('\n'.join(net)+'\n',encoding='utf-8')
    report=dict(status='Exploratory generic-model DC evidence, not a circuit release',
                model_limitations=['No TI controller or buck model',
                    'No transients, reverse/surge, temperature-dependent MOS model or real zener knee',
                    'BSS131 stress uses 5uA at 150C/240V for kill; other FET stress remains 125C, not a common temperature guarantee',
                    'Fixed hot leakage stress is conservative at low VDS but not a full guaranteed corner',
                    'MCU GPIO high assumed 3.3V, vehicle 5V assumed ideal; startup not validated'],
                cases=results,
                model_logic_failures=sum(not r['meets_DC_logic_in_this_model'] for r in results))
    (out/'dc-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (out/'ngspice.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"{len(results)} DC cases; {report['model_logic_failures']} failed logic criteria. No release.")
    for mode in [p[0] for p in profiles]:
        cases=[r for r in results if r['leakage']==mode]
        print(mode, 'failures',sum(not r['meets_DC_logic_in_this_model'] for r in cases))
if __name__=='__main__':main()
