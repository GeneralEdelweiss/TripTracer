from pathlib import Path
import runpy,re,html
import cairosvg
from PIL import Image
P=Path(__file__).parent
z=runpy.run_path(str(P/'build_schematic.py'))
# SVG technical overview derived from actual schematic component/pin coordinates
styles='''<style>text{font-family:DejaVu Sans,Arial,sans-serif}.tiny{font-size:2.45px;fill:#43506b}.net{font-size:2.25px;fill:#2e5684}.part{font-size:3.1px;font-weight:700;fill:#124963}.value{font-size:2.15px;fill:#40586f}.section{font-size:4.0px;font-weight:bold;fill:#193d65}.wire{stroke:#247353;stroke-width:.33;fill:none}.comp{stroke:#1f5391;stroke-width:.34;fill:#eff6fb}</style>'''
A=['<svg xmlns="http://www.w3.org/2000/svg" width="2800" height="1980" viewBox="0 0 1189 841">','<rect width="1189" height="841" fill="#fffefa"/>',styles]
sections=[(25,47,399,406),(418,47,795,418),(797,47,1165,418),(25,430,406,824),(415,430,917,824),(920,430,1165,824)]
for i,(x1,y1,x2,y2) in enumerate(sections):
 A.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="2" fill="{("#f5f9ff" if i%2==0 else "#f8fbfc")}" stroke="#c6d7e5" stroke-width=".38"/>')
for (a,b) in z['lines']:
 A.append(f'<line class="wire" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>')
# shapes components
for chunk in z['parts']:
 rr=re.search(r'\(property "Reference" "(.*?)"',chunk); val=re.search(r'\(property "Value" "(.*?)"',chunk)
 if not rr:continue
 ref=rr.group(1);va=val.group(1) if val else ''
 x1,y1,x2,y2=z['coords_box'][ref]
 A.append(f'<rect class="comp" x="{x1:.2f}" y="{y1:.2f}" width="{x2-x1:.2f}" height="{y2-y1:.2f}" rx=".7"/>')
 A.append(f'<text class="part" x="{x1}" y="{y1-6.2}">{html.escape(ref)}</text>')
 A.append(f'<text class="value" x="{x1}" y="{y1-3.0}">{html.escape(va[:28])}</text>')
 for (r,num),(x,y,side,ptype,name) in z['pinprops'].items():
  if r!=ref:continue
  if ptype=='no_connect':continue
  if side=='L':tx,anchor=x+3.2,'start'
  elif side=='R':tx,anchor=x-3.2,'end'
  else:tx,anchor=x,'middle'
  if side in ('L','R'):
   A.append(f'<text class="tiny" x="{tx:.2f}" y="{y-.68:.2f}" text-anchor="{anchor}">{html.escape(name[:20])} [{html.escape(num)}]</text>')
for snippet in z['labels']:
 m=re.search(r'\(label "(.*?)" \(at ([0-9.]+) ([0-9.]+) (0|180)\)',snippet)
 if not m:continue
 net,x,y,orientation=m.groups();x=float(x);y=float(y)
 anchor='end' if orientation=='180' else 'start'
 A.append(f'<text class="net" x="{x}" y="{y-0.8}" text-anchor="{anchor}">{html.escape(net)}</text>')
for snippet in z['texts']:
 m=re.search(r'\(text "(.*?)" \(at ([0-9.]+) ([0-9.]+) 0\).*?\(font \(size ([0-9.]+)',snippet)
 if not m:continue
 v,x,y,sz=m.groups();sz=float(sz)
 A.append(f'<text class="{("section" if sz>=2.5 else "value")}" x="{x}" y="{y}" font-size="{max(2.5,sz*1.2)}">{html.escape(v.replace("\\n"," "))}</text>')
A.append('</svg>')
(P/'Tripmaster_V0_3_Schaltplan_Vorschau.svg').write_text('\n'.join(A))
cairosvg.svg2png(bytestring='\n'.join(A).encode(),write_to=str(P/'Tripmaster_V0_3_Gesamtansicht.png'),output_width=2800,output_height=1980)
im=Image.open(P/'Tripmaster_V0_3_Gesamtansicht.png')
for title,(x1,y1,x2,y2) in {
 '01_Versorgung':(25,40,410,405),'02_ESP32':(420,40,798,418),'03_GNSS_FRAM':(800,40,1165,418),
 '04_USB':(25,424,410,825),'05_Display':(415,423,923,828),'06_Tasten':(919,423,1165,825)
}.items():
 k=2800/1189
 im.crop(tuple(round(v*k) for v in (x1,y1,x2,y2))).save(P/(title+'.png'))
print('preview generated')
