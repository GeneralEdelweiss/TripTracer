# TripPower Weg D – Round 10: TPS26631 Hersteller-SPICE-Versuch, 58V-Eingangsgrenzen, Laborplan (2026-10-16)

**Entscheidung:** **KONDITIONALER LABOR-GO** für den vorhandenen Weg-A-TPS26631-Prototyp; **NO-GO für PCB-/Automotive-/Serienfreigabe**. Das offizielle TI-PSpice-Makromodell wurde in diesem Durchlauf **nicht ausgeführt**. Ein unabhängiges TI-Formel-Screening und ein **ausgeführtes passives RLC-Netzwerk** belegen potenziell unzureichende Spannungsreserven; das ist keine Vorhersage einer konkreten Fahrzeuginstallation. Keine LTC4368-Schaltung und keine zusätzliche TVS ohne belegte Vorteile.

## 1. Verbindliche Primärdateien und jüngste echte Weg-A-Schaltung

Gelesen: AGENTS.md, docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md, docs/HARDWARE_REQUIREMENTS.md PWR-44–56, docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md, Weg D Round 9 und FINDINGS_LOG.md. Die aktuellen Weg-A-Dateien wurden auf design/trippower-a einzeln gelesen: 01_TPS26631_REV6.kicad_sch, 02_5V_LMR38020_REV6.kicad_sch und REV6_A_25_PART_ORDER_BOM_2026-10-15.csv im Ordner hardware/modules/TripPower_REV6_A/.

**Aktueller elektrischer Ist-Stand:** U201 TPS26631PWPR, Q201 SQM100N10-10_GE3 (100V/VGS±20V), Q202 BSS138LT1G (50V/VGS±20V). R201=100kΩ, R202=12,0kΩ (Panasonic ERA-8AEB123V), R203=4,22kΩ, R204=6,04kΩ (Ilimit ~3A). C201=KEMET C1210C105K1RACAUTO 1µF/100V an **IN_SYS nach Q201**, C202 identisch an U201 OUT, C203=100nF an dVdT. U101 TI LMR38020SQDDARQ1 mit C101+C108=2×4,7µF/100V KYOCERA AVX 12101C475K4Z2A und C107=100nF/100V am Buck-Eingang; C104–C106=3×22µF/25V Taiyo Yuden MCAST32MSB7226KPNA01 am 5V-Ausgang, L101=Bourns SRP7050TA-150M **15µH, Isat6A / Irms3,5A**. Die tatsächlichen effektiven Kapazitäten unter DC-Bias @58V/Temperatur/Alterung sind **nicht nachgewiesen**.

**Wichtige Korrektur zu D Round9:** Die aktuelle A-CSV nennt mittlerweile **R202=12,0kΩ ERA-8AEB123V**, also dieselbe MPN/Wert wie im Schaltplan. Der frühere CSV-Schaltplan-Differenzbefund ist **behoben**. Auch der 15µH-Induktor ist nun ein konkret benannter Bourns-Typ. **Weiter offen**: TI TPS2663 Rev G §9.4 fordert bei externer Reverse-FET-Beschaltung **mindestens 300kΩ zwischen IN_SYS und UVLO**; die aktuelle A-Schaltung hat dort R201=100kΩ. Nicht blind R201 austauschen, da 10V UVLO und 32–36V OV zugleich neu berechnet werden müssen.

## 2. Offizielles Hersteller-SPICE: wirklich versucht, aber nicht ausgeführt

**HERSTELLER:** TI TPS2663 PSpice Transient Model (Rev A), Identifikation **SLVMD03A.ZIP, etwa317KB**, offizieller Herstellerdownload https://www.ti.com/lit/zip/SLVMD03 ; Produktseite https://www.ti.com/product/TPS2663 . Herstellerdatenblatt TI TPS2663 Rev G https://www.ti.com/lit/ds/symlink/tps2663.pdf .

**Ausgeführte Prüfungen:** Herstellerlink im Web-Dokumentwerkzeug aufgerufen → ZIP-Inhalt dort nicht lesbar, Fehlermeldung **unsupported content-type: application/zip**. Downloadversuch über Container → **download failed**; zusätzlich curl -IL auf TI → **curl(6) Could not resolve host: www.ti.com**. Lokale binäre Befehle ngspice, Xyce, PSpice, wine und LTspice geprüft: **nicht installiert**. NumPy/SciPy in lokaler Python-Laufzeit dagegen vorhanden.

**Darum: KEIN offizielles TI-Makromodell gerechnet; KEINE konkrete ngspice-Inkompatibilität festgestellt.** Ohne extrahierte LIB/OLB könnte eine Diagnose zu PSpice-ABM-Syntax oder Konvergenz nur erfunden werden. Präziser nächster Vorgang auf einer internetfähigen Windows-Workstation: TI-SLVMD03A.ZIP laden; Quelle, SHA256, korrekten TPS26631-Subcircuit, Pinmapping, Modellvariante, PSpice-for-TI Version und Simulationsergebnisse inklusive Transienten-/Fehlerfälle dokumentieren. Portierung nach ngspice erst mit realer ZIP und einem tatsächlichen Parser-/Simulationslog; nicht stattdessen eine eigene Verhaltensstromquelle als „TI-Modell“ ausgeben.

## 3. HERSTELLERBELEG für die gefährliche Abschaltspitze

TI TPS2663 Rev G §9.5.1 Gleichung 14 aus tatsächlichem Datenblatt:
**Vpeak ungefähr Vsource + Iload × sqrt(Linput/Cinput)**.

TI warnt explizit, dass eFuse-Stromabschaltung bei Eingangsinduktivität positive Spitzen erzeugt, welche Absolute-Maximum überschreiten können. Eine lokale Eingangskeramik, kurze GND-Stromschleifen, ggf. richtig qualifizierte TVS sind Gegenmaßnahmen. Die Formel ist eine **Näherung ohne ESR/ESL/R-Loss/MOSFET-Gate**, kein garantiertes reales Maximum. Bei einem 350ms-VIN=58V-OFF-Plateau fließen womöglich 0A durch die eFuse; Iload und VIN=58 dürfen daher **nur als hypothetische Worst-Case-Überlagerung** verwendet werden, nicht als reale Gleichzeitigkeit behauptet.

| L angenommen | I-Abschaltung | effektive C | TI-Näherung ab58V | Ceff nötig für maximal60V |
| --- | ---:| ---:| ---:| ---:|
| 0,8µH | 1,75A | 0,5µF | **60,21V** | **0,613µF** |
| 0,8µH | 3,0A | 0,5µF | **61,79V** | **1,800µF** |
| 5µH | 1,75A | 0,5µF | **63,53V** | **3,828µF** |
| 5µH | 3,0A | 0,5µF | **67,49V** | **11,250µF** |

Ceff≥L×(I/(60−58))² gilt **nur** im idealisierten TI-Screening. 60V ist die EMPFOHLENE Betriebsgrenze, 67V Absolute-Maximum keine Dauer-/Wiederholreserve. Ein 58V-Bordnetztypenschild garantiert an TPS-Pins keine 58V.

## 4. Zweiter, gesondert ausgeführter Nachweis: passives Source-Step-RLC

Neu auf Weg D: [tps26631_ti_eq14_passive_step.py](tps26631_ti_eq14_passive_step.py), [zugehörige Tests](test_tps26631_ti_eq14_passive_step.py). Passive zwei Zustände, Serien-R+L -> Ceff, eFuse bereits OFF, 32→58V Quellenflanke, per RK4 integriert. **Kein TI TPS26631-Makromodell und keine Q201/LMR-Hochfrequenzschaltung!** Ceff/ESR/ESL-Herstellerdaten weiterhin offen. Im separaten Round9-Modell wurden eFuse-Kurzschluss-/OFF- und Buck-Kopplungsfälle als vereinfachte Annahmen modelliert, nicht als Hersteller-Spice.

**Entscheidende Messgrenze:** Wenn die SOURCE des Passivmodells die **M8-Buchse mit nachgewiesenem ≤58V(t)** ist, darf die modellierte Induktivität L nur **hinter M8** (Kontakt, Q201, PCB) angesetzt werden. Wenn man stattdessen 0,8–5µH Kabel vom Generator bis M8 eingibt, modelliert man einen anderen Quellknoten, dessen M8-Ringing **zusätzlich** überprüft werden muss. **58V am Generator ist nicht 58V am Stecker**.

**LOKAL AUSGEFÜHRTE Passive-RLC-Szenarien, keine Messungen:**

| Hypothese | Flanke32→58V | IN_SYS-naher reiner C-Peak |
| --- | ---: | ---: |
| 0,8µH / 0,4Ω / 0,5µF (nur falls diese L ab dem gewählten Source-Knoten gilt) | 20µs | **58,62V** |
| dieselbe | 1µs | **72,14V** |
| M8→IN_SYS Beispiel 0,05µH / 0,08Ω / 0,5µF | 1µs | **59,83V** |
| gleiche lokale L/R/C, schnellere Flanke | 0,2µs | **74,28V** |

Dies ist **nicht** der TI-Induktivitätsstromabriss: Startstrom hier=0; schnelles Aufladen kann hohe simulierte Ströme erzeugen, reale Quellstrombegrenzung/Groundbounce/ESL/Bodydiode sind nicht enthalten. Größere Ceff macht bei einem endlichen Quellflankenprofil den Überschwinger nicht zwingend monoton kleiner. **288 Szenarioeingaben** (L=0,02/0,05/0,2/0,8/2/5µH, Ceff=0,2/0,5/1/2µF, R=0,08/0,4/1Ω, Flanke=0,2/1/5/20µs): **139/288 >60V, 88/288 ≥67V** ausschließlich im passiven Modell, keine Häufigkeits-/Zuverlässigkeitsstatistik. **9 lokal ausgeführte Python-Rechen-/Integrationschecks erfolgreich**; noch kein belegter GitHub-Actions-Run.

Reproduktion im Repository-Root ohne externe Python-Abhängigkeit:
- python3 hardware/modules/TripPower_5V2A/weg_d/tps26631_ti_eq14_passive_step.py
- python3 hardware/modules/TripPower_5V2A/weg_d/tps26631_ti_eq14_passive_step.py --sweep > round10_sweep.json
- python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_d -p test_tps26631_ti_eq14_passive_step.py -v

**Alter Round9-Sweep (60/144 über60V, 2/144 ≥67V) ist ein ANDERES Modell:** eFuse-OFF-Timing + Buck/RAW, kein kombinierter statistischer Datensatz mit den neuen 288 Passiv-Flankenfällen.

## 5. Die neun kritischen Fehler-/Lastszenarien

1. 10V-Start: A-ILIM ca3A, 5V2A + RAW0,5A, Buck wirklicher Wirkungsgrad, Inrush, TI-spezifisches Hot-SOA und L101 Isat. Das alte reduzierte RLC ist **kein vollständiges LMR-Buck-Schaltmodell**.
2. 32→36V/400ms: A-OVP steigt nominal über32, Schalt-/FAULT-Delay keine gemessene Gate-Sperrzeit.
3. 32→58V/350ms: TI Eq14 Stromabriss und separates passives M8-Flankenmodell, A-C201eff/ESR/ESL und f_event/10 Wiederholungen offen.
4. **58→32V-Restart: aktiver P0-Fehler.** R201100k/R20212k/R2034,22k: TI-Ovfall=1,09..1,15V, Rising1,176..1,224V; gezeichneter Teiler ohne leakage: Falling ~30,02..31,67V. Automatischer Restart bei exakt32V **nicht garantiert**. Zudem I_OVP±150nA und R-/Temp-Toleranzen. Ein einzelner idealer Teiler könnte beide unabhängigen Grenzbedingungen Rising≤36V und Falling>32V nur im k-Fenster 0,034000..0,0340625 erfüllen (0,184% Gesamtbreite **vor** Widerstand/Leck/Temperatur). Keine automatische Reparatur durch größeren MLCC.
5. Kurzschluss 10/32/58V: TI overload/current limit, 2x-IOL-Pulse und thermische Abschaltung nicht real simuliert; bei58V OVP bereits OFF, außer Fehlerfall.
6. Kabel-L-Variation: Quell-R/L **bis M8** und örtliche Induktivität **ab M8** im Labor getrennt messen.
7. C201/C202/C101/C108: tatsächliche Ceff @58V/Ta, MLCC ESR/ESL und Charge/Discharge getrennt; nominell100V rating heißt nicht Nenn-C bei58V.
8. Q201 D-S-Kurz/OPEN sowie Q202-Gatepfad: U201 kann bei Q201-Kurz weiterhin OVP abschalten, **Verpol-/Rückstromsperre entfällt**; MAX Q201 VDS100V/VGS±20V, Q202 VDS50V/VGS±20V, nicht mit U201 max67V gleichsetzen.
9. U201 interner FET D-S-SHORT: bis58V Eingang ggf direkt an 80V-Buck/RAW/USB-Pfade; funktionelle OV-Unterbrechung weg, Fahrzeug-F_MAIN hilft nicht notwendig bei thermisch heißen Fehlern unter Sicherungsstrom.

**Alle 29 erforderlichen Messdomänen:** [ROUND10_58V_PAD_STRESS_MATRIX_2026-10-16.csv](ROUND10_58V_PAD_STRESS_MATRIX_2026-10-16.csv). Physikalische PIN-MAX über 350ms für IN1–3, IN_SYS6, BGATE4, DRV5, OVP8, UVLO7, SHDN13, OUT18–20, Q201 D/G/S und Q202 G/D/S, C201/C202/C101/C108, Buck VIN/SW/BOOT **nicht aus dem Passivmodell bestimmbar**. Ergebnisse dieser Pins dürfen nicht erfunden werden. TI IN/IN_SYS ≤60V recommended /67V absolute, OUT/UVLO/PGOOD/FLT/PGTH ≤60 recommended/67 absolute; BGATE-GND81 / BGATE−IN_SYS14 abs, DRV-GND72 / DRV−IN_SYS20 abs, OVP/dVdT/IMON/MODE ≤4V recommended/5,5 absolute; SHDN≤5V recommended/5,5 absolute; Q201100V, Q20250V, LMR VIN80 recommended/85 absolute, SW und BOOT separat datenblattabhängig.

## 6. Kleinste Gegenmaßnahmen

**Zuerst** 58V M8-Worst-Case-Quelle inklusive R/L, Flanken und Verpol-MOSFET-Laden qualifizieren; A-OVP-Restart/UVLO-R201300k-Herstellerhinweis beheben; Hersteller-C201eff bei58V/Temperatur beschaffen. **Danach** möglichst kurze Schleifen Q201D→U201IN, Q201S→U201 IN_SYS→C201→GND, Q202 nahe Q201G/S, GND-Plane und schalt-/reglerseitige Ground-Separation, kurze MLCC-HF-Verbindungen. Falls nötig ein gezielt RC-gedämpftes Netz (kein teurer Hochvolt-LDO/200V-TVS, kein stromfressender Inline-Widerstand) mit R/C-Worst-Case-Energie. Erst bei echten Labordaten über60V trotz optimierten Layouts und sauberer Dämpfung alternative Schutzarchitektur wie LTC4368 bewerten **einschließlich VOUT/SENSE80V und externem MOSFET-SOA**, nicht nur dessen 100V-VIN-Rating.

**Keine pauschale 58V-SMBJ-TVS**: deren VC bei qualifiziertem Surge-Strom schützt TPS26631 unter67V gerade nicht automatisch. F_MAIN/Halter bleibt **externer Fahrzeug-/TripTracer-Kabelschutz**, niemals auf dem TripPower-Modul; keine Einmal-SMD-Fuse und keine nutzlose PPTC.

## 7. Konkreter ausführbarer Labor-Prüfplan

**Testgerät/Schutz:** Professionelle DC-Transientenquelle / ISO16750-2 Test-B-Generator mit programmierten10/32/36/58V und **am M8 wirklich ≤58V inkl Ringing**, Quelle Rsrc_min/max, Stromlimit, Fern-/Not-Aus und berührungsgeschützte Prüfzelle. Beispiel Pulse 58V×5A×350ms=101,5J, 58V×10A×350ms=203J **nur Leistung-Zeit-Energieoberhülle** ohne vorgeladene Cs/L; Kurztest immer zuerst energiereduziert und sicher abgeschirmt. Externe DC-taugliche F_MAIN/Halter und BAT-/ACC-Kabelschutz ausschließlich Quelle/Harness.

**Fixtures/Quellgrenze:** kurze0,5m und lange3m M8-Testkabel, jede R_DC, L(f) incl Rückleiter und Kontakt-R messen; Quelle Rise/Fall z.B 0,2/1/5/20/100µs nur falls der Generator sie beherrscht, mit gemessenem M8-I/V statt nur Setpoint. Unterschiedliche C201-Ceff-Lose/Temperaturen; Groundloop/Schraube nicht als Modellkabel fingieren.

**Messgeräte:** ≥100MHz Oszilloskop ≥500MS/s als erste Laborstufe, gut kalibrierte differenzielle Spannungssonden mit geeigneter tatsächlicher Bandbreite/Pegel-Isolierung, DC-fähige HF-Stromzange (Richtwert≥5MHz) oder qualifizierter Kelvin-shunt, Zeitkorrelation von Strom/Pin. Bei 0,2µs Flanken bzw ns-Gate-Peaks Sonden-/Scope-Bandbreite erhöhen oder Bereich ausdrücklich als nicht aufgelöst deklarieren; nie gemeinsame Scope-Masse an Plus/Gate/Schalter legen.

**Pflichtmesspunkte:** M8 BAT/GND, vor/nach externer Fahrzeug-Fuse, Q201 D/S/G, Q202 D/S/G, U201 TPS IN1–3, IN_SYS6, OUT18–20, BGATE4 zu GND UND zu IN_SYS, DRV5 zu GND UND zu IN_SYS, UVLO7, OVP8, dVdT10, ILIM11, SHDN13, PGOOD/PGTH/FLT, C201/C202 positive/negative Pads, Buck U101 VIN/SW/BOOT/PGND, C101/C108, RAW0/0,5A, USB VBUS, PWR_FAIL/FRAM. JEDEN Messpunkt mit seiner eigenen Pin-Datenblattgrenze prüfen.

**Läufe:** -20/+25/+60°C 5V0/1/2A, RAW0/0,5A; 10V Start; 32→36V 400ms; 32→58V 350ms / Wiederholung ≥10x und definierter Abstand; 58→**32V exakt** Recovery; Soft-/Hart-Kurz10/32/58V (58V normalerweise OVP-OFF), M8-plug/unplug über geschützte Fixture; Reverse-Q201-/Q202-/U201-FET Einzelfehler mit stromlimitierter Quelle; -20..+70°C Betrieb/Derating, +85°C safe-off (eigene Temperaturabschaltung fehlt im jetzigen A-Prototyp); USB-only/ACC-HOLD, FRAM-first (kein M8-Stromabzug-Vorwarnversprechen).

**PASS:** Alles innerhalb der **recommended** TI-Pingrenzen inklusive Probe-Messfehler/Temperatur/Losstreuung (z.B. interner Engineering-Zielwert VIN_SYS peak≤59V, wenn nachweislich max1V Gesamtunsicherheit besteht, kein TI-Datenblattlimit), niemals 67V abs beanspruchen; sichere automatische OVP-Abschaltung vor36V UND ON bei32V nach voller Pulswiederkehr, 10V/2A Betrieb, keine MOSFET-VGS-/ESL-/Buck-SW-/Gate-Überschwinger über Max, keine Rückspeisung, RAW-Überstrom-/F_MAIN-Kabel-/PCB-Schaden, +85°C sicher aus und FRAM konsistent. **FAIL** bei einem relevanten Überschreiten, fehlendem Restart oder gefährlicher Fehlerenergie. **NICHT GETESTET = OFFEN / keine Freigabe**, weder ein positives Python-Passivmodell noch ein späteres grünes ERC ersetzt die Labor-/Temperatur-/FMEA-Prüfung.

## 8. Abschließende Architekturentscheidung

**TPS26631/Weg A bleibt die priorisierte Prüfgrundlage** mit wenig Aufwand und kleinen gezielten Layout-/Kapazitätsmaßnahmen. Der entscheidende Safety-Bottleneck ist derzeit **nicht allein eine hypothetische 58V-RLC-Spitze**, sondern zusätzlich der nach Hersteller-Min/Max **nicht garantierte 32V-Restart** und die 300k-UVLO-Vorgabe. Erst wenn sich im realen M8-/PCB-/Hersteller-SPICE-Test trotz kontrollierter Flanken und Dämpfung ein nicht beherrschbarer U201 >60V-Stress ergibt, werden LTC4368/Alternativen gezielt gegenüber Mehr-BOM und Pin-/MOSFET-SOA geprüft. **Keine KiCad-/PCB-Fertigungsfreigabe, kein durchgeführtes TI-SPICE-Makromodell und keine 58V-Hardwaremessungen.**
