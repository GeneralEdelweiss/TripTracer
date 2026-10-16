> **Neue Bauteilrevision 15.10.2026:** R313/R314/R315 = je **3,3 kΩ Vishay CRCW25123K30FKEGHP (2512, AEC-Q200, pulsfeste CRCW-HP-Serie)** als nach [Hersteller-Pulsdiagramm](https://www.vishay.com/docs/20043/crcwhpe3.pdf) und [Mouser](https://eu.mouser.com/en/ProductDetail/Vishay/CRCW25123K30FKEGHP) konkretisierter **Bauteilkandidat** in der Standalone-KiCad-Schaltung. Gesamtkette 9,90 kΩ statt historisch 9,96 kΩ. **KEINE FREIGABE:** pulsgeprüftes Datenblatt ersetzt nicht 85°C/155°C-Filmtemperatur, Wiederholung, Leiterplatten-Kühlung, Zener-Kurzschluss oder 9-V-Startmessung. Siehe [neuer Stress-Gate-Bericht](INPUT_STRESS_GATE_2026-10-15.md). Historische Rechnungen auf 3,32 kΩ unten gelten nur für die frühere Revision.

# TripPower LM74930-Q1 – konkrete Schutzstufen-Dimensionierung

> **Verbindliche Folgeentscheidung 14.10.2026:** **EINE** austauschbare, geeignete DC-Hauptsicherung der Fahrzeugzuleitung **vor** dem TripTracer-Strompfad, nahe der Quelle. Keine separate Hilfszweig-Sicherung auf TripPower oder TripTracer. Der im bisherigen Text fuer den Hilfsausgang genannte separate Fuse-Pfad wurde ersetzt: `VIN_PROTECTED_UNFUSED` liegt jetzt ohne F302 direkt hinter R301. **3 A ist nur ein Auslegungsbeispiel**; bei 9 V / 5 V 2 A / AUX 1 A sind ca. 2,39 A Quelle moeglich, fuer eine typische 58V-MINI-3A-Sicherung ist bei 80 °C aber nur ca. 2 A Dauerlast laut [Littelfuse-Derating](https://www.littelfuse.com/assetdocs/automotive-passenger-car-catalog?assetguid=613475c5-28ce-4646-a46e-0a9344b7a944) angesetzt. Bei 4 oder 5 A sind Leiterbahnen und Kabel entsprechend des realen Ausloese-I2t und moeglichen Kurzschlussstroms zu dimensionieren. Zusicherung einer 3-A-Strombegrenzung gibt es nicht.


**Stand 2026-10-14 | User-Entscheidung: LM74930QRGERQ1 fuer NEUES Kopiermodul fest; Haupt-Buck LMR38020SQDDARQ1 bleibt.** 
**Status: Werte- und Pinplan erstellt, keine aktive KiCad-Umstellung, kein eigenstaendiger ERC/DRC, keine Labor-, ISO-, Fahrzeug- oder Bestellfreigabe.**

Basis: [AGENTS.md](../../../AGENTS.md), [Modulvertrag](module_contract.json), [auswertbarer Pin- und Werteplan](lm74930_design_v1.json), [TI SNOSDF6](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) 8.2 Fig.8-1 / Formeln 14–18, [TI Design Calculator](https://www.ti.com/tool/download/LM74930-CALC/REV-A), [TI E2E zur erforderlichen D1-VS-Startdiode](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1411181/lm74930-q1-question-regarding-disabling-reverse-current-blocking-and-it-s-effect-on-the-imon-pin).

## 1. Was genau darf durch die Schutzstufe?

| Verbraucher | Auslegungsanforderung | 9-V-Eingangsstrom |
|---|---|---:|
| Hauptregler LMR38020-Q1 | 5 V x 2 A = **10 W** | ca. 1,31 A bei 85 % / **1,39 A bei 80 %** Wirkungsgrad |
| Externer Ausgang VIN_PROTECTED_UNFUSED | **zunaechst 1,0 A maximale Strom-Zielgroesse, vorbehaltlich gemeinsamer Hauptsicherungs-, Kupfer- und FET-Nachweise** | 1,0 A |
| **Gemeinsamer Strom hinter den Schutz-FETs** | **ca. 2,4 A bei 9 V** (80 %-Annahme) | 2,39 A |

Bei einem angehaengten Verbraucher an `VIN_PROTECTED_UNFUSED` ist dessen Laststrom **nicht** identisch mit dem 5-V-Ausgangsstrom. Bei 30 V und 1 A Zusatzabgriff nimmt dieser Verbraucher bereits 30 W auf: Quelle, Kontakt, externer Abzweig, Layout und Verlustleistung sind deshalb gesondert zu dimensionieren.

**Grundschaltung / Shunt-Position:**

```text
 abgesicherte 9..30V DC Quelle -- Q_HV 250V -- Q_IDEAL 60V -- [R_SENSE 5mOhm] --+--> LMR38020/5V/2A
                                                                                    |
                                                                                    +--> J302.1 VIN_PROTECTED_UNFUSED (OHNE eigene Zweigsicherung)
                                                                                | 
                                                             Systemweit F_MAIN extern vor VIN_FUSED
```

Alle 24 LM74930-Pins + isolierter RTN-Thermalpad sind im [Werteplan](lm74930_design_v1.json) konkret einem Netz oder NC zugeordnet. Besonders: **CS+ und CS- als Kelvin-Verbindung zu BEIDEN Messwiderstandsseiten**, **RSET 50 Ohm zwischen C und CS+**, **ISCP 470 Ohm vom Q2-Drain**, MODE auf VS, OVCLAMP an GND (**Cut-Off**, nicht lineares OV-Clamping), RTN-Pad elektrisch isoliert (**nicht GND**). U101-Buck-EN bleibt am eigenen geschuetzten VIN.

## 2. Einstellwerte, TI-Formeln und Grenzen

| Bauteil | Gewaehlter Wert | Rechenfunktion / Status |
|---|---:|---|
| Controller | LM74930QRGERQ1 | **Controller fixiert**, RGE-24 Pin/RTN gem. Datenblatt |
| RSENSE | **5 mOhm**, 1 %, 2512 >=1 W | Messung VOR den beiden Verbrauchern; TA-I Tech RLM25FEER005 (LCSC C185817) derzeit **MPN-Kandidat, AEC/Footprint pruefen** |
| RSET | **50 Ohm**, 1 % | TI empfohlene 50–100 Ohm, zwischen C und CS+ |
| RILIM | **33,2 kOhm**, 1 % | `I_OC=12*50/(33200*0.005)=3,614 A` |
| RISCP | **470 Ohm**, 1 % | `I_SCP=(0,020+470*11uA)/0,005=5,034 A` |
| CTMR | **47 nF**, X7R | `t_oc~1.2*C/82.3uA=0,685 ms` **ohne** 100k-Parallelresistor, der die reale Abschaltzeit aendert |
| RTMR | **100 kOhm** zu GND | TI Latch-off statt Auto-Retry nach Fault, Ruecksetzung per EN-Low oder VS-Powercycle |
| RIMON | **6,8 kOhm** zu GND | Optionale Stromanzeige: nominal ca. 1,5 V bei 2,4 A; ADC-Kopplung/Filter offen |
| R_OV_TOP | **2 x 750 kOhm** in Serie | Direkt am RAW abgesicherten VIN **vor** dem HV-FET, um Load-Dump trotz geoeffnetem FET zu detektieren |
| R_OV_BOTTOM | **25,5 kOhm** | OV-Abschaltung nominal **35,89 V** |
| R_UV_TOP | **2 x 750 kOhm** in Serie | Direkt am RAW abgesicherten VIN fuer Kaltstart-Unterspannung |
| R_UV_BOTTOM | **130 kOhm** | Einschalten nominal **7,52 V**, Abschalten ca. **6,90 V** |
| R_VS | **3 x 3,32 kOhm in Serie**, pulsfest | Gesamt **9,96 kOhm** nach TI-10k-Referenz, konkreter 200V-fester MPN **nicht festgelegt** |
| DZ_VS / CVS | **56-V-/3-W-Zener / mind. 1uF** | Aus altem LM74800-Kandidatenstand; echte 202V-Puls-/Temperaturpruefung offen |
| D_BOOST A→VS | **BAV21WQ-7-F** (200 V AEC-Q101, SOD-123) | Anode A/COMMON_SOURCE, Kathode VS. Gegenueber altem 75V-1N4148WSQ mehr Reverse-Marge, exakte Spannungstransienten pruefen |
| CCAP / C_COMMON | 100nF CAP–VS / 1uF A–GND | Effektive Kapazitaet mit DC-Bias/Temperatur und kurze Massewege pruefen |
| C_DVDT + RG | 10nF HGATE–OUT + 100Ohm | **Nur Startwert:** Q_HV-SOA/Inrush/Buck-Eingangskapazitaet auf realem Modul nachweisen |
| Q_HV | STD17NF25 / 250V / 165mOhm max | **NOCH NICHT FIXIEREN**; hoehere Leistung durch Zweiglast erfordert heisse RDS-/SOA-/Layoutrechnung |
| Q_IDEAL | BUK7Y4R8-60EX / 60V / 4,8mOhm @10V | Vorlaeufig wiederverwendbar, 60V VDS und VGS/ISO-Puls pruefen |

**Begrenzung OCP:** Mit TI-Komparatorschwelle 1,08..1,32 V zu 1,22 V typ, sowie 1 % Toleranz fuer RSET, RILIM und RSENSE erhaelt man ueberschlaegig **3,10–4,04 A**. Diese Abschaltung muss zeitlich und thermisch mit dem FET und der Zuleitung abgestimmt werden.

**Schneller SCP:** Mit 17,4–22mV im IC, 9,5..12uA ISCP Bias und 1 % Widerstaenden ungefaehr **4,32–5,60 A**. Ein paar Mikrosekunden Fehlerstrom koennen trotzdem fuer Steckkontakte oder Bauteile kritisch sein. Die Bereiche ueberlappen nach dieser ersten komparatorbasierten Eckwertrechnung nicht; Leiterbahninduktivitaet, Waerme und Inrush ungetestet.

**Warum UVLO tiefer als 9 V?** Das 9-V-Ziel ist ein weiches Motorstartziel, kein gefordertes garantiertes Funktionieren bei 6 V. Ein UVLO-Einschaltpunkt von 7,52 V erlaubt bei 9 V nominell Startreserve. Unter TI-VUVLOR von 0,585..0,63V, 1 % Widerstand und als konservativer ±0,2uA Stromeinfluss in den UVLO-Pin bleibt der berechnete Worst-Case-Einschaltpunkt <9V. Das ist **nicht** dasselbe wie ein erfolgreiches Gate-/VS-Chargepump-Startverhalten.

**OV-Schwelle:** Mit 0,585..0,63V und denselben Widerstands-/Leckstromannahmen liegt sie grob **34–39 V**; genaue Zahlen liefert [CI-Skript](../../../tools/check_trippower_lm74930_values.py). Oberhalb 30 V normal wird getrennt, aber deutlich unter dem 80V-Max des Buck-Reglers. VIN_PROTECTED_UNFUSED verschwindet bei OV. **Bei 202V RAW sind die beiden OV-750k einzeln mit ungefaehr 100V beaufschlagt; Puls-Arbeitsspannung und Platinenkriechstrecken pruefen.**

**Ruhestrom:** Die beiden direkt an VIN angeschlossenen OV-/UVLO-Teiler brauchen bei 30V zusammen rechnerisch ca. **38uA**, der LM74930 im Shutdown bis **5uA** gemaess TI, zusaetzlich kommen TVS-/Zener-/Pegelwandler-/Kondensatorleckstroeme. Das gesamte TripTracer-BAT-OFF-Ziel **<100uA bleibt offen**, insbesondere bei +70 bis +125 Grad an Bauteilen.

## 3. Gefaehrliche Bauteilstressfaelle – wichtig

**R_VS bei 202V Lastdump, 350ms:** Bei nominell 56V-Zener liegen 146V ueber 9,96kOhm. P`RVS=(146)^2/9960 = 2,14W`, Energie **0,75J** (rechteckiges 350ms-Stressszenario) verteilt auf drei 3,32kOhm-Widerstaende: **ca. 0,25J je Widerstand**. Die Zener verheizt nominell ca. **0,82W**. **3 x 1210 wegen nomineller Wattzahl allein NICHT freigeben**. Genaue Hersteller-Pulsdiagramme, Start bei 9V und heisse Wiederholung muessen passen. E2E-Hinweise von TI zeigen, dass ein 10k-VS-Widerstand allein beim Start einbrechen kann; deshalb die A→VS-Diode NICHT wegoptimieren.

**HV-MOSFET am kombinierten 9V-Maximalbetrieb:** 10W/80% bei 9V plus zusaetzlich 1A = **2,39A**; bei maximalem RDS(on) des STD17NF25 von 165mOhm **ca. 0,94W bei 25C**. Bei hoher Temperatur steigt RDS(on) und damit Verlustleistung. Das ist nicht mit der MAXIMUM-SOA bei 202V und Abschaltzeit gleichzusetzen. Erwaegenswert ist ein 250-V-MOSFET mit niedrigerem RDS(on), sofern real verfuegbar und kein unvertretbarer Aufpreis. Aktuell erst QHV-Kandidat, **nicht MPN-Freeze**.

**VIN_PROTECTED_UNFUSED-Fehler:** Ein Kurzschluss am Zusatzabgriff kann den gesamten elektronischen Circuit Breaker und damit die 5 V abschalten. **KEINE separate Abzweigsicherung**: Die eine austauschbare Hauptsicherung F_MAIN in der Fahrzeugzuleitung muss passend fuer ALLE dahinterliegenden Steckverbinder, Leitungen und Leiterbahnen dimensioniert sein. Bei FET-Kurzschluss kann der LM74930 nicht helfen. Nennspannung/Abschaltvermoegen, I2t, Zeit-Strom-Kennlinie, Kupfererwaermung und Brandverhalten sind noch NICHT nachgewiesen. Kein direkt ungesicherter Ausgang am Shunt.

**Start/Kondensatoren:** Das 5V-Buck-Eingangsnetz benoetigt lokale MLCCs, die bei VIN=30V wirksam bleiben. Kein grosser 100uF-Hold-up aus der TI-45W-EVM blind kopieren. Die VOUT-Inrush-Spitze hinter den Schutz-FETs, 0,69ms-Timer, TPS2116-Anlauf und 3.3V-Diagnose sind im Verbund zu testen.

## 4. Konkrete KiCad-Schritte nach AGENTS.md

1. **Eigenes** `TripPower_5V2A.kicad_pro` mit Rootseite, eigenen Unterseiten `01_Protection_LM74930.kicad_sch` und `02_5V_LMR38020.kicad_sch` sowie lokalen Bibliotheken und genau EINEM eigenen PCB aufbauen. Aus alter TripTracer-01I keine FET-/TVS-Symbole ungeprueft uebernehmen; bei U921 → U_PROT alle 24 RGE-Pins gemaess TI zuordnen, RTN Pad elektrisch FLOAT (nicht 13=GND verwechseln).
2. Schutzschaltung und `VIN_PROTECTED_UNFUSED`-Stecker **physisch verdrahten**, R_SENSE an Q2-Drain Kelvin, nach Shunt Hauptbuck + direkter J302.1-Abzweig ohne eigene Sicherung; Quellsicherung F_MAIN extern zwingend und fuer ALLE Leiterbahnen berechnen. Allgemeines `RUN_CMD` muss 3,3V/5V + ALWAYS_ON ohne MCU erlauben und bei OFF/BAT reverse/USB backfeed sicher sein.
3. Erst wenn R_VS-Puls, Anlauf, MOSFET-SOA, OV/UV, Run-Pegelschutz und Zweigsicherung in Datenblattrechnung tragbar sind, Schaltplan-Gate A/B und **eigenstaendigen nativen KiCad-10-ERC** ausfuehren. Ein bestandenes **reines Python-Rechenskript** ist keine ERC-Freigabe.
4. Footprint-Pads/3D, Layoutstrompfad und thermische Polygonflaechen sowie reale Jumper/Stecker bestaetigen; natives PCB-Parity-/DRC, danach Messung 9/12/24/30 V x 0..2A, zusaetzliche 0..1A Auxiliary, Fehlerstrom, Latch-Off und OEM-/ISO-Impulse.

**Noch offen und nicht behauptet:** Ein kompletter verfuegbarer BOM-/Kostenkorb fuer 1/10/100, exakte SI/EMV-Werte, KiCad-10-ERC/DRC, 9V-Kaltstart in Hardware, 202V/350ms und Temperaturzulassung. **Keine Platine bestellen.**
