from pathlib import Path
import re,runpy,json,collections
p=Path(__file__).parent
z=runpy.run_path(str(p/'build_schematic.py'))
# balanced S expressions, correct escapes even within quoted strings
def balanced(s):
 depth=0;quote=False;esc=False
 for j,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  else:
   if c=='"':quote=True
   elif c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth<0:raise AssertionError('early close at '+str(j))
 assert depth==0 and not quote,(depth,quote)
for fn in [p/'Tripmaster_V0_3.kicad_sch',p/'Tripmaster_Sym.kicad_sym',p/'fp-lib-table',p/'sym-lib-table']:
 balanced(fn.read_text())
issues=[];stats=[]
for ref,d in collections.defaultdict(list,{r:[] for r in z['used_refs']}).items():pass
# map each part to library, compare symbol pins with footprint and 3D model exists
for chunk in z['parts']:
 rr=re.search(r'\(property "Reference" "(.*?)"',chunk); fp=re.search(r'\(property "Footprint" "(.*?)"',chunk)
 libid=re.search(r'\(lib_id "Tripmaster_Sym:(.*?)"',chunk)
 if not rr or not libid:issues.append('missing ref/library ID');continue
 ref=rr.group(1); typ=libid.group(1)
 exp=set(z['lib'][typ]['pins'])
 if not fp or not fp.group(1):continue
 fname=fp.group(1).split(':')[-1]
 foot=p/'Tripmaster.pretty'/(fname+'.kicad_mod')
 if not foot.exists():issues.append(f'{ref} missing footprint {fname}');continue
 dat=foot.read_text();balanced(dat)
 got=set(re.findall(r'\(pad "([^\"]+)"',dat))
 got.discard('')
 if got!=exp:issues.append(f'{ref}: symbol vs pads extra {got-exp} missing {exp-got}')
 for model in re.findall(r'\(model "([^\"]+\.step)"',dat):
  mp=p/model.replace('${KIPRJMOD}/','')
  if not mp.exists():issues.append(f'{ref}: STEP missing {mp}')
 stats.append((ref,typ,len(exp)))
# no short via switch: common pairs 2+4 and 1+3
for i in list(range(1,8)):
 sw=f'SW{i}'
 if sw not in z['used_refs']:continue
 m=z['pad_nets']
 assert m[(sw,'2')]==m[(sw,'4')] and m[(sw,'1')]==m[(sw,'3')]
 assert m[(sw,'2')]!=m[(sw,'1')]
# Polarities
assert z['pad_nets'][('D1','2')]=='BAT_FUSED' and z['pad_nets'][('D1','1')]=='VIN_PROT'
assert z['pad_nets'][('D2','1')]=='VIN_PROT' and z['pad_nets'][('D2','2')]=='GND'
assert not issues,issues
out={'status':'structurally_passed_not_ERC','component_count':len(z['parts']),'footprint_count':len(list((p/'Tripmaster.pretty').glob('*.kicad_mod'))),'named_connections':len(z['pad_nets']),'no_connect_marks':len(z['noc']),'pin_footprint_checks':len(stats),'errors':issues,'kicad_ERC':'not_executed','kicad_DRC':'not_executed','note':'This test is a structural file/pad check, not a KiCad electrical rule check.'}
(p/'Validierung.json').write_text(json.dumps(out,indent=2))
print(out)
