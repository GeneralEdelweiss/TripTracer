# GPS-Rallye-Tripmaster – KiCad-10-Schaltplan V0.3

**Status: elektrisch ausgearbeiteter Entwurf / Schaltplanentwurf zur Sicht- und ERC-Prüfung. Noch NICHT für eine Platinenbestellung oder den direkten Betrieb am Fahrzeug freigegeben.**

## Öffnen

1. ZIP vollständig entpacken (die `.pretty`- und `.3dshapes`-Ordner nicht verschieben).
2. `Tripmaster_V0_3.kicad_sch` mit dem KiCad-10-Schaltplaneditor öffnen; alternativ `Tripmaster_V0_3.kicad_pro` mit KiCad-Projektverwaltung öffnen.
3. Falls KiCad die Bibliotheken nicht automatisch findet: `sym-lib-table` und `fp-lib-table` im Projektverzeichnis lassen; Bibliotheksname `Tripmaster_Sym` / `Tripmaster`.
4. ERC über **Werkzeuge → Elektrische Regeln prüfen (ERC)** ausführen; Warnings und Errors individuell kontrollieren. Ein ERC konnte hier nicht auf einer lokalen KiCad-Installation ausgeführt werden.
5. Vor dem PCB-Layout jedes Bauteil mit dem Hersteller-Datenblatt vergleichen.

## Bereiche im Schema (ein zusammenhängendes A0-Blatt)

1. 12-V-Eingang J1, F1, Verpol-Diode D1 und Eingangs-TVS D2; 3,3-V-Synchronbuck TI LMR36510ADDAR, 22-µH-Spule, Kondensatoren, Feedback, Power-Good.
2. ESP32-S3-MINI-1-N8 inkl. Entkopplung, ENABLE/BOOT-Tastern, Pullups und Power-Good-Eingang.
3. u-blox MAX-M10N-00B, V_IO (3,3 V), HF-U.FL, optionale aktive Antennenspeisung mittels HF-Drossel, FRAM-Speicher und I2C-Pullups.
4. USB-C (GCT USB4105-GF-A), 2x Rd an CC, ESD-Schutz USBLC6-2SC6, Serienwiderstände D+/D−, VBUS-Erkennung.
5. EA DOGL128W-6 zusammen mit EA LED68X51-A, 9 Kondensatoren der Kontrastpumpe, PWM-Low-Side-LED-Treiber und je LED-Zweig 47-Ω-Strombegrenzung.
6. Fünf Fronttasten, separater RESET/BOOT, Anschluss für externen Trip-Reset.

Signalübergreifende Verbindungen über **eindeutige lokale Netzlabels** (z.B. `+3V3`, `GNSS_TX_TO_MCU`, `LCD_SCL`, `USB_DM_MCU`). Im aktiven Schaltplan sind Netze an Symbolpins mit Drahtsegmenten angeschlossen. Die KiCad-Powerflags sind ausschließlich an vorgesehenen Quellen platziert: geschützter Vin-Eingang, 3,3-V-Versorgung, GND und USB-VBUS.

## Wichtige Hinweise und Grenzen

- **Automobil-Bordnetz:** Die SS36, 500-mA-Sicherung und SMCJ24A sind Entwurfsannahmen. Die Schaltung ist nicht auf ISO 7637-2, ISO 16750, Load Dump, ESD, EMV oder Verpolungsfehler bei Fahrzeugbetrieb geprüft. TVS-Dimensionierung, thermische Reserven und Fehlerszenarien sind vor echter Verwendung neu zu bemessen. Versorgung am Labornetzteil zunächst strombegrenzt testen.
- **Buck:** 22 µH statt 10 µH; TI empfiehlt für 3,3 V / 400 kHz eine 22-µH-Spule und die Widerstandspaarung 100 kΩ / 43,2 kΩ. Bourns SRN6045-220M und Ausgangs-Cs müssen auf Sättigungsstrom, DC-Bias-Kapazität, Ripple und Loop-Verhalten geprüft werden.
- **USB-C:** USB ist ein **datenbasierter, selbstversorgter Geräteanschluss**. USB VBUS speist die interne 3,3-V-Elektronik nicht. Für Firmwareupdates muss das Gerät zusätzlich über J1 versorgt werden.
- **GNSS:** VIO_SEL am MAX-M10N ist absichtlich offen für 3,3-V-V_IO. Die Pins RESET_N / SAFEBOOT_N haben interne Pullups. `RF_IN` ist 50 Ω und Bias-T (47 nH/100 pF) ist vor der PCB-Freigabe HF-technisch auf eine konkrete Aktivantenne abzugleichen. Kein Batteriepuffer für V_BCKP.
- **LCD:** 9x 1 µF gemäß Hersteller-Single-Supply-Anwendung; Spannungsfestigkeit der Ladungspumpen-Kondensatoren ist nach den jeweiligen Ausgangsknoten zu prüfen, ebenso Kondensatoranordnung (5x V0..V4). Die ST7565R-Ansteuerung braucht eine zur Einbaulage passende Initialisierungssequenz.
- **LED-Beleuchtung:** separate 47 Ω pro Zweig bei 3,3 V; LED-PWM über DMN2056U. Thermisches Derating und Mindesthelligkeit testen.
- **Omron B3F-1000:** Pin 2+4 sind innen verbunden, ebenso 1+3. Der V0.2-Footprint hatte die Pinpositionen falsch benannt. V0.3 enthält eine korrigierte Nummerierung.
- **STEP-Modelle:** vereinfachte mechanische Darstellung, nicht alle Hersteller-CAD-Modelle sind 1:1 übernommen; besonders bei Steckverbinder, Tastern und neuen Passive-Footprints.
- **Keine DRC-/ERC-Freigabe:** Die S-Expression-Struktur, Pad-zu-Symbol-Pinnummern (65 bestückte Symbolinstanzen mit Footprint), referenzierte STEP-Dateien und Netztabellen wurden automatisiert geprüft. Das ist **kein Ersatz für die KiCad-ERC** und keine manuelle Prüfung auf dem gekoppelten Windows-Rechner.
- **Vorschau-Bilder:** aus Positionsdaten erzeugte schematische Darstellungen, **keine nativen KiCad-Screenshots**.

## Referenzunterlagen

- LCD/Backlight: https://www.lcd-module.de/deu/pdf/grafik/dogl128-6.pdf
- Buck: https://www.ti.com/lit/ds/symlink/lmr36510.pdf
- ESP32-S3: https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html
- GNSS: https://content.u-blox.com/sites/default/files/documents/MAX-M10N-00B_DataSheet_UBXDOC-963802114-13143.pdf
- USB: https://gct.co/files/drawings/usb4105.pdf
- Taster: https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf

## Projektdateien

- `Tripmaster_V0_3.kicad_sch`: echter editierbarer KiCad-Schaltplan.
- `Tripmaster_V0_3.kicad_pro`: Projektstarter.
- `Tripmaster_Sym.kicad_sym`: Symbolbibliothek; `sym-lib-table` lokale Registrierung.
- `Tripmaster.pretty`: Footprintbibliothek; `fp-lib-table` lokale Registrierung.
- `Tripmaster_3dmodels.3dshapes`: vereinfachte STEP-Modelle.
- `Pad-Netze.csv`: elektrische Netzbelegung aller definierten Pins.
- `Bauteilliste.csv`: Stückliste.
- `Validierung.json`: Resultate der strukturellen Prüfung.
- `*_Vorschau.svg`, `*_Gesamtansicht.png` sowie einzelne PNG-Bereiche: Vorschau.

`build_schematic.py`, `addfootprints.py`, `verify.py` und `make_preview.py` sind Entwicklungsskripte zur Reproduzierbarkeit. Bei einem Neuerzeugen werden Symbol-/Instanz-UUIDs neu vergeben: bitte keine regenerierte Datei über ein bereits manuell editiertes KiCad-Projekt kopieren.
