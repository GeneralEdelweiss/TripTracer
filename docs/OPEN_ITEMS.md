# TripTracer – offene technische Prüfungen


## Neuer Prüfschritt 14.10.2026 – Kaufmodule vor Eigenentwicklung

**Marktvergleich dokumentiert:** [COTS_POWER_SUPPLY_EVALUATION.md](COTS_POWER_SUPPLY_EVALUATION.md). Die vorläufigen Alternativen **TI LM74800-Q1 + RECOM R-78K5.0-2.0L**, **LM74930-Q1 + RECOM** und **RECOM RPH-3.0-CT mit Enable** müssen vor dem weiteren individuellen Buck-Redesign gegen die **LMR38020-Q1**-Entwicklungsbasis unter gleichen Bedingungen verglichen werden.

- [ ] Vollständige **1/10/100-Stück-Gesamt-BOM** mit realer Verfügbarkeit, MwSt./Versand, Hand- oder PCBA-Bestückung und Testkosten; 11–14 € nur überholte/unvollständige Chat-Schätzung.
- [ ] 9–30 V normal, ~9 V Startziel, RECOM 36-V-Eingangsgrenze plus OVP-Toleranzen und ISO-Transienten prüfen; Last-/Ripple-/EMV-/Thermiknachweise für 5 V / 2 A.
- [ ] Beim LM74800 (kein Overcurrent-Limit) nachweisen, wie gefährliche Kurzschlüsse/Leitungsschäden verhindert werden; LM74930/alternative eFuse und externe Sicherungen *mit gleichem Schutzumfang* vergleichen.
- [ ] Bei SIP3 ohne Enable zusätzlichen ACC/MCU-HOLD-Abschaltpfad und **<100 µA** BAT+-OFF-Gesamtruhestrom belegen; USB-Service, SD-Flush und Rückspeisesperre erhalten.
- [ ] 202-V-Test-A-Referenz nicht als freigegeben übernehmen: Q1-SOA, Q2-Klemmspannung, TVS, Leiterbahnen, Sicherungen und Test B separat verifizieren. 
- [ ] Vor Änderungen der KiCad-Baugruppen Entscheidung dokumentieren; dann Symbole/Footprints/3D, gesamtes ERC/DRC und Labortests durchführen. **Bisher keine Änderung am aktuellen Schaltplan oder BOM.**


**AKTUELLE ENTSCHEIDUNG (13.10.2026): Variante C ist verbindlich festgelegt: LM74930-Q1 + LMR36520, relaislose ACC-/MCU-HOLD-Logik.** Keine separate TPS26631, keine fest eingelöteten Einmalsicherungen mit Auslötpflicht; **quellseitig getrennt abgesicherte** ACC-/BAT+-Kabel bleiben Pflicht. **Reichelt und andere deutsche Lieferanten zuerst prüfen, wenn Gesamtpreis inkl. MwSt./Versand/Mindestmenge und Lagerbestand konkurrenzfähig**; sonst Mouser/DigiKey/LCSC möglich. Alte Varianten nur noch Vergleichsdokumentation. Offen: FET/Footprint/Shunt-Design, 6-V-Start, ISO-Transienten, Ruhestrom, Kurzschluss-/Thermiktest, realer BOM-Korb.

**Stand: 13.10.2026.** Aktiver Entwicklungsstand: [TripTracer V1](../hardware/kicad/TripTracer_V1_README.md); V0.3 ist eine historische Referenz. **Kein fertiges oder freigegebenes PCB.**

**Konkreter 80/20-Schutzkonzept-Entwurf:** [POWER_INPUT_80_20_DECISION.md](POWER_INPUT_80_20_DECISION.md). **OV-Abschaltung statt 200-V-Ausgangsklemme** bevorzugt; LM74800-Q1 + lieferbaren **250-V-HV-MOSFET** und günstigeren 60-V-FET prüfen, keine eFuse-/Sicherheitsfunktion ohne Fehleranalyse stillschweigend streichen. **OV-Teiler im OFF** auf Ruhestrom und während Surge auf Pulsfestigkeit testen; Q1/Fuse/Buck Kurzschluss sicher begrenzen.

**Priorisierter Vergleich:** **LM74930-Q1** (eine Schutz-IC-Stufe mit Überstrom-/Kurzschluss-Limiter, 200-V-Load-Dump, UVLO/OVP) vs. **LM74800-Q1** (ohne eFuse; nur bei anderweitig nachgewiesenem Kurzschluss-/Leitungsschutz). Siehe [POWER_INPUT_80_20_DECISION.md](POWER_INPUT_80_20_DECISION.md). Im portablen KiCad-10-Symbollib ist der **LM74930-Q1 als 24-Signalpin-Kandidat** eingetragen; **Thermal-Pad RTN muss frei bleiben; Footprint/Pin-Pad-Mapping noch offen, Symbol nicht im Schaltplan verdrahtet, kein ERC**.

**Neue Reihenfolge nach MegaSquirt-Versorgungsvergleich (13.10.2026):** **Zuerst** günstigen 9–36-V-/5-V-/2-A-Buck **LMR36520** mit 6-V-Kaltstart und einfacherer **ACC OR MCU_HOLD → Buck_EN**-Selbsthaltung komplett elektrisch auslegen; verifizierbaren Kurzschluss-/Brandschutz sowie getrennt abgesicherte BAT+/ACC-Zuleitungen dimensionieren. **Dann** den 200-V-ungedämpften ISO-16750-2-Load-Dump über geeignete vorgeschaltete, stromsparende Abschaltstufe **vor jedem Fahrzeugeinsatz** nachweisen. Einkaufsreihenfolge: tatsächliche Verfügbarkeit/Herstellerqualität/Preis/Handlötbarkeit, **JLCPCB-PCBA optional und nachrangig**. Vollständige Argumentation: [MEGASQUIRT_POWER_BENCHMARK.md](MEGASQUIRT_POWER_BENCHMARK.md). Ursprüngliches 18-V-MOV/26-V-Linearregler-MegaSquirt-Design NICHT einfach kopieren.

**Tatsächlich im KiCad geändert (Buck a1, 13.10.2026):** U101-TI-Referenz mit R101/R102=100k/24.9k, L101=10µH Bourns SRP6030VA-100M, zwei 4.7µF + 220nF Eingang und zwei 22µF Ausgang, separate `BUCK_ENABLE`-Steuerleitung. Provisorischer Bourns-Land-Pattern-Footprint und vorläufige BOM/Preispositionen hinzugefügt. **Offen:** LMR36520-Pad9/thermisches Kupfer, Drossel-5A-Isat/Temperatur und Footprint-GUI-Prüfung, MLCC-DC-Bias, tatsächliche 6V-Regelung, EN-Driver/ACC-HOLD, LM74930-Versorgungsanbindung, KiCad-CLI-ERC/DRC/Realtest.

## Priorität A – Stromversorgung V1, Variante 3 (relaislos)

Maßgebliche Analyse: [SOLID_STATE_POWER_ARCHITECTURE.md](SOLID_STATE_POWER_ARCHITECTURE.md). Die Entscheidung für Variante 3 ist **eine Entwicklungsrichtung, keine Sicherheits- oder Fertigungsfreigabe**.

- [ ] 9–36-V-Haupt- und ACC-Eingangs-/Transienten-/Verpol-/Load-Dump-Prüfprofile für **beide** 12-/24-V-Bordnetzklassen definieren.
- [ ] Aktuelles Lastbudget des Displays/Backlights, ESP32-S3, GNSS, FRAM, SD und der 5-V-Radgeber aufstellen (Dauer-/Peak-/Startströme).
- [ ] U401 TPS26631 samt externen Q401-/Q402-FETs vollständig dimensionieren: ILIM, UVLO, OVP, dVdT, Rückstromsperre, thermischer Retry, Footprints und Layout.
- [ ] Unabhängigen zweiten Hardware-Abschalter Q601 inklusive Body-Diode-/USB-Rückstromrichtung, Gate-Clamp, Schutz gegen Dauer-EIN und SOA auslegen; ROHM-P-FET nur ein ungeprüfter Kandidat.
- [ ] Schutz-/Wake-/HOLD-Logik ohne bisherige dauerhaft aktive 5-V-AUX-Versorgung zeichnen. **01B muss neu entworfen** werden, 01C-Timer ist nur ein ungeprüfter Teilschaltplan.
- [ ] MCU-unabhängigen, zeitbegrenzten Shutdown / USB-only-Vehicle-Interlock / Frühzeit-ACC-Wake testen; ACC AUS mit BAT+ nach Dateischluss schaltet beide Pfade aus.
- [ ] <100 µA gesamten BAT+-OFF-Ruhestrom bei 9/12/24/36 V und relevanter Temperatur **messen**; 60 µA maximalen U401-Shutdown-Strom plus OVP-Divider/TVS/Leckströme berücksichtigen.
- [ ] 12-/24-V-Startprofile mit **6 V als unterer Motorstart-Funktionsgrenze** (keine 3-V-/15-ms-Fortsetzungsforderung mehr) und zeitlichem Verlauf nach ISO-16750-2-Testmatrix dimensionieren. Kernversorgung/SD/GNSS bei 6 V prüfen, Backlight bei Bedarf abschalten, definierte Brownout-Zustände unter 6 V testen.
- [ ] Erst anschließend die Hierarchie der `hardware/kicad/TripTracer_V1.kicad_pro` mit vollständig gezeichneten Netzen aktualisieren; projektweit **KiCad-10-ERC**, PCB-Netzübernahme/**DRC** und echte Schutz-/Fault-Injection-Tests durchführen.
- [ ] Alternativcontroller LTC4380 (AEC-Q100, niedriger Iq) **nur technisch vergleichen**, **nicht** ohne gesonderte Freigabe als Ersatz der festgelegten SMD-eFuse verbauen.

## Priorität B – übrige V1-Baugruppen

- [ ] `03_3V3_USB`: separate USB-Servicestromversorgung, Fahrzeug-USB-Quellenpriorität, keine Rückspeisung; MSC-/Flash-/SD-Exklusivmodi validieren.
- [ ] GNSS MAX-M10N, aktive SMA/U.FL-Antenne, I/O-Pegel/UART/Zeitsignal und 5-Hz-Datenfluss mit Herstellerdaten vergleichen.
- [ ] Riverdi-3,5-Zoll-Display, 6 FILN-Taster, Backlight-/Ringdimmung, GPIO-Strapping und Strom-/Temperaturbudget prüfen.
- [ ] RTC mit Backup, interne microSD per dediziertem SPI, FRAM-Atomarität und SD-Flush-/FAT32-Tests einschließlich plötzlichem M8-Abziehen.
- [ ] Zwei geschützte Radimpuls-Sensoreingänge und geschaltete 5-V-Versorgung elektrisch/EMV prüfen.
- [ ] Footprints und Bibliotheken/STEP lokal portabel halten, JLCPCB-BOM und 5-PCB-/2-PCBA-Angebote erst nach Schaltungsfreigabe prüfen.

## Historische V0.3-Checks (unverändert offen, keine V1-Freigabe)

1. Schaltplan in KiCad 10 laden und native ERC-Pruefung durchfuehren.
2. Komplettes PCB layouten und nach JLCPCB-Regeln DRC pruefen. Der V0.1-Placement-Entwurf ist explizit kein Fertigungs-PCB.
3. Automobilversorgung: Load Dump, Transienten, ESD/EMV, Verpolung, Sicherung und Temperaturbelastung nachweisen.
4. 3.3-V-Buck-Spule, Kondensator-Derating, Ripple und thermische Auslegung pruefen.
5. GNSS-Antenne und Bias-T (50 Ohm, aktive Antenne) am konkreten Aufbau testen.
6. LCD-40-Pin-Layout, Modulabmessungen und Ladungspumpen-Kondensatoren gegen Herstellerunterlagen pruefen.
7. USB-C: VBUS versorgt laut V0.3 nicht das Geraet; Firmwareflash erfordert zusaetzlich J1.
8. Firmware V0.1 mit V0.3-Schaltplan abgleichen, ESP32-S3-Build und 10-Hz-GNSS-Konfiguration testen.
9. Mechanik V0.1: Druck- und Passprobe; Schalterhoehe, Dichtung, Vibration und Antennenanschluss bestaetigen.
10. Bibliothek: 3D-Modelle sind teils vereinfachte Geometrien, keine freigegebenen Hersteller-CAD-Modelle.

Nichts hiervon darf als abgeschlossen oder getestet bezeichnet werden, bevor ein konkreter Testbericht existiert.

Die Statusangaben bleiben nur dann „geprüft“, wenn ein zugehöriger ERC-/DRC-/Datenblatt-/Laborbericht tatsächlich existiert.
