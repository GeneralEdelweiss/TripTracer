**NACHTRAG 14.10.2026 (neuerer Stand):** Die LM74800-Schutzstufe wurde inzwischen als [aktives KiCad-Blatt 01I](../hardware/kicad/01I_LM74800_INPUT.kicad_sch) umgesetzt. Die ursprünglichen Hinweise „nicht im aktiven Schaltplan“ weiter unten sind **historisch**. Aktuelles Wiring einschließlich J901-Board-Pigtail, externen F901/F902/J902, C10-15nF-Entscheidung, ACC/HOLD und offenen Sicherheitsprüfungen: [Integrationsbericht](LM74800_01I_INTEGRATION_2026-10-14.md). Bauteilauswahl weiterhin **nicht elektrisch/fertigungstechnisch freigegeben**.

# TripTracer V1 – verbindlicher Teile-Stand LM74800-Q1 (14.10.2026)

**Entscheidung des Nutzers: Diese Teile für den nächsten Prototypen bevorzugen und als Entwicklungsstand speichern. KEINE elektrische Freigabe, keine Bestellung, kein Schaltplan-Swap.**

Die bisherige aktive KiCad-Eingangsseite `01G_SIMPLE_INPUT` mit D901/D902 ist **nicht** durch diese BOM ersetzt. Der bestehende LMR38020SQDDARQ1-5V-Buck, TPS2116 USB/M8-Pfad und ACC/HOLD-Funktionen bleiben unangetastet. Der inaktive LM74930-Entwurf `01D` wird nicht als integriert bezeichnet. Maschinenlesbare Stückliste: [power_frontend_design_freeze.json](../hardware/kicad/power_frontend_design_freeze.json).

## Klärung der „85-V-Diode“ im TI-Datenblatt
**Die D2 (85V) in Abb. 10-25 der [TI LM7480-Q1 Rev C](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf) ist KEINE 85-V-Zener-/Gateschutzdiode.** Sie ist eine **gerichtete Versorgung von Knoten A nach VS**, um bei niedriger Bordnetzspannung bzw. Charge-Pump-Anlauf den 10-kΩ-Widerstand für den Versorgungsstrom zu überbrücken. Ein direkter Draht A↔VS ist unzulässig, da er einen Bypass um den Abschalt-FET Q1 bildet. TI erklärt dies explizit in [E2E Support](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1029524/lm7480-q1-200-v-unsuppressed-load-dump-protection-application-in-figure-10-25).

Die **tatsächliche EVM-BOM** [LM74800EVM-CS SLVUBU4 Tabelle 6-1](https://www.ti.com/lit/ug/slvubu4/slvubu4.pdf) verwendet dafür **D6 1N4148WS-7-F, 75V 150mA SOD-323**, und die EVM-Schaltung setzt die Diode mit **Anode an A und Kathode an VS** ein. Das widerspricht **nicht** der 85-V-Beschriftung als schematischem Spannungsfestigkeitsbeispiel, erfordert aber Grenzwertprüfung unserer Q1/Q2/VS-Wellenformen.

**Fixierte bevorzugte Automotive-Version: DIODES 1N4148WSQ-7-F, 75 V, 150 mA, SOD-323, AEC-Q101.** DigiKey DE listet sie zum Prüfzeitpunkt für ungefähr 0,18 EUR/Stück netto (0,111 EUR/10) und mit fünfstelligem Lagerbestand. [DigiKey](https://www.digikey.de/de/products/detail/diodes-incorporated/1N4148WSQ-7-F/5305485).
**Günstige, exakt im TI-EVM verwendete Prototypenalternative:** 1N4148WS-7-F, **ca. 0,04 EUR/Stück inkl. MwSt. ab Lager bei [Reichelt](https://www.reichelt.de/de/de/shop/produkt/schalt-diode_75_v_150_ma_sod-323-219385)**, ferner [LCSC C60580](https://www.lcsc.com/product-image/C60580.html) mit schwankenden Lager-/Preis-Snapshots. Der Standardtyp ist laut [Diodes Incorporated](https://www.diodes.com/part/view/1N4148WS) **nicht** AEC-qualifiziert. Original-EVM-Status bedeutet keine Automotive-Bauteilefreigabe für TripTracer.

**Zwei verschiedene Funktionen – nicht verwechseln:** D_A_VS (75-V-Schaltdiode A→VS) und D_VS (56-V-Zenerklemme VS→GND) sind **beide** erforderlich. Es wird aber **keine zusätzliche 85-V-Zenerdiode** aufgenommen. Die zuvor vorgebrachte Erklärung „85-V-Gateklemme“ war falsch.

## Ergänzung 14.10.2026: alle bislang fehlenden Standard-MPNs bestimmt

[Verifizierte Standard-SMD-Auswahl mit DigiKey-Beständen, Kosten und offenen EVM-Abgleichen](POWER_FRONTEND_PASSIVES_SOURCING_2026-10-14.md). **R_OV_A/B = Yageo RC1206FR-07330KL (je 330k); R_OV_BOTTOM = Yageo RC1206FR-0723K2L (23,2k); C_CAP = KEMET C1206C224K5RACTU (220nF/50V); R_SLEW = Yageo RC1206FR-07100RL (100Ω); C_SLEW = KEMET C1206C103K1RACTU (10nF/100V).** Alle bislang sechs MPN-Nullpositionen sind geschlossen. `power_frontend_order_bom.csv` ist eine **separate geplante BOM**, keine aktive KiCad-Stückliste. EVM C10 15nF, ACC/EN-Leitung und Kurzschlussschutz sind weiterhin auf Schaltungs-Ebene zu klären.

## Festgelegte Design-/BOM-Kandidaten
| Funktion | Stück | Bevorzugte MPN bzw. festgelegter Wert | Reifegrad |
|---|---:|---|---|
| U Schutzcontroller | 1 | TI LM74800QDRRRQ1 | Bauteil gewählt |
| Q_HV | 1 | ST STD17NF25, 250 V | SOA/Automotive-Status offen |
| Q_LV | 1 | Nexperia BUK7Y4R8-60EX, 60 V | VDS und Layout-Puls offen |
| D_A_VS, Boostrap | 1 | **1N4148WSQ-7-F**, automotive 75 V SOD-323 | **Funktion und Ersatztyp geklärt**, Extrema zu messen |
| D_VS, Schutzklemme | 1 | onsemi 1SMB5943BT3G, 56 V / 3 W | Pulse und VS-Spitzen offen |
| D_TVS | 2 | SMBJ150A-13-F + SMBJ33CA-13-F | ISO-Pulse offen |
| R_VS | 1 | Vishay CRCW121010K0FKEAHP, 10 kΩ / 0,75 W / 1210 | 0,7-J-Pulsbeständigkeit offen |
| R_OV oben | 2 | **Yageo RC1206FR-07330KL**, 330 kΩ / 1 % / 1206 in Serie | MPN fix, Leckstrom-/OV-Grenzen offen |
| R_OV unten | 1 | **Yageo RC1206FR-0723K2L**, 23,2 kΩ / 1 % / 1206 | MPN fix, Region-Bestand vor Bestellung prüfen |
| C_VS | 2 | KEMET C1210C225K1RACTU, 2,2 µF 100 V | DC-Bias-Effekt offen |
| C_A | 1 | KEMET C1210C105K1RACTU, 1 µF 100 V | Belegung gegen TI-EVM prüfen |
| C_IN | 1 | KEMET C1210C104JARACTU, 100 nF 250 V | realer Input-Peak offen |
| C_CAP | 1 | **KEMET C1206C224K5RACTU**, 220 nF 50 V X7R 1206 | MPN fix, effektive C offen |
| C_LOAD | 1 | Panasonic EEE-FK1J470P, 47 µF 63 V | Pufferung prüfen |
| Slew-Glied | je 1 | **Yageo RC1206FR-07100RL**, 100 Ω + **KEMET C1206C103K1RACTU**, 10 nF / 100 V | MPNs fix, genaue Netzzuordnung prüfen |

## Pflichtprüfungen vor einem fertigen Abschnitt
1. **VS-Bootstrap:** 9-V-Kaltstart und alle kritischen Eingangsspannungen mit aktueller Diode + 10k R + 56V Zener simulieren und messen. Besonders VS-POR und maximale Charge-Pump-Ströme. Kein Draht von A nach VS!
2. **Impulsfestigkeit:** R_VS bei 200-V-/350-ms-konservativem Rechteckversuch etwa 2W bzw. 0,7J; dazu 56-V-Zenerleistung, Kondensator-Derating, heiße Leckströme. Nenn-Dauerleistung 0,75W ist **kein** Pulsnachweis.
3. **OV-Teiler:** unsere 2×330k+23,2k-Lösung ist keine direkt aus TI kopierte geprüfte Konfiguration. Laut TI verursacht Eingangsleckstrom relevante Fehlerschwellen, weshalb das Referenzdesign wesentlich kleinere Widerstände verwendet. OVP schwellenfest bei 30V Normalbetrieb und ISO-Störpuls erst rechnen/messen.
4. **FETs und Leitungsschutz:** Q1-SOA/250-V-Reserve, Q2-60-V-Stress, +/-20V Gate-Grenze, gefahrlose Kurzschlussbehandlung auch **vor** dem Buck. LM74800-Q1 hat keine integrierte Hauptstrombegrenzung; externe geeignete Quellen-Sicherungen und Fehleranalyse bleiben Pflicht.
5. **ACC/HOLD/USB:** EN-Profil mit sicherem Cold-Start und unabhängigem Timeout, M8 USB-Priorität/keine Rückspeisung, <100µA Batterie-Ruhestrom.
6. **KiCad-10:** erst nach vollständig gezeichneter Schaltung Netzliste, ERC, PCB-Übernahme, Footprints, DRC und reale Labor-/ISO-Prüfungen. Nicht vorhandene ERC-/DRC-/Labortests werden nicht als bestanden markiert.

**Entwicklungs-Freeze ist kein Freigabevermerk.** Auswahländerungen nur mit bewusst dokumentierter Revision. Aktive Eingangsplatine bleibt WIP.
