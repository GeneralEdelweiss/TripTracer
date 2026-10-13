# TripTracer – 80/20-Vergleich der Versorgung: Kosten, Teilezahl und Sicherheit

**Vergleich: 13.10.2026 · Konzeptprüfung, kein vollständiges verifiziertes Schaltbild, keine ISO-/ERC-/DRC-/Testfreigabe.** Sicherheitspriorität: Vermeidung von Brand, Leiterbahn-/Kabelüberhitzung und gefährlichen Kurzschlüssen; kurzzeitiger Ausfall, Reset oder seltener Verlust einer noch offenen Aufzeichnung sind akzeptabel. Einsatz: 12-/24-V-Fahrzeuge, **9–36 V normal**, **6 V beim Motorstart**, **ISO 16750-2:2023 als Entwicklungsziel mit ungedämpftem ~200-V-/24-V-Load-Dump**, ACC-/BAT+-M8, MCU-geordneter ACC-AUS-Nachlauf, USB ohne Backfeed. **JLCPCB-PCBA ist nur Option; lieferbare Herstellerteile und Handbestückung zuerst.**

## 1. Vergleichsgrenze: nicht Äpfel mit Birnen

Verglichen wird **BAT+ bis geregelte 5 V plus einfache ACC+MCU_HOLD-Ansteuerung**. Sämtliche Varianten enthalten denselben **LMR36520 5V/2A-Buck mit erforderlicher Induktivität, Ein-/Ausgangskondensatoren, Feedback und Entkopplung**. **Nicht enthalten**: externe BAT+/ACC-Fahrzeugleitungssicherungen und Halter, Stecker/Kabel, 3V3-LDO, USB-/SD-Service-Power-Path, Display-/Backlight-Treiber, PCB, Bestückungszeit, MwSt., Zoll/Versand und Testkosten. Die BAT+/ACC-Fahrzeugleitungssicherungen bleiben in allen Varianten zwingend, ihr Strom-/DC-Spannungsrating und Auslöseverhalten sind noch auszulegen.

**Bauteilanzahlen sind grobe Architekturzählungen, KEINE vollständige Netlist/BOM**; sie zählen auch Widerstände/Kondensatoren, nicht bloß aktive Halbleiter. Geschätzte Gesamtbauteilpreise sind **Planungsspannen**, NICHT echte aktuelle Händler-Warenkörbe und nicht über Mengenstufen übertragbar. Die genannten bekannten EUR-IC-Preise sind dagegen direkt aus den betreffenden Einzel-/Staffelangeboten entnommen. USD-LCSC-Preise **nicht ohne Wechselkurs und Nebenkosten mit EUR summieren**.

| Variante | Aufbau, gemeinsamer 5V-Buck immer enthalten | Grobe Stückzahl BAT+→5V inkl. ACC-HOLD | Grobe Materialspanne 1 Gerät, netto | 200-V-Test-A-Ziel | gefährliche Fehler nach aktuellem Kenntnisstand |
|---|---|---:|---:|---|---|
| **A – MegaSquirt-Prinzip** | DC-Fuse extern, 24-V-geeignete TVS + Diode/Verpolschutz, 5V-Buck, Dioden-ACC-HOLD | **ca. 17–25** | **ca. 6–11 €** | **NEIN, 200-V-/350-ms-Energie und 65V-Buck nicht geschützt** | Buck-5V-Hiccup/Temperaturschutz vorhanden; *Buck-VIN/PCB vor Regler* nur Sicherung/TVS, kein abgesicherter unsuppressed Load-Dump-Fall |
| **B – LM74800 + externe Schutzsicherung** | LM74800, 250-V-Q1, 60-V-Q2, Zener/TVS, 63-V-geeignete und strom-/I²t-/Abschaltvermögen-geprüfte *einmalige* SMD-Sicherung **nach** der geschützten Stufe, Buck, ACC-HOLD | **ca. 29–40** | **ca. 10–16 €** | **TI-Referenz vorhanden; unser Design ungetestet** | Aktive Surge-OFF/Verpol- und Rückstromsperre; **harter** Kurzschluss kann durch Sicherung getrennt werden, **mittlere/langsame Überlast unter dem Fuse-Schmelzstrom** nicht unbedingt. Sicherung muss geeignet platziert und voll dimensioniert sein |
| **C – LM74930** | LM74930, 250-V-Q1, 60-V-Q2, Zener/TVS, Shunt, OC-/SCP-/Fault-R/C, Buck, ACC-HOLD; **keine zweite TPS26631** | **ca. 35–48** | **ca. 14–20 €** | **TI-Referenz und Test-A-Applikationsnotiz vorhanden; unser Design ungetestet** | Wie B plus **einstellbarer Überstromschutz und Kurzschluss-Circuit-Breaker**, wahlweise **Latch-Off** statt dauerndem Heiz-Zyklus; bessere Kontrolle auch bei mittelgroßen Fehlerströmen; Fehlprogrammierung/Fehlverhalten des IC bleibt relevant |

**Nicht verwechseln:** Die früher genannten **21,92 €/Gerät** galten *allein* für die überdimensionierte Schutz-BOM aus **LTC4380 + TPS26631 + zwei 250-V-FETs**, **ohne gemeinsamen 5V-Buck**. Diese Doppelcontroller-Lösung wird **nicht empfohlen**; obige C-Planungsspanne enthält bereits den 5-V-Buck. Die Materialspannen sind bewusst breit wegen noch fehlender verbindlicher FET-/TVS-/L-/MLCC-/Zener-/Sicherungs-MPNs.

### Harte IC-Einkaufspreise, EUR netto pro Gerät, getrennt von der Schätzung oben

| ICs pro Gerät | 1 Gerät | 10 Geräte | 100 Geräte |
|---|---:|---:|---:|
| A: **LMR36520** | **2,80 €** | **2,11 €** | **1,74 €** |
| B: **LMR36520 + LM74800** | **5,38 €** | **4,05 €** | **3,33 €** |
| C: **LMR36520 + LM74930** | **8,19 €** | **6,24 €** | **5,21 €** |
| **C gegenüber B nur IC-Mehrkosten** | **2,81 €** | **2,19 €** | **1,88 €** |

Preise: [Mouser LMR36520ADDAR](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LMR36520ADDAR), [Mouser LM74800QDRRRQ1](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74800QDRRRQ1), [Mouser LM74930QRGERQ1](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74930QRGERQ1). **Zusatzkosten von C:** Sense-Shunt, mehr Passivbauteile, 24-VQFN + Unterseitenpad schwerer handzulöten als 12-WSON von B, jedoch auch B nicht trivial. Erste Risikoreserve für C gegen B: **ungefähr 3–5 € pro Einzelsatz**, erst nach vollständiger BOM zu bestätigen.

**Beschaffbare MOSFETs:** onsemi **FQD16N25CTM 250V DPAK** bei LCSC ca. **$0.9493/1**, **$0.8064/10**, **$0.6652/100**, zuletzt lagernd: [LCSC C415866](https://www.lcsc.com/product-detail/C415866.html). **Nicht unkritisch final verwenden**: R_DS(on) nur bei V_GS=10V spezifiziert, 6V-Kaltstart/Gate-Charge/SOA/Temp/200V+Ringing prüfen. Für 60V-FET wäre z.B. **Infineon IRFR7546TRPBF** bei LCSC ca. **$0.5658/1**, **$0.441/10**, **$0.3194/100**, [C114422](https://www.lcsc.com/product-detail/MOSFETs_Infineon-Technologies-IRFR7546TRPBF_C114422.html); dessen Gate-Ladung/Leckstrom/Package ebenfalls prüfen. **Echte Quellenverfügbarkeit vor Kauf neu abfragen**.

**Konkrete mögliche Sicherheitsersparnis für B:** Eine **63V-DC/2A-SMD-Sicherung** ist kein teurer eFuse-IC. Zum Beispiel **Littelfuse 1206SFS200F/63-2** mit **63V DC, 50A Abschaltvermögen**, [LCSC-Produkt](https://www.lcsc.com/product-detail/C315917.html) zuletzt allerdings ausverkauft (Preisreferenz **$0.3418/1**). Alternativ **SCHURTER 3413.0219.22** 63V/2A/63A Abschaltvermögen [LCSC](https://www.lcsc.com/product-detail/C3164908.html), zuletzt nur wenige lieferbar; hier **$0.4854/1**. Entsprechend **keine** Lagerfähigkeit/finale Freigabe behaupten. **2A ist nur ein Testwert, kein ausgerechneter Sicherungsstrom**: Bei 6V/Lastspitzen könnte sie zu früh öffnen, bei Teilkurzschlüssen womöglich nicht. Die Sicherung **nach** OV-FET muss selbst bei **FET-defekt-leitend** und 200V transient elektrisch sicher bleiben; eine 63V-Nennsicherung bietet in diesem gemeinsamen Fehlerfall **keine allgemeine 200V-Interrupt-Garantie**. Externe Quelle weiterhin separat passend absichern.

## 2. Sicherheits-/Risikovergleich (nicht mit „funktioniert“ gleichsetzen)

| Fall | A | B (mit echter Sicherung) | C |
|---|---|---|---|
| 9–36V normal | Bauteilziel, ungeprüft | wie A, ungeprüft | wie A, ungeprüft |
| 6V Start & 5V_OUT | **kritisch bei Serien-Diode**: 0,5–0,8V Vf lässt kaum Buck-Dropout-Reserve | FET-Verlust viel kleiner, aber Gate-/Buck-Dropout zu verifizieren | wie B |
| 200V Test-A Last Dump | **NEIN** | TI-Referenz vorhanden, nach VDS/SOA/TVS/OV-FET-Gate-Auslegung | TI-Test-A-Applikationsbeispiel, ebenfalls neu zu validieren |
| Verpolung/Rückspeisung | Diode, ggf. zusätzlicher Power-Path; 6V-Drop | Q1 ideal-diode | Q1 ideal-diode |
| 5V-Ausgang Kurzschluss | Buck-Hiccup + Thermal Shutdown | Buck wie A | Buck wie A, zusätzlich Eingangsschutz bei hochströmigen Fehlern |
| Kurzschluss **zwischen Schutz-IC und Buck** | Externe Fahrzeug-Sicherung | Externe Sicherung + ggf. lokale Schmelzsicherung **nach HV-Schutz** | Externe Sicherung + elektronische Cut-off durch Sense |
| Dauernder Teilkurzschluss mit gefährlicher PCB-Erwärmung, aber **unter Sicherungsauslösestrom** | muss als Risiko bewertet werden | **B hat Lücke ohne passenden I²t-/Thermiknachweis** | **C bietet justierbare Trip-Schwelle; keine Garantie ohne Rsense-/Kühlungsprüfung** |
| Thermisches Fehlverhalten FET/TVS selbst | Sicherung + SOA/TVS-Impulsenergie prüfen | Sicherung + Q1/Q2/SOA prüfen | wie B; elektronischer Schutz behebt nicht alle eigenen FET-Kurzschlussfehler |
| Handlötbarkeit | am besten, trotzdem Buck-PowerPad | aufwendiger (WSON-12 + 2 DPAK) | am aufwendigsten (VQFN-24 + DPAK + Shunt) |
| OFF-Standby <100µA | Buck-EN gut möglich, ACC-Teiler prüfen | OV-Teiler 100k/3.48k dauerhaft ~348µA bei 36V, **muss korrigiert/abgeschaltet werden** | auch hochohmige oder geschaltete Teiler prüfen; controller I_SD nicht allein maßgeblich |

Schutz-ICs nach [TI LM7480](https://www.ti.com/product/LM7480-Q1), [TI LM74930](https://www.ti.com/product/LM74930-Q1), [TI 24V Test A Applikationsnotiz](https://www.ti.com/document-viewer/lit/html/SNOAAA1/GUID-A29F6540-095F-4408-8FD4-388A1740884B), [TI LMR36520](https://www.ti.com/product/LMR36520) (inkl. Hiccup-5V-Kurzschlussschutz). MegaSquirt Referenz [Original V3.57 Seite 6](https://www.megamanual.com/357/MS357.pdf).

## 3. Entscheidung

**Entwicklungspräferenz: C = LM74930-Q1 plus LMR36520**, mit **OV CUT-OFF statt linearer Leistungsklemme**, **Latch-Off** bei hartem/anhaltendem Fehler als noch zu testende Betriebsart und **einfacher ACC+MCU_HOLD-Einschaltsteuerung**. **Keine** zweite TPS26631, kein teures Relais, kein zusätzlicher Hardwaretimer, keine großen Datenerhalt-Puffer, kein „Vollbetrieb während 200V“. Für eine geringe vorläufige Mehrkostengröße von ca. **3–5 € gegenüber B** verbessert C gezielt den für den Nutzer wichtigsten Fehlermodus: **überhöhter Strom, überhitzte PCB**, anstatt nur eine selten unterbrochene GPX-Aufzeichnung zu retten. **Das ist der Funktionsgewinn, der den Preis begründet.**

**80/20-Fallback:** B + entsprechend dimensionierte Schmelzsicherung (lokal + externe Fahrzeugleitung) **statt** LM74930, **falls** Worst-Case-Kurzschluss-/Teilkurzschluss-/Dauerüberlast-/FET-Fehlertests die gleiche elektrische/thermische Sicherheit belegen und B inklusive Handmontage signifikant günstiger ist. Der B-Aufbau darf nicht allein aufgrund „Sicherung vorhanden“ als sicher deklariert werden. A ausschließlich als **strombegrenzter Labornetzteil-Basisaufbau** ohne ISO-Test-A-Anspruch oder Fahrzeugfreigabe.

### Nächster fest verdrahteter Entwurf

1. **Zunächst echten Schaltplan** (Hersteller-Rev., pin- und footprintgeprüft) für 6–36V, 200V **CUT-OFF**, 5V/2A, MCU-HOLD und USB-Entkopplung erstellen; keine Platzhalterblöcke als validiert ausgeben.
2. **Strom-/Thermikbudget 6 V, 9/12/24/36 V** und FET-OFF-/Schutz-Ruhestrom berechnen; Sense-Schwelle beim LM74930 nicht aus dem für 45W/5A entwickelten TI-Beispiel kopieren.
3. **Kosten-BOM aus realen bestellbaren Herstellernummern** mit 1,10,100-Stückzahlen, Leiterplatten- und Handbestückungswerten; Alternate B+SMD-Fuse mit tatsächlichen I²t-/Ausschaltvermögen-/Kaltstarttests parallel prüfen.
4. **Kein Fahrzeugtest ohne geeigneten strombegrenzten Erstaufbau und Automotive-/Fault-Injection-Nachweise**. Fehlermodi: Kurzschluss vor Controller, Kurzschluss nach Controller/vor Buck, 5V-Short, Zwischenlast ~1A bei 36V, HV-FET D-S-Short, 200V OV, Rückspeisung USB, ACC-Abfall.

**Status:** Vorläufige Architektur-/Preis-/FMEA-Beurteilung, kein ERC/DRC und kein Labor-/ISO-Test; alle Preise vor Einkauf neu prüfen.
