# TripTracer – offene technische Prüfungen

**Stand: 13.10.2026.** Aktiver Entwicklungsstand: [TripTracer V1](../hardware/kicad/TripTracer_V1_README.md); V0.3 ist eine historische Referenz. **Kein fertiges oder freigegebenes PCB.**

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
