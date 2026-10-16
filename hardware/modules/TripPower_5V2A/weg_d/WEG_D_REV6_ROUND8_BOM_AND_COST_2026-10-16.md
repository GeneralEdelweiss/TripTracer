# Weg D REV6 Round 8 – vergleichbare Stücklisten / Kosten 1, 10 und 100 (2026-10-16)

**Ehrliche Abgrenzung:** [Exakte Positionsmatrix mit 85 CSV-Zeilen](WEG_D_REV6_ROUND8_BOM_MATRIX_2026-10-16.csv) enthält alle **25 tatsächlichen Weg-A-Revisionspositionen**, Alternative TPS26600 (8 zu qualifizierende Frontendpositionen), LTC4368 (13 Frontendpositionen), die gemeinsamen 15 Buck-/PG-Positionen und funktional **fehlende** Thermik-/RAW-/Anschluss-Positionen sowie OFF-BOARD Fahrzeug-/Hauptplatinenkosten. **Kein voll bestellbarer REV6-Entwurf** ist vorhanden; unbekannte Positionen/EOL werden niemals zu 0€ oder einer vermeintlich vollständigen Kostenberechnung addiert.

## 1. Stückzahl und physischer Ort

| Block | A TPS26631 | B TPS26600 | C LTC4368-2 | Ort |
|---|---:|---:|---:|---|
| Gemeinsamer Weg-A-Buck TI LMR38020 inkl. L/C/R + PGOOD-Puffer (historischer Prototyp) | 15 | 15 | 15 | TripPower |
| Eingangscontroller | 1 | 1 | 1 | TripPower |
| Externe Leistungs-MOSFETs | 1 (reverse) | 0 | 2 (reverse + OV) | TripPower |
| Zusätzlicher MOSFET-Gate-Helfer | 1 | 0 | 0 (GATE intern gesteuert) | TripPower |
| Strommesswiderstand | 0 (IC intern) | 0 (IC intern) | 1, Kelvin | TripPower |
| UV/OV/Current-R | 4 | 4 (neue Werte) | 4 UV/OV +1 Gate =5 | TripPower |
| VIN/OUT/dVdt/GATE/RETRY-C | 3 | 3 (neue Werte) | 4 | TripPower |
| **Explizite Prototyp-Frontendpositionen** | **10** | **8** | **13** | nur A ist KiCad-netlist-derived |
| **Bestückte Basissumme ohne offene Zusatzfunktionen** | **25 (KiCad)** | **23 (Konzept)** | **28 (Konzept)** | TripPower |
| +85°C Ambient-Off mit definierter Sensor-Open/Short-FMEA | TBD | TBD | TBD | TripPower bzw. belegter TripTracer Shutdown-Control |
| RAW 0.5A thermisch sicherer Abzweigschutz und mechanische Verbindung | TBD | TBD | TBD | TripPower/TripTracer-Schnittstelle |
| Fehlender realer Connector, Testpads/3D | TBD | TBD | TBD | TripPower/TripTracer |
| Quelle BAT+/ACC Sicherung plus Sicherungshalter | **0** | **0** | **0** | **NUR Fahrzeugkabel/System**, NICHT TripPower |
| PPTC/Einmal-SMD-Schmelzsicherung/200V DO218 | **0** | **0** | **0** | nicht bestücken (PPTC nur bei begründetem neuen Gate) |
| USB-Stromweg/RTC/FRAM-Power-Mux/SD-Backup | nicht hier gerechnet | nicht hier gerechnet | nicht hier gerechnet | TripTracer-Hauptplatine |

**Klarstellung:** Die 25 Weg-A-Positionen sind ein tatsächlicher nativer KiCad-10-ERC0-Prototyp. Die anderen Positionszahlen sind rechnerische Hersteller-Referenz-Architekturen, **keine** geprüften Schaltpläne. Die Temperaturfunktion und RAW-Selektivität fehlen bei allen dreien – deswegen **keine vollständige endgültige bestückte Positionszahl**.

## 2. Nachprüfbare Kostenstaffeln (EUR netto je Teil, 1 / 10 / 100)

| Bauteil | MPN | 1 | 10 | 100 | Quelle und Stand |
|---|---|---:|---:|---:|---|
| A eFuse | TPS26631PWPR | 3.870 | 2.937 | 2.4461 | DigiKey DE: https://www.digikey.de/de/products/detail/texas-instruments/TPS26631PWPR/12165168 |
| A reverse FET | SQM100N10-10_GE3 | 3.780 | 2.490 | 1.750 | Weg-A-25er-Recherche, erneut verifizieren |
| A Gate-Helfer | BSS138LT1G | 0.292 | 0.129 | 0.113 | Weg-A-25er-Recherche, erneut verifizieren |
| B eFuse | TPS26600PWPR | 3.440 | 2.594 | 2.1495 | DigiKey DE: https://www.digikey.de/de/products/detail/texas-instruments/TPS26600PWPR/6199305 ; industrielle Variante, Lagerbestand schwankt |
| C Controller | LTC4368HMS-2#WPBF | 7.570 | 5.880 | 4.990 | Mouser DE: https://www.mouser.de/ProductDetail/Analog-Devices/LTC4368HMS-2WPBF , Automotive W |
| C 2x Demo MOSFET | SIR870DP-T1-GE3 | je2.930 | je1.910 | je1.3256 | DigiKey DE: https://www.digikey.de/de/products/detail/vishay-siliconix/SIR870DP-T1-GE3/3748958 ; **unbelegte AEC/SOA** |
| Gemeinsamer Buck | LMR38020SQDDARQ1 | 3.910 | 2.965 | 2.4703 | DigiKey DE https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286 ; Teil ist in A-BOM enthalten |

**Für einen fairen Preisvergleich nur des jeweils notwendigen Eingangs-IC-/FET-Blocks** (ohne passive Bauteile; keine Teilebestände oder AEC-Eignung behaupten):
- **A Controller + Verpol-FET + Gate-Helfer = 7,942 / 5,556 / 4,3091 €**
- **B TPS26600 = 3,440 / 2,594 / 2,1495 €**. Gegen A theoretisch −4,502 / −2,962 / −2,1596 €.
- **C LTC4368 + 2 Demo-FET = 13,430 / 9,700 / 7,6412 €**. Gegen A **+5,488 / +4,144 / +3,3321 €**, **vor** C-Kelvin-Shunt und Präzisions-R/C.

Preiswährungen homogen EUR NETTO; Versand/Mindestwert/PCBA/PCB/Montage/Ausschuss nicht enthalten. A-Bauteilpreise stammen teilweise aus älteren Snapshots; neue Preise sind nur Abfragen, keine garantierten Lieferangebote.

## 3. Aus echter Weg-A-BOM ableitbare, aber nicht gleichwertig vollständige Teilbeträge

Die **14 von 25** in A-Order-BOM bepreisten Teile summieren sich historisch zu **15,789 / 10,632 / 8,4331 €** je1/10/100. Die zwei MOSFETs + A eFuse sind Teil davon (historische U201 3,89/2,96/2,46; Q201 3,78/2,49/1,75; Q202 0,292/0,129/0,113). Rest der bepreisten Originalteile (tatsächliche Buck+PG/passives Teilgruppe) ist **7,827 / 5,053 / 4,1101 €**.

Rein arithmetischer **preisbelegter Kern** unter Annahme sonst gleicher bepreister A-Bauteile:
- **A**: 15,789 / 10,632 / 8,4331 € (**14/25** A-Positionen mit Preisen, nicht 25).
- **B**: Rest 7,827/5,053/4,1101 + TPS26600 3,440/2,594/2,1495 = **11,267 / 7,647 / 6,2596 €**, noch nicht angepasste OVP-/RILIM/C/Footprint-Werte und Preise offen.
- **C**: derselbe Rest + LTC Controller + 2×FET = **21,257 / 14,753 / 11,7513 €**, Shunt, gate passives und precise resistors noch **unbepreist**.

**Weder die A-BOM noch die B-/C-Konzept-BOM ist vollständiger bestellbarer Preis.** Weg A: 11/25 nicht bepreist, drei **GRM32ER71E226KE15L** EOL, L101-FCH0650 Hersteller/Isat/Thermik und Footprint ungeprüft. In B/C müssen auch getauschte R/Cap-Werte nach exact MPN qualifiziert werden. C-FET SiR870 kein belegter Automotive-Hot-SOA. Bei +85°C fehlen Thermalsafe und eigener RAW-Fehlerstromschutz – daher sind die arithmetischen Summen **keine** kostenfunktional gleichwertigen Endpreise und der Preisabstand kann sich verändern. Spezifische Teilwerte und Notizen vollständig in der CSV.

## 4. Vollkosten-Pflichtregister (nicht stillschweigend auf Null setzen)

Vor einem abschließenden 1/10/100 **Seriengesamtpreis** explizit auspreisen (und Installationskosten nicht ins Modul mischen): vorgeschriebener HOT-SHUTDOWN / Sensorfehlerkette (typisch eigene Temperaturmessung+Schaltglied+Pull-Netz), RAW0.5A lokale Kurzschluss-/Leitungs- und Steckerkonfiguration, alle aktuell unbepreisten 1206/1210 100V-passiven Teile, IN-C nach tatsächlichem 58V-HF-Ringing, ggf. nachweislich zweckmäßige schnelle TVS bei EMI/ESD, wirklicher 100V-FET-Hot-SOA, Shunt für C, 0.1%-R, REV6 5V2A/60°C-Buck-/Induktor-/MLCC-Ersatz, benötigte Montagepads und PCB-Thermik. Grundsystem TripTracer Microrelais/ACC, USB-C/Haupt-5V Power-Mux, RTC/FRAM/SD-Backup und notwendige fahrzeugnahe Leitungssicherung/Halter **separat**.

**Externer Systemfuse-Benchmark (NIE TripPower-BOM):** Littelfuse MINI58V 4A **0997004.WXN** plus **0FHM0001ZXJ-RED** 58V-Durchleitungs-Halter laut Weg B; Sicherung z.B. ~0.88/0.673/0.5153 €/Teil1/10/100 aus B (aktuelle Preise erneut prüfen). Sicherungs-/Halter-Preis gehört nur in **SYSTEM_HARNESS**. An tatsächlicher Fuse-Unterbrechstelle muss DC-break ≤58V inkl Ringing sowie maximaler Fehlerstrom/Kabeltemperatur geprüft werden. Kein nicht rückstellendes Teil auf TripPower; keine 58V-PPTC pauschal in V1.

## 5. Ausgabezustand und Entscheidung

- **Kostengünstigste plausibel qualifizierbare Ausgangsbasis:** Weg-A-TPS26631-Prototyp; neuer LTC-Nachbau ohne nachgewiesene lokale Überspannungs-/AEC-Anforderung hat keinen rationalen Kosten-/Montagevorteil.
- **Günstigstes IC-Teil:** TPS26600, jedoch wegen62V/350ms-Ringing, Last-/Anlauf-Stromgrenze und eingebautem Industrial-Grade aktuell **kein bevorzugter V1-Schutz**.
- **Risikoreserve:** LTC4368 nur bei gemessenen TPS-gefährdenden Überschwingern und dann vollständig neu zu qualifizieren. Kein LTC-KiCad bei nicht nachgewiesenem Vorteil.
- **A/B/C oder gemeinsamer REV5-Stand wurden nicht verändert.** Die Abgrenzung „vollständige Bauteilliste vs teilweise bestückfähiger Preis“ bleibt P0.
