> **Aktuelle U302 RESET-RUN-Verriegelung 15.10.2026:** [gesteuerter Q303 EN-Durchlass](RESET_RUN_INTERLOCK_2026-10-15.md). Beide Anforderungen AUTO+RUN_CMD jetzt auf `EN_REQUEST_RAW` vor Q303; U302 RESET schaltet gatebasierte EN-Freigabe über D306/D307 und D308 zusätzliche CTRL_EN-Klemme. R31822k, R3165.6k, R334470k, R3351M, Q303 BVSS123LT1G, BAS70 AEC Schottkys D306/D308, 10V AEC Zener D307; C309 DNP. **9V-Start, 125C-Off-Kriterium <0,41V, Gate-Schaltspannung, Q303 56V/350ms thermisch sind ausdrücklich UNQUALIFIZIERT; keine Hardware/Automotive/PCB Freigabe.**

> **Prototyp 9–30V VS-Bootstrap / Ansatz A 15.10.2026:** [Auslegung & Fehlermodi](OPTION_A_VS_EN_RC_2026-10-15.md). C308 neu 10µF/100V Panasonic EEE-TG2A100P an VS parallel C302=1µF, C309 neu 10µF/50V X7R AVX 12105C106K4T2A von EN nach GND. Alle 9,9kΩ-VS-Pulswiderstände bleiben. Natives Netlist-/RC-Sensitivity-Gate ergänzt. **Nur AUTO_ON-Prototyp; aktive RUN_CMD-Einschaltung und schnelle Restartfälle umgehen die Verzögerung; Ceff und 9V-Pumpeneingangsstrom ungesichert. KEINE 9V Startfreigabe oder 202V/PCB-Qualifikation.**

> **9–30V-Anlaufprüfung 15.10.2026:** [vollständige Startfenster-/VS-Vorwiderstands-Analyse](STARTUP_9_30V_REVIEW_2026-10-15.md). Bei 9V kann R313–315=9,9kΩ bis VS≥4V nur **0,505mA** liefern (12V **0,808mA**); TI-LM74930 I_Q unter VS12V-Testbedingungen typ. **0,665mA**, max **0,780mA**. **Keine nachgewiesene 9V-/12V-Erststartfähigkeit** trotz D302 A→VS-Nachladediode; D302 greift erst nach Q301-Start. 470nF-C303 typ. 1,324ms Pumpenfreigabe bei idealem VS, LMR38020 ~4ms Softstart. Rechnung in `tools/check_trippower_9_30v_startup.py` und CI. 9,9k nicht blind verringern, 202V-Fuse/SOA-Gates bleiben. Keine 9–30V-SYSTEM-Funktionsfreigabe.

> **Aktive Auswahl C303 (15.10.2026):** [CAP/VS-Komponentenauslegung](C303_CAP_VS_SELECTION_2026-10-15.md): KEMET **C1206C474K1RECAUTO7210**, AEC-Q200, 470nF/100V/X7R/1206 statt alter 100nF im wirklichen KiCad-01-Unterblatt; TDK CGA5L2X7R2A474K160AA als Alternative. Unter Toleranz/X7R-Temperatur rechnerisch 359,55nF vor DC-Bias/Alterung, Mindestgrenze **100nF effektiv**. Normative Prüfungen und KEMET K-SIM/DC-Bias/9V-Start noch offen. Keine PCB-/Fahrzeugfreigabe.

> **OV-/HGATE-Sicherheitsreview 15.10.2026:** [Q301_OV_HGATE_SHUTDOWN_2026-10-15.md](Q301_OV_HGATE_SHUTDOWN_2026-10-15.md). U301.HGATE steuert Q301 Gate nun direkt; R320=100Ω und neu C307=10nF/250V liegen als TI-dVdt-Zweig in Reihe nach GND, statt R320 inline. Ergänzte native Netzlistenprüfung, rechnerischer Start-Ladestrom 0,31A unter Idealannahmen. C303/CAP effektiv zu knapp, 202V-Hot-SOA/Anlaufdynamik **nicht validiert**; nur Entwurfsstand.

> **Q301-Auswahl 15.10.2026:** Der aktive Standalone-Schaltplan verwendet vorläufig den automotivequalifizierten Vishay **SQM10250E_GE3**, 250 V, D2PAK, statt des STD17NF25. [Datenblatt-, Kosten- und Safety-Gates](Q301_FET_SELECTION_2026-10-15.md). Keine OV-202-V-SOA-, Temperatur-, Gate-Timing-, PCB- oder Fertigungsfreigabe; `F_MAIN` weiterhin extern.

> **15.10.2026: TripPower-Eingangsschutz R313–315 als Vishay CRCW25123K30FKEGHP (3,3k/2512/AEC-Q200) konkretisiert; thermische, wiederholte Puls- und 9V-Start-Nachweise offen.** [Nachweis- und Sperrbericht](INPUT_STRESS_GATE_2026-10-15.md). Keine PCB-/Automotive-Freigabe.

# TripPower 5V/2A – eigenstaendiges, kopierbares DC/DC-Modul

> **FORTSETZUNG MORGEN / NEUER CHAT:** **[START_HERE_NEXT_CHAT.md](START_HERE_NEXT_CHAT.md)** ist der **verbindliche, aktuellste Projektstand** mit Architekturbeschluss, realen KiCad-Dateien, Pruefnachweisen und priorisierten Folgearbeiten. Bei abweichenden historisch formulierten alten Abschnitten bitte diesem Handoff und den aktuellen Schaltplandateien folgen. Die eigenstaendige Schaltung hat KiCad10 ERC 0 Verletzungen und 46 native Pin-Netz-Checks im CI-Run 38636492660; **kein PCB/DRC/ISO-/Fertigungsfreigabe**. 


## Standalone KiCad-10-Projekt – aktiver neuer Arbeitsstand 14.10.2026

**Jetzt vorhanden:** [`TripPower_5V2A.kicad_pro`](TripPower_5V2A.kicad_pro) und [Root-Schaltplan](TripPower_5V2A.kicad_sch) mit zwei echten verknuepften Schaltplanseiten [01: LM74930-Eingangsschutz](01_Protection_LM74930.kicad_sch) und [02: LMR38020 5-V-Buck](02_5V_LMR38020.kicad_sch). Die lokalen `sym-lib-table`, `fp-lib-table`, `TripPower_Sym.kicad_sym`, `TripTracer_V1.kicad_sym`, `Tripmaster_Sym.kicad_sym` und `Tripmaster.pretty/` befinden sich im selben Projektordner. **Einfach den GESAMTEN Ordner kopieren und `TripPower_5V2A.kicad_pro` in KiCad 10 oeffnen.**

**Schaltung real elektrisch verknuepft, nicht nur textuell:** VIN_FUSED → Q301/Q302 Common Source → RSENSE 5mΩ → `VIN_PROTECTED_UNFUSED`, gemeinsam zum 5V-Buck und ohne eigene Sicherung direkt zu J302.1. Die Netze verbinden die beiden Unterseiten in der Root-Hierarchie; es sind echte Bauteilsymbole, Wires und globale Labels. Standalone `RUN_CMD` geht ueber R317 und Sperrdiode D305 zum LM74930 EN, mit R316 Pulldown. 0R-R319 ist die optionale `ALWAYS_ON`-Bestueckung. **RUN_CMD niemals direkt mit 12-/24-V-ACC verbinden**; TripTracer braucht einen separaten, geschuetzten ACC/HOLD-Logikadapter.

**Pruefung:** Die GitHub KiCad-10-Actions erzeugen einen **eigenstaendigen** ERC-JSON-Bericht, nativen Netlist-Export und dreiseitiges PDF sowie die Netzlistenpruefung [`tools/check_trippower_native_netlist.py`](../../../tools/check_trippower_native_netlist.py) fuer alle kritischen Pins. Der Teststand ist ein **Schaltplanentwurf**; bis der aktuelle Action-Lauf erfolgreich abgeschlossen ist, keine globale/ERC-Clean-Aussage und keine Freigabe behaupten. Keine eigenstaendige PCB-Datei, kein geroutetes DRC, keine Hardwaremessung.

**Verbindliche Manufacturing-Gates:** Es gibt nun absichtlich **KEIN F302** auf TripPower. Die einzige **wartbar austauschbare Hauptsicherung F_MAIN** muss in der Fahrzeugzuleitung vor dem TripTracer-Strompfad liegen; kein Hilfszweig-Sicherungsbauteil auf TripPower/TripTracer. Saemtliche dahinterliegenden Leiterbahnen, Stecker und Kabel muessen fuer ihren realen Zeit-Strom-/I2t-Fehlerfall dimensioniert werden. Zudem sind 202-V-MOSFET-SOA/thermische Q301-Verluste, 9-V-VS-Chargepump-Start, 3x3.32k-VS-Pulsfestigkeit, das FCH0650-Spulen-Landpattern, RUN-OFF/Backfeed und EMV nicht freigegeben. Die zugelieferten Standard-Footprints und 3D-Verweise sind vor Bestellen dennoch manuell zu qualifizieren.

## Nutzerentscheidung und Werte-Freeze zur LM74930-Schutzstufe (14.10.2026)

**Fest vorgegeben: LM74930QRGERQ1 statt LM74800 fuer das NEUE eigenstaendige TripPower-Modul.** Der bisherige TripTracer-Schaltplan 01I mit LM74800 bleibt bis zur separaten Modulimplementierung unveraendert. 5V-Buck bleibt LMR38020SQDDARQ1.

- [Ausfuehrliche Auslegung einschliesslich OC/SCP, 9V/202V, UV/OV, Thermik und Safety-Gates](LM74930_DIMENSIONING_2026-10-14.md)
- [Maschinenlesbarer 24-Pin+RTN-Netzplan und Werte-/MPN-Kandidaten](lm74930_design_v1.json)
- [Auslegungstest mit TI-Formeln und Eckwerten](../../../tools/check_trippower_lm74930_values.py) (**Python-Mathematik, KEIN KiCad ERC/DRC oder Labortest**)

**Vorlaeufig 5mOhm Shunt, RSET=50Ohm, RILIM=33,2k (nom. 3,61A), RISCP=470Ohm (nom. 5,03A), CTMR=47nF+RTMR=100k Latch-Off, UVLO ~7,52V Start, OV-Abschaltung ~35,89V.** Der Zusatzabgriff ist mit 1A als Lastziel vorbemessen; zentrale F_MAIN-Absicherung mit Temperaturderating, Leiterbahnbelastung und Fehlerstrom-I2t ist noch nicht nachgewiesen. Thermik und SOA des bestehenden STD17NF25 bei erhoehter Eingangsleistung sind **offen**. Kein Versprechen fuer ~9V-Start bei 10k-VS-Versorgung ohne Test, keine 202V/350ms-Freigabe.


## Controllervergleich 14.10.2026: Schutz mit elektronischem Circuit Breaker

[Vergleich LM74800-Q1 / LM74930-Q1 inkl. Kosten, Livebestand und TI-Referenz](CONTROLLER_COMPARE_LM74800_LM74930_2026-10-14.md).

**Ausgewaehlt fuer die neue TripPower-Platine: LM74930-Q1; Werte der Peripherie noch nicht fertigungsqualifiziert.** Gegenueber dem LM74800 bietet er OCP, schnelle Kurzschlusserkennung, Einstell-Timer, FLT und IMON. Ein gemeinsam ausgelegter Shunt **vor** der Aufteilung sichert den Gesamtpfad hinter den Schutz-FETs. VIN_PROTECTED_UNFUSED hat **keine eigene Zweigsicherung**; stattdessen ist ein gemeinsamer Sicherungsschutz der Fahrzeugzuleitung vor ALLEN TripTracer-Lasten Pflicht. Die aktive TripTracer-`01I_LM74800_INPUT.kicad_sch` bleibt bis zur verifizierten Entscheidung UNVERAENDERT. 9V-Bootstrap, Ruhestrom, passende FET-/Shunt-Werte, Gate-/OV-Sicherheit, physische PCB-Anschluesse und LCSC/DE-Beschaffung sind noch offene Gate-A/B-Punkte.

**Preisdelta nur Schutz-IC, Mouser DE Snapshot 14.10.2026:** +2,81 EUR/1pc, +2,19 EUR/10pcs, +1,88 EUR/100pcs gegenueber LM74800; OCP-Zusatzpassive/Kelvin-Shunt/QFN-Bestueckung sowie Versand/USt. kommen hinzu. Entscheidung ueber das vollstaendige Modul erst nach BOM auf gleichem Schutzumfang.


**Stand 2026-10-14: eigenstaendiger KiCad-10-Zweiseitenschaltplan EXISTIERT, aber keine eigene geroutete Leiterplatte und keine Labor-/ISO-/Fertigungs- oder Fahrzeugfreigabe.**

## Ziel

Eine **einzelne, spaeter ohne TripTracer abtrennbare und als ganzen Ordner kopierbare Platine** fuer eine 9–30-V-DC-Quelle (12-/24-V-Bordnetz) mit 5,0 V/2 A (10 W). Die Bauteile stammen soweit geeignet aus den bestehenden Hersteller-Referenzschaltungen und dem aktuellen TripTracer-Branch. Nicht mehrere unfertige Versorgungsvarianten parallel erfinden.

Der derzeitige V1-Schaltplan im TripTracer-Projekt ist weiter die **einzige aktive Schaltungswahrheit**:
- [Aktiver Eingangs-/Verpol-/OV-Schutz](../../kicad/01I_LM74800_INPUT.kicad_sch) mit TI LM74800QDRRRQ1 und zwei FETs, aber **OHNE elektronische Eingangsstrombegrenzung**;
- [Aktiver 5V/2A-Buck](../../kicad/02_5V_Buck.kicad_sch) mit LMR38020SQDDARQ1, 15µH und 3x22µF am Ausgang, EN direkt an eigenem geschuetztem VIN;
- [ACC/HOLD](../../kicad/01H_ACC_HOLD_GATE.kicad_sch) und [USB/3V3](../../kicad/03_3V3_USB.kicad_sch) gehoeren zum **TripTracer-Geraet**, nicht als untrennbarer Teil auf eine fremde Universalplatine.

**Maschinenlesbarer Vertrag:** [module_contract.json](module_contract.json). Bei Unklarheit ist `AGENTS.md` und die neueste verbindliche Hardwareentscheidung massgeblich. Inaktive/historische Tests in Docs sind kein Schaltungsfreigabenachweis.

## Hardware-Grenze / Modulanschluesse (vorgeschlagen, noch NICHT elektrisch umgesetzt)

| Signal | Richtung | Funktion |
|---|---|---|
| `VIN_FUSED` | Eingang | Von **geeignet abgesicherter** DC-Quelle; 9–30 V Normalbetrieb. Bei Fahrzeugbetrieb geeignete, ohne Entloeten tauschbare Sicherung nahe der Quelle |
| `GND` | gemeinsam | Modul- und Verbraucher-Masserueckleitung; geringe Schleifen und stern-/flaechenbewusstes Layout |
| `5V_OUT` | Ausgang | 5 V / max. 2 A. Ausgangskurzschluss-, Ueberlast-, Rueckspeisungs- und Entladeverhalten pruefen |
| **`VIN_PROTECTED_UNFUSED`** | **Pflicht-Ausgang, J302.1** | **Ungeregelte Bordnetzspannung hinter LM74930-Verpol-/OV- und gemeinsamer OCP-/SCP-Stufe, ohne separate Sicherung. Eine gemeinsame austauschbare Quell-/Leitungssicherung vor TripPower ist zwingend.** |
| `RUN_CMD` | optionaler Eingang | Ziel: 3,3-V-/5-V-kompatibler aktiver Einschaltbefehl, schwebend = AUS im gesteuerten Modus; **eigene Schutz-/Pegelstufe erforderlich**, noch nicht konstruiert |

## Verbindliche Gesamtabsicherung – genau eine Hauptsicherung in der Fahrzeugzuleitung

**Beschluss 14.10.2026:** Kein separater Sicherungshalter oder Schmelzsicherung fuer `VIN_PROTECTED_UNFUSED` auf **TripPower oder TripTracer**. Stattdessen wird **die komplette TripTracer-Versorgung** mit **einer wartbar austauschbaren, fuer 12-/24-V-Bordnetz geeigneten DC-Hauptsicherung** in der Fahrzeugleitung **moeglichst nah an der Energiequelle, VOR dem Kabel zur Elektronik** abgesichert. Diese Sicherung ist eine zwingende **Einbau- und Nutzungsvoraussetzung**, nicht Bestandteil der kleinen TripPower-Platine.

```text
Fahrzeug BAT+ --- F_MAIN (extern; Wert zu pruefen) --- VIN_FUSED / TripPower
                                                        |
                                            LM74930 + Q301/Q302
                                           OV/Verpolung/OCP/SCP
                                                        |
                                                 R301 5mOhm
                                                        |
                                        +---------------+----------------+
                                        |                                |
                                 LMR38020 5V/2A                  J302.1 VIN_PROTECTED_UNFUSED
                                        |                                |
                                     5V_OUT                    direkte Leitung/Platine zu TripTracer
                                                                         |
                                                               Zusatzverbraucher ohne
                                                               eigene Schmelzsicherung
```

**Ein gemeinsamer Leitungsschutz reicht nur dann**, wenn **jeder** Leiterbahnabschnitt, jeder Stecker und jede Leitung **hinter `F_MAIN`** – einschliesslich der 5-V-Versorgung auf ihrem jeweiligen Stromniveau und der ungesicherten Zwischenverbindung – hinsichtlich Dauerlast, hoechstem real moeglichem Fehlerstrom, **Sicherungsausloesezeit/I²t**, Kurzschluss, thermischem Verhalten und defektem/kurzgeschlossenem Schutz-MOSFET angemessen dimensioniert ist. Bei den 5-V-Leiterbahnen sind zudem die **strombegrenzenden Eigenschaften des Bucks** gesondert nachzuweisen; ein 3-A-Bordnetz-Sicherungsetikett ersetzt diese Auslegung nicht.

Der LM74930-Q1 ist **zusaetzlicher gemeinsamer elektronischer Circuit Breaker** (nominale OC-Schwelle ca. 3,61A; schnelle SCP ca. 5,03A), **keine unabhaengige Leitungsschmelzsicherung**. Bei einem Fehler am Zusatzabzweig koennen auch die 5 V ausfallen. Wenn ein Schutz-MOSFET kurzgeschlossen ausfaellt, ist allein die passend ausgelegte Hauptsicherung die verbleibende Schutzinstanz der Bordnetzzuleitung.

### Hauptsicherungswert – 3A ist nur ein Kandidat

| Last- bzw. Sicherungsfall | Wert / Schlussfolgerung |
|---|---|
| 5V x 2A, 9V Eingang, 80 % Buck-Wirkungsgrad | ca. **1,39A** Bordnetzeingangsstrom |
| Zusaetzliche 1A Last an VIN_PROTECTED_UNFUSED (Auslegungsziel) | **2,39A** zusammen bei 9V |
| **3A** 58V-MINI-Beispiel bei 80 Grad C Umgebung | typischer zulaessiger Dauerstrom nur ca. **2,0A** nach Littelfuse-Temperaturtabelle → bei voller kombinierter Last **zu knapp** |
| **4A** 58V-MINI-Beispiel bei 80 Grad C | ca. **2,7A** typischer zulaessiger Dauerstrom → weniger Temperaturreserve |
| **5A** 58V-MINI-Beispiel bei 80 Grad C | ca. **3,4A** typischer zulaessiger Dauerstrom → mehr Reserve, aber groessere zu beherrschende Fehlerenergie |

Quelle fuer die Beispieltemperaturen: [Littelfuse MINI 58V, Tabelle zum Temperatur-Derating](https://www.littelfuse.com/assetdocs/automotive-passenger-car-catalog?assetguid=613475c5-28ce-4646-a46e-0a9344b7a944). **Weder 3, 4 noch 5 A sind ausgewaehlt oder freigegeben.** Ein 3-A-Schmelzeinsatz ist auch im Kurzschlussfall *keine* feste 3-A-Strombegrenzung; der Strom kann bis zum Schmelzen deutlich darueber liegen.

**Pflichtpruefungen vor Freigabe:** tatsaechlicher Lastfall bei 9V und heissem Einbauort, Einschaltstrom, 12-/24-V-DC-Nennspannung und Abschaltvermoegen des gewaelten **austauschbaren** Sicherungstyps, Zeit-Strom-/I²t-Kurve, Fahrzeug-Kurzschlussstrom, thermische Stromtragfaehigkeit von 35µm-Leiterbahnen und Steckkontakten, thermisches Derating sowie Kurzschluss vor und hinter dem LM74930/bei defekten Schutz-FETs. **Ein normaler 32V-Kfz-Sicherungstyp ist nicht ohne weitere Pruefung als universelle 24V-Bordnetzloesung gesetzt.**

**Wortbedeutung `VIN_PROTECTED_UNFUSED`:** Nach Verpol-/OV- und **gemeinsamem** elektronischem Ueberstromschutz, **UNGEREGELT, ohne eigene Sicherung im Zweig**; lediglich durch die **verbindliche zentrale Hauptsicherung** der Quelle abgesichert. Keine Zusage zur selektiven Abschaltung des Zusatzabgriffs oder auf feste 15V.

### Bevorzugte Display-Anbindung (TripTracer, ausserhalb TripPower)

Fuer das Riverdi RVT35HITNWC00-B bevorzugen wir einen separaten **5-V-auf-LED-Konstantstrom-Boost** hinter `V5_SYS` (USB-/Buck-Umschaltung). Die Hintergrundbeleuchtung benoetigt typ. ca. **15V bei 100mA**; es handelt sich um eine LED-Last, nicht um einen frei nutzbaren geregelten 15-V-Eingang. **TI TPS61165-Q1** ist ein zu verifizierender Treiberkandidat. Bei geschaetzten 85% Effizienz beanspruchen 1,5W LED-Ausgang ca. **0,35A an 5V** innerhalb des bestehenden 2-A-Budgets. USB-Stromaufnahme, PWM, Open-LED-Schutz und EMV bleiben gesondert zu pruefen.

**Standalone statt gesteuert:** Eine spaetere klar beschriftete **hardwareseitige Bruecke `ALWAYS_ON`** soll den Wandler ohne MCU mit gesteckter Versorgung einschalten. Im TripTracer steuert eine getrennte ACC/HOLD-Anpassstufe `RUN_CMD`. Vor Schaltplan-Umsetzung der Pegelanpassung sind Funktion, Stromverbrauch, Fail-OFF und Auswirkungen auf VIN/EN verbindlich zu pruefen; eine externe MCU-3,3-V-Schiene darf **nicht** direkt die 56-V-VS-Schiene oder das Fahrzeugnetz rueckspeisen. **Eine Fehlverdrahtung von Buck-EN oberhalb Buck-VIN waere unzulaessig.**

**Bewusst NICHT auf der Universalplatine:** M8-Fahrzeugbelegung, Zeitnachlauf/TLC555, ESP32, 3V3-LDO, USB-C-/TPS2116-Umschalter, Display-Backlight, GNSS. Diese Funktionen bleiben fuer TripTracer extern am Moduladapter. Es wird **kein** Anspruch auf USB-Backfeed-Schutz durch die DC/DC-Platine allein erhoben.

## COTS FIRST – Bestand und Vergleich

Der projektweite, bereits durchgefuehrte [Hersteller-/Kaufmodulvergleich](../../../docs/COTS_POWER_SUPPLY_EVALUATION.md) ist vor dem Re-Use-Entwurf erneut gesichtet:

| Kandidat | Vorteile | Grund fuer den aktuellen Stand |
|---|---|---|
| **TI LMR38020-Q1** (ausgewaehlt) | AEC-Q100, 4,2–80 V, 2 A, EN, Buck-OC/Hiccup/TSD; vorhandener TI-400kHz-EVM/Referenzschaltplan | Bleibt Kern; hoechste Wiederverwendung aktueller KiCad-Bauteile, aber eigene PCB/EMV/Thermik weiterhin zu qualifizieren |
| RECOM R-78K5.0-2.0L | Fertiger 5V/2A-SIP3-Regler, handloetbar | 6,5–36 V und kein EN; eigener vorgeschalteter OFF-Schalter noetig; Automotive-ISO-Test-A und Eingangskurzschluss nicht dadurch geloest |
| RECOM RPH-3.0-CT | Bis 55 V, 3 A, ON/OFF integriert | 47-Pad-SMD-Modul schwieriger handzuloeten, keine vollstaendige 200V-/Fahrzeugschutzloesung |
| TI LM74930-Q1 | Integrierte einstellbare Ueberstrom-/Kurzschlussschutzfunktion neben Verpol/OV | Sinnvolle Alternative, wenn extern abgesicherter LM74800 wegen gefaehrlicher Fehler nicht qualifizierbar ist. **Keine eigenmaechtige Teileumstellung** |

Herstellerquellen: [TI LMR38020-Q1](https://www.ti.com/product/LMR38020-Q1), [TI LMR38020QEVM](https://www.ti.com/tool/LMR38020QEVM), [TI LM7480-Q1](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf), [TI LM74930-Q1](https://www.ti.com/product/LM74930-Q1), [RECOM SIP3](https://recom-power.com/de/products/switching-regulators/switching-regulators-sip/rec-p-R-78K5.0-2.0L.html).

**Kostenkontrolle:** Bestehende Einkaufsansätze sind keine aktuellen verbindlichen Komplettpreise. Fertiger Vergleich fuer **1/10/100 Stueck** muss Buck und Schutz inklusive Fuse, FETs, Kondensatoren, PCB, Handloeten/PCBA, Versand/MwSt. gegen Module bei gleichem Sicherheitsumfang stellen. Kein erdachter Gesamtpreis. Vorhandene aktive Buck-Teileliste: [5V-BOM](../../kicad/TripTracer_5V_BUCK_SELECTED_BOM.csv).

## Sicherheits- und Nachweisgates vor der eigenstaendigen Leiterplatte

1. **Input-Schutz und Fail-Safe:** LM74930 hat eine gemeinsame elektronische OCP-/SCP-Abschaltung, aber keine Schmelzsicherung. Bei FET-Fehler oder vor dem Schalter nur die externe gemeinsame Quell-Sicherung F_MAIN; diese muss Kurzschluss, DC-Abschaltvermoegen, I2t und Temperatur absichern. 200-V-Load-Dump Test A / Test B getrennt nachweisen.
2. **9-V-Kaltstart und Abschalten:** R921 10k/VS-Aufladung, D924 A→VS, heisse Transistorleckstroeme und geforderter OFF-BAT-Strom. Fuer das universelle RUN-Signal gilt **definierter, rueckspeisungsfreier Zustand**, auch wenn V5_OUT zuvor aus einem fremden USB-/Netzteil gespeist wurde.
3. **Exakte Herstellergeometrie:** U921 RTN13 **isolierte** Kupferinsel (nicht GND); FCH0650-150M-Landpattern **noch provisorisch**; EP9 von LMR38020 thermisch anbinden. 3D-Modelle nur aus realen Quellen.
4. **Schaltplan und PCB:** Erst nach Gate A/B eigener KiCad-10-Root mit **echten** Ein-/Ausgangsnetzen und Bauteilen, nur lokalen Symbolen/Footprints/3D. Native ERC **fuer das eigenstaendige Modul**; Routing mit Stroembahnen, Rueckstrom, Thermal-Vias, TVS-/Transientenpfaden und anschließend DRC. Der aktuelle `TripTracer_V1.kicad_pcb` ist hierfuer nicht die finale Modulplatine.
5. **Labor vor Fertigung/Fahrzeug:** 9/12/24/30 V x 0/0,5/1/2 A, >2A-Kurzschluss und Fehler hinter/vor Buck, 9-V-Start/Stop, 60–80-°C-Gehause-Szenarien, Ripple/Schwingen/EMV, Verpolung, getrennte ISO-Transienten und unguenstige Sicherungs-/Kabelimpedanzen. Ein passendes Modul kann bei einer Stoerung sauber abschalten; es darf nicht thermisch gefaehrlich werden.

**Thermische Vorplanung:** Bei 10 W OUT und angenommenen 85 % Buck-Wirkungsgrad entstehen ca. 1,76 W Buck-Verluste; FETs, Sicherung, Leiterbahnen und EMV kommen dazu. **2,5 W ist eine grobe Layout-Planungsreserve, keine garantierte maximale Gesamtverlustleistung.**

## Arbeitsreihenfolge nach AGENTS.md

- **Schritt 1 – abgeschlossen:** Diese Wiederverwendungs-/COTS-/Schnittstellenentscheidung versionieren. Bestehende TripTracer-Schaltung und BOM fuer diesen Planungsschritt nicht veraendern.
- **Schritt 2 – SCHALTPLANENTWURF vorhanden, nicht qualifiziert:** LM74930, RUN/ALWAYS_ON, OV/UV/Breaker und VIN_PROTECTED_UNFUSED real gezeichnet. Keine Abzweigsicherung auf beiden Platinen; stattdessen externe F_MAIN vor der kompletten Fahrzeugzuleitung und Nachweis aller Leiterbahnen/Stecker als Pflicht. Fail-OFF, Quellsicherung, VS-Start und 200V/MOSFET-SOA offen.
- **Schritt 3 – offen:** Rueckkopplung/Regelkreis, Buck-Eingangsfilter und vollstaendige 5V/2A-BO-MPN-/Footprint-/DC-Bias- und thermische Verifikation. Einzelseitiger KiCad-10-ERC/Netlist-Gate plus parallele TripTracer-Regressionspruefung.
- **Schritt 4 – TEILERFUELLT:** Separates kopierbares KiCad-10-Projekt mit Root, echten Schaltplan-Unterseiten, lokalen Symbolen/Footprints und automatischem Schaltplan-PDF erzeugt. **Eigenes PCB, DRC, 3D-Vollstaendigkeit, bestellfertige BOM und Freigabe weiterhin offen.**
- **Schritt 5 – offen:** 2- oder 4-Lagen-Auswahl anhand EMV/Thermal, Footprints, Layout, DRC, Fertigerregeln, Kosten und USB-Rueckspeiseszenarien; Labortest-/Sicherheitsreport.

**Keine fertige Platine vorgaukeln:** Der Ordner enthaelt jetzt einen echten kopierbaren KiCad-Schaltplan, **aber KEIN freigegebenes PCB oder fertigungssicheres Modul**. Die Schaltplanpruefungen ersetzen keine Hersteller-Puls-/Thermik-/FET-SOA-/ESD-/ISO-Gates.

## Kurzprotokoll Schritt 1

- Hersteller COTS erneut geprueft; bestehender TI LMR38020-Q1-Buck bleibt ohne Teile-Swap.
- Signale und klare Verantwortung zwischen Modul, Quelle und TripTracer definiert.
- Die bestehenden TripTracer-01I/02-Aktivblaetter, sein Root und PCB wurden **nicht** geaendert; separate TripPower-KiCad-Dateien gebaut und eigene KiCad-10-ERC-/Netlist-Checks im Workflow hinzugefuegt. Aktuelle CI-Ergebnisse vor einer Freigabe nachlesen.
- Offene kritische Entscheidungen sichtbar: LM74800 ohne OCP, ~9V-VS-Start, Fail-OFF und Geometrie FCH-Spule.
- Keine neue Bestellung, keine Kostenzusage, keine Fahrzeugfreigabe.
