# TripTracer V1 – MegaSquirt-Stromversorgung als 80/20-Vorbild

**Jüngste bindende Nutzerentscheidung (13.10.2026):** Die Projektversorgung wird als **Variante C mit LM74930-Q1 + LMR36520 und relaisloser ACC-/MCU-HOLD-Selbsthaltung** umgesetzt; die in dieser früheren Studie diskutierten **LM74800-/LTC4380-/MegaSquirt-Mindestvarianten sind nur Vergleiche**, keine aktuelle Teileauswahl. **Keine zusätzliche TPS26631 und keine auf der Platine verlöteten Schmelzsicherungen, deren Tausch Auslöten erfordert.** Die Fahrzeugzuleitungen ACC und BAT+ bleiben separat quellseitig abgesichert; gegebenenfalls mit **ohne Löten tauschbaren** Sicherungen. Bei der Beschaffung **Reichelt und andere deutsche Lieferanten bei wirtschaftlichem Gesamtpreis bevorzugen**; Mouser/DigiKey/LCSC weiterhin nach Preis/Verfügbarkeit möglich. **Keine Fertigungs-/ISO-/ERC-/DRC-Freigabe**. Verbindliche Details in [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md).


**Stand 13.10.2026 · Untersuchung anhand Originalschaltplan MegaSquirt V3.57 (2007), Seite 6/8. Kein fertiger TripTracer-Schaltplan, kein ERC/DRC, keine Automotive-/ISO-Freigabe.**

**Verbindliche Priorität:** ZUERST eine **preiswerte, thermisch/elektrisch sichere und funktionierende** Fahrzeugversorgung mit einfacher ACC-Selbsthaltung entwerfen und nachweisen. **Keine Nice-to-haves, keine künstliche Redundanz.** Bauteilauswahl vorrangig **elektrische Eignung → tatsächlich lieferbare MPNs (DigiKey/Mouser/Reichelt/LCSC/andere verlässliche Händler) → ganze Schaltungskosten → Handlötbarkeit → optionale JLC-PCBA**. **JLCPCB Basic/Extended ist keine Beschaffungsvoraussetzung**. Manuell bestückte Prototypen können bei zahlreichen Extended-Teilen erheblich günstiger sein. Ursprüngliche 5-Roh-PCB/2-PCBA-Planung als *Option*, keine automatische Bestellung oder Verpflichtung zur PCBA. Spätere Serienbestückung erst anhand eines realen Komplettangebots abwägen.

## 1. Tatsächlich untersuchter Originalschaltplan

[Original MegaSquirt V3.57 PDF](https://www.megamanual.com/357/MS357.pdf), **Seite 6 von 8 – „Megasquirt – Power“**, Schaltplan-Original vom 19.02.2007; [Montageanleitung V3.0](https://www.megamanual.com/ms2/V3assemble.htm).

| Originalteil | Tatsächliche Schaltfunktion | Übertragung auf TripTracer |
|---|---|---|
| MOV1 **Panasonic ERZ-V20D220** | Überspannungspulse am 12V_RAW-Eingang gegen Masse ableiten | **NICHT kopieren**: nur **18 V DC Dauerbetrieb**, bei 36 V ungeeignet; Panasonic **NRFND/Last Time Buy**, [Hersteller](https://industrial.panasonic.com/ww/products/pt/surge-components/models/ERZV20D220) |
| D11 1N4001 + D13 12V/1W-Zener | weitere Eingangstransientenbegrenzung | Prinzip übernehmen; Ströme/Polarität und Zener-Pulsenergie für 12/24 V und jeweilige ISO-Prüfprofile neu dimensionieren |
| D10 1N4001 | Serien-Entkopplung/Verpolschutz vor Spannungsregler | Prinzip übernehmen; **1N4001 mit 1A nicht blind** auf unseren Fahrzeug-Eingang übertragen (Buck-Eingangspeak bei 6 V prüfen), Vorwärtsspannungsverlust bei Kaltstart beachten |
| D12 22V/1W Zener | lokaler Schutz des Reglereingangs | **Nicht** als 24-V-Eingangsklemme übernehmen; unter Normalspannungen >22V thermisch problematisch |
| U5 **LM2937ET-5.0** | 5V/0,5A Automotive-LDO inkl. Verpol-, 60-V-/100-ms-Transient-, Überstrom- und Thermal-Schutz | **NICHT kopieren**: **26 V maximal kontinuierlich**, Leistung und Verlustwärme unpassend, [TI-Datenblatt](https://www.ti.com/lit/ds/symlink/lm2937.pdf) |
| F1 RXE050 | ca. 0,5A PTC im 5V-Ausgang | **schützt nicht das Eingangskabel**. Die Fahrzeug-M8-ACC/BAT+-Zuleitungen brauchen weiterhin geeigneten quellseitigen DC-Leitungsschutz |
| C16/C17/C18, D9 | lokale Reglerpuffer und Ausgang-zu-Eingang-Rückstromschutz | Lokale Entkopplung/Power-Sequencing mit dem neuen Schaltregler-Datenblatt auslegen |

**Schlussfolgerung:** MegaSquirt ist ein hervorragender Beleg für **sparsame Schutz-/Versorgungstopologie**, aber **kein 36-V-Dauerbetriebs- oder 200-V-Test-A-Nachweis**. Brand- und Kabelschutz sind wichtiger als ein garantiert unterbrechungsfreier Track. Seltener Reset/aktuell beschädigter Datensatz akzeptiert, 6-V-Motorstart ohne Reset als aktuelles Ziel.

### Warum wir einen Schaltregler statt LDO benötigen

Im bisherigen TripTracer-Leistungs**szenario**, **nicht gemessene Dauerlast**, liegen wir bei ca. **5,24 W**. Bei 5 V wären das etwa 1,05 A auf der 5V-Schiene. Ein linearer 5V-LDO würde bei **0,5 A** und **24 V** schon **9,5 W** verheizen; bei 36 V **15,5 W** – und wäre mit 0,5A bereits zu klein. Bei **1 A** und 36 V wären es **31 W**. Ein effizienter 5V-Buck ist daher kein Luxus, sondern Grundlage einer sicheren Lösung.

## 2. Favorisierte preisgünstige Grundversorgung für einen LABOR-Prototypen

```text
 Fahrzeug +BAT+ M8 Pin4 (extern passend DC-abgesichert)
       |
  [Eingangs-Surge/Verpol-Front-End nach V3.57-Prinzip:
   KEINE unbemessene 12V-Zener-/18V-MOV-Kopie;
   24V-ISO-Lastdump-Abschaltung vor Ort noch nachzuweisen]
       |
  VIN_PROTECTED  (zuerst 9–36V, bei Cranking ab 6V)
       |
   TI LMR36520ADDAR
   4,2–65V Buck, 5V/2A, hiccup Kurzschluss und Thermal Shutdown
       |
       +---- 5V_MAIN -> 3V3 für ESP32-S3/GNSS/FRAM/SD
       +---- 5V_RADSENSOR über eigene geeignete Begrenzung
       +---- Backlight Boost mit eigener Stromregelung
       
 ACC M8 Pin1 (separat extern abgesichert) --> transientenfeste
   hochohmige Pegelanpassung --> D_START --+
                                             +--> BUCK_EN (defined default LOW)
   ESP32 MCU_HOLD (3V3) ------------> D_HOLD --+
                      (GPIO nur während Fahrzeugmodus)
 
 USB-C VBUS --> separate rückspeisegesperrte USB-SERVICE-Versorgung
   (keine Einspeisung in BAT+ und keine ungewollte HOLD-Aktivierung)
```

**Selbsthaltung – einfaches Funktionsprinzip, noch keine freigegebene Bauteilliste:** Geprüftes ACC-Signal hebt `BUCK_EN` an und startet die Hauptversorgung ohne schon laufenden MCU; die MCU setzt **früh** `MCU_HOLD` HIGH. Bei ACC LOW sichert sie nur noch wichtige Daten und setzt `MCU_HOLD` LOW, wodurch der Buck ohne bistabiles Relais/immeraktiven 5V-AUX und ohne zusätzliche Serien-Leistungs-MOSFETs abschaltet. Die Diode-OR-Logik vermeidet MCU-Rückspeisung durch ACC. `EN` hat beim LMR36520 eine präzise Einschaltgrenze von **max. ~1,3 V**, `I_SD ≈ 5,3 µA typ. bei VIN=24 V`; ein geeigneter **Hardware-Pulldown** gewährleistet AUS ohne ACC/HOLD. Werte/Pegel **sind nicht final**: ACC bis 36 V und positive/negative Pulsbedingungen, Widerstands-Spannungsfestigkeit, Zener-Spitzenstrom, Timing bei raschem ACC-Wegfall, 3.3V-GPIO-Bootstrap und VIN/EN-Absolute-Max müssen geprüft werden. Kein direkter Anschluss von ACC an MCU.

**Im Fehlerfall:** Buck-Hiccup schützt den 5V-Ausgang gegen Kurzschluss; er **schützt keinen Kurzschluss zwischen M8 und seinem eigenen VIN-Pad, keine externen 5V-Geber vor Stromdefekten und keine TVS im Kurzschluss**. Ein korrekt DC-bemessener externer BAT+- und ACC-Leitungsschutz und der Leiterbahnen-/Stecker-/Kabel-Querschnitt sind erforderlich. Übertemperatur-Auslösung/Schutz-IC ist Notabschaltung und kein Ersatz für kontinuierlich unter Grenzwert betriebene Leiterplatte.

**Kaltstart 6 V:** 5V-Ausgang bei 6V VIN bleibt eine **Regler-Dropout-Aufgabe**, besonders mit Spannungsabfall des Verpolschutzes und 5V-Volllast. Backlight darf ausgeschaltet werden, MCU/GNSS/SD nicht resetten. LMR36520 maximal 98% duty spezifiziert, aber **keine** 6V-/5V-Volllast-Freigabe ohne Test. Bei sporadischem Eingang **unter 6 V** ist ein definierter Reset zulässig.

## 3. Unverzichtbarer Unterschied: 200-V-ungedämpfter 24V-Load-Dump

**Die bestätigte ISO 16750-2:2023-Prüfausrichtung bleibt bestehen**. Laut [TI-Applikationsschrift zu LM74930-Q1](https://www.ti.com/document-viewer/lit/html/snoaaa1) kann 24V-Test A **151–202 V** über **100–350 ms** bei Quellimpedanzen **1–8 Ω** verlangen. Eine gewöhnliche 600W-SMBJ-TVSDiode ist für solche lang andauernde Lastdump-Energie **nicht automatisch geeignet**; ein 18V-Original-MOV erst recht nicht. Bei direkter Ableitung bis unter die 65V-Grenze des Bucks muss die große Quellenergie verbraten werden; ohne Energie-/Temperaturrechnung droht genau die Brandgefahr, die wir vermeiden wollen.

Zwei getrennte **elektrisch ehrliche Optionen**:

| Lösung | Erfüllt 36V Dauer/6V Start? | Test-A 200V | Sicherheit/Kosten |
|---|---|---|---|
| **A – Minimaler funktionierender LABOR-Versorgungsprototyp**: geeignete Sicherung, einfache 24V-taugliche TVS/Verpol-Stufe, LMR36520, Dioden-HOLD | bei Nachweis von Kaltstart/UVLO und Reglerlast wahrscheinlich | **NICHT NACHGEWIESEN**; **kein Fahrzeug-/ISO-Freigabestand** | geringste Zahl an Teilen, gut um Buck/HOLD mit strombegrenztem Labornetzteil zu beweisen; TVS/Fuse-Belastung separat |
| **B – 24V-200V-Test-A-Ziel ohne teure Doppelkette**: TI **LM74800-Q1** mit externen 200/250V- und 60V-FETs in **OV CUT-OFF** oder TI **LM74930-Q1** als Circuit-Breaker-Alternative **vor demselben Buck** | Herstellerbeispiel für 6V Start; finaler 5V-Buck-Dropout noch offen | TI-Referenz für 200V-Test-A vorhanden, **Gesamt-PCB weiterhin ungetestet** | Controller/FETs kosten mehr, sparen potenziell shunt-/thermalbelastete Shunt-Begrenzer; **keinen zweiten unabhängigen Controller automatisch dazubauen** |

**80/20-Vorentscheidung:** Erst **A auf dem Tisch** (mit Schutz-Kleinspannungs-/Stromlimits) funktional bestätigen, danach für **Fahrzeugeinsatz** die **preiswerteste nachweisbare 200V-Surge-Abschaltung aus B** dimensionieren, **ohne** redundante eFuse/extra Watchdog/Tripmaster-nice-to-haves. **Ein A-Prototyp ist nicht automatisch für das Fahrzeug geeignet.** Laufen lassen während Test A ist nicht gefordert; sicheres Abschalten ist zulässiges Entwicklungsziel.

## 4. Verfügbarkeit und Kostensicht – echte Teile statt JLC-Extended-Dogma

| Kandidat | Nachgewiesene Versorgung / Preisstufe | Relevanz |
|---|---|---|
| **TI LMR36520ADDAR**, HSOIC-8 DDA | **Mouser Deutschland 2,80 €/1, 2,11 €/10, lagernd ~14.107** ([Mouser](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LMR36520ADDAR)), **LCSC C2879422 ~1,5894 USD/1 und ~1,3389 USD/10, zuletzt ~316 lagernd** ([LCSC](https://lcsc.com/product-detail/DC-DC-Converters_Texas-Instruments-LMR36520ADDAR_C2879422.html)) | **Preis-/Funktionsfavorit** für 5V/2A; thermischer PowerPad mit Lötpaste/Heißluft/Reflow oder bestückt, nicht als einfaches Lötkolben-IC behandeln |
| **TI LM74800QDRRRQ1**, WSON-12 | Vorheriger Preisstand **~2,58 €/1, ~1,94 €/10**, aktueller Stückpreis vor Bestellung prüfen ([Mouser](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74800QDRRRQ1)) | Variante B: 200V-Test-A-Schutzreferenz mit **zwei** externen FETs; keine eigene Hauptstrombegrenzung |
| **TI LM74930QRGERQ1**, VQFN-24 | **Mouser Deutschland 5,39 €/1, 4,13 €/10**, zuletzt rund 62 lagernd ([Mouser](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74930QRGERQ1)) | Variante B, Circuit Breaker integriert, teurer, manueller Lötaufwand mit QFN höher |
| **TI LM2937ET-5.0**, TO-220 | Reichelt, Mouser, DigiKey beschaffbar, aber max 26V/0,5A ([TI](https://www.ti.com/lit/ds/symlink/lm2937.pdf)) | **kein TripTracer-Kandidat**, nur Original-MegaSquirt-Referenz |
| Externe **BAT+/ACC-DC-Sicherungen** | 58V-taugliche Typen als Kandidaten; Quellenseite, Amperewert, Kurzschluss-Abschaltvermögen, Fassung und Kabelquerschnitte offen | Pflicht gegen Kabel-/PCB-Brand; typischer 32V-Sicherungstyp ist für 36V regulären Betrieb **nicht vorbehaltlos zulässig** |
| TVS/MOV, Verpol-Diode/-FET, Zener, ACC-Kleinsignal-Dioden, passives Buck-Netz | **MPNs und Gesamtpreise offen** | **Nicht** in eine falsche Gesamtpreiszahl hineinschätzen und als fertige BOM ausgeben |

**Reiner Regler-Einkaufsanker:** ~**2,80 €** (Mouser) bzw. ~**1,59 USD** (LCSC) für den Hauptbuck. Das ist **keine** fertige Versorgung: Induktivität, MLCC, ESD/TVS, Sicherung, Verpolschutz, MCU-HOLD und ggf. HV-Controller fehlen. Der frühere 21,92€-Doppelcontroller-Ansatz darf nicht als Mindestkostenwert benutzt werden.

## 4.1 Konkreter Nachbau des schon vorhandenen U101-Buck-Blocks

In der bestehenden KiCad-V1-Hierarchie gibt es **bereits** `hardware/kicad/02_5V_Buck.kicad_sch` mit **U101 LMR36520**. Der bisherige Vorentwurf benutzt **L101 = 15 µH als Symbolwert**, während der Footprint einen **alten Bourns-SRN6045-220M-/22-µH-Typ** benennt. **Keine Freigabe für irgendeines dieser beiden Werte/Footprints.**

Die **aktuelle TI-Datenblatt-Rev.-C-Referenztabelle für 5 V / 2 A / 400 kHz** nennt als bevorzugten Startpunkt:

| Schaltposition | TI-Referenzwert | Umsetzungs-/Kostenpunkt |
|---|---|---|
| U101 | **LMR36520ADDAR**, HSOIC-8 DDA | schon im Projekt; nur exaktes TI-Pad-9-/Footprint-Mapping verifizieren |
| L101 | **10 µH**, ausreichend I_SAT/DCR und Layoutstrom | bisher 15/22µH inkonsistent; **erst neue reale MPN mit echter Lieferbarkeit auswählen** |
| R_FB_TOP | **100 kΩ** | bisher 172kΩ: 5-V-Funktion grundsätzlich möglich, aber TI-Tabelle ist zuverlässigerer Ausgangspunkt |
| R_FB_BOTTOM | **24,9 kΩ** | bisher 43,2kΩ: zu neuem 100k-Referenzteiler paarweise wechseln, nicht nur einen Widerstand |
| C_OUT | **2 × 22 µF nominell**, Spannungs-/DC-Bias-/Thermik-Derating prüfen | kein blindes „22µF nominell = 22µF effektiv“, echte 10V-/25V-MLCC-MPN und Kapazität prüfen |
| C_IN | **2 × 4,7 µF plus 220 nF**, ≥36V Eingangs- und transientenbedingte Kondensator-Ratings wählen | nur **hinter** geprüftem Überspannungs-Front-End sinnvoll; Kapazität/Voltage-Derating/PCB-Loop prüfen |

**Herstellerquelle:** [TI LMR36520 Rev. C Table 8-1 und Section 8.2](https://www.ti.com/lit/ds/symlink/lmr36520.pdf). Das heißt ausdrücklich **NICHT**, dass die vorhandene Topologie mit 100k/24,9k/10µH ohne sorgfältigen Pin-/Layout-/Stabilitätscheck sofort funktionsfähig sei, oder dass sich die 6-V-VIN-Brownout-Regelung aus einer 24-V-Referenztabelle beweisen lässt. Zunächst Datenblatt/Netze/3D/Footprints und alle späteren 5-V-Abzweige prüfen.

### Was NICHT mehr priorisiert wird

- JLCPCB-Basic-Quote und automatisierte Bestückung um jeden Preis.
- Teure redundante eFuse-/Schalter-/Watchdog-Stufen *nur* für seltene Datenverluste.
- 3V-/15ms-Hold-up, 3-s-M8-Kabelabzugspuffer und große Start-Supercaps.
- Ausbau zusätzlicher LED-Effekte, Features, Nice-to-haves vor **funktionierendem und sicher getesteten** VIN→5V→3V3 + ACC-HOLD.

### Unmittelbare nächste Tests / Freigabe-Sperren

1. LMR36520-Schaltregler-BOM aus **TI-Datenblatt-Referenzdesign**, tatsächlicher 5V-Last und vorhandener 15µH-vs-22µH-Footprint-Diskrepanz dimensionieren; keine ungeprüften KiCad-Footprints freigeben.
2. ACC-zu-EN mit **geprüfter** Surge-/Polarity-fester Logik und MCU_HOLD als einzigem Nachlaufpfad zeichnen, dabei BAT+-OFF <100µA **messen**. ESP32 setzt HOLD früh, schließt bei ACC AUS, löst nach Dateischluss; interne Watchdogs/Reset definieren.
3. Kurzschluss-Tests bei 6/12/24/36V mit **strombegrenztem Labornetzteil**, Temperaturen, Buck-Hiccup, 5V/3V3-Schienen, Sensorzweigschutz und USB-only-Rückspeisesperre prüfen.
4. **Vor jedem Fahrzeugeinsatz** 200V-ISO-Test-A-Schutz und Quellen-/Leitungs-Sicherungen inklusive SOA, negative Pulse, Verpolung, Gehäusetemperatur und PCB-Kupfer auslegen und am Prototyp messen. **Keine Schaltung als normkonform bezeichnen, solange nicht geprüft**.
5. Tatsächlich lieferbare MPNs zuerst bei deutschen/EU-Distributoren und LCSC suchen, mindestens eine sinnvolle 2nd-source je Standardteil, **von Hand bestückbare** Teilmenge vor JLC-PCBA-Extended-Quote.
