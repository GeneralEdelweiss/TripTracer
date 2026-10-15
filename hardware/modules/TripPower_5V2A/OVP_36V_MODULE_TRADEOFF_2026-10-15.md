# TripPower – 36-V-Automotive-Powermodul durch niedrigere OVP? (2026-10-15)

**Entscheidung: Nur Widerstand R309 (aktuell 25,5 kΩ) zu ändern ist mechanisch einfach, schafft aber KEINE robust qualifizierbare Schnittstelle für TPSM33620S5QRDNRQ1 mit VIN max 36 V bei unverändertem 9–30 V-Dauerbetriebsziel.** REV5-LMR38020-Q1 und OV R309 bleiben im aktiven KiCad-Schaltplan UNVERÄNDERT. Ein späterer Modultausch ist nur mit separater OVP-/Wiederanlauf-/Transiente-Qualifikation zulässig. Das spart eine neue Schleife mit einem unsicheren Grenzwert.

## Herstellerquellen
- [LM74930-Q1 Datenblatt SNOSDF6, Tabelle 6.5/6.6, Seite 7–8](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): OV steigend min/typ/max **0,585/0,600/0,630 V**, OV fallend **0,533/0,550/0,573 V**, OV-Eingangsstrom max **200 nA**; HGATE-OV-Abschaltentprellzeit bis **7 µs** (anschließend echte Gate-/Leitungsdynamik beachten). TI verweist explizit auf Spannungsteilerfehler durch den Eingangsleckstrom.
- [TPSM33620-Q1 Automotive 5 V/2 A](https://www.ti.com/product/TPSM33620-Q1): empfohlen VIN maximal **36 V**, Absolutmaximum VIN **40 V**, Paket enthält Induktivität und Boot-C, nur vier externe Passivbauteile im empfohlenen 5V-Fixed-Circuit. TI warnt vor Eingangsschwingungen jenseits 40 V; 40 V ist **kein** erlaubter Arbeitswert.

## Berechnung für aktuelles TripPower-OVP-Netzwerk

**OV-Top:** R307 + R308 = 750 kΩ + 750 kΩ = 1500 kΩ, je 1 %. **OV-Bottom:** R309 aktuell 25,5 kΩ, 1 %; alternative R309-Werte nur als Simulation.

- V_UP_nom = 0,600 × (1 + 1.500 MΩ / R309).
- V_DOWN_nom = 0,550 × (1 + 1.500 MΩ / R309).
- Konservatives *statisches* Modell mit unabhängigem 1%-Widerstandsfehler und ±0,20µA Leckwirkungsrichtung:
  - V_UP_min = 0,585 × (1 + 1,485 MΩ / (R309×1,01)) − 0,20µA×1,485 MΩ;
  - V_UP_max = 0,630 × (1 + 1,515 MΩ / (R309×0,99)) + 0,20µA×1,515 MΩ;
  - V_DOWN_min = 0,533 × (1 + 1,485 MΩ / (R309×1,01)) − 0,20µA×1,485 MΩ;
  - V_DOWN_max = 0,573 × (1 + 1,515 MΩ / (R309×0,99)) + 0,20µA×1,515 MΩ.
- +/- Richtung des pin-bias ist ein absichtlich breites **Modellszenario**; real TI tabelliert 50–200nA und exakter Stromfluss/Temperaturbedingungen müssen berücksichtigt werden. Diese Tabelle ist kein gemessenes Abschalt-Fenster.

| R309 | OV rising typ V | Rising konservativ min…max V | OV falling typ V | Falling konservativ min…max V |
|---:|---:|---:|---:|---:|
| 25,5 kΩ IST | 35,89 | 34,02…38,74 | 32,90 | 30,97…35,26 |
| 27,4 kΩ | 33,45 | 31,68…36,12 | 30,66 | 28,84…32,88 |
| 28,0 kΩ | 32,74 | 31,01…35,36 | 30,01 | 28,22…32,19 |
| **28,7 kΩ** | **31,96** | **30,26…34,53** | **29,29** | **27,54…31,43** |
| 29,4 kΩ | 31,21 | 29,54…33,73 | 28,61 | 26,89…30,70 |

**Drei unvereinbare Anforderungen mit reinem R309-Tausch:**
1. Dauerbetrieb VIN_FUSED bis **30 V** nach Hersteller-/Widerstandstoleranzen und mit sinnvoller Ripple-Marge, d.h. OV rising MIN wesentlich über 30 V.
2. Nach Überspannungsereignis **bei 30 V automatisch wieder einschalten**, d.h. OV falling MIN über 30 V.
3. Im gesamten OVP-Grenzfall **VIN des 36V-Buckmoduls dauerhaft <36 V** plus zusätzliche Dynamikreserve, d.h. OV rising MAX deutlich unter 36 V, idealisiert z.B. ≤34 V.

Bei 28,7 kΩ erfüllt die rein statische Schwelle Rising min>30 / Rising max<36, aber **Falling typ=29,29V** ist unter dem zulässigen 30V-Arbeitspunkt; Wiedereinschalten bei 30V nach OVP ist nicht garantiert. Für Falling min>30 benötigt man R309 ungefähr ≤26,3kΩ; dann liegt OV rising MAX bei ca 37,6V und verletzt die 36V-Betriebsgrenze. Selbst ohne Dynamik ist daher **kein robuster Bereich** durch bloßes Erhöhen von R309 erreichbar.

**Dynamik offen:** OV-HGATE-deglitch maximal 7µs unter TI-Testbedingungen und realer MOSFET-Gateentladung, Leitung/Kabelinduktivität, Filterkondensatoren und Q301 SOA während 202V/350ms. Selbst ein niedrigerer statischer Schaltpunkt begrenzt weder die Spitze am TPSM-Buck auf 36V noch die 40V-absolute-Grenze; OV-Corner bei VIN-Rampen/Leitungsinduktivität muss am tatsächlichen VIN-Pad mit geeigneter Messung erfasst und über alle Temperaturen validiert werden. Ein 36V-Modul zusätzlich direkt per 36V-TVS zu schützen ist wegen 30V Normalbetrieb/Clamping-Toleranz kein triviales Bauteiltauschproblem.

## Konsequenz / nächste Entwicklung

- **Kurzfristig empfohlen:** Bestehenden **LMR38020SQDDARQ1 (4,2–80V, 2A, AEC-Q100)** beibehalten. Das spart 7 Platzierungen zwar nicht, vermeidet aber eine sehr enge und dynamisch unbelegte Spannungsschutzschnittstelle vor der ersten Bestellung.
- **Wenn Bauteilzahl absolute Priorität hat:** Für 9–30V+202V zuerst ein **AEC-qualifiziertes 60V/65V/80V-2A-Powermodul mit integrierter Drossel, realem Preis/Lagerbestand** finden; aktuell evaluiertes TI TPSM65620SVCGR = 65V aber Catalog/nicht AEC/kein DE-Lager. Nur dann komplette Buck-Seite gegen Herstellerreferenz tauschen und neuen Footprint/DRC prüfen.
- **Nur nach bewusster Zieländerung** (z.B. VIN 9–28V statt 9–30V, nur wenn Nutzer explizit zustimmt) macht 28,7kΩ mit genügend zusätzlichem Ringing-Proof eventuell Sinn; **keine heimliche Einschränkung des 30V-Vertrags**.
- **REV5 TPS38 und AUTO/RUN** weiter unabhängig anhand KiCad ERC/Netlist, Beschaffbarkeit, Stückzahl und VIN0-RUN-Rückspeisung prüfen. Die OVP-Abschaltschwelle nicht gleichzeitig verändern, damit Fehlerursachen trennbar bleiben.

**Freigabestatus:** BROKEN-OUT PROPOSAL ONLY, keine KiCad-Änderung, keine OVP-/36V-Powermodul-Sicherheitsfreigabe.
