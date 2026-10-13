# TripTracer – erste konkrete Bauteil- und Schaltplanprüfung für Hardware-V1

**Datum:** 13.10.2026  
**Status:** Ingenieurmäßiger Vorab-Review; **KEINE ERC-/DRC-, Schaltplan-, PCB-, Schutz- oder Fertigungsfreigabe**.  
**Verbindliche Vorgaben:** [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md), insbesondere HW-01–86.  
**Quelle des bisherigen KiCad-Standes:** [Tripmaster_V0_3.kicad_sch](../hardware/kicad/Tripmaster_V0_3.kicad_sch), [V0.3-BOM](../catalog/Bauteilliste_V0_3.csv).

## 1. Festgelegte erste Fertigung (HW-69–72)

- **5 nackte Hauptplatinen**, davon nach Möglichkeit **2 bei JLCPCB SMD-bestückt** und **3 als unbestückte Reserve**; tatsächliche zulässige PCBA-Bestellmenge noch beim Anbieter verifizieren.
- **Interner 2-poliger, abgesicherter 5-V-Laboreinspeisestecker**, ohne Rückspeisung von USB, Buck oder M8.
- **35 µm / 1 oz Kupfer**, **1,6 mm PCB-Dicke**; 2 Lagen bevorzugt, 4 bei technisch dokumentiertem Bedarf.

## 2. Abgleich bestehender KiCad-V0.3 mit Hardware-V1

Geprüft wurden der tatsächliche Dateikopf und die vorhandenen Symbole im **einseitigen A0-Schaltplan** (`Tripmaster_V0_3.kicad_sch`), die V0.3-BOM sowie die Projekt-Readme. V0.3 enthält 69 instanziierte Schaltplansymbole, aber **keinen hierarchischen V1-Schaltplan**. Kein nativer KiCad-ERC oder DRC wurde bei dieser Prüfung ausgeführt.

| Bereich | Vorhanden in V0.3 | Erforderliche V1-Änderung | Status |
|---|---|---|---|
| MCU | ESP32-S3-MINI-1-N8 | Beibehalten, USB/BOOT/EN und GPIO-Budget neu prüfen | Weiterverwendbar, **nicht freigegeben** |
| GNSS | MAX-M10N-00B, U.FL und Entwurf eines Bias-T | Beibehalten, UART/TIMEPULSE, Antennenversorgung/-schutz und SMA-Pigtail finalisieren | RF-Prüfung offen |
| Versorgung | TI LMR36510A, **3,3-V-Buck / max. 1 A**; 12-V-Vorentwurf mit einfacher Schutzbeschaltung | **9–36 V → geschützter 5-V-/2-A-Synchronbuck** (IC mindestens 60 V), 3,3-V-LDO, eFuse mit nachgewiesenem Verpolschutz, TVS, **ACC/BAT+-Mikrorelais mit MCU-Selbsthaltung** und nur noch funktionsnotwendiger Glättung/Startstützung | **Neu entwerfen** |
| Display | EA DOGL128W-6, 128 × 64 monochrom | **Riverdi RVT35HITNWC00-B** einschließlich 50-poligem FPC, SPI und Backlight-Boost | **Ersetzen** |
| Tasten | Fünf Omron-Taster auf der PCB | Sechs externe FILN-Taster mit **je eigenem JST-Anschluss und GPIO**, gemeinsamer LED-Dimmkanal | **Ersetzen** |
| USB | USB4105 mit CC- und ESD-Beschaltung, nicht als Betriebsversorgung nutzbar | Native USB-Daten inkl. USB-only 5-V-Serviceversorgung, MSC, Firmware-Flash, Quellenentkopplung | **Strompfad neu entwerfen** |
| Speicher | MB85RC256VPNF-FRAM vorhanden | Beibehalten, RTC/CR1220 und interne SD an eigenem SPI-Host ergänzen | **Ergänzen** |
| Radsensor | Zwei außenliegende geschützte Kanäle fehlen | M8-4-polig, unabhängige Eingangsaufbereitung mit Pull-up-Bestückungsoptionen und geschütztem 5-V-Lastschalter | **Neu entwerfen** |
| Fertigungsprüfung | V0.3-Strukturprüfung vorhanden | KiCad-10-ERC, visuelle Prüfung jeder hierarchischen Seite, DRC und Hersteller-Pinout/Fußabdruck-Prüfung erforderlich | **Offen** |

## 3. Herstellerverifizierte Bauteilkandidaten und Schlüsseldaten

### 3.1 Riverdi RVT35HITNWC00-B – Bauteilreferenz bestätigt, PCB-Anschluss noch offen

Quelle: [Riverdi-Datenblatt Rev. 1.1 vom 20.07.2026](https://download.riverdi.com/RVT35HITNWC00-B/DS_RVT35HITNWC00-B_Rev.1.1.pdf), insbesondere Seiten 6–8, 12–13.

- **ILI9488**, **320 × 480**, RGB/SPI, **50-poliges FPC mit 0,5-mm-Pitch** und 0,30 mm FPC-Stärke laut Zeichnung.
- 4-Draht-SPI gemäß Mode-Tabelle mit **IM2/IM1/IM0 = 1/1/1**: Pins **5/4/3**. Weitere relevante Pins: **1 GND, 2 VCI, 6 RESET, 37 SDA (serieller Dateneingang), 39 WR/SCL, 40 DCX, 41 CS, 42 GND, 49 LEDA, 50 LEDK**. Pin 36 SDO für Lesezugriffe optional nach ILI9488-Betriebsmodus prüfen.
- **VCI typisch 2,8 V** (zulässiger Bereich 2,5–3,3 V), **IOVCC 1,7–3,3 V**; 3,3-V-Logik nur im tatsächlich zulässigen Power-up-/Interface-Konzept vorsehen, **niemals 5 V an die Displaylogik**.
- Backlight **typisch 15 V / 100 mA ≈ 1,5 W**, spezifiziert ca. 13,5–17 V; **separaten stromgeregelten Step-up-LED-Treiber** von einer geeigneten Geräteschiene vorsehen und dimmen.
- **Achtung Datenblatt-Inkonsistenz:** Klassifikations-Tabelle kennzeichnet `N` als *without touch panel*, aber Seite 2 und spätere Abschnitte enthalten Touch-Controller-/Pinangaben (Pins 43–47). Physische Bestückung und Lieferantenspezifikation prüfen; **Touch nicht ohne Nachweis als tatsächlich vorhanden annehmen**. Der TripTracer nutzt ohnehin sechs mechanische Fronttaster.
- Auswahl des ZIF-Gegenstücks erst nach verbindlicher FPC-Kontaktseite, Verriegelung, Cable-Fit und mechanischer Zeichnung.

### 3.2 TI LMR36520 – aussichtsreicher 5-V-Buck-Kandidat, noch **nicht freigegeben**

Quelle: [TI LMR36520 Produktseite/Datenblatt](https://www.ti.com/product/LMR36520).

- **4,2–65 V Betrieb, synchroner Buck, integrierte Schalter, bis 2 A**, 400 kHz; erfüllt nominell 9–36 V und Hardwarevorgabe mindestens 60 V.
- **Pin-kompatibel zu V0.3-Regler LMR36510 (1 A)** laut TI. Trotzdem sind V0.3-Spule, Rückkopplung, Ausgangskondensatoren und Eingangsschutz wegen **neuer Ausgangsspannung 5 V, anderer Last 2 A und neuer Architektur nicht unverändert freigabefähig**.
- **Warnung:** TI nennt ca. **90 % bei 24 V → 5 V / 1 A**; dies ist **kein Nachweis für ≥90 % bei 2 A**. Der 2-A-Nennstrom bietet wenig thermischen/Lastspitzen-Spielraum. Verluste, Temperatur und alternative Regler mit Reserve vor Wahl prüfen. Bei Bedarf HW-07/23 im Review erneut bewerten, statt die 90-%-Vorgabe stillschweigend als erfüllt zu markieren.

### 3.3 TI TPS2663 – eFuse-Kandidat mit **externem** Verpol-MOSFET, noch **nicht freigegeben**

Quelle: [TI TPS2663 Produktseite/Datenblatt](https://www.ti.com/product/TPS2663).

- Eingang **4,5–60 V**, verstellbarer Stromgrenzwert **0,6–6 A**, automatischer Retry nur mit geeigneter Variante/Konfiguration; E-Fuse enthält eigenen Last-MOSFET.
- Verpolschutz und Reverse-Current-Blocking unterstützt die Familie **nur zusammen mit einem zusätzlichen externen N-Kanal-FET** über den dafür vorgesehenen B-FET-Treiber. **Kein Verpolschutz allein durch das einzelne eFuse-IC.**
- 60-V-Nenn-Eingangsgrenze und TVS-Klemmverhalten unter realen Automotive-Surges/Load-Dump, SOA beim Laden großer Pufferelkos und eFuse-Abschaltung bei negativen Eingangsspannungen prüfen; kein Bauteil allein als Automotive-Freigabe ausgeben.

**Mögliche Alternative zum Schutzkonzept (nicht beschlossen):** TI LM74900-Q1 ist ein Automotive-Ideal-Diode-/Circuit-Breaker-Controller (3–65 V, reverse-polarity support), benötigt **externe Back-to-back-MOSFETs**; entsprechende Varianten und Auto-Retry-Verhalten sind noch nicht gegenüber den Anforderungen verifiziert. Herstellerquelle: https://www.ti.com/product/LM74900-Q1.

### 3.4 ESP32-S3 / USB – konkrete feste Signale

Quelle: [Espressif USB/JTAG Pinbelegung](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html).

- **GPIO19 = USB D−**, **GPIO20 = USB D+**. USB-C-CC-Sink-Beschaltung, ESD, VBUS-Erkennung und Rückspeiseschutz bleiben erforderlich.
- Boot-/Recovery-Jumper gemäß `STO-16` mit **GPIO0/BOOT** und Zugriff auf **EN/RESET** beibehalten; nativer USB kann den separaten USB-UART-Chip ersetzen.
- Vor dem neuen Schaltplan Pinbudget inklusive **6 Tastern, 2 Radgebern, Display-SPI, microSD-SPI, GNSS-UART/TIMEPULSE, I²C, Backlight, Sensorversorgung und JST-GH-Erweiterung** nachweisen.

### 3.5 MAX-M10N – Hardware bleibt, Antennenversorgung offen

Quelle: [u-blox MAX-M10N-00B Datenblatt](https://content.u-blox.com/sites/default/files/documents/MAX-M10N-00B_DataSheet_UBXDOC-963802114-13143.pdf).

- UART weiterhin vorgesehen; **VIO_SEL offen → 3,3-V-I/O** (nach Datenblatt), `RF_IN` mit nominell **50 Ω**, integrierter DC-Block.
- `VCC_RF` liefert eine antennenbezogene Versorgung abhängig von `VCC` mit **50 mA spezifiziertem Betriebsstrom**; `LNA_EN` kann externe aktive Antenne/LNA schalten. Antennenstromverbrauch, Bias-T, Überspannung/ESD am SMA-Eingang, U.FL-Pigtail und geschütztes Ein-/Ausschalten konkret auslegen.
- Eine feste Bias-Spannung ist beschlossen, ihr tatsächlicher Wert noch **nicht** ohne Auswahl einer aktiven Antenne nachgewiesen.

## 4. Geänderte Versorgungsarchitektur: ACC + BAT+ und Mikrorelais-Selbsthaltung (Stand 13.10.2026)

**Neu: [Baugruppe-01-Relais- und AUX-Buck-Designreview](POWER_RELAY_DESIGN_REVIEW.md).** Darin sind konkrete Omron-/TI-Kandidaten, vorläufige Spulen-/Kontaktlasten, Schnittstellen und noch nicht bestandene Hardware-Gates dokumentiert.

**Aktuelle Nutzerentscheidung (PWR-10/16/20/22/34, HW-84):** M8 Pin 1 geschaltetes ACC, Pin 3 GND, Pin 4 separat abgesichertes BAT+. ACC schaltet ein kleines Mikrorelais ein; das Relais leitet BAT+ in den geschützten 9–36-V-Eingang des TripTracer. Die MCU hält das Relais nach Zündung AUS über HOLD bestromt, sichert FRAM/GPX/CSV/SD/FAT32 und lässt es danach abfallen. **Keine garantierte Aufzeichnungssicherung bei vollständigem Abziehen des M8 oder BAT+/GND-Ausfall.** Das wird als akzeptierter Bedienfehler behandelt.

**Früherer 3-s-Elko-Pufferentwurf ist damit überholt.** Die zuvor errechneten 185.000 µF (12→6 V, 3 W) bzw. 444.000 µF (9→6 V) waren ausschließlich illustrative Rechnungen zur vollständigen Drei-Sekunden-Überbrückung aus Kondensatoren. Sie sind **keine V1-Designanforderung oder BOM-Position** mehr und dürfen nicht wieder ungefragt eingeplant werden.

**Weiter erforderlich:** stabile und definierte Relais-/HOLD-Beschaltung über das 12-/24-V-Bordnetz (9–36 V normal, Startprofile separat), Schutz/Entkopplung von beiden Plusadern, M8-Fahrzeug-Kabelsicherungen, eFuse samt Verpol-/Transientenschutz, Relaiskontakt-Stoßstrom und Spulen-Freilauf, Ruhestrom bei BAT+ im OFF, SD-/FRAM-Flush und ein Watchdog-/Hardware-Timeout gegen endlose Selbsthaltung. Kleine/reguläre Eingangs- und Ausgangskondensatoren sowie ggf. Startspannungsstützung bleiben erforderliche Auslegungsaufgabe.

**Manueller Standby:** eine vorhandene Fronttaste lässt MCU in Deep-Sleep gehen bzw. weckt sie wieder; unnötige Peripherie aus. Bei weiterhin eingeschaltetem ACC bleibt das monostabile Relais voraussichtlich angezogen: Relais-Spulenstrom ist **Teil des Standby-Stroms**, kein <1-mA-Versprechen. Ein stromloser OFF-Zustand nach ACC AUS ist ein anderer Betriebszustand.

**Prüfstatus:** Das Blatt `01_Eingangsschutz.kicad_sch` ist weiterhin ein Planungsblatt ohne echte Relais-Verdrahtung, Hersteller-Pinout-Prüfung oder natives KiCad-ERC. Vor PCB-/BOM-Freigabe zuerst vollständigen elektrisch prüfbaren Relais-/Bordnetzschutz-Schaltplan entwickeln.

## 5. Priorisierte, derzeit offene elektrische Freigabepunkte

1. **Display-FPC**: exakt richtige Connector-Kontaktseite/Typ, Stromversorgung 2,8/3,3 V, 4-Draht-SPI und Boost-LED-Treiber samt PWM.
2. **Eingangsschutz**: passend spezifizierte eFuse-Variante inklusive externem Verpol-FET; TVS/Lastabwurf, 9–36-V-Dauerbereich, Relais-HOLD/Freilauf/Kontaktstoßstrom und Quellen-Entkopplung.
3. **Buck/3,3-V-LDO**: 5 V/2 A inklusive tatsächlicher Spitzenströme, Wirkungsgrad bei Volllast, Spule, Kondensatoren und 3,3-V-Verlustwärme.
4. **RTC/CR1220, microSD und I²C**: Datenblätter, Busadressen, separate SD-SPI-Signale, geschaltete SD-Versorgung sowie SPI-/Boot-Pinbudget.
5. **JST-/M8-/SMA-Steckverbinder**: Kontaktbelegung, Lieferartikel, mechanische Zugangsmöglichkeit, Zugentlastung, Schutz- und Testeinspeisepfade.
6. **Native KiCad-Prüfung**: hierarchische V1-Schaltplanseiten neu erstellen, ERC, manuelle Symbole/Footprints, anschließend PCB-DRC, DFM und Inbetriebnahmeplan.

**Fertigungsstatus:** Der bisherige V0.3-Schaltplan kann als technische Referenz dienen, **nicht als V1-Elektrofreigabe**. Diese Datei ist eine Bauteil-/Risikovorauswahl, kein fertig konstruierter oder elektrisch getesteter KiCad-V1-Schaltplan.
