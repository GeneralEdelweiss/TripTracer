# TripPower Weg B Round12 – konkrete Temperaturabschaltung und selektiver RAW-Prototyp

**Branch:** `design/trippower-b` | **Datum:** 2026-10-16 | **Status:** nativ geprüfter isolierter KiCad-10-ENTWICKLUNGSPROTOTYP – **NO FAB / NO VEHICLE / NO SAFETY RELEASE**.

## 0. Quellen und tatsächliche Architektur

Verbindlich und auf den aktuellen Branches neu gelesen: `AGENTS.md`, `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR-44–56, `docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md`, B-Round11 `WEG_B_ROUND11_A23_INDEPENDENT_SAFETY_2026-10-16.md`. A23-Quelle auf `design/trippower-a` **f30f35d404e6ba549ee6202c46d660f498c36545** (elektrischer Round5-Commit 3f3dd727...); A Round5; C Round11 auf `design/trippower-c` **bab593fdac16ac68f8c9e58e47df577fd7f9fe4e**; D Round11 auf `design/trippower-d-load-dump` **7d3f53b8c6c517aeb4d258fe2b1c783b63098a57**.

Aktiver TripTracer-Root `hardware/kicad/TripTracer_V1.kicad_sch` referenziert eigene `01_Eingangsschutz`, `01I_LM74800_INPUT`, `01H_ACC_HOLD_GATE`, `01C_HOLD_TIMER`, `02_5V_Buck`, `03_3V3_USB` und weitere; **A23 ist NICHT eingebunden**. Keine Annahme eines fertigen Thermo-Abschalters oder historischen K101-Relais. B hat **kein** A-/C-/D-Sheet und **keine** Host-Haupthierarchie verändert. Voriger A23-nativer B-KiCad-Audit [Run38881195864](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38881195864) war erfolgreich; seine ERC-Ausführung wurde nicht als eigener neuer Temperatureingriff ausgegeben.

## 1. Wirklich gezeichnete KiCad-Dateien

- `TripPower_B_REV6_R12_SAFETY.kicad_pro` / `TripPower_B_REV6_R12_SAFETY.kicad_sch`: komplett eigene A2-KiCad10-Wurzel, **30 bestückte Positionen**; beide Hardwarefunktionen plus Schnittstellen zu A23/Host.
- `TripPower_B.kicad_sym` und projektlokale `sym-lib-table`: portable eigene **hersteller-pinbezogene Symbole** für LDO/TMP390/Supervisor/LTC4368/Reverse-FETs/BJTs/Passives; zusätzlich **nicht bestückte** `#FLG01` (elektrischer GND-Power-Flag) und `TP301` (rein logischer Host-Handoff, kein PCB-Testpad, kein Stecker).
- `TripPower_B.pretty/TI_DGN0008B_HVSSOP_8_EP.kicad_mod` samt `fp-lib-table`: **TI-Originalzeichnung** DGN0008B, 8 Pads 1,4×0,45mm in 0,65mm Raster, EP-Pad9 1,88×1,98mm. Quelle TI TPS7A4001 RevB S.21–22. **Nur geometrischer Layout-Entwurfsstand, noch kein unabhängiges EP-/Pad-/Lötschablonen-/JLCPCB-/Montage- oder DRC-Gate.**
- `check_round12.py`, `ROUND12_30_POSITION_BOM_ESTIMATED_EUR_2026-10-16.csv`, `ROUND12_FMEA_AND_LAB_TEST_MATRIX_2026-10-16.csv`, Workflow `.github/workflows/trippower-b-round12-safety.yml`.

Originale Datenblätter:
[TI TMP390-Q1 RevB](https://www.ti.com/lit/ds/symlink/tmp390-q1.pdf) – Bild 8-5 und Tabelle 8-2 S.15; [TI TPS7A4001 RevB](https://www.ti.com/lit/ds/symlink/tps7a4001.pdf) – Pin-/Package/Fußabdruck; [TI TPS3838-Q1](https://www.ti.com/lit/ds/symlink/tps3838-q1.pdf) – SOT23-5, Active-LOW RESET, CT-GND 10ms; [ADI LTC4368 RevC](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4368.pdf) – Fig.2 und §Applications; [onsemi BSS123LT1G](https://www.onsemi.com/pdf/datasheet/bss123lt1-d.pdf); [Vishay 50mΩ WSL2512R0500FEA](https://www.digikey.de/de/products/detail/vishay-dale/WSL2512R0500FEA/712568); [KEMET C1210C225K1RACAUTO](https://search.kemet.com/component-documentation/download/specsheet/C1210C225K1RACAUTO).

## 2. Hardware-Temperatur-Interlock – bewusste Default-OFF-Logik

**Bestückung (Positionen):**

| Ref | Konkreter Typ / Funktion | Reale Netzaufgabe |
|---|---|---|
| U301 | TI `TPS7A4001DGNR`, 100V HV-LDO | Aus `VIN_SAFETY_FUSED` **vor Q201**, via D301 BAV21W (reverse), `SAFE_3V3` 3,29V |
| R301/R302 | 180kΩ /100kΩ, 1% | TI Vref 1,173V: 1,173×(1+180/100)=**3,2844V nominal**. Min/Max Ref, heißes I_FB und Last noch zu verifizieren |
| C301/C302/C303 | 4,7µF/100V Eingang; 22µF/16V Ausgang; 100nF | tatsächliche **Ceff nach DC-Bias/T** und Startup des LDO nachmessen |
| U302 | TI `TMP390AQDRLRQ1`, SOT563 | Hot-Trip-Sensor unabhängig von MCU und der abgeschalteten 5V-Schiene |
| R303 | 24,9kΩ, 1% | **SETA1 und SETB2 verbunden**, Hersteller-Einkanalvariante Tabelle8-2: **74°C nominal HOT / 5°C Hysterese**, OUTB unbenutzt |
| U303 | TI `TPS3838K33QDBVRQ1` | 2,93V nominelle SAFE_3V3-Schwelle, OD-RESET, CT=GND typische 10ms Entprellung; RESET und TMP390-OUTA gemeinsame aktive LOW-Leitung |
| R304/R305 | 10k Pullup SAFE_3V3 /100k Pulldown gegen GND | `TEMP_OK_OD` nur HIGH, wenn **Temperatur OK und LDO-Spannungswächter freigegeben**; Verlust der Hilfsspannung → Q302-Gate definiert LOW |
| Q301/Q302/R306 | onsemi MMBT3904LT1G NPN; BSS138LT1G NMOS; 330k R306 | `VIN_SAFETY_FUSED` über **330k** schaltet Q301 normalerweise EIN → Q301-Collector hält TPS26631-SHDN **LOW**; **erst gültiges** TEMP_OK_OD HIGH schaltet Q302 EIN, zieht Q301-Basis LOW und erlaubt SHDN-High durch TPS-internen Pullup |

**Grundidee: unabhängig vom MCU und selbsthaltend während Abschaltung.** Ohne gültiges SAFE_3V3 bleibt der Sensor-/Supervisor-Open-Drain-Ausgang unzuverlässig; aber Q302 wird zusätzlich über 100k gegen GND gesperrt und Q301 zieht TPS-SHDN **weiter aktiv LOW**, solange die über die externe Fahrzeugleitung abgesicherte Eingangsspannung vorliegt. Die ganze Schaltung hat **kein HIGH-treibendes 58V-Signal direkt auf SHDN**; dessen Absolute Maximum ist 5,5V. Eine MCU darf den SHDN-Knoten im späteren Host höchstens zusätzlich per Open-Drain LOW ziehen, niemals der thermischen Abschaltung entgegen HIGH erzwingen. U301 benötigt eine unabhängig von eFuse-/Buck-AUS gespeiste und aus Rückspeisegründen getrennte Hilfsdomäne; **keine Verbindung von SAFE_3V3 zu USB_VBUS, RTC-Zelle oder Host-5V**.

**Dimensionierung:** VDD des TMP390 ≈3,3V; für VDD2,5–5,5V und Schwellbereich30..130°C gibt TI für HOT **±2,5°C max**, also Trip-Spanne **71,5..76,5°C** am *Sensor*, Reset näherungsweise 5°C kälter; 0,5s nominales Sampling, POR/RC/Supply- und mechanische Wärmelags hinzufügen. **Bis +85°C Umgebung bleiben rechnerisch nur 8,5K Sensor-zu-Ambient-Gradient/Verspätungsreserve**. Verbindliches Chamber-Test-Gate: im gesamten Hotspot/Leitungs-/Gehäuse-Bereich bei +85°C Umgebung muss SHDN und der physische Leistungszweig zuvor sicher abgeschaltet haben. Ohne Hotspot-Platzierung und Messung keine behauptete 85°C-Freigabe. Der Schaltpunkt darf näherungsweise derating-ab+60/+70°C erzwingen, nach REV6 zulässig.

**Ruhestrombudget, nur Vorrechnung:** VIN=24V → R306 Strom ungefähr (24−0,7)/330k =**70,6µA**; 32V → ~94,8µA; 58V → ~173,6µA. LDO Eigendauerstrom typisch etwa25µA, TMP390 typisch0,5µA, Supervisor typisch0,22µA, LDO-R301+R302 bei3,28V ~11,7µA; OD-R304/R305 teilen im freigegebenen Zustand etwa30µA; noch Q302-Gate-Leck, Schutzdiode/LDO und alle Host-Ströme. **Gesamtes BAT-OFF <1mA / Ziel0,5mA ist NICHT nativ geprüft und nicht bei +85°C worst corners garantiert.** SHDN13 muss bei VIN10V, HOT und Sensor-VDD0 auch bei schlechtester Q301 hFE/Leck/Temperatur sicher LOW bleiben (R306 liefert grob 28µA Basis bei10V), Schaltzeit und sichere Rückkehr messen.

**Erkannte Restrisiken, bewusst keine falsche Sicherheit:** TMP390-OUTA an GND kurz → fail-OFF. SETA/SETB offen/kurz beim POR können die Hersteller-Fault-Methode auslösen, aber Laufzeit-Fehlererkennung und Wiederanlauf sind **nicht** ohne Labor-/Hersteller-Nachweis garantiert. TMP390 OUTA **stuck-HIGH/stuck-release**, Q301-Collector OPEN, Q302 Drain–Source SHORT, dauerhaft unterbrochene R306 oder ein intern leitend zerstörter **U201-Leistungs-FET** sind **nicht** durch eine einzelne Temperaturmessung mit SHDN sicher abgefangen. Daher ausdrücklich **P0-Einzelfehler-GATE OFFEN**: entweder zweite unabhängige thermische Barriere **mit eigener Cutoff-Ausgangsstufe** und tatsächlicher zweiter mechanischer Serie-Schalter auf Host oder nachweisbar ungefährliche Passivtemperaturen im geprüften Worst-Case. Das K101-Relais ist nicht nachgewiesen und kein Bestandteil der Schaltung. Nicht einfach softwareseitig lösen.

## 3. RAW-0,5-A-Branchausgang – echte elektronische Kurzschluss-Latch-Funktion

**Auswahl:** **ADI `LTC4368HMS-2#WPBF`** an `MAIN_EFUSE_OUT`, **hinter** A23 U201 TPS26631 OUT, und **vor** dem eigentlichen externen `RAW_OUT`. Im Gegensatz zu TPS26600 mit ABS62V besitzt LTC4368 eine -40..100V **Schutz-/Überlebensgrenze am VIN**, jedoch normale Betriebsgrenze2,5–60V und **andere PIN-MAX** z.B. SENSE/VOUT/SHDN/GATE. **100V auf dem VIN-Etikett ist NICHT 100V für alle Pins und ist keine 58V-Ringing-Messfreigabe!** Umgekehrt dürfen wir Q201/D und U201 IN/IN_SYS nicht mit LTC-Ratings verwechseln.

Tatsächlich gezeichnete Hauptbauteile: LTC4368HMS-2 MSOP10, **zwei** 100V AEC-FETs `TK11S10N1L,LQ` mit **Source-Source (Back-to-Back)** und gemeinsamen Gates; Vishay `WSL2512R0500FEA` **50mΩ ±1% 2512, 1W, AEC-Q200** in Serie zwischen `SENSE` und `RAW_OUT/VOUT`, Herstellerstromkomparator; RETRY4 direkt GND = **LATCH-OFF** bei Forward-OCP, nicht periodisch heißer Auto-Retry. Reproduzierbares OCP-Kurzschluss-Corner-Screening laut ADI ∆Vmax/min0,030..0,070V bei Rnom0,05Ω ±1% → **I_OC≈0,594..1,414A**; typ50mV/0,05Ω=**1,00A**. **0,5A Dauerlast hat 94mA statische Reserve im pessimistischen Grenzfall**, aber Schaltspitzen und Hersteller-Überstromtiming (µs) sind gesondert gegen Lastinrush zu prüfen. Der Controller **ist ein schnell abschaltender Circuit Breaker und kein garantierter stufenloser 0,5A-Stromregler**.

Originale ADI-R-U-V-/OV-Ladder **R401464k/R4021,5M/R403121k/R40429,4k**; Ausgangszweig an VIN→SHDN→UV→OV→GND, erwartete nominelle Schaltschwellen ca **UV 7,03V** und **OV 35,96V**; Toleranz, Comparator-Max- und TPS-Schwellen gemeinsam prüfen. C402100nF/100V vor IC und **C403 KEMET 2,2µF/100V/X7R am RAW_OUT** nach ADI **VOUT benötigt mindestens 1µF tatsächlich effektiv**; Hersteller-Ceff@32V und Alterung ist **noch offen**. Die anfänglich fehlende VOUT-Kapazität wurde im nativen Schaltplan explizit ergänzt, nicht als C402 verrechnet. R40622k/C4012,2nF100V GATE-Ramping, inklusive 0,5A+externem COUT beim Start prüfen.

**Reset:** N-MOS onsemi `BSS123LT1G` **100V VDS** Q403 zieht mit definiertem `RAW_HW_RESET_HIGH` den LTC SHDN6 aktiv LOW; R407100k setzt Reset-Gate sonst definiert LOW. **RETRY4 GND** und kein Auto-Retry-Timer. Ein gültiger Hardware-Reset benötigt nach ADI SHDN-LOW-Puls **mindestens 15µs**, aber bevor der LTC in Low-Power-Zustand wechselt (Datenblatt dazu 20..48ms) für den spezifizierten Fault-Latch-Clear; die tatsächliche Reset-Pulsbreite und 3,3V-Gate-Level von Q403 über Temperatur müssen A/Host nachweisen. Für V1 muss dieser Reset von **hardwarebelegtem ACC-OFF→ON**, nicht ausschließlich vom hängbaren MCU-GPIO, stammen. MCU-stuck-HIGH auf diesem Eingang hält Q403 im Prinzip LOW-ziehend und damit RAW **AUS**, nicht retriggernd – Gate-Toleranz muss gemessen werden.

**Physikalische Grenzen:** Bei 32V und legitimen 0,5A kann eine **defekte äußere 0,5A Last dauerhaft 16W** aufnehmen, ohne überhaupt eine Überstrommeldung auszulösen; ein passiver Stromlimiter kann diese Last nicht von einer normalen 0,5A-Last unterscheiden. Die RAW-Kabel-/Stecker-/Last-Temperaturhülle bzw. begrenzte Hardware-Aktivierungszeit oder eigene Temperatur-Abschaltung am Verbraucher ist zwingend für gefährliche Teilkurzschlüsse. Bei U201-FET-SHORT kann der LTC4368 58V plus lokale Überschwinger an VIN sehen – getrennte Messung von LTC VIN, SENSE, VOUT, GATE, SHDN und beiden MOSFET-VGS/VDS, ADI-ABS-Ecken und realer 58V-Quellenflanke erforderlich. U401/FET stuck-ON und zwei gleichzeitige Q401/Q402-SHORT erfordern externen Kabelschutz; LTC-Beruhigung allein genügt nicht.

**Kein PPTC-Folkloreersatz:** optionale rückstellende SMD-PPTC erst bei Hersteller-Vmax inkl58V+Peak, I_hold@60/70C, I_trip(T), max Leakage/Restwärme und realer Fehllast/Kabelschutz; keinen ungeprüften 72V0,5A-PPTC in die 30er BOM. **0 bestückte TripPower Schmelzsicherungen, Halter, Einmal-SMD-/Thermosicherungen.** Externe Fahrzeug-BAT+/ACC-Zuleitungen weiterhin möglichst quellnah passend DC-abgesichert.

## 4. Kostenziel – vollständige 30er Bestück-Positionen, keine erdachte Preisgarantie

`ROUND12_30_POSITION_BOM_ESTIMATED_EUR_2026-10-16.csv`: **30/30 echte Referenzen** mit Hersteller/MPN/nominalem Wert/Footprint; alle in B KiCad native BOM, alle in XML-Export. 12/30 Positionen mit **konkreten Euro-Dealer-/Branch-Snapshotpreisen**, 18/30 **ausdrücklich mit ENGINEERING_ALLOWANCE_UNQUOTED gekennzeichnet** (Preisannahmen, keine bewiesenen Angebote). Gemischtes Budget **EUR netto pro zusätzlicher Temp+RAW-Schutzplatine**:

| Stückzahl | €/Schutz-Zusatzmodul | Gesamt Bestellung € netto | davon Preispositionen noch nicht quote-verifiziert |
|---:|---:|---:|---:|
|1|**23,5460**|23,5460|18|
|10|**16,4030**|164,0300|18|
|100|**13,0707**|1307,0700|18|

**Nur additiver, hypothetischer Materialwert** bei alter A23-BOM 20,2570/13,5610/10,6266 EUR: zusammen **43,8030 / 29,9640 / 23,6973 EUR** je kompletten A23+getrennten B-Schutz-Bauteilen, **NICHT** eine integrierte oder optimierte BOM. Viele Positionen könnten bei Integration entfallen/geteilt werden (z.B. vorhandene Host-Stromversorgungs-Supervisor-Funktion) **nur nach realem Host-Netzlistennachweis**. Keine PCB-, Schablonen-, Serienmontage-, Stecker-, Kabel-/Fahrzeugsicherung-, Versand-, MwSt-, Labor-/Automotive-/System-/Layoutkosten. Reichelt/-DigiKey/-Mouser-/TME-Stückzahlen und Lieferorte vor Einkauf neu prüfen; Umsatzsteuer/Währung nicht vermischen. Beispiel bestätigte Einträge: [ADI LTC4368 DigiKey EUR 8,69/6,769/5,7627](https://www.digikey.it/en/products/detail/analog-devices-inc/LTC4368HMS-2-WPBF/12385748), [TI TPS3838 DigiKey EUR 2,77/2,073/1,7092](https://www.digikey.at/de/products/detail/texas-instruments/TPS3838K33QDBVRQ1/571409), [Vishay 50mΩ Mouser](https://www.mouser.de/de/ProductDetail/Vishay-Dale/WSL2512R0500FEA), [KEMET C403 TME](https://www.tme.eu/de/details/c1210c225k1racauto/kondensatoren-mlcc-smd/kemet/).

**COTS-Trade-off:** 60V- bzw. 62V-ABS-Standard-eFuse kann billiger mit wenigen externen Teilen sein, **scheitert aber im noch ungeprüften U201-intern-FET-SHORT/58V+lokalen Peak-Szenario an nicht belegter Pinreserve**. LTC4368 benötigt Controller + zwei MOSFETs + Rshunt + vier UV/OV-Widerstände, schützt diese Fehlertopologie deutlich flexibler, verlangt selbst aber P0-Hardwareprüfung. Kein vorschneller IC-Zukauf und keine Behauptung, dass diese 30 zusätzlich Bestückungen schon wirtschaftlich optimal sind.

## 5. Prüfung, FMEA und Freigabematrix

Reproduzierbare detaillierte **26-Zeilen**-Fehlerszenarien in `ROUND12_FMEA_AND_LAB_TEST_MATRIX_2026-10-16.csv`; jedes mit Auslösung, erwarteter Reaktion, Messmethode, P0/P1 und ehrlichem Nachweiszustand, darunter MCU-stuck-HIGH, SETA/B OPEN/SHORT beim POR und laufend, OUTA stuck-low/high, Sensorversorgung weg, Q301/Q302 und U201-FET-SHORT, RAW-Hard-/Teilschluss, ±OCP-Corners, hardware reset stuck-high, USB-only/BAT-OFF, 10V-Start, 58V/350ms, –20/+60/+70/+85°C und 5V/FRAM-first.

| Gate | Status | Reproduzierbarer Nachweis |
|---|---|---|
| **30-Positionen KiCad-Schema** | **PASS native/CI** | Native KiCad10 ERC0, XML-Schutz-Netze, native BOM 30, Projektbibliothek/Footprint vorhanden |
| **74°C nominal HOT/5°C Hyst** | **PASS TI-Stufen-Rechnung; OFFEN physisch** | Hersteller-TMP390-Q1 Table8-2, Wärmegradient und VDD/POR real testen |
| **VDD0 Default-OFF NPN SHDN** | **PASS nur NETZE; OFFEN physisch** | R306 von PreQ201 VIN, Q302 Gate via R305 low, TPS SHDN-Sink; NPN V_CEsat Hot messen |
| **Eine TMP390 stuck-high/defekter MAIN-FET** | **FAIL P0 als Einzelkanal-Schaltung** | Kein 2. Temperaturkanal, kein unabhängiger auf Host gezeichneter Serien-Cutoff |
| **RAW über0,5A eindeutiger OCP** | **PASS ADI-Cornerrechnung; OFFEN Labor** | Rshunt50mΩ, min0,594A max1,414A, RETRY=GND |
| **RAW sicher bei .5A defekter Last** | **FAIL P0 als generischer Endverbraucherschutz** | bis16W bei32V unauffällig möglich; Verbraucher/Kabelthermik muss spezifiziert werden |
| **RAW Einschalt- und Kurzschluss-Latch** | **PASS Netz/Funktionskonzept; OFFEN Labor** | Hardware-ACC-off Q403-Puls + tCLEAR, max OCP + inrush/thermal |
| **58V lokale LTC-/TPS-Pinspitzen** | **OFFEN P0** | Weg-D-M8- vs TPS-IN/IN_SYS-Trennung und zusätzlicher LTC VIN/SENSE/VOUT/GATE-Fault-Test |
| **USB-only, Iq<1mA, MCU stuck** | **OFFEN P0/P1** | Noch keine aktive TripTracer-Host-Integration oder Backfeed-Messung |
| **Host-PCB/EP/3D/DRC/Fertigung/Fahrzeug** | **OFFEN, STOP** | separates B-KiCad-Schema statt PCB, keine Messungen/Automotive/Serienfreigabe |

**Evidenz strikt getrennt:** B-KiCad10 native ERC/Net/BOM und Quellen-Pinvergleich **ausgeführt**; TI/ADI Datenblattkennzahlen und Ω-/Schwellenrechnungen **durchgeführt, keine Geräteausfallmessung**; Weg-D-58V-RLC-Sensitivität **Simulation mit hypothetischen Parametern**, keine TI-PSpice- oder Automobilqualifikation; **keine** eigene reale Temperaturkammer-/Kurzschluss-/58V-/Backfeed-/SOA-Messung.

## 6. Exakte Übergabe/Anschlussregeln für Weg A (nach formaler Host-Migration)

1. `VIN_SAFETY_FUSED`: physisch an **extern quellnah abgesichertes** Fahrzeug-BAT+, **vor Q201**, jedoch **nicht ungesichert**! Serien-D301 an SAFE_HV, eigene GND-Sternführung. *Nie* Sensor/LDO aus `5V_OUT` speisen, weil er sich beim Abschalten selbst stromlos macht. 100V TPS7A4001 VIN/EN bei echtem 58V-Puls plus Ringing, D301 Verpol-SOA, Leck/BAT_OFF erst messen.
2. `TPS_SHDN_SAFETY`: Q301-Collector an **A23 U201 TPS26631 SHDN13** und ausschließlich mit zusätzlichem Open-Drain-LOW vom Host kombinieren. Kein 12/24/58V an SHDN, kein aktiv HIGH treibender MCU-Pin, kein anderer Pullup über 5,5V; Q301 bleibt FAIL-OFF wirksam.
3. `MAIN_EFUSE_OUT`: unmittelbar A23 `VIN_PROTECTED_UNFUSED` / U201 OUT18–20 **hinter der Haupt-eFuse**, innerhalb der richtigen GND-/Stecker-/Leitungsführung. `RAW_OUT` ist allein der **nach** U401/Q401/Q402/R405 abgesicherte Ausgang, darf niemals direkt an alten TP202/A23 OUT als vermeintlich geschützten Verbraucherport angeschlossen werden.
4. `RAW_HW_RESET_HIGH`: nur über **nachgewiesenes, hardwarezeitbegrenzt stabiles ACC-OFF→ON**-Signal und niemals als unqualifiziertes MCU-Restart-HIGH; Q403-BSS123 100V und VGS@3,3V bei SHDN<1,2V Hot/58V prüfen. Optionales MCU-Monitoring `RAW_FAULT_N` nur an isolierter 3,3V-Logik; `PWR_FAIL` und FRAM-first bleiben auf Host unabhängig.
5. Ungefährliche Einzel-Fehlerklasse *Sensor stuck-release oder U201-FET-SHORT* mit **einem zweiten tatsächlich gezeichneten Host-Serienabschaltweg samt eigener Sensor-/Thermikentscheidung** schließen oder belegte inhärente Sicherheit begründen. Ohne diesen Nachweis **kein eigenständiger +85°C-SAFE-OFF-PASS**. Offen/kurz getrennt auf SEN-VDD/SETA/SETB/OUTA und auf Sensor-Cutout testen.
6. **Nur dann** isolierte B-Symbole/Bauteile in die *wirklich aktive* Host-Hierarchie integrieren, Port-/Netzprüfungen und neue native KiCad10-ERC/BOM/PCB-DRC durchführen und die 26 Fehlertests an 10/32/36/58V, –20/+60/+70/+85°C, USB-only, BAT-OFF und RAW 0,5A ausführen. Bis dahin **keine Änderungen auf A/C/D** durch Weg B.

**Endurteil:** Zwei echte hardwareseitig prüfbare **Schaltplanprototypen** mit minimaler MCU-Abhängigkeit sind implementiert. **Die Erfüllung aller Sicherheitsanforderungen einschließlich Einzel-Fehler bei stuck-good-Sensor, internem Main-FET-Kurzschluss und externer 0,5A-Fehlerlast ist explizit NICHT erreicht.** `MODE=GND` für isoliertes A23 bleibt unberührt, `RETRY=GND` für RAW ist bewusst latching, keine Reset-Schleifen nach Kurzschluss. Kein Schmelzsicherungshalter oder Einmal-Fuse auf TripPower. **NO FAB / NO VEHICLE**.
