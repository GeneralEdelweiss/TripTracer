# VS_READY Supervisor U302 – konkrete Bauteilauswahl und Schaltplan-Zwischenstand (2026-10-15)

**Ausgewähltes, echt beschaffbares Bauteil:** Texas Instruments `TPS3760A012DYYRQ1`, AEC-Q100 Automotive Grade 1, verstellbare Unterspannungsüberwachung **0,8V Referenz, 2% interne Hysterese, RESET aktiv LOW / Open Drain**, SOT-23-THIN-14 (DYY0014A), −40 bis +125°C. [TI Rev. B (März 2026)](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf), Tabelle 4-1, 5-1, Package DYY0014A. Die unveränderte feste 2%-Hysterese genügt **nicht** für gewünschte 8V EIN / 6V AUS.

**Mouser Europa** [Bestellseite](https://eu.mouser.com/en/ProductDetail/Texas-Instruments/TPS3760A012DYYRQ1): Cut Tape ab 1 St.; Momentaufnahme ca. 760 lieferbar, **2,30€/1, 1,71€/10, 1,40€/100 NETTO** (exkl. Versand/USt; Lieferstand vor Bestellung bestätigen). [DigiKey Automotive-Bestellseite](https://www.digikey.com/en/products/detail/texas-instruments/TPS3760A012DYYRQ1/16677062) als Zweitquelle.

## Festgelegter KiCad-Prototypstand
- **Portables Symbol:** `TripTracer_V1.kicad_sym:TPS3760A012DYYRQ1` als **U302**, alle 14 echten DYY-Pins nach TI: VDD1; SENSE3; RESET_N_OD6; CTR9; CTS10; GND8 und13; **NC2,4,5,7,11,12,14 offen**.
- **Portabler Footprint:** `Tripmaster.pretty/TI_TPS3760_DYY14.kicad_mod` nach TI DYY0014A, Hersteller-Landpattern **0,5mm pitch, 1,05 × 0,30mm Pads, x=±1,5mm, y=−1,5..+1,5mm**, Body 1,9 ×4,1mm. Noch NICHT in KiCad PCB/3D/manuell nachgemessen oder DRC-freigegeben.
- **Dritte eigenständige KiCad-Seite:** `03_VS_READY_TPS3760.kicad_sch` an `TripPower_5V2A.kicad_sch` angebunden. U302 VDD direkt an VS_CLAMP, GND an GND, 100nF/100V VDD-C310, CTS frei, CTR zu 220nF C311 an GND (Verzögerung ca. 280ms typisch; Temperatur/Bias-Validierung ausstehend). Widerstände R330=845k VS→SENSE, R331=100k SENSE→GND, R332=1,91M RESET→SENSE positive Rückkopplung, R333=1M VS→RESET Pullup. MPNs für Standard-R/C müssen noch beschaffbar fixiert werden. **RESET_N_OD läuft ausschließlich auf VS_READY_RESET_OD_PRELIM**, bewusst NICHT auf LM74930 CTRL_EN!

## Nominale Schwellen (nicht garantiert)
Die TPS3760 UV schaltet Open-Drain-RESET aktiv bei SENSE unter **0,8V** und löst nach SENSE ≥0,8V+2% = **0,816V** auf.
RESET **LOW** zieht R332 zur Masse, Schwelle VS rising:
`VON = 0,816 × [1+R330/R331+R330/R332] ≈ 8,07 V`.
RESET **High-Z** wird nur über R333 nach VS gezogen. R333 und R332 bilden dann den zweiten VS-Pfad nach SENSE. `VOFF = 0,8 × [1+R330/R331+R330/(R332+R333)] / [1+R330/(R332+R333)] ≈ 6,04 V`.
Die Formeln ignorieren V_RESET(LOW) bis 0,3V, 100nA SENSE-Bias, 300nA RESET-Leakage und Widerstands-/Temperaturtoleranzen. Eine R ±1%-/VREF-/Hysterese-/Leckage-Szenarioanalyse und 9V-Startmarge sind noch **FREIGABEBLOCKER**. Alle SENSE-, RESET- und VDD-Pins sind für max65V Betrieb spezifiziert, trotzdem D301/VS worst-case Pulszener bis ≤65V bei 202V überprüfen.

**Kritischer Integrationsblocker:** Die per U302 getriebene Open-Drain-Leitung muss **beide** RUN-Wege AUTO R319 sowie extern RUN_CMD R317/D305 sperren. Direkte Verbindung RESET→CTRL_EN führt ggf. zur ungewollten Betriebsspannungs-Rückspeisung über den RESET-Pullup R333 und verändert durch den RUN-Pegel das Schmitt-Feedback. Ein einfacher Diode-Clamp garantiert am EN-Pin nicht die geforderten <0,41V über Temperatur. Deshalb U302/RESET bis zur vollständig berechneten fail-safe Freigabestufe bewusst **isoliert**, C309=10uF bleibt als historische RC-Prototypbestückung und wird im finalen VS_READY-Gate entfernt/DNP. Eine KiCad ERC-Freigabe dieses **getrennten** Kandidaten beweist keine funktionierende Gesamtabschaltung.

**Garantierte Startspannung 9–30V weiterhin nicht ableitbar.** SUPERVISOR und zusätzliche 10uF VS verändern die 9V-Vorladelast und Resetfeedback. 202V/350ms FET-SOA, externe F_MAIN und Ceff-Kälte/Hot bleiben offen. Nach elektrischer Gate-Freigabe ist ein natives KiCad10 ERC/netlist plus echter VS/CTR/EN Transiententest obligatorisch.
