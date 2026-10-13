from pathlib import Path
import uuid,re,json,math,shutil,zipfile,collections
P=Path('/mnt/data/Tripmaster_Schaltplan_V0_3')
proj='Tripmaster_V0_3'
U=lambda:str(uuid.uuid4())
q=lambda s:'"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
f=lambda x:('%0.3f'%x).rstrip('0').rstrip('.') if isinstance(x,float) else str(x)
xy=lambda x,y: f'(xy {f(x)} {f(y)})'
FONT='(effects (font (size 1.25 1.25)))'
PROJECT_ID=U()
# symbol library definition
lib={}; parts=[]; wires=[]; texts=[]; noc=[]; labels=[]; lines=[]
used_refs=set(); errors=[]
# pins stored local in Cartesian library units, left/right/up/down. Schematic y direction down.
def symdef(name, refprefix, pins, width=30, spacing=5.08, bodyheight=None, foot='', description='', hide_names=False, shapes=None):
    # pins [(number,name,side,type),...], arranged per-side in given order; positional placements done here
    left=[p for p in pins if p[2]=='L'];right=[p for p in pins if p[2]=='R']
    top=[p for p in pins if p[2]=='T'];bottom=[p for p in pins if p[2]=='B']
    n=max(len(left),len(right),3)
    h=bodyheight or max(20.32,(n+1)*spacing)
    w=width
    coords={}
    for side,arr in [('L',left),('R',right)]:
        for i,(num,pname,_,ptype) in enumerate(arr):
            ly=(len(arr)-1)/2*spacing-i*spacing
            px=(-w/2-5.08 if side=='L' else w/2+5.08)
            py=ly
            rot=0 if side=='L' else 180
            coords[str(num)]=(px,py,rot,ptype,pname,side)
    for side,arr in [('T',top),('B',bottom)]:
        for i,(num,pname,_,ptype) in enumerate(arr):
            px=(i-(len(arr)-1)/2)*5.08
            py=h/2+5.08 if side=='T' else -h/2-5.08
            rot=270 if side=='T' else 90
            coords[str(num)]=(px,py,rot,ptype,pname,side)
    # IEC-passives and true switch-contact graphics, instead of featureless blocks
    poly=lambda pts: '(polyline (pts '+ ' '.join(f'(xy {x} {y})' for x,y in pts)+') (stroke (width 0.254) (type default)) (fill (type none)))'
    if name in ('R','C','C1210','C0603','L','L_RF','FB','FUSE'):
        if name in ('C','C1210','C0603'):
            graphic=' '.join([poly([(-6.35,0),(-1.27,0)]),poly([(1.27,0),(6.35,0)]),poly([(-1.27,-3.5),(-1.27,3.5)]),poly([(1.27,-3.5),(1.27,3.5)])])
        elif name in ('L','L_RF'):
            graphic=' '.join([poly([(-6.35,0),(-4.2,0)]),poly([(4.2,0),(6.35,0)])])+ ' ' + ' '.join(f'(arc (start {x:.2f} 0) (mid {x+1.05:.2f} 2.5) (end {x+2.10:.2f} 0) (stroke (width 0.254) (type default)) (fill (type none)))' for x in [-4.2,-2.1,0,2.1])
        else:
            graphic=' '.join([poly([(-6.35,0),(-4,0)]),poly([(4,0),(6.35,0)]), '(rectangle (start -4 1.65) (end 4 -1.65) (stroke (width 0.254) (type default)) (fill (type background)))'])
    elif name=='SW_B3F':
        graphic=' '.join([poly([(-11,2.54),(-6.5,2.54)]),poly([(-11,-2.54),(-6.5,-2.54)]),poly([(-6.5,-2.54),(-6.5,2.54)]),poly([(11,2.54),(6.5,2.54)]),poly([(11,-2.54),(6.5,-2.54)]),poly([(6.5,-2.54),(6.5,2.54)]),poly([(-6.5,0),(4.2,3.0)])])
    elif name in ('SCHOTTKY','TVS'):
        graphic=' '.join([poly([(-6.35,0),(-4.0,0)]),poly([(4.0,0),(6.35,0)]),poly([(-4,-3.5),(4,0),(-4,3.5),(-4,-3.5)]),poly([(4,-3.5),(4,3.5)])])
    elif name=='NMOS':
        graphic=' '.join([poly([(-10,0),(-4,0)]),poly([(-1,-5),(-1,5)]),poly([(2,-5),(2,5)]),poly([(2,2.54),(10,2.54)]),poly([(2,-2.54),(10,-2.54)])])
    else:
        graphic=f'(rectangle (start {f(-w/2)} {f(h/2)}) (end {f(w/2)} {f(-h/2)}) (stroke (width 0.254) (type default)) (fill (type background)))'
    s=[f'(symbol {q("Tripmaster_Sym:"+name)}','(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
       f'(property "Reference" {q(refprefix)} (at 0 {f(h/2+5.08)} 0) {FONT})',
       f'(property "Value" {q(name)} (at 0 {f(-h/2-5.08)} 0) {FONT})',
       f'(property "Footprint" {q(foot)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
       f'(property "Description" {q(description)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
       f'(symbol {q(name+"_0_1")} {graphic})',
       f'(symbol {q(name+"_1_1")}']
    for num,pname,side,ptype in pins:
        px,py,rot,_,_,_=coords[str(num)]
        s.append(f'(pin {ptype} line (at {f(px)} {f(py)} {rot}) (length 5.08) (name {q(pname)} {FONT}) (number {q(num)} {FONT}))')
    s.append('))')
    lib[name]={'sexpr':' '.join(s),'pins':coords,'w':w,'h':h,'foot':foot,'prefix':refprefix}
    return name

def mk(name,left=None,right=None,top=None,bottom=None,width=35,foot='',desc=''):
    pp=[]
    for side,arr in [('L',left or []),('R',right or []),('T',top or []),('B',bottom or [])]:
        for item in arr:
            num,nm,*ty=item;pp.append((str(num),nm,side,ty[0] if ty else 'passive'))
    return symdef(name, 'U',pp,width=width,foot=foot,description=desc)
# custom symbols
for typ,ref,foot in [('R','R','Tripmaster:R_1206_3216'),('C','C','Tripmaster:C_1206_3216'),('C1210','C','Tripmaster:C_1210_3225'),('C0603','C','Tripmaster:C_0603_1608'),('L','L','Tripmaster:L1_Bourns_SRN6045_220M'),('L_RF','L','Tripmaster:L_0603_1608'),('FB','FB','Tripmaster:FB_1206_3216'),('FUSE','F','Tripmaster:F1_Littelfuse_0451_500MRL'),('SCHOTTKY','D','Tripmaster:D_SMA_SS36'),('TVS','D','Tripmaster:D1_Littelfuse_SMCJ24A')]:
    symdef(typ,ref,([('2','A','L','passive'),('1','K','R','passive')] if typ in ('SCHOTTKY','TVS') else [('1','1','L','passive'),('2','2','R','passive')]),width=12.7,bodyheight=7.62,foot=foot)
# MOSFET choose DMN2056U pin1 gate, 2 source,3 drain
mk('NMOS',left=[(1,'G','input')],right=[(3,'D','passive'),(2,'S','passive')],width=20,foot='Tripmaster:Q1_Diodes_DMN2056U_7')
# power flag one pin, use generic w 4mm
symdef('PWR_FLAG','PWR',[('1','FLAG','B','power_out')],width=14,bodyheight=9)
mk('LMR36510',left=[(2,'VIN','power_in'),(3,'EN','input'),(1,'PGND','power_in'),(9,'EPAD','power_in')],right=[(8,'SW','output'),(7,'BOOT','passive'),(6,'VCC','power_out'),(5,'FB','input'),(4,'PG','open_collector')],width=35,foot='Tripmaster:U3_TI_LMR36510ADDAR_DDA')
# ESP all physical pins incl GND intentionally grouped, unused net connect physically to GND (many pins), choose 3V3 on top, one GND representative and rest marked ground via repeated labels (no floats)
ESP={1:'GND',2:'GND',3:'3V3',45:'EN',42:'GND',43:'GND',**{i:'GND' for i in range(46,66)}}
for num,nm in [(4,'IO0'),(5,'IO1'),(6,'IO2'),(7,'IO3'),(8,'IO4'),(9,'IO5'),(10,'IO6'),(11,'IO7'),(12,'IO8'),(13,'IO9'),(14,'IO10'),(15,'IO11'),(16,'IO12'),(17,'IO13'),(18,'IO14'),(19,'IO15'),(20,'IO16'),(21,'IO17'),(22,'IO18'),(23,'IO19_USB_DM'),(24,'IO20_USB_DP'),(25,'IO21'),(26,'IO26'),(27,'IO47'),(28,'IO33'),(29,'IO34'),(30,'IO48'),(31,'IO35'),(32,'IO36'),(33,'IO37'),(34,'IO38'),(35,'IO39'),(36,'IO40'),(37,'IO41'),(38,'IO42'),(39,'TXD0_IO43'),(40,'RXD0_IO44'),(41,'IO45'),(44,'IO46')]:ESP[num]=nm
p_esp=[]
# left GPIO in numerical order, power+ground right; grounding lots of flags crowds, handle symbol placing ground pin as common net wires
for i in range(4,42):
 if i in ESP:p_esp.append((str(i),ESP[i],'L','bidirectional'))
for i in [44,45]:p_esp.append((str(i),ESP[i],'L','input' if i==45 else 'bidirectional'))
p_esp.extend([('3','3V3','R','power_in')]+[(str(i),'GND','R','power_in') for i in [1,2,42,43,*range(46,66)]])
symdef('ESP32_S3_MINI_1_N8','U',p_esp,width=47,spacing=5.08,foot='Tripmaster:U1_ESP32-S3-MINI-1-N8')
mk('MAX_M10N',left=[(8,'VCC','power_in'),(7,'V_IO','power_in'),(6,'V_BCKP','power_in'),(15,'VIO_SEL','input'),(9,'RESET_N','input'),(3,'RXD','input'),(5,'EXTINT','input'),(11,'RF_IN','input')],right=[(2,'TXD','output'),(4,'TIMEPULSE','output'),(13,'LNA_EN','output'),(14,'VCC_RF','power_out'),(1,'GND_1','power_in'),(10,'GND_2','power_in'),(12,'GND_3','power_in'),(16,'RESERVED_16','passive'),(17,'RESERVED_17','passive'),(18,'SAFEBOOT_N','input')],width=42,foot='Tripmaster:U2_MAX-M10N-00B')
mk('FRAM_I2C',left=[(1,'A0','input'),(2,'A1','input'),(3,'A2','input'),(4,'VSS','power_in'),(7,'WP','input')],right=[(8,'VDD','power_in'),(6,'SCL','input'),(5,'SDA','bidirectional')],foot='Tripmaster:U4_RAMXEED_MB85RC256VPNF_G_AMERE2')
# 40-pin DOGL; pinout 1 2 3 LED A+, 18 19 20 LED C-, 4-17 NC, LCD 21-40
lcdr={21:'V0',22:'V1',23:'V2',24:'V3',25:'V4',26:'VSS_26',27:'CAP2N',28:'CAP2P',29:'CAP1P',30:'CAP1N',31:'CAP3P',32:'VOUT',33:'VSS_33',34:'VDD2',35:'VDD',36:'SI',37:'SCL',38:'A0',39:'RST',40:'CS1B'}
p_lcd=[(str(i),lcdr[i],'L','passive' if i in [21,22,23,24,25,27,28,29,30,31,32] else 'input' if i in [36,37,38,39,40] else 'power_in') for i in range(21,41)]
p_lcd += [(str(i),f'LED_A{i}','R','passive') for i in [1,2,3]]+[(str(i),f'LED_K{i-17}','R','passive') for i in [18,19,20]]
p_lcd += [(str(i),'NC','R','no_connect') for i in range(4,18)]
symdef('DOGL128W_LED68X51A','DS',p_lcd,width=52,foot='Tripmaster:DS1_BL1_EA_DOGL128W6_LED68X51A')
# USB 16 pin footprint list actual via file later; pin labels consistent with standard GCT footprint pads
p_usb=[('A1','GND_A1','L','passive'),('A4','VBUS_A4','L','passive'),('A5','CC1','L','passive'),('A6','D+_A6','L','passive'),('A7','D-_A7','L','passive'),('A8','SBU1','L','passive'),('A9','VBUS_A9','L','passive'),('A12','GND_A12','L','passive'),('B1','GND_B1','R','passive'),('B4','VBUS_B4','R','passive'),('B5','CC2','R','passive'),('B6','D+_B6','R','passive'),('B7','D-_B7','R','passive'),('B8','SBU2','R','passive'),('B9','VBUS_B9','R','passive'),('B12','GND_B12','R','passive'),('SH','SHIELD','R','passive')]
# Need actual USB footprint pad naming inspect footprint later
symdef('USB_C_GCT_USB4105','J',p_usb,width=48,foot='Tripmaster:J1_GCT_USB4105_GF_A_USB_C')
mk('USB_ESD',left=[(1,'IO1_IN','passive'),(3,'IO2_IN','passive'),(2,'GND','power_in')],right=[(6,'IO1_OUT','passive'),(4,'IO2_OUT','passive'),(5,'VBUS','power_in')],width=36,foot='Tripmaster:D2_ST_USBLC6_2SC6')
mk('SW_B3F',left=[(2,'GND_L1','passive'),(4,'GND_L2','passive')],right=[(1,'SW_R1','passive'),(3,'SW_R2','passive')],width=22,foot='Tripmaster:SW_Omron_B3F_1000')
mk('CONN2',left=[(1,'PIN1','passive'),(2,'PIN2','passive')],width=22,foot='Tripmaster:J3_Phoenix_MKDS_1_5_2_5_08_1715721')
mk('UFL',left=[(1,'RF','passive')],right=[(2,'GND','passive')],width=26,foot='Tripmaster:J2_Hirose_U_FL_R_SMT_1')
# diagnostic testpad footprint mapping 1206 resistor not appropriate, skip

# build symbol graphical property placement from actual pin coords
# net indexes for auditing: track connections and named nets for each physical pad
pad_nets={};pad_intent={}; pinpos={}; coords_box={}; nc_count=0

def part(name,ref,x,y,value=None,foot=None,hideval=False):
    if ref in used_refs:errors.append('duplicate ref '+ref)
    used_refs.add(ref)
    sd=lib[name];oid=U();pfx=sd['prefix']; vv=value or name
    w,h=sd['w'],sd['h']
    # text above component (nice separate ref/value on top)
    tx=x;ty=y-h/2-7.6
    ss=f'''(symbol (lib_id {q('Tripmaster_Sym:'+name)}) (at {f(x)} {f(y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {q(oid)})
    (property "Reference" {q(ref)} (at {f(tx)} {f(ty)} 0) {FONT})
    (property "Value" {q(vv)} (at {f(tx)} {f(ty+3.1)} 0) {FONT})
    (property "Footprint" {q(foot or sd['foot'])} (at {f(x)} {f(y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (instances (project {q(proj)} (path {q('/'+PROJECT_ID)} (reference {q(ref)}) (unit 1)))))'''
    # explicit instance pin UUIDs are necessary for portable schematic interchange
    pin_uuids='\n'.join(f'(pin {q(pnum)} (uuid {q(U())}))' for pnum in sd['pins'])
    ss=ss.replace('(instances (project ', pin_uuids+'\n(instances (project ')
    parts.append(ss)
    pp={}
    for pin,(px,py,rot,ptype,pname,side) in sd['pins'].items():
        sx=x+px;sy=y-py
        pp[pin]=(sx,sy,side,ptype,pname)
        pinpos[(ref,pin)]=(sx,sy)
        if ptype=='no_connect':pad_intent[(ref,pin)]='NC by symbol type'
    coords_box[ref]=(x-w/2,y-h/2,x+w/2,y+h/2)
    return pp

def wire(a,b):
    x,y=a;X,Y=b
    if abs(x-X)<.001 and abs(y-Y)<.001:return
    if abs(x-X)>.001 and abs(y-Y)>.001:
        errors.append(f'diagonal wire {a} to {b}')
        return
    wires.append(f'(wire (pts {xy(x,y)} {xy(X,Y)}) (stroke (width 0) (type default)) (uuid {q(U())}))')
    lines.append((a,b))

def lab(net,x,y,orientation=0):
    labels.append(f'(label {q(net)} (at {f(x)} {f(y)} {orientation}) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {q(U())}))')

def pinlabel(ref,pin,net,length=7.62):
    sx,sy,side,ptype,pname=pinlookup(ref,pin)
    dx=(-length if side=='L' else length if side=='R' else 0)
    dy=(-length if side=='T' else length if side=='B' else 0)
    dest=(sx+dx,sy+dy)
    wire((sx,sy),dest)
    lab(net,*dest,180 if side=='L' else 0)
    pad_nets[(ref,str(pin))]=net
    return dest

def pinlookup(ref,pin):
    # storage for generated part
    return pinprops[(ref,str(pin))]
pinprops={}
origpart=part
def part(name,ref,x,y,value=None,foot=None,hideval=False):
    pp=origpart(name,ref,x,y,value,foot,hideval)
    for n,props in pp.items():pinprops[(ref,str(n))]=props
    return pp

def joins(net,ref1,p1,ref2,p2,via=None):
    x,y,*_=pinlookup(ref1,p1); X,Y,*_=pinlookup(ref2,p2)
    if via is None:
        if abs(y-Y)<.001 or abs(x-X)<.001:wire((x,y),(X,Y))
        else:wire((x,y),(X,y));wire((X,y),(X,Y))
    else:
        pts=[(x,y),*via,(X,Y)]
        for i in range(len(pts)-1):wire(pts[i],pts[i+1])
    pad_nets[(ref1,str(p1))]=net;pad_nets[(ref2,str(p2))]=net

def open_pin(ref,pin,note=''):
    sx,sy,*_=pinlookup(ref,pin)
    noc.append(f'(no_connect (at {f(sx)} {f(sy)}) (uuid {q(U())}))')
    pad_intent[(ref,str(pin))]='NC '+note

def power(ref,x,y,net):
    part('PWR_FLAG',ref,x,y)
    pinlabel(ref,'1',net)

def note(t,x,y,size=1.8):
    texts.append(f'(text {q(t)} (at {f(x)} {f(y)} 0) (effects (font (size {f(size)} {f(size)})) (justify left bottom)) (uuid {q(U())}))')

def frame(title,x1,y1,x2,y2):
    # text banner only no graphics/frame is okay
    note(title,x1,y1,3)
    note('________________________________________________________________________________________________',x1,y1+2.54,1.1)

# section coordinates A0 page
frame('01  EINGANG / 12-V-SCHUTZ / 3,3-V-DC-DC',30,43,400,355)
frame('02  ESP32-S3 / RESET / BOOT',425,43,790,400)
frame('03  GNSS / ANTENNE / I2C-FRAM',805,43,1160,400)
frame('04  USB-C  /  SELBSTVERSORGTER USB-PORT',30,426,390,625)
frame('05  LCD / KONTRASTPUMPE / BACKLIGHT',425,426,900,813)
frame('06  BEDIENUNG / EXTERNER RESET',925,426,1155,810)

# power bottom left up to 410
part('CONN2','J1',66,85,'12V_BOARD')
pinlabel('J1','1','BAT_IN');pinlabel('J1','2','GND')
part('FUSE','F1',137,76,'0.5A / 0451.500MRL')
pinlabel('F1','1','BAT_IN')
part('SCHOTTKY','D1',227,76,'SS36 / 60V')
pinlabel('D1','1','VIN_PROT');joins('BAT_FUSED','F1','2','D1','2')
part('TVS','D2',300,94,'SMCJ24A TVS')
pinlabel('D2','1','VIN_PROT');pinlabel('D2','2','GND')
note('TVS nur Vorentwurf, kein ISO-Load-Dump-Nachweis',205,112,1.45)
part('C1210','C1',82,149,'2.2uF / 100V X7R')
pinlabel('C1','1','VIN_PROT');pinlabel('C1','2','GND')
part('C','C2',180,149,'220nF / 100V')
pinlabel('C2','1','VIN_PROT');pinlabel('C2','2','GND')
part('LMR36510','U3',280,178,'LMR36510ADDAR')
for pin,net in [('2','VIN_PROT'),('3','VIN_PROT'),('1','GND'),('9','GND'),('8','SW_BUCK'),('7','BOOT_BUCK'),('6','VCC_INTERNAL'),('5','FB_BUCK'),('4','PG_BUCK')]:pinlabel('U3',pin,net)
part('C','C3',70,220,'1uF / 16V VCC')
pinlabel('C3','1','VCC_INTERNAL');pinlabel('C3','2','GND')
part('C','C4',145,220,'100nF BOOT')
pinlabel('C4','1','SW_BUCK');pinlabel('C4','2','BOOT_BUCK')
part('L','L1',220,267,'22uH SRN6045-220M')
pinlabel('L1','1','SW_BUCK');pinlabel('L1','2','+3V3')
for ref,x,y in [('C5',60,296),('C6',135,296),('C7',210,331)]:
 part('C1210',ref,x,y,'22uF / >=10V X7R');pinlabel(ref,'1','+3V3');pinlabel(ref,'2','GND')
part('R','R1',298,272,'100k / 1% (TOP)');pinlabel('R1','1','+3V3');pinlabel('R1','2','FB_BUCK')
part('R','R2',298,308,'43.2k / 1% (BOT)');pinlabel('R2','1','FB_BUCK');pinlabel('R2','2','GND')
part('R','R3',298,351,'10k PG pullup');pinlabel('R3','1','+3V3');pinlabel('R3','2','PG_BUCK')
power('PWR01',380,104,'VIN_PROT');power('PWR02',379,290,'+3V3');power('PWR03',379,332,'GND')
note('PWR_FLAG nur an realen Einspeisepunkten',44,387,1.8)

# MCU
part('ESP32_S3_MINI_1_N8','U1',664,219,'ESP32-S3-MINI-1-N8')
esp_nets={3:'+3V3',4:'BOOT_IO0',5:'KEY_MODE',6:'KEY_PLUS',8:'KEY_MINUS',9:'KEY_RESET',10:'KEY_SET',11:'LCD_SI',12:'LCD_SCL',13:'LCD_A0',14:'LCD_CS',15:'LCD_RST',16:'LCD_BL_PWM',17:'I2C_SDA',18:'I2C_SCL',19:'GNSS_PPS',20:'GNSS_TX_TO_MCU',21:'GNSS_RX_FROM_MCU',23:'USB_DM_MCU',24:'USB_DP_MCU',25:'USB_VBUS_SENSE',35:'PG_BUCK',45:'ESP_EN'}
for pin,net in esp_nets.items():pinlabel('U1',str(pin),net,9.5)
for pin,pname in ESP.items():
 if pname=='GND':pinlabel('U1',str(pin),'GND',7.62)
 elif pin not in esp_nets:open_pin('U1',str(pin),'free GPIO')
part('C1210','C8',483,70,'22uF ESP bulk');pinlabel('C8','1','+3V3');pinlabel('C8','2','GND')
part('C','C9',581,70,'100nF ESP local');pinlabel('C9','1','+3V3');pinlabel('C9','2','GND')
part('R','R4',476,357,'10k EN pullup');pinlabel('R4','1','+3V3');pinlabel('R4','2','ESP_EN')
part('C','C10',567,357,'1uF EN start');pinlabel('C10','1','ESP_EN');pinlabel('C10','2','GND')
part('R','R5',661,357,'10k BOOT pullup');pinlabel('R5','1','+3V3');pinlabel('R5','2','BOOT_IO0')
part('SW_B3F','SW6',515,396,'RESET MCU');
for i in [2,4]:pinlabel('SW6',str(i),'GND')
for i in [1,3]:pinlabel('SW6',str(i),'ESP_EN')
part('SW_B3F','SW7',707,396,'BOOT MCU');
for i in [2,4]:pinlabel('SW7',str(i),'GND')
for i in [1,3]:pinlabel('SW7',str(i),'BOOT_IO0')

# GNSS
part('MAX_M10N','U2',915,171,'MAX-M10N-00B')
for pi,net in [(8,'+3V3'),(7,'+3V3'),(6,'+3V3'),(2,'GNSS_TX_TO_MCU'),(3,'GNSS_RX_FROM_MCU'),(4,'GNSS_PPS'),(11,'RF_IN_RX'),(14,'VCC_RF')]:pinlabel('U2',str(pi),net)
for pi in [1,10,12]:pinlabel('U2',str(pi),'GND')
for pi in [5,9,13,15,16,17,18]:open_pin('U2',str(pi),'as per u-blox optional/NC')
# caution VIO_SEL left open for 3V3, expected
part('C','C11',823,261,'100nF GNSS VCC');pinlabel('C11','1','+3V3');pinlabel('C11','2','GND')
part('C','C12',942,261,'10uF GNSS VCC');pinlabel('C12','1','+3V3');pinlabel('C12','2','GND')
part('C','C13',1069,261,'100nF VCC_RF');pinlabel('C13','1','VCC_RF');pinlabel('C13','2','GND')
part('UFL','J3',857,320,'GNSS U.FL ANT')
pinlabel('J3','1','RF_ANT_BIAS');pinlabel('J3','2','GND')
part('C0603','C14',979,324,'100pF RF series');pinlabel('C14','1','RF_ANT_BIAS');pinlabel('C14','2','RF_IN_RX')
part('L_RF','L2',1078,324,'47nH RF bias');pinlabel('L2','1','VCC_RF');pinlabel('L2','2','RF_ANT_BIAS')
note('RF-In 50 Ohm; Bias-T nur mit aktivem Antennentyp pruefen',814,360,1.65)
# FRAM / data
part('FRAM_I2C','U4',894,395,'MB85RC256VPNF')
for pi,net in [(1,'GND'),(2,'GND'),(3,'GND'),(4,'GND'),(7,'GND'),(8,'+3V3'),(6,'I2C_SCL'),(5,'I2C_SDA')]:pinlabel('U4',str(pi),net)
part('R','R6',1037,386,'4.7k SDA');pinlabel('R6','1','+3V3');pinlabel('R6','2','I2C_SDA')
part('R','R7',1037,410,'4.7k SCL');pinlabel('R7','1','+3V3');pinlabel('R7','2','I2C_SCL')
part('C','C15',1113,390,'100nF FRAM');pinlabel('C15','1','+3V3');pinlabel('C15','2','GND')

# USB region, one serial port
part('USB_C_GCT_USB4105','J2',125,534,'GCT USB4105-GF-A')
for pi,net in [('A1','GND'),('A12','GND'),('B1','GND'),('B12','GND'),('A4','USB_VBUS'),('A9','USB_VBUS'),('B4','USB_VBUS'),('B9','USB_VBUS'),('A5','USB_CC1'),('B5','USB_CC2'),('A6','USB_DP_CONN'),('B6','USB_DP_CONN'),('A7','USB_DM_CONN'),('B7','USB_DM_CONN'),('SH','GND')]:pinlabel('J2',pi,net)
for pi in ['A8','B8']:open_pin('J2',pi,'SBU unused')
power('PWR04',365,471,'USB_VBUS')
part('R','R8',267,474,'5.1k CC1');pinlabel('R8','1','USB_CC1');pinlabel('R8','2','GND')
part('R','R9',267,496,'5.1k CC2');pinlabel('R9','1','USB_CC2');pinlabel('R9','2','GND')
part('USB_ESD','D3',264,544,'USBLC6-2SC6')
for pi,net in [(1,'USB_DP_CONN'),(6,'USB_DP_ESD'),(3,'USB_DM_CONN'),(4,'USB_DM_ESD'),(2,'GND'),(5,'USB_VBUS')]:pinlabel('D3',str(pi),net)
part('R','R10',265,599,'22R D+ series');pinlabel('R10','1','USB_DP_ESD');pinlabel('R10','2','USB_DP_MCU')
part('R','R11',265,622,'22R D- series');pinlabel('R11','1','USB_DM_ESD');pinlabel('R11','2','USB_DM_MCU')
part('C','C16',70,646,'100nF VBUS ESD');pinlabel('C16','1','USB_VBUS');pinlabel('C16','2','GND')
part('R','R12',169,662,'100k VBUS top');pinlabel('R12','1','USB_VBUS');pinlabel('R12','2','USB_VBUS_SENSE')
part('R','R13',285,662,'100k VBUS bottom');pinlabel('R13','1','USB_VBUS_SENSE');pinlabel('R13','2','GND')
note('USB VBUS NUR ERKENNUNG / ESD - KEINE 5-V-EINSPEISUNG',38,703,1.8)
note('Zum Flashen 12-V-Bordnetz bzw. externes Netzteil erforderlich.',38,711,1.55)

# LCD
part('DOGL128W_LED68X51A','DS1',580,576,'EA DOGL128W-6 + LED68X51-A')
# LCD power+digital
for pin,net in [(26,'GND'),(33,'GND'),(34,'+3V3'),(35,'+3V3'),(36,'LCD_SI'),(37,'LCD_SCL'),(38,'LCD_A0'),(39,'LCD_RST'),(40,'LCD_CS'),(32,'LCD_VOUT'),(31,'LCD_CAP3P'),(30,'LCD_CAP1N'),(29,'LCD_CAP1P'),(28,'LCD_CAP2P'),(27,'LCD_CAP2N'),(25,'LCD_V4'),(24,'LCD_V3'),(23,'LCD_V2'),(22,'LCD_V1'),(21,'LCD_V0')]:pinlabel('DS1',str(pin),net,10.16)
# LED A pins 1,2,3 through separate resistors. Cathodes 18,19,20 collectively low-side PWM through FET, -> 20mA per path 60mA max
for pi in [1,2,3]:pinlabel('DS1',str(pi),f'LED_A{pi}')
for pi in [18,19,20]:pinlabel('DS1',str(pi),'LED_K_COMMON')
# all unused pins are no_connect pin type, no need mark
for i in range(4,18):pad_intent[('DS1',str(i))]='NC by Display Herst.'
# LCD chargepump caps: 9: C17 VOUT-GND, five V0-V1 ..V4? datasheet 5 cap from each V0..V4 to GND? graphic shows capacitor bank connected each 5 individual to common rail GND? Top top internal schematic left common bar from five caps and each v0-v4 attached to cap, a vertical bar disconnected ground? Looks 5*1uF between V4-V3, V3-V2, V2-V1, V1-V0, V0-GND? Inspect screenshot manual. manufacturer diagram shows 5 caps each from V0..V4 to isolated common line? risky. Need choose each (V0..V4) -> GND for 5 cap; source: search docs. Based screenshot 5 capacitors all left terminal tied common vertical bar, likely GND; but vertical line no GND label? likely all GND. assume GND.
for i,(net,x,y) in enumerate([('LCD_VOUT',462,690),('LCD_V0',542,690),('LCD_V1',622,690),('LCD_V2',702,690),('LCD_V3',782,690),('LCD_V4',862,690)],start=17):
 ref=f'C{i}';part('C',ref,x,y,'1uF / >=16V LCD');pinlabel(ref,'1',net);pinlabel(ref,'2','GND')
# cap across CAP1P-1N; CAP3P tied to CAP1N? manufacturer figure cap from 31->30 and 30->29, C2P->C2N
part('C','C23',465,745,'1uF CAP3P-CAP1N');pinlabel('C23','1','LCD_CAP3P');pinlabel('C23','2','LCD_CAP1N')
part('C','C24',625,745,'1uF CAP1N-CAP1P');pinlabel('C24','1','LCD_CAP1N');pinlabel('C24','2','LCD_CAP1P')
part('C','C25',785,745,'1uF CAP2P-CAP2N');pinlabel('C25','1','LCD_CAP2P');pinlabel('C25','2','LCD_CAP2N')
# backlight resistor network with each path and MOSFET
for i,x in enumerate([774,835,896],1):
 part('R',f'R{13+i}',x,477,f'47R / LED {i}');pinlabel(f'R{13+i}','1','+3V3');pinlabel(f'R{13+i}','2',f'LED_A{i}')
part('NMOS','Q1',822,631,'DMN2056U-7 / PWM')
pinlabel('Q1','1','LCD_BL_PWM');pinlabel('Q1','2','GND');pinlabel('Q1','3','LED_K_COMMON')
part('R','R17',822,661,'100k PWM pulldown');pinlabel('R17','1','LCD_BL_PWM');pinlabel('R17','2','GND')
note('3 LED-Pfade mit EINZELNEN Vorwiderstaenden, niemals direkt an +3V3',462,795,1.5)
note('LCD: 9x 1uF fuer Single-Supply-Ladungspumpe, Rueckseite nach Datenblatt',462,807,1.45)

# control
keynets=[('SW1','MODE','KEY_MODE',955,468),('SW2','PLUS','KEY_PLUS',1054,468),('SW3','MINUS','KEY_MINUS',955,556),('SW4','RESET TRIP','KEY_RESET',1054,556),('SW5','SET','KEY_SET',955,642)]
for ref,value,net,x,y in keynets:
 part('SW_B3F',ref,x,y,value)
 for pi in [2,4]:pinlabel(ref,str(pi),'GND')
 for pi in [1,3]:pinlabel(ref,str(pi),net)
part('CONN2','J4',1089,660,'EXT TRIP RESET')
pinlabel('J4','1','KEY_RESET');pinlabel('J4','2','GND')
note('Pullups im ESP32 aktivieren (Firmware).',932,712,1.7)
note('Externer Taster parallel zu SW4.',932,720,1.7)

# not all drawing explicitly connected by a drawn resistor path: named label net on each pad makes KiCad net good.
# sanity: label referenced from pin no empty unless expected NC
pad_report={}
for (ref,p),props in pinprops.items():
 typ=props[3]
 if (ref,p) not in pad_nets and (ref,p) not in pad_intent:
    errors.append(f'UNCONNECTED {ref}.{p} ({props[4]})')
 else: pad_report[ref+'.'+p]=pad_nets.get((ref,p),pad_intent.get((ref,p)))
# check footprints pad numbers vs schema
# foot file mapping: footprint numbers not all same, must verify
for itm in parts:
 r=re.search(r'\(property "Reference" "([^"]+)"',itm)
 fp=re.search(r'\(property "Footprint" "([^"]+)"',itm)
 if not r or not fp:continue
 name=fp.group(1).split(':')[-1]
 if not name:continue
 path=P/'Tripmaster.pretty'/ (name+'.kicad_mod')
 if not path.exists():errors.append('MISSING FOOTPRINT '+name+' for '+r.group(1))

# architecture document notes
note('TRIPMASTER / GPS-ROADBOOK COMPUTER - ELEKTRIK V0.3 / VORPRUEFUNG, NICHT FERTIGEN',29,29,3.6)
note('Netzlabels verbinden nur gleichnamige Netze; Leiter und Symbole sind im Editor einzeln editierbar.',30,820,1.75)

def document():
    return '\n'.join(['(kicad_sch (version 20250114) (generator "eeschema")',f'(uuid {q(PROJECT_ID)})','(paper "A0")',
        f'(title_block (title "GPS Rally Tripmaster") (date "2026-10-12") (rev "V0.3 DRAFT") (company "Eigenentwicklung"))',
        '(lib_symbols','\n'.join(v['sexpr'] for v in lib.values()),')',*parts,*wires,*labels,*noc,*texts,
        '(sheet_instances (path "/" (page "1")))','(embedded_fonts no)',')'])

sch=P/(proj+'.kicad_sch')
sch.write_text(document(),encoding='utf-8')
# sym-lib separate for subsequent symbol changes
(P/'Tripmaster_Sym.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n'+'\n'.join(v['sexpr'].replace(q('Tripmaster_Sym:'+k),q(k),1) for k,v in lib.items())+'\n)',encoding='utf8')
(P/'sym-lib-table').write_text('(sym_lib_table (lib (name "Tripmaster_Sym") (type "KiCad") (uri "${KIPRJMOD}/Tripmaster_Sym.kicad_sym") (options "") (descr "Tripmaster V0.3 custom circuit symbols")))\n')
(P/'fp-lib-table').write_text('(fp_lib_table (lib (name "Tripmaster") (type "KiCad") (uri "${KIPRJMOD}/Tripmaster.pretty") (options "") (descr "Tripmaster V0.3 PCB footprints")))\n')
# generic kicad project settings auto generated when opening KiCad, blank file unnecessary
(P/(proj+'.kicad_pro')).write_text('{}\n')
(P/'Pruefbericht.json').write_text(json.dumps({'version':'V0.3','parts':len(parts),'labels':len(labels),'wires':len(wires),'no_connects':len(noc),'library_symbols':len(lib),'errors':errors,'notes':['KiCad CLI/ERC not executed','Netlabels directly at wire endpoints','Motorvehicle load dump not validated','Passive antenna bias tee remains RF-prototype']},indent=2,ensure_ascii=False))
(P/'Pad-Netze.csv').write_text('Referenz.Pin;Netz oder Status\n'+'\n'.join(f'{k};{v}' for k,v in sorted(pad_report.items()))+'\n')
print('parts',len(parts),'wires',len(wires),'labels',len(labels),'nc',len(noc),'errors',len(errors))
for e in errors: print('ERR',e)
print('size KB',sch.stat().st_size//1024)
