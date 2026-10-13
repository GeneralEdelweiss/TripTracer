# TripTracer V1 – KiCad-10-Projektstart (13.10.2026)

**Status: BEGINN DER SCHALTPLANENTWICKLUNG – NICHT ERC-/DRC-GEPRÜFT UND NICHT FERTIGUNGSREIF.**

## Öffnen

`TripTracer_V1.kicad_pro` oder `TripTracer_V1.kicad_sch` mit **KiCad 10** öffnen. Alle Dateien und Bibliotheken **im vorhandenen Ordner `hardware/kicad/` belassen**, damit `sym-lib-table`, `fp-lib-table` und `Tripmaster.pretty` aufgelöst werden. `Tripmaster_V0_3.*` bleibt unverändert als historische Referenz.

## Echte vorhandene V1-Projektdateien

- `TripTracer_V1.kicad_sch` – hierarchisches V1-Hauptblatt mit **8 verlinkten Schaltplanseiten**;
- `01_Eingangsschutz.kicad_sch` – Arbeitsblatt/Offenpunkte: M8, TVS, eFuse, Verpol-FET, HV-Puffer; **noch nicht elektrisch umgesetzt**;
- `02_5V_Buck.kicad_sch` – **erste elektrische Verdrahtung** der 5-V-Buck-Kandidatenschaltung mit **9 Symbolinstanzen**, Eingangskondensator, LMR36520, BOOT- und VCC-Kondensator, Induktor, zwei Ausgangskondensatoren und FB-Teiler; **noch nicht ERC- und thermisch freigegeben**;
- `03_3V3_USB.kicad_sch` – offenes Blatt für 3,3-V-LDO, USB-Serviceversorgung und abgesicherte 5-V-Testeinspeisung;
- `04_ESP32_USB.kicad_sch` – offenes Blatt ESP32-S3, USB, BOOT und GPIO;
- `05_GNSS.kicad_sch` – offenes GNSS-/RF-/Antennenbias-Blatt;
- `06_Display_Tasten.kicad_sch` – offenes Riverdi-/Tasten-/Backlight-Blatt;
- `07_Speicher_RTC.kicad_sch` – offenes FRAM-/microSD-/RTC-Blatt;
- `08_Radsensoren.kicad_sch` – offenes Radgeber-/Erweiterungs-Blatt;
- `TripTracer_V1.kicad_sym` – erstes V1-Projektsymbol für LMR36520; in projektlokaler `sym-lib-table` registriert.

## Aktuelle 5-V-Buck-Bauteilskizze

| Referenz | Vorläufige Funktion | Vor Freigabe erforderlich |
|---|---|---|
| U101 | **TI LMR36520ADDAR**, synchron, 4,2–65 V, 2 A | Datenblatt, tatsächliche Bestellbarkeit und 90-%-Ziel bei 24 V / 2 A prüfen |
| L101 | Induktor, vorläufig 15 µH | Datenblatt-Auslegungsbeispiel, Stromspitzen/Sättigung, DCR, Bauform – alter Footprint **nur vorläufig** |
| R101/R102 | 172 kΩ / 43,2 kΩ, FB-Teiler | Für ca. 5 V nach 1,0-V-FB-Referenz; Widerstandstoleranz und Layout |
| C101 | 2,2 µF, 100 V Eingang | Spannungsspitzen, Keramik-DC-Bias und Ripple |
| C102 | 100 nF BOOT–SW | Abstand/Platzierung am Regler |
| C103 | 1 µF VCC–GND | VCC ist interne Regler-Versorgung, **keine Lastversorgungsquelle** |
| C104/C105 | je 22 µF am 5-V-Ausgang | reale wirksame C bei 5 V, Ripple/Reglerstabilität |

**LMR36520 ist nach TI ausdrücklich pin-kompatibel zum bestehenden LMR36510.** Der erste Symbolentwurf übernimmt die Pin-Geometrie des alten Projektstandes mit neuer Benennung; Footprint- und Padprüfung bleibt verpflichtend. Datenblatt: https://www.ti.com/lit/ds/symlink/lmr36520.pdf.

**Wichtige Lücken der ersten Schaltung:** Die geschützte Hochvolt-Eingangsspannung ist bisher ein offener Cross-Sheet-Anschluss `HV_PROTECTED_AFTER_EFUSE`. Die echte eFuse-/TVS-/Rückstromschutz- und Elko-Schaltung ist noch **nicht** angeschlossen. Ebenso fehlen der definierte vollständige 5-V-Quellenwahlschalter, die Laboreinspeisung und der 3,3-V-LDO. Keine Spannung einspeisen, nur weil das Buck-Blatt gezeichnet ist.

## Validierungsstand

- Projektstruktur, **11 neu erzeugte KiCad-Dateien einschließlich Projektstarter und Symbolbibliothek** sowie S-Ausdruck-Klammer-/Zitatbalance der `.kicad_sch`-Dateien automatisiert geprüft.
- Auf dem Buck-Blatt sind **8 Junction-Dots** für T-Verzweigungen ergänzt.
- **Keine native KiCad-10-Parserprüfung, kein ERC, kein DRC, keine visuelle KiCad-Editorprüfung**, keine SPICE-/Benchvalidierung.
- Benötigte weitere Schritte: zunächst Eingangsschutz/eFuse+N-MOSFET mit nachgewiesenem Verpolschutz, TVS/Clamp, regelbare Pufferladung und ACC-Sense elektrisch fertigstellen; danach Quellenentkopplung, LDO, MCU/USB und übrige Baugruppen; im Anschluss Pinout-/Footprint-Abgleich, ERC und Berechnungen.

## Beschlossene Fertigungsdaten

**5 PCBs, davon 2 bestücken (soweit JLCPCB unterstützt), 3 unbestückt; 35 µm/1 oz Kupfer; 1,6 mm Dicke; SMD-JLCPCB plus manuelle Sonderteile.** Diese Daten sind **kein Fertigungsauftrag** und ausdrücklich **keine Produktionsfreigabe**.

Siehe [HARDWARE_REQUIREMENTS.md](../../docs/HARDWARE_REQUIREMENTS.md) und [PROTOTYPE_V1_SCHEMATIC_REVIEW.md](../../docs/PROTOTYPE_V1_SCHEMATIC_REVIEW.md).
