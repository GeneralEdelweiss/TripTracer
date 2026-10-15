# TripPower Weg C — C2-HV-Architekturentscheid und Nachweise (15.10.2026)

**Status/Entscheid: C2-HV NO-GO als vollstaendige, fehlersichere Spannungsversorgung.** 80V-LM70840-Q1 bleibt als guter, bereits lieferbarer 5V/2A-Buck-Kandidat interessant, aber die Kombination **AP74502HQ + 2x 300V-NMOS + TPS26631 + LM70840-Q1** ist derzeit weder ein sicherer 200V/350ms-Aufbau noch nachweislich einfacher/billiger als eine passende COTS-Alternative. **Keine C2-KiCad-Fertigungsschaltung/PCB-Freigabe begonnen**: sicherheitsrelevanter Einzelkurzschluss umgeht das nur aus zwei FET bestehende Schutzpaar physikalisch. C1-Schaltplan und A/B werden nicht veraendert. Dieser Befund verlangt eine andere Frontend-Loesung bzw. einen nachgewiesenen sicheren Fehlerenergiepfad, *nicht* blind weitere diskrete Schutzschaltungen.

## Hersteller-Datenblattbasis

- Diodes AP74502Q/HQ [DS47093 Rev.2-2, 2025], 200V-Demo **S.15**, Gate-Timing S.5: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf
- TI TPS2663 [SLVSE94G], 4.5..60V recommended, abs VIN **67V**, integrierter 31mohm eFuse: https://www.ti.com/lit/ds/symlink/tps2663.pdf
- TI LM70840-Q1 [SNVSBX7A], 4.5..80V recommended, VIN **87.5V abs**, 4A/5V-Fixoption, externe Induktivitaet **UND Mess-Shunt**, Referenz S.31 ist **LM70880-Q1 fuer 5V/8A**, NICHT 4A: https://www.ti.com/lit/gpn/LM70840-Q1
- Vishay SQM35N30-97_GE3, 300V FET, VGS10V RDSmax97mohm@25C / 214mohm@125C / 285mohm@175C: https://www.vishay.com/docs/66742/sqm35n30-97.pdf
- ADI MAX16126 200V-Kfz-Referenz: https://www.analog.com/en/resources/technical-articles/loaddump-protection-for-24v-automotive-applications.html (externer Versuch bis **202V/400ms**, nicht TripPower-Nachweis von **200V/350ms**)
- ADI LTC4366: https://www.analog.com/en/products/ltc4366.html (controller bis >500V, externer FET, 200V Fehlerschutz nicht automatisch)
- F_MAIN DC-Grenzen: https://www.littelfuse.com/products/fuses/automotive-passenger-car/blade-fuses/atof.aspx (typ. 32V DC, keine 200V-Trennzusage).

## 1. Normaler 200V/350ms-Puls und dynamische Eingangsmaxima

AP74502HQ-OvLO mit Rtop=1M, Rbot=35k (beide ±1%) und IOV bis 110nA, konservativ beide Stromrichtungen (Grenzmodell, keine Korrelation):

\`Vtrip = VOV * (Rtop+Rbot)/Rbot + IOV*Rtop\`.

- VOV rise **max=1.333V**, fall **min=1.063V**. Worst rising cutoff **40.299V** bei 1% R und 110nA, worst falling **30.724V**. So ist Wiederanlauf bei 30V nach rein statischer Threshold-Rechnung moeglich (rising/falling keine Toleranzkorrelation; beim Einbruch weitere Reset-Gates noetig).
- Beim theoretischen zeitlinearen 30->200V-Flankenanstieg in **10us** betraegt dV/dt=17V/us. Falls das externe FET-Paar optimistisch noch 1us nach Erreichen des OVLO-Pins voll leitend ist, liegt die Eingangsspannung **57.30V** am nachfolgenden eFuse-Pin, **nur 2.70V unter 60V**. Bei **2us** waeren es **74.30V > TPS26631 67V absolute max**, bei **3us ~91.30V > LM70840 87.5V absolute max**.
- Die Diodes **max 1us** gilt nur mit **4.7nF** Test-Gatekapazitaet unter spezifizierten Bedingungen. Die beiden realen Vishay-FETs benoetigen bis zu **2x130nC Gate-Ladung** (Testbedingungen beachten). **Keine** garantierte 1us-Zusage am voll montierten Zweifach-MOSFET mit Miller-Effekt, Hoechsttemperatur, Kabelinduktivitaet und Schaltknoten-Ringing. 10us ist ein *illustrativer schneller Transientenrand*, nicht als massgebliche ISO16750-2-Lastabwurfanstiegszeit behauptet. ISO7637-2 getrennt pruefen. Der eFuse-Schutz darf hier nicht als schneller selbststaendiger 200V-Stopper interpretiert werden.
- Die externe F_MAIN kann Strompfade im Fehlerfall begrenzen, **aber** nur mit DC-Abschaltvermoegen, I²t-Kennlinie und nachgewiesener Stromkoordination bei **200V**. Ein normaler 32V-KFZ-Flachsicherungshalter darf nicht als 200V-Aus-Trenner gelten; bei Strom unter Nennstrom loest eine Schmelzsicherung nicht zuverlaessig aus.
- Fehlerfreie AP-Schaltung selbst braucht 200V-rated Eingangskondensator, R1+R2 pulsleistungsgeprueft, Zener geklemmt und Eigen-SOA; Herstellerseite15 zeigt 220uF nach dem FET und 100nF vor dem FET; C2-HV Frontend in der Studie enthaelt diese Funktionen bislang nicht als fertig festgelegte MPN.

**Ergebnis**: Normaler 200V-Abschaltbetrieb plausibel fuer bestimmte ausreichend langsame Flanken, aber **nicht** qualifiziert gegen definierte 200V/350ms-Wellenformen und die schnelleren Transienten samt Nachschwingen; 60V eFuse bleibt der schwache Punkt.

## 2. Physikalische Einzelbauteilfehler: harte NO-GO-Pruefung

| Einzelfehler | Leitender Pfad / Spannung | Folge und Bewertung |
|---|---|---|
| Eingangs-Q1 Drain–Source **Kurzschluss** | VIN=200V -> Q1 kurz -> gemeinsame Sources -> **Q2 Bodydiode** -> HV_PROTECTED -> TPS26631-IN | Etwa 200V minus Vf am 67V-absolute-max-eFuse; bei offenem/nicht ausloesendem eFuse kann LM70840 (87.5V abs) ebenfalls geschaedigt werden. **Nicht durch OVLO oder Gate LOW vermeidbar.** |
| Ausgangs-Q2 Drain–Source kurz | Q1-Bodydiode bei MOSFETs common-source ist in anderer Richtung orientiert; **nicht als symmetrischer 200V-Durchgang anzunehmen** | Reverse/ring currents, Q1-SOA und nachgeschaltete C-Abschaltung noch testen; Ausgangsauftrennung/Verpolschutz anders betroffen. |
| VIN-Zener **offen** | 200V-Impuls ueber R1+R2 -> AP VIN Kondensator; Potential steigt gegen 200V | AP VIN 80V abs kann verletzt werden, der Controller wird unzuverlaessig/defekt; unkontrollierte Gate-Stellung und Energie im FET moeglich. |
| VIN-Zener **kurz** | 200V direkt ueber insgesamt 10.2kOhm nach Masse | 3.922W Puls, **1.373J in 350ms** insgesamt, bei gleichen 5.1k je **0.686J**; resistiver Bauteilbrand unterhalb F_MAIN-Ausloesestrom moeglich. |
| MOSFET-Switching-Loss/SOA / Schutzzener soft short | Trotz 300V VDS koennen FET, R oder TVS thermisch versagen | Pulsenergie/HotSOA 350ms ist **nicht** 300V-Nennwert. |

Nominaler 60V-*idealer* AP VIN-Zener, 10.2k, Rechteck 200V/350ms: I=13.725mA, PR=1.922W, ER=0.673J total, PZ=0.824W, EZ=0.288J. Echte SMCJ56A-Sperrspannung/Clamp/Leckströme, 125C und Einzelbauteilimpulsrating NICHT dadurch bewiesen.

Ein anderer Denkansatz, naemlich ein starker Eingangs-TVS allein: Fuer eine **reine hypothetische rechteckige** 200V-Quelle, 60V Clamp und 1Ohm Quellwiderstand waeren (200−60)/1=140A, 8.4kW und **2.94kJ/350ms** abzufuehren. Bei 8Ohm 17.5A/1.05kW/**367.5J**. Ein echter exponentieller Load Dump hat eine andere Energie; gerade deshalb ist Vpeak allein kein ausreichender Nachweis. TVS > MOV, fuses etc. nur nach spezifiziertem Pulseenergie-/Endurance-Diagramm.

## 3. 9V-Start und +125C-Dauerlast (mit Pfad-Spannungsabfall)

Ziel 5Vx2A=10W **plus 1A RAW gleichzeitig**. Beispielhafte **η=90%** des LM70840 bei 9V nach HV-MOSFETs; kein Hersteller-guaranteed Wirkungsgrad, da Frequenz, L, PCB und 125C noch nicht gemessen.

- Bei Q1,Q2 je **0.214Ω** @ Tj125C, TPS26631 **0.053Ω** RON max und 9V Eingang wird der Gesamtstrom selbstkonsistent durch \`I=1A + 10W / [0.9*(9V−I*(2*0.214+0.053)Ω)]\` berechnet:
  - I=**2.418A**, hinter Schutz noch **7.837V**; zwei FETs **2.502W** gesamt bzw **1.251W/FET**, eFuse **0.310W**, gesamt **2.812W** reine Eingangspfad-Waerme. Resistiv-halbgegleitete Verluste steigen bei steigender Junction-Temperatur weiter.
  - Diese Vishay-RDSmax gelten bei VGS=10V; 9V-Bordnetz plus Charge-Pump-Dynamik koennen andere Betriebszustaende erfordern. +125C thermische Maximalgrenze 175C, nicht mit nomineller 300V-VDS vergleichen. Ohne Kupfer-/Gehäuse-/Gate-Messung kein garantierter thermischer Nachweis. Unterhalb 9V darf Reset erfolgen.
- LM70840: thermische Eckrechnung bei T_A=125C, Pout10W und η90%: Verlust 1.111W (Waermeverteilung zwischen IC/Induktivitaet wird fuer diese konservative Budgetrechnung als IC-Aufwaermung angesetzt). \`T_J=125+θJA*1.111\`: mit TI EVM-θ=18.6K/W **145.67C**, mit JEDEC θ=33.5K/W **162.22C**; nur EVM-aehnliche Waermeabfuhr ist bei optimistischem Wirkungsgrad unter TJmax150C. Bei η85%, θ18.6K/W waere **157.82C**. Erforderlich η>=**88.15%** fuer EVM-artige 18.6K/W bzw >=**93.06%** fuer 33.5K/W, bei +125C, ohne Sicherheitsabstand. Die 4A-Nennangabe ist keine 125C-/2A-Freigabe.
- **9V-Start:** AP VIN min4V und LM70840 min4.5V: bei stationaerem 7.8V Buck-In prinzipiell technisch moeglich. Inrush, strombegrenzte eFuse mit 2x/3x Puls, 220uF COUT, tolerierte EN-Pegel/ACC-Brownout und UVLO-Schwellen koennen Start trotzdem verhindern; der Nachweis ist offen.
- **Ruhestrom <100uA:** 1M+35k OVLO-Teiler bei 30V zieht schon **29.0uA**. AP Disabled typ0.9/max1.5uA, LED/MUX/ACC-Teiler/GPIO/USB plus eFuse und Widerstandsnetzwerk duerfen restliche max ~69.5uA ueber -40..125C nicht uebersteigen; System-Messung fehlt.

## 4. Realer Bestueckungsumfang, Referenz und Kosten

Der unveraenderte C1 hat **28 tatsaechliche Schaltplanreferenzen** einschliesslich C10/C11; davon gehoeren nominal **acht** zum alten TPSM33620-Buck-Teilblock (U3 und 7 Kondensatoren, im tatsaechlichen Netzauszug verifizieren), bleiben also **20** bestehende Frontend-/eFuse-/Steuer-/Steckerpositionen.

TI LM708x0-Q1 **Figur 8-8, Seite 31 ist ausdruecklich LM70880-Q1 fuer 8A, nicht LM70840-Q1 fuer 4A.** Enthaltene demonstrative Positionen wurden in \`C2_LM70840_REFERENCE_PARTS_SCOPE.csv\` transparent gezaehlt: **25 Bauteilpositionen** inkl Regler, 4 CIN, CINHF, 2 REN, CVCC, CBOOT, RBOOT, Spule, Shunt, 4 COUT, 2 RFB, 3 Kompensationsbauteile, CVDDA, CONFIG R, RT R. Der **4A/2A-Entwurf kann diese Positionen reduzieren** (5V intern fest, interne Kompensation, kleinere COUT), aber erst nach korrekter Hersteller-Dimensionierung. Bei ungekuerztem Beispiel waere die denkbare Kombination **20+25=45 Referenzen**, mit fehlendem 200V-Eingangs-C und erforderlichem Bulk mindestens **47**, plus ACC/RUN/USB-Fehlerabsicherung und etwaige Schutzpfade. **47 ist keine KiCad-gezaehlte Fertigplatine und kein definitives Minimum**; die einzige wirklich vorhandene C-KiCad-BOM ist C1/28.

Aktuelle belegbare europaeische Brutto-/Nettofrage: Die folgenden Web-Angebote sind **je Einheit EUR ohne MwSt.**, ohne Versand/PCB/Gehäuse/Stencil/externen F_MAIN; MPN und Warenkorb vor Kauf nochmals pruefen. Quelle:
- AP74502HQTA8-7 (x1), Mouser EU (https://eu.mouser.com/en/ProductDetail/Diodes-Incorporated/AP74502HQTA8-7): **0.636/0.450/0.352** EUR fuer 1/10/100.
- SQM35N30-97_GE3 (x2), DigiKey DE (https://www.digikey.de/en/products/detail/vishay-siliconix/SQM35N30-97-GE3/7566806): **4.480/2.963/2.1059** EUR je MOSFET.
- TPS26631PWPR (x1), Mouser DE (https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS26631PWPR): **3.890/2.960/2.460** EUR; Momentaufnahme 57 St. Lager, daher *100 nicht sofort komplett verfuegbar*.
- LM70840QRRXRQ1 (x1), Mouser EU (https://eu.mouser.com/ProductDetail/Texas-Instruments/LM70840QRRXRQ1): **6.300/4.860/4.110** EUR; groesserer Lagerbestand.
- Wuerth 744393445033 (x1), DigiKey DE (https://www.digikey.de/de/products/detail/w%C3%BCrth-elektronik/744393445033/26976004): **1.770/1.430/1.0872** EUR 3.3uH AEC-Q200, Isat12.5A, 13.9A Irated, 15.4mohm DCR, -40..125C.
- TDK CGA6P1X7S1A476M250AC (x4), DigiKey DE (https://www.digikey.de/en/products/detail/tdk-corporation/CGA6P1X7S1A476M250AC/10413496): **2.400/1.645/1.254** EUR pro 47uF 10V automotive MLCC. **Nur TI-8A-Beispiel**, 2A vielleicht erheblich weniger Teile/Kosten.
- TI-TPSM33620S5QRDNRQ1 (x1) nur historische C1-Vergleichsbasis: **1.990/1.960/1.860** EUR.

| Teilkosten-Untergrenze pro theoretischer C2-Versorgung | 1 St. EUR netto | 10 St. | 100 St. |
|---|---:|---:|---:|
| AP74502HQ + 2x 300V FET + TPS26631 + LM70840 (**5 Positionen**) | **19.786** | **14.196** | **11.134** |
| Zuzueglich **1x L + 4x COUT** aus 8A-Referenz (**weitere 5 Positionen**) | **31.156** | **22.206** | **17.237** |
| **Fehlende Teile** | 20 bestehende Frontend/Interface-Pos. plus 15/25 sonstige TI-Referenzteile, externe F_MAIN und Schutz | gleich | gleich |

**Untergrenze ist kein vollstaendiger Einkaufspreis und keine fertige BOM.** Die C2-Referenz-Dokumentation hat 25 Positionen, ihre Einzel-MPNs und echten Preise sind nur fuer U, L und 4 COUT verfuegbar. Anlagenteile fuer 200V/350ms und -40..125C sind **nicht finalisiert**. Bei 100 Stueck ist eFuse aktuell nicht voll lagernd. Die Bestaetigung aktueller Preise ist nur ein Stand vom 15.10.2026, keine Liefergarantie.

### Vergleich C1 36V und C2 80V

- C1 Silizium-5-Positionen **15.476 / 11.296 / 8.884** EUR netto fuer 1/10/100; C2 **19.786 / 14.196 / 11.134** EUR. C2-80V kostet **4.310/2.900/2.250 EUR mehr** bereits fuer die IC/2FET; Induktivitaet/Filter/Shunt kommen dazu. C1 bleibt 36V NO-GO und ist nicht die zu bauende billigere Alternative.
- **C2 wiederholt den NO-GO durch Q1-D/S-Kurz genauso wie C1.** Der hoehere 80V-Buck schafft den Fehler nicht aus der Welt und macht U2/eFuse nicht spannungsfester.
- Ein separater downstream-1A-RAW-current switch koennte RAW intern wirklich auf 1A beschraenken, waere aber ein weiterer COTS-IC+Passiva; gegen den 200V-Bypass bietet das keine gesicherte Abschaltung.

## 5. Marktalternativen (gezielter COTS-Pruefpfad)

| Fertigkonzept | Nutzen | Aktuelle Sperre |
|---|---|---|
| **ADI MAX16126-Herstellerreferenz fuer 24V-Load Dump** | Externer qualifizierter, dokumentierter Aufbau mit geschalteter OV, TVS-Schirm und Labordaten bis **202V/400ms**, 1..8Ohm Ri; Quelle ADI-Herstellerartikel | Der Referenztest ist **nicht** unsere 200V/350ms-Wellenform; externe MOSFET-Short-Fehler, PWM-/Thermik und F_MAIN-I²t muessen separat analysiert werden; nicht als sofort gleichwertiger Ersatz anbieten |
| **ADI LTC4366-2** | Controller fuer >500V-Surge, SOA-/Timer-/Auto-Retry-Optionen; kann HV-Klemmung statt sofortigem Shutdown pruefen | Teuer, externer Leistungstransistor, fuer +125C/2.4A-/200V/350ms und Einzel-FET-Short kein Selbstnachweis; Resistor-MOSFET-Verluste gross |
| **Qualifizierte 200V-Pulsabsorption plus F_MAIN und 80V-Buck** | Wenig aktive Bauteile; bewusster akzeptierter Bauteilausfall moeglich | 350ms/200V/Quelle bis 1Ohm kann kJ-Bereich bedeuten. Ohne passende 200V-DC-Ausloesung, sichere Energie- und Temperaturbegrenzung KEIN integrierter TVS-Ersatz.
| **Fertige vollständige Automotive-5V-/2A-Frontends** | Idealerweise OVP, current limit, thermalschutz, 200V prufbar in einem Baustein/Modul | Zum Recherchezeitpunkt noch kein gesichert >200V/350ms fehlersicheres, guenstiges Modul mit +125C und 1A RAW nachgewiesen |

**Naechster konkreter Schritt:** Nicht C2 routen. Einen 200V/350ms-geeigneten **fertigen Hochvolt-Eingangsschutz mit dokumentiertem Einzelkurzschluss-/Fehlerenergiepfad** oder ein Hersteller-Eingangskonzept mit auf Stromkreis/F_MAIN abgestimmter klaren Fail-Safe pruefen. Nur wenn dieser Pfad mit wenigen qualifizierbaren Teilen erreichbar ist, den LM70840-Q1 mit TI 4A-Schaltung nach 5V2A dimensionieren und in ein neues, eigenstaendiges KiCad10-C2-Projekt ueberfuehren, native ERC/Netlist/PCB-DRC+Hardware-Gates. **Anforderungen unveraendert, nur Architektur-NO-GO.**

## Ehrlicher Teststand

- Ausfuehrbare quantitative Regression: \`python3 -m unittest -v c2_hv_gate_checks\` und \`python3 c2_hv_gate_checks.py\`. Zeitbereich idealisierter Worst-Slew und Sicherheitsgrenzen ist statisch, keine Spice-/physische Simulation mit echtem Datenblatt-/Layoutmodell.
- **Native KiCad10 ERC/Netlist fuer C2 nicht moeglich, da bewusst kein als sicher plausibler C2-Schaltplan erstellt wurde**. Keine DRC-Behauptung; keine Hardware-/200V/350ms-/ISO-/125C-Freigabe. Die Tests koennen ueber eine eigene Weg-C-GitHub-Action wiederholt werden, sagen aber nichts ueber Boardfreigabe.
