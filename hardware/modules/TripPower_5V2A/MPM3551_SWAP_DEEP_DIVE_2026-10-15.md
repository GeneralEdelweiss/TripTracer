# TripPower REV5 – Detailpruefung eines 5-V-Wandlerwechsels (15.10.2026)

**Ergebnis: MPM3551GQWE-AEC1-Z als direkter Ersatz des LMR38020SQDDARQ1 nicht empfehlen; keine Aenderung an aktivem KiCad/OVP.** Das Ziel von 9–30 V Dauerbetrieb, 5 V / 2 A, RAW-AUX 1 A, 200 V/350 ms ungedeckeltem Puls (separates Schutzgate), externer F_MAIN und -40..+125°C wird nicht abgesenkt. 9V-Systemstart ist weiterhin nicht verifiziert; keine PCB-/Automotive-/Fertigungsfreigabe.

## Gepruefte Quellen (herstellerprimaer)
1. MPS MPM3551-AEC1 Datenblatt, Rev.1.0, 24.07.2023: https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MPM3551GQWE-AEC1/
   - S.4: PIN-Map und Pflicht-C fuer VBOOT/VCC, zwei VIN-Entkopplungen.
   - S.5: VIN/EN absolut max 40V normal, 42V nur **automotive load dump** (siehe Herstellerhinweis ISO16750, KEINE allgemein freigegebene 350ms/125C-Toleranz), empfohlen 3.3..36V.
   - S.6: interne VIN-OVP Rising **35.5/37.5/40V min/typ/max**; Falling **34.5/36.5/39V**. Diese OVP *stoppt switching*, ist **keine Hardware-Klemme vor VIN**.
   - S.11 (Druckseite 11, PDF-Seite 10): Effizienz 5V/2A VIN 36V etwa **87..88%** an 25C, grob aus Herstellerkurve abgelesen. Kein garantierter Worst-Case.
   - S.25 Fig.7: einstellbare 5V-Ausfuehrung mit 2x10uF + 2x100nF CIN, 2x22uF COUT, 47nF CBOOT, 1uF CVCC, 2 FB-Widerstaende (100k+19.1k), optionaler EN/PG-Beschaltung.
   - S.29: MPS empfiehlt explizit 4-Lagen PCB; Front- und Back-Kupferflaechen fuer thermische Eignung und VIN-Pins symmetrisch entkoppeln.
2. MPS Produktseite, aktive Bestellnummern: https://www.monolithicpower.com/en/products/mpm3551-aec1.html . Die erhaeltliche OPN MPM3551GQWE-AEC1-Z ist **nicht** als 5V-fixed-Variante zugesichert. Fuer die Standard-OPN externen FB-Teiler annehmen. Fixed-output-Variante erst bei verifizierter exakter MPN und Bestellung als neue Option zaehlen.
3. MPS technisches Hersteller-Forum: https://forum.monolithicpower.com/t/setting-mpm3551-output-voltage/5673 – FAE erklaert externe FB-Widerstaende der Standardvariante.
4. TI LMR38020-Q1: https://www.ti.com/product/LMR38020-Q1 – AEC-Q100 80V/2A, bestehend 400kHz, externe 15uH-Induktivitaet.
5. TI TPSM33620-Q1: https://www.ti.com/product/TPSM33620-Q1 – 36V/2A, 5V fixed mit integriertem Boot + Spule; **4 externe** in Herstellerreferenz moeglich. Aber separate OVP-/Wiedereinschalt-/Transienten-Kollision.
6. TI TPSM65620: https://www.ti.com/product/TPSM65620 – 65V/2A mit Spule, **Catalog** (kein AEC-Q100), DigiKey DE am 15.10.2026 **0 Lager**. Nicht freigegeben.

## Elektrische OVP-Analyse: statisch vs Transienten
- REV5 LM74930 OV: R307+R308=1.5Mohm, R309=25.5kohm, typisch **35.89V**, konzervative Fehlerhulle ca **34.02..38.74V** (R1%, TI OV-Pin +/-200nA, 0.585..0.630V steigende Schwelle).
- MPM3551 VIN normal maximal 36V, absolute normale +40V, nur begrenzter 42V-load-dump-Kontext. Es kann intern bei 40V erst zu schalten aufhoeren; **die externe LM74930-Stufe begrenzt das PIN-VIN im transienten Fall NICHT sicher auf 40 oder 42V**, deren Gate-Abschaltzeit und VIN-Pad-Ringing wurden nicht gemessen.
- Ein bisher modellierter R309=28.7k Versuch ergibt Rising 30.26..34.53V, aber Falling 27.54..31.43V -> keine garantierte Wiedereinschaltung nach OV bei 30V. Eine eigene schnelle OVP plus neu belegte lokale Clamp koennte mehr Bauteile brauchen als sie spart.
- 200V/350ms ist **Spannung an VIN_FUSED vor LM74930**, nicht am MPM-Pin. Fuer Ersatz ist MPM VIN-Pin ueber vollstaendiges 200V/350ms-Testspektrum, Ueberschwinger, Langsamrampe, 30V Restart, 125C, Q301 Hot SOA zu pruefen.
- OVP intern des MPM ist **kein Ersatz** fuer LM74930-Q1, Q301/302, Shunt, Zener und F_MAIN.

## Bauteilzaehlung – echte Schematic-Stueckliste
Aktiver REV5 Buck laut `02_5V_LMR38020.kicad_sch` **12 aktive Positionen**:
- U101, L101,
- C101,C107,C108 (3x Eingang),
- C104,C105,C106 (3x Ausgang),
- C102 (BOOT),
- R101,R102 (2x FB),
- R103 (RT) = **12**.
MPS MPM3551 mit **einstellbaren 5V**, NO-PG und vereinfachtem VIN->EN, Referenz 2x10uF+2x100nF Eingang, 2x22uF Ausgang, 1x47nF BOOT, 1x1uF VCC, 2x FB: 1+4+2+1+1+2=**11 Positionen** (Zielwert, kein KiCad-Symbol und kein PCB). Nur **1 Position Ersparnis** bei einfacher EN-Beschaltung. Mit externem EN-Widerstand = **12**, zusätzliche EMV-/HV-Spannungsreserve waeren weitere Teile. **Die zuvor geschaetzten bis 7 weniger fuer MPM3551 sind falsch**; diese groessere Einsparung gehoert zum TI TPSM33620 *nur unter einer komplett qualifizierten, heute nicht vorhandenen 36-V-Schutzschnittstelle*.
Fixed-5V-MPM nur bei real existierender und verfuegbarer exakter MPN anrechnen (kann 2 FB-R vermeiden, derzeit nicht nachgewiesen).

## Thermik-Screen – bereits fraglich bei 125C
Aus MPS Effizienzkurve bei 5V/2A und VIN36V, TA25C: eta~87.5% -> P_LOSS = 10/0.875 -10 = **1.43 W**.
MPS Table 5 thermal theta_JA ca **34.8 K/W auf 8.3x8.3cm, 4-Lagen, 2oz Kupfer EVM**; JEDEC theta_JA Vergleichswert 46.2 K/W (kein Applikationswert!).
Mit EVM-Theta -> Delta_T ~1.43*34.8=**49.7K**, bei TA125C -> TJ ~**174.7C**, groesser **TJ_MAX 150C**. Bessere ETA/kleinere P bei VIN30 moeglich, aber hohe Temperatur erhoeht die FET-Verluste. Bedingte max Verlustleistung bei TA125C: (150-125)/34.8=**0.718W**, erfordert bei 10W **eta >=93.30%**, auf kleinem TripPower-Board eher mehr. Das EVM-Thermikmodell ist eine *Warnrechnung* und keine garantierte echte T_J-Vorhersage. Der bestehende LMR38020 2A bei +125C ist ebenfalls noch nicht experimentell nachgewiesen, hat aber verteilte Drossel-/IC-Verlustwaerme und viel mehr VIN-Reserve.
MPS 2.2MHz, min tON 65ns typ / 80ns max; bei 5V/30V, 2.2MHz ideal tON~75.8ns, bei 36V~63.1ns -> Naehe zur min-on-/FSS-Grenze, PFM/Pulse-Skipping/EMV neu pruefen. Bestehender 400kHz LMR hat ideal tON bei 30V etwa 416.7ns.

## Beschaffung – Preise nur Momentaufnahmen, verschiedene Haendler/Waehrungen NICHT unbereinigt addieren
- [Mouser DE MPM3551](https://www.mouser.de/en/ProductDetail/Monolithic-Power-Systems-MPS/MPM3551GQWE-AEC1-Z): **5.19 EUR/1, 3.42 EUR/100** und Bestand bei Abruf 3241 (abweichende regionale Listen).
- [Mouser DE LMR38020](https://www.mouser.de/ProductDetail/Texas-Instruments/LMR38020SQDDARQ1): **3.92 EUR/1, 2.49 EUR/100**; konkreten aktuellen Lagerbestand beim Checkout bestaetigen (Mouser Listings widersprechen).
- [LCSC FCH0650-150M](https://www.lcsc.com/de/product-detail/Power-Inductors_FANGCHENG-FCH0650-150M_C20415538.html): **0.1579 USD/5+, 0.1085 USD/150+** ohne Versand/Zoll/Steuern, nicht direkt EUR addieren.
- [DigiKey DE TI TPSM33620S5](https://www.digikey.de/de/products/detail/texas-instruments/TPSM33620S5QRDNRQ1/27687227): **2.10 EUR/1, 1.882 EUR/100** und vorrätig. Geraet und 200V-Schutzfunktion aber trotz billigem Buck nicht bewiesen.
- [DigiKey DE TI TPSM65620](https://www.digikey.de/de/products/detail/texas-instruments/TPSM65620SVCGR/29281629): **4.58 EUR/1, 4.107 EUR/100**, **0 Lager**, erwartete Lieferungen Anfang 2027; Produkt 'Catalog' – kein AEC.
Extra-Kondensatoren, lokales PCB, EMV-Pruefung, Bestueckung und Versand nicht bewertet; keine System-Endkostenzusage.

## Designentscheidung und naechste Gate-Sequence
1. **Keine KiCad-Produktiv-Aenderung fuer den MPM3551**. Beide eingesparten DNP-R305/R321 bleiben in REV5 dokumentiert.
2. Wenn es um *Teilezahl* geht: TI TPSM33620 ist der bessere COTS-BOM-Kandidat, aber 36V/40V-Grenze und 30V-Restart machen ein vollstaendiges neues OV/PAD-Transientenmodell noetig.
3. Wenn es um *Risiko, thermische Reserve und 200V-Entwicklung* geht: bestehenden 80V LMR38020 beibehalten und 9V-Start-/Q301-200V-SOA-/PCB-Gates schliessen.
4. Langfristig 60..80V-2A-AEC-Q100-Modul mit integrierter Drossel und wirklichem Bestand nur wechseln, wenn es auch nach thermischem 125C-Derating, BOM und OVP-VIN-Pad-Nachweisen Vorteile hat. Markt-Screen ergab derzeit kein gleichwertig qualifiziertes kaufbares Bauteil.
5. Fuer jeden Wechsel: eigene verifizierte KiCad10-Symbol/Footprint/3D, genuine Buck-Referenz, 9/12/24/30V 0..2A, 125C Heat, VIN0-RUN, 200V/350ms test gate und nachvollziehbarer Review. 4-Lagen-Layout fuer MPS empfohlen.

**Keine echten Hardware-/Fertigungstests in dieser Studie durchgefuehrt.**
