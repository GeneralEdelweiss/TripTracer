> **REV6 – NEUER VERBINDLICHER STAND (15.10.2026):** Kein 200V/350ms- oder +125C-Vollastschutz fuer V1 mehr. 10–32V/5V2A bis Ta+60C, Abschaltung oberhalb32 bis36, begrenzter 58V/350ms-Puls bei nachweislich geklemmtem 24V-Fahrzeug, RAW0.5A-Ziel, FRAM-first/Power-Fail, kein Normalbetrieb aus RTC-Zelle. Unabhängiger COTS-Vergleich **A: TPS26631 + 100V Schottky + LMR38020 80V**, **B: TPS26600 integrated reverse + LMR38020**, **C: TPS26631 + RPH-3.0-CT**. Vorläufig A wegen 67V eFuse absmax gegen B62V und C55V-Modul; B billiger/1 Bestückposition weniger. Aber **alle noch ohne freigegebenes PCB/Schematic**, namentlich 32V-Wiederanlauf mit Schottky und 58V-Pad-Ringing, 10V Start, Ta60C 2A /+85C Fail-Off, RAW0.5A und SHDN-Kabel-/MCU-Latch sicherheitstechnisch offen. Fixed TPS26631 OVP alleine genuegt nicht fuer 32V-Restart! Datenblattbasierte externe OVP-Teiler 100k/3.78k (A), 100k/3.74k (B), 0.1%, vorläufig berechnet. **Abnahme-Mess-/Sicherheitsmatrix: [REV6_BENCH_AND_NATIVE_GATE_MATRIX_2026-10-15.md](REV6_BENCH_AND_NATIVE_GATE_MATRIX_2026-10-15.md). Aktuell massgeblich:** [REV6-COTS-Entscheidung](REV6_COTS_ARCHITECTURE_DECISION_2026-10-15.md), [real gepreiste aber unvollständige BOM-Scope](REV6_COTS_VENDOR_BOM_SCOPE_2026-10-15.csv), [13 native Python-Grenzwerttests](rev6_protection_gates.py), [tatsächlich erfolgreich gelaufener GitHub-CI](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38812555462). Keine KiCad10-ERC/Netlist, 58V/350ms oder 60C-Hardwareprüfung erfolgt. Alle folgenden C1/C2 und R6-200V Berichte sind historische NO-GO-Dateien. 

> **WEG C ROUND 6 (15.10.2026) – COTS-RESET, KEINE FREIGABE:** Drei grundverschiedene Herstelleransätze untersucht: TLD8S36AH Load-Dump-TVS-Shunt, MAX16126 200V-Referenz-Abschaltung und LTC4366H-2 Surge-Stopper mit Timer. Alle bleiben aufgrund 200V/350ms-Energie-/F_MAIN-DC-Abschalt-/125C-/Einzelfehler-Gates **NO-GO fuer eine fertige Versorgung**. Neu: Power-Fail und rueckspeisefreie Backup-Notdomäne auf TripTracer, PWR-38–43, CR1220 nicht ungeprüft als SD-Energiespeicher einsetzen. Maßgebliche neue Entscheidung: [R6_COTS_RESET_DECISION_2026-10-15.md](R6_COTS_RESET_DECISION_2026-10-15.md); [verifizierbare EU-Teilpreise](R6_VENDOR_PRICE_SNAPSHOT_2026-10-15.csv), [positionsweise Vollumfang-Scope mit bewusst gesperrten TBDs](R6_ARCHITECTURE_POSITION_SCOPE_UNRELEASED.csv), [ausführbare Testrechnung](r6_independent_gates.py). Neue unverfälschte Lösung/Schaltplan erst nach P0-Gates. Die folgenden C1-/C2-Designtexte sind historische No-Go-Unterlagen.

> **NEUESTE WEG-C-ENTSCHEIDUNG (15.10.2026): AUCH C2-HV NO-GO.** Die 80V/4A-LM70840-Q1-Alternative mindert die normale Abschaltgrenzenproblematik, **aber** ein Drain-Source-Kurzschluss des eingangsseitigen 300V-FETs fuehrt 200V ueber die Bodydiode des zweiten FET direkt zum nur 67V-abs-max-eFuse-Eingang. Die 200V/350ms-/Zener-Kurz- und Unterbrechungsfehler sowie +125C-Last und Sicherungskoordination sind nicht geloest. Kein C2-PCB/Schaltplan als sicher freigegeben. Hier die massgebliche [C2-HV-Sicherheits-, Bauteil- und Kostenentscheidung](C2_HV_SAFETY_COST_DECISION_2026-10-15.md), [25 TI-Hersteller-Referenzpositionen](C2_LM70840_REFERENCE_PARTS_SCOPE.csv) (**TI-Beispiel fuer 8A, kein 4A-Release**), [belegte C2-HV-Teilkosten](C2_HV_VERIFIED_PRICE_PARTS_2026-10-15.csv) und [automatisierte Rechentests](c2_hv_gate_checks.py). Erster [GitHub-Actions-Lauf](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38748545904) bestaetigte 11/11 mathematische Regressionen; keine nativen C2-KiCad10/ERC/PCB- und keine Hardwaretests.

> **AKTUELLE SICHERHEITSENTSCHEIDUNG 15.10.2026: C1 NO-GO / KEINE BESTELLUNG.** Der AP74502HQ mit bisherigem 1M/39k-OVLO-Teiler garantiert weder Wiederanlauf bei 30V noch trotz 1us nomineller GATE-Abschaltung sicheren Betrieb des TPSM33620S5 (40V abs). Schwere TPS26631-SHDN-Fehlverdrahtung wurde korrigiert. Es fehlt zudem ein nachgewiesener Q1-D/S-Kurzschluss-Schutzpfad, die 200V-Energie sowie 125C-Thermik. Pin-Audit: [C1_SURGE_AUDIT_2026-10-15.md](C1_SURGE_AUDIT_2026-10-15.md). Neue unabhaengige Entwicklungsrichtung: [C2_HV_80V_ALTERNATIVE_2026-10-15.md](C2_HV_80V_ALTERNATIVE_2026-10-15.md). **Die folgenden C1-Praeferenzen sind historische erste Studien und keine aktuelle Bauempfehlung.**

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
3. Schutzversorgung 10.2-kOhm-Vorwiderstand (2x 5.1k): 1.922 W fuer 350 ms (0.673 J), Zener 0.824 W/0.288 J bei angenommener 60-V-Klemme. **Nicht** ohne spezifizierte Pulsbauteile freigeben.
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
- Infineon Vishay SQM35N30-97_GE3 300-V-HV-FET-Kandidat: https://www.infineon.com/part/SQM35N30-97_GE3

## Zusammenarbeit

Dieser Branch gehoert nur Weg C. Keine A-/B- oder REV5-Bauteil-/Schaltplaene uebernehmen oder veraendern. Projektregeln in AGENTS.md, aber hier gilt die explizite Neuentwicklungsanweisung. Herstellerbeispiele werden nicht als ISO-/Fahrzeug-Nachweis ausgegeben.
