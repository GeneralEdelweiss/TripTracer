# TripPower Weg C – unabhaengiger COTS-Entwurf (15.10.2026)

**Status:** Schaltungsarchitektur als eigenstaendige Ingenieurvariante ausgewaehlt; **keine Fertigungs-, Fahrzeug- oder 200-V-Prueffreigabe**. Weg A, Weg B und bestehender REV5 sind unveraendert.

## Technischer Auftrag

9–30 V DC Dauerbetrieb; Ausgang 5.0 V / 2 A; unabhaengig als 1-A-Nennlast nutzbarer geschuetzter RAW-Ausgang; 12/24-V-Bordnetz; -40 bis +125 °C Umgebung; selbststaendiger Wiederanlauf bei 30 V nach OV; Ueberleben von 200 V fuer 350 ms ungedaempft, Abschaltung zulaessig; externer austauschbarer F_MAIN; OFF-Gesamtsystem <100 uA; ACC-Einschaltung und RUN_CMD-Selbsthaltung, USB-only ohne Rueckspeisung.

## Unabhaengiger Marktentscheid

Ausgewaehlte **vorlaeufige Referenzarchitektur C1**:
  
```text
 Fahrzeug BAT+  -> externe austauschbare F_MAIN -> J_BAT_IN
                                                |
                   AP74502HQ (OVLO/UVLO/RPP/EN, eigene geklemmte IC-VIN)
                                                |
                         2x Back-to-back 300-V-N-MOSFET
                                                |
                             TPS26631 (eFuse, gemeinsames Stromlimit)
                                                |
                          +---------------------+------ RAW_PROTECTED (1 A Nennlast)
                          |
                 TPSM33620S5-Q1 (5 V, 2 A, Induktivitaet integriert)
                          |
                       +5V_MAIN
 ```

AP74502HQ ist **kein** 200-V-direktversorgbarer Baustein. Seine VIN muss gemaess Hersteller-Surge-Schaltung ueber impulsfesten Widerstand und geprueften Zener/TVS unterhalb der Pin-Grenze gehalten werden. OVLO misst die urspruengliche Fahrzeugspannung. Die beiden externen MOSFETs muessen jeweils 200 V plus Schaltueberschwinger aushalten; nur ein hoher VDS-Aufdruck reicht nicht. eFuse und Buck werden **erst hinter** den abgeschalteten MOSFETs betreiben; ihre 60-V/36-V-Eingangsgrenzen duerfen beim Lastabwurf nicht erreicht werden. Kein Gueltigkeitsnachweis dafuer ohne Hardwarepruefung.

Der RAW-Zweig und der Buck teilen **ein** vorgeschaltetes elektronisches Stromlimit. Der RAW-Ausgang ist dadurch **nicht separat auf 1 A begrenzt**. Deshalb muessen J_RAW, seine Leiterbahnen und gegebenenfalls Anschlusskabel fuer das **volle gemeinsame Fehlerstrom-/Pulsprofil** ausgelegt sein. Falls das nicht moeglich ist, wird eine zweite begrenzende Lastschalterstufe erforderlich.

## Drei grundverschiedene Umsetzungsvarianten

| Variante | Hochvoltschutz | Strom-/Kurzschlussschutz | 5 V / 2 A | Charakter |
|---|---|---|---|---|
| **C1 (vorlaeufig bevorzugt)** | AP74502HQ + 2 HV MOSFET | TPS26631 eFuse | TPSM33620S5-Q1 (Induktivitaet integriert) | Beste Ausgangslage bei Bestueckungszahl und IC-Kosten, thermisch bei +125 C **nicht verifiziert** |
| **C2** | AP74502HQ + 2 HV MOSFET | TPS26631 eFuse | LMR43620RS5-Q1 + diskrete Induktivitaet | Frequenz-/Thermikoptimierung moeglich, hoeherer Layout- und Bestueckungsaufwand; Verfuegbarkeit eingeschraenkt |
| **C3** | LTC4366H-2 Surge-Stopper + HV MOSFET (+ Rueckpolschutz) | TPS26631 eFuse | TPSM33620S5-Q1 | Hoher Hochvolt-Spielraum am Schutzcontroller, aber wesentlich teurer und Nachweis externer FETs trotzdem erforderlich |

Ein fertiges RECOM-R-78K-5V/2A-Modul wurde geprueft, scheitert als direkte Empfehlung an der erforderlichen +125-C-Vollastqualifikation. Alternative COTS-Hochvolt-Regler mit 200-V-direktem Eingang sind in dieser Groesse/Preisregion nicht als risikolos geeigneter, 5-V-/2-A-/RAW-1-A-Komplettbaustein identifiziert.

## Warum C1 trotz offener Risiken?

- Der AP74502HQ integriert Verpol- und Ueberspannungsabschaltung, anstatt ein selbst entworfenes Komparator-/Relais-/Zener-Logiknetzwerk aufzubauen.
- TPS26631 integriert einen 31-mOhm-Leistungspfad, Kurzschluss-, Stromlimit- und Thermalschutz, Auto-Retry konfigurierbar.
- TPSM33620 integriert Buck-Schalter, Spule, Bootkapazitaet und weitere Funktionen bei nur wenigen Aussenbauteilen.
- **Kein** Zugestaendnis bei 200 V oder +125 C: C1 bleibt *vorlaeufig*, bis Pulsenergiemargen, Abschaltdynamik, thermisches Derating und Einzelbauteilfehler nachgewiesen sind. Falscherweise als fertig freigeben waere teurer als ein sorgfaeltiger Prototyp.

## Elektrische Schnittstelle (noch konzeptionell; keine Pinout-Freigabe)

| Netz | Richtung | Bereich/Zustand | Pflicht |
|---|---|---|---|
| BAT_FUSED_IN | Eingang | 9–30 V, 200 V/350 ms Puls | Vorher externe **auswechselbare** DC-bemessene F_MAIN nahe Einspeisung |
| ACC_SENSE | Eingang | geschaltete Fahrzeugspannung 0/9–30 V und transiente Peaks | Eigener geschuetzter Spannungsteiler/Isolierung; niemals direkt MCU-3V3 |
| RUN_CMD | Eingang | 3.3-V-MCU-Logik | Darf nur nach initialem ACC-Start halten; definiertes Low bei Reset; bei USB-only keine Rueckspeisung |
| RAW_PROTECTED | Ausgang | hinter HV-Abschaltung **und gemeinsamer eFuse**, 0–30 V | 1 A normal, PCB/Stecker fuer gesamten gemeinsamen Grenzstrom auslegen |
| +5V_TRIPPOWER | Ausgang | 5 V, 2 A | USB Power-MUX/Ideal-Diode **auf der Hauptplatine**, BAT/USB nicht direkt parallel |
| GND | gemeinsam | Fahrzeugmasse | Strompfad, Stern-/Rueckfuehrung und EMV im PCB pruefen |

**AUTO:** ACC aktiviert Controller; RUN_CMD wird fuer kurzen SD-Abschluss ueber qualifizierte Pegelanpassung ODER-verknuepft; bei beiden Low Abschaltung. **RUN-Variante:** separat bestueck-/konfigurierbar, darf bei fehlendem BAT keine Spannung erzeugen. Kein fest vorgegebener Timer, da Ausfall der MCU als harmloser Reset akzeptiert wird; fuer Dauerhalt bei MCU-Absturz muss jedoch ein begrenzender Hardware-Timeout separat geprueft werden. USB-only versorgt nur die 5V-Domaene auf der TripTracer-Hauptplatine und darf niemals den RAW-Ausgang speisen.

## Offene FREIGABESTOPPS

1. Genaues AP74502HQ-Pin-/OVLO-/EN-Verhalten bei 9 V, bei 200 V/350 ms und Rueckkehr zu 30 V; High-Ohm-Teiler inklusive Leakage/Temperatur.
2. 200-V-Quelle definieren: Wellenform, Quellimpedanz, Kabelinduktivitaet; 200 V ist **kein** Ersatz fuer Pulsenergie. Ausschaltspitzen und 300-V-MOSFET-SOA, Hot-RDSon und Gate-ESD.
3. Schutzversorgung 10-kOhm-Vorwiderstand: nominal 1.96 W fuer 350 ms (0.686 J), Zener nominal 0.84 W/0.294 J bei 60-V-Klemme. **Nicht** ohne spezifizierte Pulsbauteile freigeben.
4. eFuse-Limit und Leitungs-/Steckerstroeme: 2-A-5-V-Buck erfordert bei 9 V ca. 1.2–1.35 A plus RAW 1 A; Fehlerstrom kann hoeher sein als 1-A-RAW-Nennlast.
5. Kritischster Kompaktheitsengpass: TPSM33620 mit maximaler 5-V-/2-A-Last bei +125 C und VIN=30 V. Thermisch gerechnet und an realem Board zu messen; TI-Junction max 150 C.
6. System OFF <100 uA inklusive OVLO-Teiler, Controller-Leckstroemen, ACC, MUX und MCU bei +125 C. Keine 100k/3.5k-Dauerteiler unbedacht einsetzen.
7. ACC-Eingang transientsicher, USB/M8-Rueckspeisung in allen 0/1-Kombinationen, definierter Reset und MCU-Ausfall.
8. KiCad 10 nativer ERC + Netlist, Hersteller-Pinout/Footprint, PCB/DRC, Puls-, Kurzschluss-, Thermik- und Wiederanlauf-Labortests. **Nicht erfolgt.**

## Quellen (nur verifizierbare Produktseiten und Datenblaetter)

- Diodes AP74502Q/HQ, Herstellerbeispiel 200-V-Surge-Stopper: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf
- TI TPS2663x: https://www.ti.com/lit/ds/symlink/tps2663.pdf
- TI TPSM33620-Q1: https://www.ti.com/product/TPSM33620-Q1
- TI LMR43620-Q1: https://www.ti.com/product/LMR43620-Q1
- ADI LTC4366-2: https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf
- Infineon AUIRFS6535 300-V-HV-FET-Kandidat: https://www.infineon.com/part/AUIRFS6535

## Zusammenarbeit

Dieser Branch gehoert nur Weg C. Keine A-/B- oder REV5-Bauteil-/Schaltplaene uebernehmen oder veraendern. Projektregeln in AGENTS.md, aber hier gilt die explizite Neuentwicklungsanweisung. Herstellerbeispiele werden nicht als ISO-/Fahrzeug-Nachweis ausgegeben.
