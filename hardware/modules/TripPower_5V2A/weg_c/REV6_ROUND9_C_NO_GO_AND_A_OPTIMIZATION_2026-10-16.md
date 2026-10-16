# Weg C REV6 Round 9, 16.10.2026 – ABSCHLUSS: C NO-GO, A weiter optimieren

**Managemententscheid:** Kein weiterer Weg-C-eigener TPS26600-Schaltplan. Integrierter Reverse-/Backfeed-Schutz spart gegen A nur zwei bestückte Positionen, hat aber eine unlösbare *garantierte* OVP-Hysterese bei unveränderten 32V-ON/32V-Restart/36V-OFF-Fenstern und 62V absolute VIN-Grenze bei 58V-Lastabwurf. Keine nachweislich bessere, billigere *vollständige* Lösung gefunden. **Weg A mit 25 realen nativen KiCad10-Bauteilpositionen bleibt führende Entwicklungsbasis, NICHT fertigungstaugliches Produkt.** Alle Writes nur auf design/trippower-c.

Eingelesen: aktuelle REV6, PWR-44–56, Sicherungsplatzierung, AGENTS, Backup-Spezifikation, A native 25er Einkaufsliste und aktueller Round2-Bericht, B Round8 unabhängige Sicherheitsprüfung, D Round8 TPS26631/TPS26600/LTC4368 und letzter gemeinsamer Review.

## 1. Unbedingt zu korrigierender Vorzeichenfehler: OVP Falling

Nach einer OVP-Abschaltung kann der Controller erst bei fallendem Eingang unter die Rückschaltschwelle wieder freigeben. Daher garantiert nur **MIN(V_OVP_FALL) >32V** einen Wiederanlauf bei genau32V. Frühere Weg-C-Modelle behaupteten irrtümlich, MAX(V_OVP_FALL)<32V sei PASS. Dies ist das genaue Gegenteil und wurde in diesem Branch in den Testkommentaren und in der neuesten Regression revidiert. Die früheren Round8-Berichte sind historischen Datums und **keine gültige Eignungsaussage** mehr.

**TPS26600, TI SLVSDG2G RevG S.7:** OVP rising Referenz 1.170..1.225V, falling 1.085..1.125V. Bei gleicher Spannungsteilerverstärkung G wären selbst bei idealen Widerständen, Null-TCR und keinerlei Pinleckages gleichzeitig erforderlich:
- 1.085*G >32 -> **G>29.493088**
- 1.225*G <=36 -> **G<=29.387755**
Dies hat **keine Schnittmenge**. Für garantierten falling_min >32 würde rising_max mindestens 36.129V erreichen. Toleranzen, TCR und Leckströme können keine Hersteller-Garantie aus einem unmöglichen Idealgrenzenpaar machen.

Die früher ausgelegte, herstellerkonforme TPS26600 Dreiwiderstands-UVLO/OVP-Ladder (86.6k/9.65k/3.57k, 0.1%) erzielt rising32.633..34.336V, **falling30.261..31.535V: definitives FAIL** der 32V-Recovery; UVLO rising8.846..9.277V. Die frühere Aussage PASS war verkehrt. Die factory-OVP des TPS26600 hat rising MIN31V, falling MAX31.5V und erfüllt auch den Dauerbetrieb bei32V nicht zuverlässig. Zusätzliche echte OV-Schmitt-/Referenz-/Logikbauteile würden Risiko/Kosten erhöhen und den geringfügigen 2-Positionen-Vorteil aufzehren.

**Wichtig für jede spätere Pinprüfung:** TPS26600 TPS2660 §10.4: **RTN NICHT direkt mit GND kurzschließen**, sonst wird der integrierte Verpolschutz außer Kraft gesetzt. RTN ist die lokale Bezugsklemme von ILIM, UVLO, OVP und Softstart, GND ist eigener Pin.

## 2. 58V/350ms, 10V, Ta60C und Fehlerrisiken

TPS26600 arbeitet nominal bis60V, hat aber nur **62V absolute VIN**. Das 70V-Transientenrating gilt nur **10ms bei25C**, nicht für350ms. Bei Vin58V stehen 2V empfohlen und 4V absolut Abstand zur lokalen Pinspitze. TI §11.1 warnt ausdrücklich vor Leitschleifen-Induktivität beim Überstrom-Abschalten. Ein rein illustratives TI-Näherungsmodell V_INpin≈58V + I*sqrt(L/Ceff) liefert bei angenommenen I2.35A, 2µH und effektiver C_IN0.47µF **62.848V >62V ABS**. Bei einem langsamen Load-Dump kann OVP früher abschalten; kurze Last-/Hotplug-Transiente müssen aber separat beherrscht werden. TPS26631 hat unter demselben 58V-Bedingungsfall ebenfalls nur 2V bis zur empfohlenen60V-Grenze, jedoch 9V zur67V-AbsMax. Das ist noch kein Nachweis für A: ohne tatsächliche Pad-Messung keine Freigabe.

TPS26600 Gesamt-Rds(on) über Temperaturspezifikation max250mΩ. Am ungünstigen 10V-Eingang unter angenommener Regler-Effizienz 85%, 5Vx2A + RAW0.5A: selbstkonsistente 1.730A gemeinsame Last, 9.568V hinter eFuse, 0.748W eFuse-Verlust; mit PWP-ThetaJA38.6K/W und Ta60C ergibt sich ein **nur modelliertes** Tj88.9C. 5.36k ILIM-Widerstand gibt TI 2.11A MIN/2.23A TYP/2.35A MAX an, nur 0.380A Margin im Normalbetrieb; inrush, cable drop, NTC/temp, 32V buck thermal und Ceff sind nicht getestet. Ein 2.35A eFuse-Limit ist kein selektiver RAW-0.5A-Fehlerstromschutz.

+85C **Umgebung** Safe OFF ist nicht durch TPS26600/31 eigene Junction-Thermalschutzschwelle gegeben. A untersucht 67F080/67L080 Thermostate und MF-LSMF075/72X-2 72V PPTC RAW; separater Hersteller-/Hot-/Lowcurrent-/Spulen-/PPTC-Derating-Nachweis fehlt. ACC/RUN-HOLD, fail-HIGH Power-Fail, M8/USB-Rückspeisung, Host-Mainboard, FRAM-first sind gleicher Systemumfang für alle Kandidaten. Keine ungeprüfte CR-Knopfzelle speist die 5V2A-Hauptlast. Bei M8-Abziehen ist die Vorwarnzeit Null.

## 3. Echte andere integrierte Herstellerteile geprüft

| Kandidat | Daten und Preis-/Lagerbeispiel netto je1/10/100 | Warum kein besserer vollständiger Ersatz |
|---|---|---|
| TI TPS26600PWPR | 4.2–60V, 62V ABS, interner Reverse-MOSFET, 2.35A Max. DigiKey ca3.33/2.51/2.0797EUR, Bestand abhängig vom Vertrieb (neu DE 0, ältere Treffer 16k) | Garantierbares 32V-recovery OHNE Extra-Hysterese unmöglich, <62V at pad nicht bewiesen |
| TI TPS2662 | 60V/62V ABS, integriert Reverse, 478mΩ typ, 0.025..0.88A | Keine ausreichende 10V-5V2A-Eingangsstromlast |
| TI TPS48110AQDGXRQ1 | Automotive AEC-Q100; 3.5..80V Betriebsbereich, 100V ABS; ca4.26/3.24/2.71EUR, Mouser etwa7815 | Externe 2x Back-to-back FET + Shunt + weitere R/C; keine belegte Reduktion >=3 Positionen vs A25 |
| ADI LTC4368HMS-2#WPBF | 2.5..60V empfohlen, 100V VIN ABS, SENSE/VOUT eigene80V-Grenzen; Mouser 7.57/5.88/4.99EUR und 833 Bestand im geprüften Snapshot | 2 externe Power-FETs, Shunt, mehrere UV/OV-/Gate-Passive, größer/teurer als A |
| ST STPM801-TR | Integrierte Idealdiode/HotSwap-Steuerfunktion, UV/OV mit externen MOSFETs; Mouser 8.97/7.11/6.12EUR, Momentbestand104 | Hochvolt-/Power-MOSFETs und Sense-Passive fehlen im IC, kein kompletter Kostenvorteil |
| RECOM RPH3.0 oder TI LMZ36002 | 55V bzw 60V Moduleingang | 58V im FET-short nicht ausreichend zum unabhängigen Ausgangsschutz belegt; Modul teuer und höherer Reparatur- und Derating-Aufwand |

**Keiner der Controller enthält die externen Power-MOSFETs UND garantierte Hysterese UND ausreichend belegte 58V-Padreserve plus 5V2A/RAW/85C-Aufgaben in weniger Teilen.** TLC/Controller-Preis ist keine vollständige BOM.

## 4. Faire identische TripPower-Board-Grenze und Preisvergleich

A-GitHub-Quelle, wirklicher aktuell gezeichneter 25er BOM: hardware/modules/TripPower_REV6_A/REV6_A_25_PART_ORDER_BOM_2026-10-15.csv auf design/trippower-a. In eigener Datei **REV6_ROUND9_A25_VS_A23_FACTORY_32V_RESTART_PRICE_2026-10-16.csv** wurden alle 25 Positionen exakt als Native/ACTUAL kopiert und nur für einen separaten, ausdrücklich *ungebauten* A23-Vergleich eine Hersteller-UVLO-/OVLO-Vereinfachung abgebildet. Kein Board-fremdes F_MAIN/TripTracer/ACC-Harness in der bestückten TripPower-Liste.

| Status | Echte native bestückte Positionen | Nur belegte Netto-Teilsumme 1 / 10 / 100 St | Fehlendes |
|---|---:|---|---|
| **A25 echte KiCad10-native REV6-Basis** | **25**, 23 Preise | **19.389 /12.883 /10.1371 EUR** | A-R202=12.4k nicht EUR-bepreist, L101 Fangcheng EUR-Preis/Hot-LCSC USD, volle RAW/85C/Stecker-Funktionen |
| **A23 TPS26631 factory OVP als nächste Entwicklungsoption** | **keine native Variante – 23 theoretisch** | **19.113 /12.641 /9.9001 EUR** (Preiszeilen nach echten A-MPNs und neuem 300k) | noch L101, neuer ERC, richtige Pin-Verkabelung und Temperatur-/RAW-Schutz |
| C23 TPS26600 aus früherer Round8-Projektion | **keine REV6-C-Netzliste, nicht bestückt** | Kein vollständiger vergleichbarer Preis für eine die Forderungen erfüllende Schaltung | Herstellerfallende-Hysterese garantiert FAIL, 62V riskant |
| LTC etc | keine native C-REV6-Leiterplatte | nur IC-/Power-FET-Snapshot, kein voller BOM-Preis | Mehr externe FETs, Shunt/RC, Safety-Gates |

**A-Verbesserung, konkret auf Herstellerreferenz:**
1. TI TPS2663 RevG §8.3.4: OVP PWP20 Pin8 **direkt an GND** (factory OVP). Datenblatt garantiert *rising 33.2..35.4V, falling 32.7..35.0V*. Beim 32V stabil gilt 32V unter der minimalen Rückkehrgrenze 32.7V; nach ext Reverse-Q201 drop liegt der Pin noch niedriger. Damit stimmt *statisch* Hysterese und erfordert nicht den nahezu auf57mV knappen 0.1%-Teiler aus A.
2. TI §8.3.3: UVLO PWP20 Pin7 **niemals auf GND** (factory UVLO 15.1..15.9V verfehlt10V). UVLO darf NICHT offen bleiben und bei Reverse-FET Q201 auch NICHT direkt an IN_SYS: **mindestens 300kΩ von UVLO nach IN_SYS**, laut TI explizite Vorschrift. Ein konkreter kaufbarer Yageo **RC1206FR-07300KL** 300k 1% 1206 0.25W ±100ppm/K Mouser EU **0.086/0.022/0.015EUR** 1/10/100. 330k/470k wären nach TI größerer Mindestabstand und noch auf UVLO-Leckstrom, Start10V, 58V-Fehler zu rechnen.
3. A25 R201 (100k 0.1%), R202 (12.4k 0.1%), R203 (4.22k 0.1%) aus 3er Netz entfernen und **ein** UVLO/IN_SYS-R einsetzen = **2 weniger bestückte Positionen**, gleiche Q201/Q202 Reverse-FETs; A25→hypothetisch A23. Kein nativer C-/A23/ERC-Beleg und kein vollständiger Serienpreis. Preiszeilenersparnis bisher **0.276/0.242/0.237EUR** plus zuvor unbepreister A-R202; besserer Recovery-Grenzwert ist echter technischer Grund, Bauteilersparnis sekundär.
4. Zusätzliche kostengünstige Maßnahmen bei A: beste vorhandene KEMET/Taiyo-MLCC Hersteller-DC-Bias-Ceff quantifizieren, Fangcheng L101 Hot-Isat/DCR/LCSC-Euroangebot vs Bourns SRP7050TA-150M AEC-/EUR-Angebot testen, nur nötige 100nF/COUT belassen nach Referenz-Buck-Stabilität, RAW-Abgang Hot-PPTC nur falls Fehlerbegrenzung nötig und bis70C qualifiziert, +85C ohne zusätzliche SHDN-Hilfsversorgung bevorzugt **zugelassenen** mechanischen Temperaturschalter am TripTracer-Relais prüfen. Nichts ohne eigenes Safety Gate als entfallend zählen.

## 5. Verbindliche Sicherungs-/Systemtrennung

TripPower-BOM: 0 Schmelzsicherungen, 0 Halter, 0 Einmal-SMD-Thermosicherungen. SMD-PPTC nur separat herstellerqualifiziert und zwingend funktionsmäßig nötig, nicht automatisch bestücken. F_MAIN und Halter (z.B. Littelfuse MINI 0997004.WXN 58V und 0FHM0001ZXJ-RED) gehören ausschließlich zum quellnahen Fahrzeug-Harness, optional zugängliche Sicherung auf TripTracer zur Mainboard-BOM, NIEMALS in A25 oder künftige A23 TripPower-Population. Die F_MAIN/58V-DC-Clearing-Hardware plus Kabel-I²t bleibt eigenständiger Nachweis. Mainboard MCU-Relay, USB/M8/RTC/SD und fail-high PWR_FAIL zählen separat.

## 6. Abschluss / Tests

**C NO-GO für weitere eigenständige Schaltungsentwicklung**: Mit unveränderten Anforderungen erfüllt keine getestete Alternative das 3–5-Positionen-/klarer Vollkosten-/Zuverlässigkeitskriterium. Deshalb bewusst **kein neuer KiCad10-REV6-C-Schaltplan**, keine erfundene native C-ERC/Netzliste/DRC. Die korrigierten Tests sind nur mathematische Falsifikation.

Nachfolgende Planung für Weg A: Herstellerfactory OVP + >300k UVLO als getrennten **A23-Versuchsstand** zeichnen und echten nativen KiCad10 ERC/Netlist laufen lassen; 10/32/36/58V-Dynamik, max 60V am TPS26631 Eingangspin sowie Vout/RAW/M8/USB bei eFuse-short prüfen; VIN10 full-load Ta60C LMR/Inductor/Ceff/PCB Cu messen; +85C sichere temperaturgeführte Hauptabschaltung plus RAW-selective-PPTC/Stecker-/Leitungsfehler und FRAM-first/PWR_FAIL; nach diesen Gates getrennt System/BOM Euro 1/10/100 komplettieren. **Kein PCB- oder Fahrzeug-GO**.

Quellen: https://www.ti.com/lit/ds/symlink/tps2660.pdf ; https://www.ti.com/lit/ds/symlink/tps2663.pdf ; https://www.ti.com/product/TPS4811-Q1 ; https://www.ti.com/product/TPS2662 ; https://www.analog.com/en/products/ltc4368.html ; https://www.st.com/en/automotive-analog-and-power/stpm801.html ; https://eu.mouser.com/en/ProductDetail/YAGEO/RC1206FR-07300KL ; https://www.mouser.de/ProductDetail/Analog-Devices/LTC4368HMS-2WPBF .
