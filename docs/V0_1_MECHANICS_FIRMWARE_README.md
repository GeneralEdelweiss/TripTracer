# GPS-Rallye-Tripmaster · Vorprototyp V0.1

**Status:** mechanischer und elektrischer Konzept-Prototyp, **KEINE bestellfertige Leiterplatte**. KiCad10-Datei zeigt nur mechanische Platzierung, ist nicht geroutet und nicht ERC-/DRC-geprüft. Keine Gerber-Fertigung auf Grundlage dieser Datei starten.

## Enthalten

- `gehaeuse/Tripmaster_V0_1_frontschale.stl` und `.step` – Gehäusefront mit LCD-Ausschnitt, fünf Tasten und seitlicher Antennendurchführung.
- `gehaeuse/Tripmaster_V0_1_rueckdeckel.stl` und `.step` – Rückdeckel mit Abstandssäulen.
- `gehaeuse/Tripmaster_V0_1_tastenkappe_einzeln.stl` und `.step` – eine Taste, **5× drucken**; Betätigungshöhe an realem Schalter erproben.
- `gehaeuse/Tripmaster_V0_1_passform_baugruppe.step` – vereinfachte Gehäuse-/Display-/PCB-Passprobe.
- `gehaeuse/Tripmaster_V0_1_pcb_referenz.step` – nur mechanisches PCB-Volumen.
- `kicad/*.kicad_pcb` – **NICHT ROUTEN / NICHT FERTIGEN**: 118×68-mm-Trägerplatinen-Platzierungsstudie inkl. DOGL128-Lötpads, fünf Platzhalter-Tastern und Bohrungen.
- `firmware/` – Softwareprototyp mit Display, GNSS-Geschwindigkeitsintegration, mechanischen Tasten und periodischem Flash-Speichern.
- `dokumentation/Stueckliste_V0_1.csv` – vorläufige BOM mit Einzelpreisen sowie markierten Schätzwerten.
- `dokumentation/Pinbelegung_ESP32_S3.csv` – logische Anschlussplanung.

## Mechanik (vor CAD-Freigabe nachmessen)

- Frontschale ca. **126 × 76 × 25 mm**, Tiefe inkl. Rückdeckel **28 mm**.
- Leiterplatte **118 × 68 × 1,6 mm**, 4× Bohrung Ø 3,2 mm bei ±54 × ±29 mm bezogen auf Platinemitte.
- Display-Modul EA DOGL128W-6 + EA LED68X51-A (68 × 51 mm, zusammen etwa 6,5 mm dick) links; Sichtfenster ca. 64,6 × 36,1 mm.
- Fünf Tasterachslagen rechts: X = +42 mm, Y = −25 / −12,5 / 0 / +12,5 / +25 mm relativ zur Gehäusemitte.
- Für das Gehäuse ASA bevorzugt. Erste Passprobe PETG möglich. Abdichtung, UV-Schutz und vibrationsfeste Befestigung vor Feldeinsatz ergänzen.
- SMA-Durchführung Ø 6,7 mm rechts ist **nur eine Vorabannahme**, abhängig vom tatsächlich erworbenen SMA-Bulkhead-Pigtail.
- Die seitliche Kabelausnehmung ist noch **nicht spritzwasserdicht**.
- Deckelschrauben: M2.5, Einbaulänge nach Probe; Pilotbohrungen Ø 2,1 mm für selbstschneidende Schrauben sind noch zu testen. Durchsteckung durch M3-Platinenlöcher passt geometrisch.

## Elektronik-Architektur

12-V-Eingang (abgesichert) → verpol- und transientengeschützte Eingangszone → **LMR36510, 65 V / 1 A Buck auf 3,3 V** → ESP32-S3-MINI-1-N8, MAX-M10N, EA DOGL128 und die drei LED-Stränge. DC/DC ist kein Steckmodul, sondern muss auf die Trägerplatine integriert werden. **Referenzschaltung, Spule, Layout und Schutzbeschaltung sind noch zu entwickeln und zu prüfen.** Für ein Fahrzeug sind Load-Dump-, Jump-Start-, ESD-/EMV- und Kurzschluss-Tests erforderlich. Aus 65-V-Regler-Maximalspannung allein folgt noch kein ausreichender Bordnetzschutz.

**LCD**: EA DOGL128W-6, ST7565R, 3,3-V-SPI. Das LCD benötigt **neun externe Kondensatoren**, deren Schaltung sich nach aktuellem Hersteller-Datenblatt richtet. Pinbelegung laut eingesehenem Blatt: 36 = SI, 37 = SCL, 38 = A0, 39 = /RST, 40 = /CS1; 34 = VDD2 und 35 = VDD; 26,33 = GND. LED-Beleuchtung: 3 parallel betreibbare **separate** Zweige (A1/C1, A2/C2, A3/C3), für Amber bei 3,3 V z. B. je 100 Ω als erster Versuchs-Vorwiderstand. Gesamtes LED-Kathodenpotential mit Logik-NMOS per PWM schalten. **Niemals ohne Strombegrenzung direkt anschließen.** Display-Einbau und 6:00-/12:00-Blickrichtung prüfen.

**GNSS**: MAX-M10N UART 3,3 V, externe L1-Antenne über 50-Ω-Leitung mit U.FL-Anschluss. Aktive Antennen benötigen zusätzlich eine fachgerecht ausgelegte Speiseweiche (Bias-T) und Schutzschaltung; das ist im PCB-Vorentwurf nicht umgesetzt. Antennenkabel nicht einfach an den UART oder an einen GPIO anschließen. GNSS-Modul anhand des aktuellen Integration Manuals final beschalten. Das ausgewählte M10 ist **Single-Frequency**, nicht L1/L5.

**Flashen**: USB-C → nativer USB ESP32-S3 (GPIO19 D− / GPIO20 D+), CC1/CC2 jeweils 5,1 kΩ an Masse und ESD-Schutz einplanen. Die 5-V-USB-Versorgung darf nicht gegen 12-V-Bordnetz zurückspeisen; Versorgungspfad (ORing / Umschaltung) ist noch zu entwerfen. EN-Pullup und BOOT/RESET-Taster nötig.

**Datenspeicherung**: Die Firmware sichert alle 30 Sekunden in ESP32-NVS. Bei plötzlichem Spannungsverlust können Kilometer verloren gehen. Die endgültige Lösung sollte FRAM mit letzter Integrationsprobe oder eine sauber dimensionierte Hold-up-Schaltung verwenden.

## Firmware V0.1 (experimentell)

PlatformIO, `board = esp32-s3-devkitc-1` als Build-Ziel für ESP32-S3-MINI-1 mit derselben MCU-Familie. Benötigt Bibliotheken TinyGPSPlus und U8g2. Keine verifizierte Compilation oder Hardwareprüfung durchgeführt.

**Wichtig: der MAX-M10N muss für 115200 Baud, 10-Hz-RMC-Ausgabe konfiguriert werden.** Standard-Empfänger-Konfiguration kann 1 Hz sein. Firmware integriert nur aufeinanderfolgende GNSS-Geschwindigkeitsmessungen mit zeitlichem Abstand ≤350 ms. Bei 1 Hz wird absichtlich nicht hochgezählt – bis die Messrate passend eingestellt ist. Das ist ein Schutz vor unkontrolliertem Distanzzählen bei Signalverlust.

Tasten (vorgesehene Zuordnung): MODE = Umschalten zwischen Gesamt-/Trip-Hauptanzeige, `+`/`−` = Trip um jeweils 10 m korrigieren, RESET = Trip 2 s gedrückt halten und nullen, LIGHT = vier Helligkeitsstufen. Total wird nicht unabsichtlich zurückgesetzt. Sensorfusion/Radsensoreingang ist bisher nur vorgesehen, **nicht implementiert**.

## Vor nächster Hardware-Bestellung noch offen

1. Präzise Verifikation des LCD-Footprints (40 Pins/Abstand/PAD-Bohrung) mit mechanischer Zeichnung und 1:1-Papierprobe.
2. Konkreter, verfügbarer Taster mit passender Betätigungshöhe und dazu angepassten Kappen.
3. Finaler Schaltplan für Buck / ESD / TVS / USB-/Bordnetz-ORing / GNSS-RF-Bias / Display-Kondensatoren / Sensorfilter / Speicherschutz.
4. Vollständiges KiCad10-PCB, Routing, ERC, DRC, Antennenimpedanz, Masserückführung und A/B-Test der PWM-Störungen auf GNSS.
5. Firmware-Compile, Test von Kaltstart, GNSS-Rate, Stillstand, kurzzeitigem Ausfall, Flash-Lebensdauer, Stromunterbrechung.

**Diese V0.1 ist zum 3D-Druck und zur Diskussion des elektrischen Layouts geeignet, nicht zum sofortigen Bau eines funktionsfähigen Rallyecomputers.**

## Quellen (Bauteile / technische Daten)

- Display: https://shop.lcd-module.de/128x64-BIG-white-LCD/DOGL128W-6
- Geometrie und Kondensatorschaltung LCD: https://cdn-reichelt.de/documents/datenblatt/A500/DATASHEET_EA_LED.pdf
- Display verfügbar/Preis: https://www.soselectronic.com/de-de/products/display-visions/ea-dogl128w-6-69518
- Amber-Beleuchtung/Preis: https://www.soselectronic.com/de-de/products/display-visions/ea-led68x51-a-1-69505
- ESP32: https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html
- GNSS: https://www.digikey.de/de/products/detail/u-blox/MAX-M10N-00B/28314773
- GNSS-Integration: https://content.u-blox.com/sites/default/files/documents/MAX-M10N_IntegrationManual_UBXDOC-304424225-19802.pdf
- Buck: https://www.ti.com/product/LMR36510
