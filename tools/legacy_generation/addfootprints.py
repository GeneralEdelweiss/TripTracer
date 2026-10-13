from pathlib import Path
import cadquery as cq
p=Path(__file__).parent;f=p/'Tripmaster.pretty';sh=p/'Tripmaster_3dmodels.3dshapes'
def foot(name,w,h,pitch,padw,padh,modelname,descr):
    s=f'''(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu")
(descr "{descr}; PROTOTYP - Maßangaben/Padkonturen mit Herstellerdatenblatt abgleichen")
(tags "Tripmaster") (attr smd)
(fp_text reference "REF**" (at 0 {-h/2-1.9:.3f}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.13))))
(fp_text value "{name}" (at 0 {h/2+1.9:.3f}) (layer "F.Fab") (effects (font (size 0.7 0.7) (thickness 0.1))))
(fp_rect (start {-w/2:.3f} {-h/2:.3f}) (end {w/2:.3f} {h/2:.3f}) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))
(fp_rect (start {-max(w/2,pitch/2+padw/2)-0.3:.3f} {-max(h/2,padh/2)-0.3:.3f}) (end {max(w/2,pitch/2+padw/2)+0.3:.3f} {max(h/2,padh/2)+0.3:.3f}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
(pad "1" smd rect (at {-pitch/2:.3f} 0) (size {padw:.3f} {padh:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))
(pad "2" smd rect (at {pitch/2:.3f} 0) (size {padw:.3f} {padh:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))
(model "${{KIPRJMOD}}/Tripmaster_3dmodels.3dshapes/{modelname}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))
)'''
    (f/(name+'.kicad_mod')).write_text(s)
    body=cq.Workplane('XY').box(w,h,0.85,centered=(True,True,False)).translate((0,0,0.08))
    cap1=cq.Workplane('XY').box(padw,padh,0.15,centered=(True,True,False)).translate((-pitch/2,0,0))
    cap2=cq.Workplane('XY').box(padw,padh,0.15,centered=(True,True,False)).translate((pitch/2,0,0))
    cq.exporters.export(body.union(cap1).union(cap2),str(sh/(modelname+'.step')))
foot('C_1210_3225',3.2,2.5,2.6,1.2,2.75,'C_1210_3225','MLCC 1210 imperial, 3.2x2.5mm nominal')
foot('C_0603_1608',1.6,0.8,1.5,0.85,0.9,'C_0603_1608','MLCC 0603 imperial, 1.6x0.8mm nominal')
foot('L_0603_1608',1.6,0.8,1.5,0.85,0.9,'L_0603_1608','RF choke 0603 imperial, 1.6x0.8mm nominal')
foot('D_SMA_SS36',4.4,2.6,4.8,2.1,2.0,'D_SMA_SS36','SMA DO-214AC diode pad 1 CATHODE 2 ANODE')
s= (f/'L1_Bourns_SRN6045_100M.kicad_mod').read_text().replace('L1_Bourns_SRN6045_100M','L1_Bourns_SRN6045_220M').replace('10uH 2.5A','22uH; current rating verify').replace('Bourns_SRN6045_100M.step','Bourns_SRN6045_100M.step')
(f/'L1_Bourns_SRN6045_220M.kicad_mod').write_text(s)
print('additional footprints ready:',len(list(f.glob('*.kicad_mod'))))
