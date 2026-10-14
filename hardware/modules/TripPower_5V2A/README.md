# TripPower 5V/2A – eigenstaendiges, kopierbares DC/DC-Modul

## Standalone KiCad-10-Projekt – aktiver neuer Arbeitsstand 14.10.2026

**Jetzt vorhanden:** [`TripPower_5V2A.kicad_pro`](TripPower_5V2A.kicad_pro) und [Root-Schaltplan](TripPower_5V2A.kicad_sch) mit zwei echten verknuepften Schaltplanseiten [01: LM74930-Eingangsschutz](01_Protection_LM74930.kicad_sch) und [02: LMR38020 5-V-Buck](02_5V_LMR38020.kicad_sch). Die lokalen `sym-lib-table`, `fp-lib-table`, `TripPower_Sym.kicad_sym`, `TripTracer_V1.kicad_sym`, `Tripmaster_Sym.kicad_sym` und `Tripmaster.pretty/` befinden sich im selben Projektordner. **Einfach den GESAMTEN Ordner kopieren und `TripPower_5V2A.kicad_pro` in KiCad 10 oeffnen.**

**Schaltung real elektrisch verknuepft, nicht nur textuell:** VIN_FUSED → Q301/Q302 Common Source → RSENSE 5mΩ → `VIN_PROTECTED_MAIN` → 5V-Buck und separat F302 → `VIN_PROTECTED`. Die Netze verbinden die beiden Unterseiten in der Root-Hierarchie; es sind echte Bauteilsymbole, Wires und globale Labels. Standalone `RUN_CMD` geht ueber R317 und Sperrdiode D305 zum LM74930 EN, mit R316 Pulldown. 0R-R319 ist die optionale `ALWAYS_ON`-Bestueckung. **RUN_CMD niemals direkt mit 12-/24-V-ACC verbinden**; TripTracer braucht einen separaten, geschuetzten ACC/HOLD-Logikadapter.

**Pruefung:** Die GitHub KiCad-10-Actions erzeugen einen **eigenstaendigen** ERC-JSON-Bericht, nativen Netlist-Export und dreiseitiges PDF sowie die Netzlistenpruefung [`tools/check_trippower_native_netlist.py`](../../../tools/check_trippower_native_netlist.py) fuer alle kritischen Pins. Der Teststand ist ein **Schaltplanentwurf**; bis der aktuelle Action-Lauf erfolgreich abgeschlossen ist, keine globale/ERC-Clean-Aussage und keine Freigabe behaupten. Keine eigenstaendige PCB-Datei, kein geroutetes DRC, keine Hardwaremessung.

**Verbindliche Manufacturing-Gates:** F302 verwendet als Candidate Littelfuse **58-V-MINI-FL1 PCB-Halter `178.6764.0001`** und **2-A-Sicherung `0997002.WXN`**. Die physische Sicherungsschnittstelle ist im Schaltplan gezeichnet, **Herstellerlandpattern/PCB-Footprint aber bewusst noch nicht zugewiesen**. Die 2-A-Sicherung ist KEINE garantierte 1-A-Begrenzung des Zusatzabgriffs; Leiterbahnen/Kabel, Schmelzintegral und LM74930-SCP muessen auf den tatsaechlichen Schutzfall abgestimmt werden. Zudem sind 202-V-MOSFET-SOA/thermische Q301-Verluste, 9-V-VS-Chargepump-Start, 3x3.32k-VS-Pulsfestigkeit, das FCH0650-Spulen-Landpattern, RUN-OFF/Backfeed und EMV nicht freigegeben. Die zugelieferten Standard-Footprints und 3D-Verweise sind vor Bestellen dennoch manuell zu qualifizieren.

## Nutzerentscheidung und Werte-Freeze zur LM74930-Schutzstufe (14.10.2026)

**Fest vorgegeben: LM74930QRGERQ1 statt LM74800 fuer das NEUE eigenstaendige TripPower-Modul.** Der bisherige TripTracer-Schaltplan 01I mit LM74800 bleibt bis zur separaten Modulimplementierung unveraendert. 5V-Buck bleibt LMR38020SQDDARQ1.

- [Ausfuehrliche Auslegung einschliesslich OC/SCP, 9V/202V, UV/OV, Thermik und Safety-Gates](LM74930_DIMENSIONING_2026-10-14.md)
- [Maschinenlesbarer 24-Pin+RTN-Netzplan und Werte-/MPN-Kandidaten](lm74930_design_v1.json)
- [Auslegungstest mit TI-Formeln und Eckwerten](../../../tools/check_trippower_lm74930_values.py) (**Python-Mathematik, KEIN KiCad ERC/DRC oder Labortest**)

**Vorlaeufig 5mOhm Shunt, RSET=50Ohm, RILIM=33,2k (nom. 3,61A), RISCP=470Ohm (nom. 5,03A), CTMR=47nF+RTMR=100k Latch-Off, UVLO ~7,52V Start, OV-Abschaltung ~35,89V.** Die Vorbemessung des VIN_PROTECTED-Zweigs betraegt 1A, jedoch erst nach eigener nachgewiesener Abzweig-Sicherung/Steckerkontakt/Kabel-I2t. Thermik und SOA des bestehenden STD17NF25 bei erhoehter Eingangsleistung sind **offen**. Kein Versprechen fuer ~9V-Start bei 10k-VS-Versorgung ohne Test, keine 202V/350ms-Freigabe.


## Controllervergleich 14.10.2026: Schutz mit elektronischem Circuit Breaker

[Vergleich LM74800-Q1 / LM74930-Q1 inkl. Kosten, Livebestand und TI-Referenz](CONTROLLER_COMPARE_LM74800_LM74930_2026-10-14.md).

**Aktuelle fachliche Empfehlung fuer die NEUE, kopierbare TripPower-Platine: LM74930-Q1 (noch kein Teile-Freeze).** Gegenueber dem LM74800 bietet er OCP, schnelle Kurzschlusserkennung, Einstell-Timer, FLT und IMON. Ein gemeinsam ausgelegter Shunt **vor** der Aufteilung sichert den Gesamtpfad hinter den Schutz-FETs. Der externe VIN_PROTECTED-Abzweig bekommt weiterhin seine **eigene Kurzschluss-/Leitungsabsicherung**. Die aktive TripTracer-`01I_LM74800_INPUT.kicad_sch` bleibt bis zur verifizierten Entscheidung UNVERAENDERT. 9V-Bootstrap, Ruhestrom, passende FET-/Shunt-Werte, Gate-/OV-Sicherheit, physische PCB-Anschluesse und LCSC/DE-Beschaffung sind noch offene Gate-A/B-Punkte.

**Preisdelta nur Schutz-IC, Mouser DE Snapshot 14.10.2026:** +2,81 EUR/1pc, +2,19 EUR/10pcs, +1,88 EUR/100pcs gegenueber LM74800; OCP-Zusatzpassive/Kelvin-Shunt/QFN-Bestueckung sowie Versand/USt. kommen hinzu. Entscheidung ueber das vollstaendige Modul erst nach BOM auf gleichem Schutzumfang.


**Stand 2026-10-14: eigenstaendiger KiCad-10-Zweiseitenschaltplan EXISTIERT, aber keine eigene geroutete Leiterplatte und keine Labor-/ISO-/Fertigungs- oder Fahrzeugfreigabe.**

## Ziel

Eine **einzelne, spaeter ohne TripTracer abtrennbare und als ganzen Ordner kopierbare Platine** fuer eine 9–30-V-DC-Quelle (12-/24-V-Bordnetz) mit 5,0 V/2 A (10 W). Die Bauteile stammen soweit geeignet aus den bestehenden Hersteller-Referenzschaltungen und dem aktuellen TripTracer-Branch. Nicht mehrere unfertige Versorgungsvarianten parallel erfinden.

Der derzeitige V1-Schaltplan im TripTracer-Projekt ist weiter die **einzige aktive Schaltungswahrheit**:
- [Aktiver Eingangs-/Verpol-/OV-Schutz](../../kicad/01I_LM74800_INPUT.kicad_sch) mit TI LM74800QDRRRQ1 und zwei FETs, aber **OHNE elektronische Eingangsstrombegrenzung**;
- [Aktiver 5V/2A-Buck](../../kicad/02_5V_Buck.kicad_sch) mit LMR38020SQDDARQ1, 15µH und 3x22µF am Ausgang, EN direkt an eigenem geschuetztem VIN;
- [ACC/HOLD](../../kicad/01H_ACC_HOLD_GATE.kicad_sch) und [USB/3V3](../../kicad/03_3V3_USB.kicad_sch) gehoeren zum **TripTracer-Geraet**, nicht als untrennbarer Teil auf eine fremde Universalplatine.

**Maschinenlesbarer Vertrag:** [module_contract.json](module_contract.json). Bei Unklarheit ist `AGENTS.md` und die neueste verbindliche Hardwareentscheidung massgeblich. Inaktive/historische Tests in Docs sind kein Schaltungsfreigabenachweis.

## Hardware-Grenze / Modulanschluesse (vorgeschlagen, noch NICHT elektrisch umgesetzt)

| Signal | Richtung | Funktion |
|---|---|---|
| `VIN_FUSED` | Eingang | Von **geeignet abgesicherter** DC-Quelle; 9–30 V Normalbetrieb. Bei Fahrzeugbetrieb geeignete, ohne Entloeten tauschbare Sicherung nahe der Quelle |
| `GND` | gemeinsam | Modul- und Verbraucher-Masserueckleitung; geringe Schleifen und stern-/flaechenbewusstes Layout |
| `5V_OUT` | Ausgang | 5 V / max. 2 A. Ausgangskurzschluss-, Ueberlast-, Rueckspeisungs- und Entladeverhalten pruefen |
| **`VIN_PROTECTED`** | **Pflicht-Ausgang** | **Unregulierte Bordnetzspannung nach LM74800-Verpol-/OV-Schutz; eigener Abzweig-Kurzschlussschutz zwingend, Strombelastbarkeit noch OFFEN.** |
| `RUN_CMD` | optionaler Eingang | Ziel: 3,3-V-/5-V-kompatibler aktiver Einschaltbefehl, schwebend = AUS im gesteuerten Modus; **eigene Schutz-/Pegelstufe erforderlich**, noch nicht konstruiert |

## Verbindlicher VIN_PROTECTED-Abzweig – SICHERHEITSSPERRE

Die fertige TripPower-5V/2A-Platine MUSS neben `5V_OUT` einen **physisch zugänglichen Anschluss `VIN_PROTECTED`** haben. Der Abgriff erfolgt **hinter der LM74800-Q1-Verpol-/Ueberspannungs-Abschaltstufe, vor dem LMR38020-Q1**. Der bisherige Schaltplanknoten `HV_PROTECTED_AFTER_EFUSE` liegt zwischen Q922 Drain / U921 OUT und U101 VIN und ist die vorgesehene Quelle des Abzweigs; der Name `...EFUSE` ist historisch und bedeutet **keine eFuse-Funktion**.

```text
 VIN_FUSED (9–30 V nominal; externe Quellsicherung Pflicht)
             |
    LM74800-Q1 + Schutz-FETs
             |
      VIN_PROTECTED_MAIN
             +-------------------> LMR38020-Q1 ---> 5V_OUT / 2A
             |
        SEPARATER ABZWEIG-
        KURZSCHLUSSSCHUTZ
             |
       VIN_PROTECTED ---> echter PCB-Anschluss + Messpunkt
```

> **KRITISCH – KEINE DIREKTE UNGESICHERTE EXTERNE LEITUNG:** Der LM74800-Q1 bietet **keine Strombegrenzung/keinen eFuse-Schutz**. Ein Kurzschluss am externen `VIN_PROTECTED`-Ausgang kann sonst die MOSFETs, Leiterbahnen, Stecker oder den Fahrzeugkabelbaum gefaehrden. Vor dem externen Abgriff muss deshalb eine **eigenstaendig dimensionierte und nachgewiesene Abzweig-Strombegrenzung oder passende, DC-bemessene, wartbar austauschbare Sicherung** vorgesehen werden. Zusaetzlich bleibt die abgesicherte Fahrzeugzuleitung zwingend. Schutz-Nennstrom, I²t, DC-Abschaltvermoegen, Kabelquerschnitt, Leiterbahn und Steckverbinder sowie thermische Fehlerfaelle sind noch **OFFEN**. Daher ist der Abzweig **noch nicht zur Benutzung oder Fertigung freigegeben**.

- `VIN_PROTECTED` folgt ungefaehr der **9–30-V-Bordnetzspannung**, ist **UNGEREGELT**, **kein 15-V-Ausgang** und nicht automatisch EMV-/ripplefrei. Bei OV-Abschaltung und Last kann die Spannung verschwinden; Kurzschluss und Versorgung durch externe Verbraucher separat pruefen.
- Die maximale zulaessige Ausgangsstromstaerke ist **noch nicht festgelegt**. Ein Zusatzverbraucher wird **zusaetzlich** zu den maximal 5 V / 2 A des Bucks in Fahrzeugquellenstrom, FET-SOA und Waermebilanz beruecksichtigt.
- **Aktueller KiCad-Stand:** Der VIN_PROTECTED-Abzweig ist auf der eigenen Schutzseite real verdrahtet und als J302.1 vorgesehen; F302 58V-MINI mit realem Sicherungssymbol ist im Strompfad, aber **F302-Halter-Footprint, DRC/PCB-Landpattern und I2t/Leitungsnachweise offen**.

### Bevorzugte Display-Anbindung (TripTracer, ausserhalb TripPower)

Fuer das Riverdi RVT35HITNWC00-B bevorzugen wir einen separaten **5-V-auf-LED-Konstantstrom-Boost** hinter `V5_SYS` (USB-/Buck-Umschaltung). Die Hintergrundbeleuchtung benoetigt typ. ca. **15 V bei 100 mA**; es handelt sich um eine LED-Last, nicht um einen frei nutzbaren geregelten 15-V-Eingang. **TI TPS61165-Q1** ist ein noch zu verifizierender Treiberkandidat (PWM-Dimmung); die LED-Vorwaertsspannung, Stromregelung, Open-LED-Abschaltung und EMV sind zu validieren. Bei geschaetzten 85 % Effizienz beanspruchen 1,5 W LED-Ausgang **ca. 0,35 A an 5 V** und damit einen Teil des **bestehenden 2-A-Gesamtbudgets**. Bei USB-Only-Betrieb muss die zulaessige USB-Stromaufnahme separat geprueft und das Backlight ggf. abgeschaltet werden.

Der `VIN_PROTECTED`-Ausgang wird **trotzdem verbindlich auf TripPower vorgesehen**, unabhaengig davon, ob der TripTracer ihn fuer das Display spaeter nutzt. Ein direkt angeschlossener Buck-/Boost-Treiber am unregulierten Hilfsausgang waere erst nach gesonderter 9–30-V- und Schutzpruefung zulassig.

**Standalone statt gesteuert:** Eine spaetere klar beschriftete **hardwareseitige Bruecke `ALWAYS_ON`** soll den Wandler ohne MCU mit gesteckter Versorgung einschalten. Im TripTracer steuert eine getrennte ACC/HOLD-Anpassstufe `RUN_CMD`. Vor Schaltplan-Umsetzung der Pegelanpassung sind Funktion, Stromverbrauch, Fail-OFF und Auswirkungen auf VIN/EN verbindlich zu pruefen; eine externe MCU-3,3-V-Schiene darf **nicht** direkt die 56-V-VS-Schiene oder das Fahrzeugnetz rueckspeisen. **Eine Fehlverdrahtung von Buck-EN oberhalb Buck-VIN waere unzulaessig.**

**Bewusst NICHT auf der Universalplatine:** M8-Fahrzeugbelegung, Zeitnachlauf/TLC555, ESP32, 3V3-LDO, USB-C-/TPS2116-Umschalter, Display-Backlight, GNSS. Diese Funktionen bleiben fuer TripTracer extern am Moduladapter. Es wird **kein** Anspruch auf USB-Backfeed-Schutz durch die DC/DC-Platine allein erhoben.

## COTS FIRST – Bestand und Vergleich

Der projektweite, bereits durchgefuehrte [Hersteller-/Kaufmodulvergleich](../../../docs/COTS_POWER_SUPPLY_EVALUATION.md) ist vor dem Re-Use-Entwurf erneut gesichtet:

| Kandidat | Vorteile | Grund fuer den aktuellen Stand |
|---|---|---|
| **TI LMR38020-Q1** (ausgewaehlt) | AEC-Q100, 4,2–80 V, 2 A, EN, Buck-OC/Hiccup/TSD; vorhandener TI-400kHz-EVM/Referenzschaltplan | Bleibt Kern; hoechste Wiederverwendung aktueller KiCad-Bauteile, aber eigene PCB/EMV/Thermik weiterhin zu qualifizieren |
| RECOM R-78K5.0-2.0L | Fertiger 5V/2A-SIP3-Regler, handloetbar | 6,5–36 V und kein EN; eigener vorgeschalteter OFF-Schalter noetig; Automotive-ISO-Test-A und Eingangskurzschluss nicht dadurch geloest |
| RECOM RPH-3.0-CT | Bis 55 V, 3 A, ON/OFF integriert | 47-Pad-SMD-Modul schwieriger handzuloeten, keine vollstaendige 200V-/Fahrzeugschutzloesung |
| TI LM74930-Q1 | Integrierte einstellbare Ueberstrom-/Kurzschlussschutzfunktion neben Verpol/OV | Sinnvolle Alternative, wenn extern abgesicherter LM74800 wegen gefaehrlicher Fehler nicht qualifizierbar ist. **Keine eigenmaechtige Teileumstellung** |

Herstellerquellen: [TI LMR38020-Q1](https://www.ti.com/product/LMR38020-Q1), [TI LMR38020QEVM](https://www.ti.com/tool/LMR38020QEVM), [TI LM7480-Q1](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf), [TI LM74930-Q1](https://www.ti.com/product/LM74930-Q1), [RECOM SIP3](https://recom-power.com/de/products/switching-regulators/switching-regulators-sip/rec-p-R-78K5.0-2.0L.html).

**Kostenkontrolle:** Bestehende Einkaufsansätze sind keine aktuellen verbindlichen Komplettpreise. Fertiger Vergleich fuer **1/10/100 Stueck** muss Buck und Schutz inklusive Fuse, FETs, Kondensatoren, PCB, Handloeten/PCBA, Versand/MwSt. gegen Module bei gleichem Sicherheitsumfang stellen. Kein erdachter Gesamtpreis. Vorhandene aktive Buck-Teileliste: [5V-BOM](../../kicad/TripTracer_5V_BUCK_SELECTED_BOM.csv).

## Sicherheits- und Nachweisgates vor der eigenstaendigen Leiterplatte

1. **Input-Schutz und Fail-Safe:** LM74800 hat keine eFuse-/OCP-Funktion. Kurzschluss zwischen Eingangs-Pads, FETs und Buck-VIN sowie defekter MOSFET: Fahrzeug-/Leitungs-Sicherung mit DC-Abschaltvermoegen, I2t und Temperatur pruefen; OCP-Alternative ggf. mit TI LM74930 kostenbewusst vergleichen. 200-V-Load-Dump Test A / Test B getrennt nachweisen.
2. **9-V-Kaltstart und Abschalten:** R921 10k/VS-Aufladung, D924 A→VS, heisse Transistorleckstroeme und geforderter OFF-BAT-Strom. Fuer das universelle RUN-Signal gilt **definierter, rueckspeisungsfreier Zustand**, auch wenn V5_OUT zuvor aus einem fremden USB-/Netzteil gespeist wurde.
3. **Exakte Herstellergeometrie:** U921 RTN13 **isolierte** Kupferinsel (nicht GND); FCH0650-150M-Landpattern **noch provisorisch**; EP9 von LMR38020 thermisch anbinden. 3D-Modelle nur aus realen Quellen.
4. **Schaltplan und PCB:** Erst nach Gate A/B eigener KiCad-10-Root mit **echten** Ein-/Ausgangsnetzen und Bauteilen, nur lokalen Symbolen/Footprints/3D. Native ERC **fuer das eigenstaendige Modul**; Routing mit Stroembahnen, Rueckstrom, Thermal-Vias, TVS-/Transientenpfaden und anschließend DRC. Der aktuelle `TripTracer_V1.kicad_pcb` ist hierfuer nicht die finale Modulplatine.
5. **Labor vor Fertigung/Fahrzeug:** 9/12/24/30 V x 0/0,5/1/2 A, >2A-Kurzschluss und Fehler hinter/vor Buck, 9-V-Start/Stop, 60–80-°C-Gehause-Szenarien, Ripple/Schwingen/EMV, Verpolung, getrennte ISO-Transienten und unguenstige Sicherungs-/Kabelimpedanzen. Ein passendes Modul kann bei einer Stoerung sauber abschalten; es darf nicht thermisch gefaehrlich werden.

**Thermische Vorplanung:** Bei 10 W OUT und angenommenen 85 % Buck-Wirkungsgrad entstehen ca. 1,76 W Buck-Verluste; FETs, Sicherung, Leiterbahnen und EMV kommen dazu. **2,5 W ist eine grobe Layout-Planungsreserve, keine garantierte maximale Gesamtverlustleistung.**

## Arbeitsreihenfolge nach AGENTS.md

- **Schritt 1 – abgeschlossen:** Diese Wiederverwendungs-/COTS-/Schnittstellenentscheidung versionieren. Bestehende TripTracer-Schaltung und BOM fuer diesen Planungsschritt nicht veraendern.
- **Schritt 2 – SCHALTPLANENTWURF vorhanden, nicht qualifiziert:** LM74930 statt LM74800 nach Nutzerentscheid, RUN/ALWAYS_ON, OV/UV/Breaker und VIN_PROTECTED real gezeichnet. Fail-OFF, Quelle/F302, VS-Start und 200V/MOSFET-SOA als harte Datenblatt-/Laborgates offen.
- **Schritt 3 – offen:** Rueckkopplung/Regelkreis, Buck-Eingangsfilter und vollstaendige 5V/2A-BO-MPN-/Footprint-/DC-Bias- und thermische Verifikation. Einzelseitiger KiCad-10-ERC/Netlist-Gate plus parallele TripTracer-Regressionspruefung.
- **Schritt 4 – TEILERFUELLT:** Separates kopierbares KiCad-10-Projekt mit Root, echten Schaltplan-Unterseiten, lokalen Symbolen/Footprints und automatischem Schaltplan-PDF erzeugt. **Eigenes PCB, DRC, 3D-Vollstaendigkeit, bestellfertige BOM und Freigabe weiterhin offen.**
- **Schritt 5 – offen:** 2- oder 4-Lagen-Auswahl anhand EMV/Thermal, Footprints, Layout, DRC, Fertigerregeln, Kosten und USB-Rueckspeiseszenarien; Labortest-/Sicherheitsreport.

**Keine fertige Platine vorgaukeln:** Der Ordner enthaelt jetzt einen echten kopierbaren KiCad-Schaltplan, **aber KEIN freigegebenes PCB oder fertigungssicheres Modul**. Die Schaltplanpruefungen ersetzen keine Hersteller-Puls-/Thermik-/FET-SOA-/ESD-/ISO-Gates.

## Kurzprotokoll Schritt 1

- Hersteller COTS erneut geprueft; bestehender TI LMR38020-Q1-Buck bleibt ohne Teile-Swap.
- Signale und klare Verantwortung zwischen Modul, Quelle und TripTracer definiert.
- Die bestehenden TripTracer-01I/02-Aktivblaetter, sein Root und PCB wurden **nicht** geaendert; separate TripPower-KiCad-Dateien gebaut und eigene KiCad-10-ERC-/Netlist-Checks im Workflow hinzugefuegt. Aktuelle CI-Ergebnisse vor einer Freigabe nachlesen.
- Offene kritische Entscheidungen sichtbar: LM74800 ohne OCP, ~9V-VS-Start, Fail-OFF und Geometrie FCH-Spule.
- Keine neue Bestellung, keine Kostenzusage, keine Fahrzeugfreigabe.
